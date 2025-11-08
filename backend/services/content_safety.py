"""
Content Safety Service
Monitors documents for unsafe content including child safety violations,
hate speech, violence, criminal content, and cyber threats
"""
import re
from typing import Dict, List
from loguru import logger


class ContentSafetyChecker:
    """Check content for safety violations"""

    def __init__(self):
        # Safety categories and their keywords/patterns
        self.safety_categories = {
            "child_safety": {
                "keywords": [
                    "child abuse", "child exploitation", "minor", "underage",
                    "csam", "child pornography"
                ],
                "severity": "critical",
                "description": "Content that may violate child safety"
            },
            "hate_speech": {
                "keywords": [
                    "hate speech", "racial slur", "discriminatory",
                    "racist", "sexist", "homophobic", "xenophobic"
                ],
                "severity": "high",
                "description": "Hate speech or discriminatory content"
            },
            "violence": {
                "keywords": [
                    "graphic violence", "gore", "torture", "brutal",
                    "violent death", "mass shooting", "terrorism",
                    "weapon schematic", "bomb making"
                ],
                "severity": "high",
                "description": "Violent or graphic content"
            },
            "exploitative": {
                "keywords": [
                    "human trafficking", "exploitation", "forced labor",
                    "sexual exploitation", "coercion"
                ],
                "severity": "high",
                "description": "Exploitative content"
            },
            "criminal": {
                "keywords": [
                    "how to make drugs", "illegal weapons", "fraud scheme",
                    "money laundering", "identity theft", "hacking tutorial",
                    "break into", "illegal activities"
                ],
                "severity": "medium",
                "description": "Criminal activity instructions"
            },
            "cyber_threat": {
                "keywords": [
                    "malware", "ransomware", "exploit code", "zero-day",
                    "cyber attack", "ddos", "botnet", "trojan",
                    "backdoor", "sql injection", "xss attack"
                ],
                "severity": "medium",
                "description": "Cyber threat content"
            },
            "political_misinfo": {
                "keywords": [
                    "election fraud", "conspiracy", "fake news",
                    "propaganda", "disinformation campaign"
                ],
                "severity": "low",
                "description": "Political misinformation"
            }
        }

        # Contextual modifiers that reduce false positives
        self.safe_contexts = [
            "education", "awareness", "prevention", "training",
            "security research", "academic", "news report"
        ]

    def check_content_safety(
        self,
        text: str,
        page_number: int = None,
        threshold: float = 0.5
    ) -> Dict:
        """
        Check text for safety violations

        Args:
            text: Text to analyze
            page_number: Optional page number
            threshold: Detection threshold (0-1)

        Returns:
            Dict with safety assessment
        """
        result = {
            "is_safe": True,
            "safety_flags": [],
            "overall_severity": "none",
            "requires_review": False
        }

        text_lower = text.lower()
        flags = []

        # Check each safety category
        for category, config in self.safety_categories.items():
            matches = self._find_safety_violations(
                text_lower,
                config["keywords"],
                page_number
            )

            if matches:
                # Check if in safe context
                is_safe_context = any(
                    ctx in text_lower for ctx in self.safe_contexts
                )

                confidence = 0.8 if not is_safe_context else 0.4

                if confidence >= threshold:
                    flag = {
                        "category": category,
                        "severity": config["severity"],
                        "description": config["description"],
                        "matches": matches,
                        "page_number": page_number,
                        "confidence": confidence,
                        "safe_context": is_safe_context
                    }
                    flags.append(flag)

        if flags:
            result["is_safe"] = False
            result["safety_flags"] = flags
            result["overall_severity"] = self._calculate_overall_severity(flags)
            result["requires_review"] = True

        return result

    def check_pages_safety(self, pages: List[Dict], threshold: float = 0.5) -> Dict:
        """
        Check all pages for safety violations

        Args:
            pages: List of page dictionaries
            threshold: Detection threshold

        Returns:
            Dict with aggregated safety results
        """
        all_flags = []

        for page in pages:
            page_num = page.get("page_number")
            page_text = page.get("text", "")

            if page_text:
                page_result = self.check_content_safety(
                    page_text,
                    page_num,
                    threshold
                )

                if not page_result["is_safe"]:
                    all_flags.extend(page_result["safety_flags"])

        result = {
            "is_safe": len(all_flags) == 0,
            "total_flags": len(all_flags),
            "safety_flags": all_flags,
            "overall_severity": self._calculate_overall_severity(all_flags),
            "requires_review": len(all_flags) > 0,
            "categories_flagged": list(set(f["category"] for f in all_flags))
        }

        logger.info(
            f"Content Safety Check: {'SAFE' if result['is_safe'] else 'UNSAFE'}, "
            f"{result['total_flags']} flags, severity: {result['overall_severity']}"
        )

        return result

    def _find_safety_violations(
        self,
        text: str,
        keywords: List[str],
        page_number: int = None
    ) -> List[Dict]:
        """Find keyword matches in text"""
        matches = []

        for keyword in keywords:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(keyword) + r'\b'

            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                matches.append({
                    "keyword": keyword,
                    "context": context.strip(),
                    "position": match.start()
                })

        return matches

    def _calculate_overall_severity(self, flags: List[Dict]) -> str:
        """Calculate overall severity from all flags"""
        if not flags:
            return "none"

        severity_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "none": 0
        }

        max_severity = max(
            severity_scores.get(f["severity"], 0)
            for f in flags
        )

        for severity, score in severity_scores.items():
            if score == max_severity:
                return severity

        return "none"

    def get_safety_summary(self, safety_result: Dict) -> str:
        """Generate human-readable safety summary"""
        if safety_result["is_safe"]:
            return "Content is safe for all audiences"

        summary_parts = [
            f"UNSAFE CONTENT DETECTED",
            f"{safety_result['total_flags']} violations",
            f"Categories: {', '.join(safety_result['categories_flagged'])}",
            f"Severity: {safety_result['overall_severity']}"
        ]

        return " | ".join(summary_parts)

    def should_block_document(self, safety_result: Dict) -> bool:
        """
        Determine if document should be blocked from processing

        Critical and high severity issues should block
        """
        if safety_result["is_safe"]:
            return False

        severity = safety_result["overall_severity"]
        return severity in ["critical", "high"]
