"""
PII Detection Service
Identifies Personally Identifiable Information in documents
"""
import re
from typing import Dict, List, Tuple
from loguru import logger


class PIIDetector:
    """Detect various types of PII in text content"""

    def __init__(self):
        # Regex patterns for different PII types
        self.patterns = {
            "ssn": [
                r'\b\d{3}-\d{2}-\d{4}\b',  # XXX-XX-XXXX
                r'\b\d{3}\s\d{2}\s\d{4}\b',  # XXX XX XXXX
                r'\b\d{9}\b'  # XXXXXXXXX (more prone to false positives)
            ],
            "credit_card": [
                r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b'
            ],
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "phone": [
                r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
            ],
            "account_number": [
                r'\b[Aa]ccount\s*[#:]?\s*(\d{8,17})\b',
                r'\b[Aa]cc?t\.?\s*[#:]?\s*(\d{8,17})\b'
            ],
            "drivers_license": [
                r'\b[A-Z]{1,2}\d{6,8}\b'  # Simplified pattern
            ],
            "passport": [
                r'\b[A-Z]{1,2}[0-9]{6,9}\b'
            ],
            "date_of_birth": [
                r'\b(?:DOB|Date of Birth|Birth Date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
                r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b'  # General date pattern
            ]
        }

        # Context keywords that increase PII likelihood
        self.context_keywords = {
            "ssn": ["social security", "ssn", "taxpayer id", "tin"],
            "credit_card": ["card number", "credit card", "debit card", "payment"],
            "account_number": ["account", "bank", "routing"],
            "sensitive": ["confidential", "private", "personal", "classified"]
        }

    def detect_pii(self, text: str, page_number: int = None) -> Dict:
        """
        Detect all types of PII in text

        Args:
            text: Text to analyze
            page_number: Optional page number for citation

        Returns:
            Dict with detected PII and details
        """
        result = {
            "pii_detected": False,
            "pii_types": [],
            "detections": [],
            "severity": "none"  # none, low, medium, high
        }

        detections = []

        # Check each PII type
        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))

                for match in matches:
                    # Get context around match
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    # Validate match with context
                    is_valid, confidence = self._validate_pii(
                        pii_type,
                        match.group(),
                        context
                    )

                    if is_valid:
                        detection = {
                            "type": pii_type,
                            "value": self._redact_value(match.group()),
                            "full_value": match.group(),  # For internal use only
                            "context": self._redact_context(context, match.group()),
                            "position": match.start(),
                            "page_number": page_number,
                            "confidence": confidence
                        }
                        detections.append(detection)

                        if pii_type not in result["pii_types"]:
                            result["pii_types"].append(pii_type)

        if detections:
            result["pii_detected"] = True
            result["detections"] = detections
            result["severity"] = self._calculate_severity(detections)

        return result

    def detect_pii_in_pages(self, pages: List[Dict]) -> Dict:
        """
        Detect PII across all pages

        Args:
            pages: List of page dictionaries with text

        Returns:
            Dict with aggregated PII detections
        """
        all_detections = []
        all_pii_types = set()

        for page in pages:
            page_num = page.get("page_number")
            page_text = page.get("text", "")

            if page_text:
                page_result = self.detect_pii(page_text, page_num)

                if page_result["pii_detected"]:
                    all_detections.extend(page_result["detections"])
                    all_pii_types.update(page_result["pii_types"])

        result = {
            "pii_detected": len(all_detections) > 0,
            "pii_types": list(all_pii_types),
            "total_detections": len(all_detections),
            "detections": all_detections,
            "severity": self._calculate_severity(all_detections)
        }

        logger.info(
            f"PII Detection: {result['total_detections']} detections, "
            f"types: {result['pii_types']}, severity: {result['severity']}"
        )

        return result

    def _validate_pii(self, pii_type: str, value: str, context: str) -> Tuple[bool, float]:
        """
        Validate if detected pattern is likely real PII

        Returns:
            Tuple of (is_valid, confidence_score)
        """
        confidence = 0.5  # Base confidence

        # Check context keywords
        context_lower = context.lower()

        if pii_type in self.context_keywords:
            for keyword in self.context_keywords[pii_type]:
                if keyword in context_lower:
                    confidence += 0.2

        # Specific validation by type
        if pii_type == "ssn":
            # Validate SSN format and check for invalid patterns
            if self._validate_ssn(value):
                confidence += 0.3
            else:
                return False, 0.0

        elif pii_type == "credit_card":
            # Luhn algorithm check
            if self._validate_credit_card(value):
                confidence += 0.3
            else:
                return False, 0.0

        elif pii_type == "email":
            # Check if it looks like a real email
            if '@' in value and '.' in value.split('@')[1]:
                confidence += 0.2

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        # Require minimum confidence
        return confidence >= 0.6, confidence

    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format"""
        # Remove formatting
        digits = re.sub(r'\D', '', ssn)

        if len(digits) != 9:
            return False

        # Check for invalid patterns
        if digits == '000000000' or digits == '111111111':
            return False

        if digits[:3] == '000' or digits[:3] == '666':
            return False

        return True

    def _validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        # Remove spaces and dashes
        digits = re.sub(r'\D', '', card_number)

        # Luhn algorithm
        def luhn_check(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        return luhn_check(digits)

    def _calculate_severity(self, detections: List[Dict]) -> str:
        """Calculate overall PII severity"""
        if not detections:
            return "none"

        high_risk_types = ["ssn", "credit_card", "account_number", "passport"]

        high_risk_count = sum(
            1 for d in detections
            if d["type"] in high_risk_types
        )

        if high_risk_count > 0:
            return "high"
        elif len(detections) > 5:
            return "medium"
        elif len(detections) > 0:
            return "low"

        return "none"

    def _redact_value(self, value: str) -> str:
        """Redact PII value for display"""
        if len(value) <= 4:
            return "***"
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    def _redact_context(self, context: str, value: str) -> str:
        """Redact PII value in context"""
        redacted = self._redact_value(value)
        return context.replace(value, redacted)

    def get_pii_summary(self, pii_result: Dict) -> str:
        """Generate human-readable PII summary"""
        if not pii_result["pii_detected"]:
            return "No PII detected"

        summary_parts = [
            f"Detected {pii_result['total_detections']} PII instances",
            f"Types: {', '.join(pii_result['pii_types'])}",
            f"Severity: {pii_result['severity']}"
        ]

        return " | ".join(summary_parts)
