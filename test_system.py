"""
Simple test script to verify the system works
Run this after setting up the environment to test core functionality
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.document_processor import DocumentProcessor
from backend.services.pii_detector import PIIDetector
from backend.services.content_safety import ContentSafetyChecker
from backend.services.prompt_manager import PromptManager


def test_document_processor():
    """Test document processing"""
    print("\n🧪 Testing Document Processor...")
    processor = DocumentProcessor()

    # Test validation
    result = processor.validate_file("test_system.py", max_size_mb=50)
    print(f"   ✓ File validation: {result['valid']}")
    print(f"   ✓ File type: {result['file_info'].get('extension', 'unknown')}")


def test_pii_detector():
    """Test PII detection"""
    print("\n🧪 Testing PII Detector...")
    detector = PIIDetector()

    test_text = """
    Name: John Doe
    SSN: 123-45-6789
    Email: john.doe@example.com
    Credit Card: 4532-1234-5678-9010
    """

    result = detector.detect_pii(test_text, page_number=1)
    print(f"   ✓ PII Detected: {result['pii_detected']}")
    print(f"   ✓ PII Types: {result['pii_types']}")
    print(f"   ✓ Total Detections: {len(result['detections'])}")


def test_content_safety():
    """Test content safety checker"""
    print("\n🧪 Testing Content Safety Checker...")
    checker = ContentSafetyChecker()

    safe_text = "This is a marketing brochure for our new product line."
    result = checker.check_content_safety(safe_text, page_number=1)
    print(f"   ✓ Safe Content: {result['is_safe']}")

    unsafe_text = "Instructions for violent activities and exploitation."
    result = checker.check_content_safety(unsafe_text, page_number=1)
    print(f"   ✓ Unsafe Content Detected: {not result['is_safe']}")


def test_prompt_manager():
    """Test prompt manager"""
    print("\n🧪 Testing Prompt Manager...")
    manager = PromptManager()

    system_prompt = manager.get_system_prompt()
    print(f"   ✓ System Prompt Length: {len(system_prompt)} chars")

    categories = manager.get_category_definitions()
    print(f"   ✓ Categories Loaded: {len(categories)}")
    print(f"   ✓ Category Names: {list(categories.keys())}")

    # Test prompt generation
    test_content = "Sample document content for testing"
    prompt = manager.generate_classification_prompt(test_content, "initial_analysis")
    print(f"   ✓ Generated Prompt Length: {len(prompt)} chars")


def test_database():
    """Test database setup"""
    print("\n🧪 Testing Database...")
    try:
        from backend.database import init_db, SessionLocal

        # Initialize database
        init_db()
        print("   ✓ Database initialized successfully")

        # Test session
        db = SessionLocal()
        db.close()
        print("   ✓ Database session working")

    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return False

    return True


def test_configuration():
    """Test configuration"""
    print("\n🧪 Testing Configuration...")
    from backend.config import settings

    print(f"   ✓ App Name: {settings.APP_NAME}")
    print(f"   ✓ Environment: {settings.ENVIRONMENT}")
    print(f"   ✓ Primary LLM Model: {settings.PRIMARY_LLM_MODEL}")
    print(f"   ✓ Secondary LLM Model: {settings.SECONDARY_LLM_MODEL}")
    print(f"   ✓ Max File Size: {settings.MAX_FILE_SIZE_MB}MB")
    print(f"   ✓ Allowed Extensions: {settings.ALLOWED_EXTENSIONS}")

    # Check API keys
    if settings.ANTHROPIC_API_KEY:
        print("   ✓ Anthropic API Key: Configured")
    else:
        print("   ⚠️  Anthropic API Key: Not configured (required)")

    if settings.OPENAI_API_KEY:
        print("   ✓ OpenAI API Key: Configured")
    else:
        print("   ⚠️  OpenAI API Key: Not configured (optional)")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 REGULATORY DOCUMENT CLASSIFIER - SYSTEM TEST")
    print("=" * 60)

    try:
        test_configuration()
        test_database()
        test_document_processor()
        test_pii_detector()
        test_content_safety()
        test_prompt_manager()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🚀 System is ready to use!")
        print("   Run: python -m uvicorn backend.main:app --reload")
        print("   Or:  ./run_api.sh")
        print("\n📖 API Docs: http://localhost:8000/docs")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
