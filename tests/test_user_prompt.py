"""
User Prompt Processor Test Suite

Comprehensive unit tests for UserPromptProcessor class
Ensures robust functionality across medical query scenarios.
"""

import pytest
import sys
from pathlib import Path

# Dynamically add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from user_prompt import UserPromptProcessor

class TestUserPromptProcessor:
    """Test suite for UserPromptProcessor functionality"""

    def setup_method(self):
        """Initialize test environment before each test method"""
        self.processor = UserPromptProcessor()

    def test_extract_condition_keywords_predefined(self):
        """Test predefined condition extraction"""
        query = "heart attack symptoms"
        result = self.processor.extract_condition_keywords(query)
        
        assert result is not None
        assert 'condition' in result
        assert 'emergency_keywords' in result
        assert 'treatment_keywords' in result

    def test_handle_matching_failure_level1(self):
        """Test loose keyword matching mechanism"""
        test_queries = [
            "urgent medical help",
            "critical condition",
            "severe symptoms"
        ]
        
        for query in test_queries:
            result = self.processor._handle_matching_failure_level1(query)
            
            assert result is not None
            assert result['type'] == 'loose_keyword_match'
            assert result['confidence'] == 0.5

    def test_semantic_search_fallback(self):
        """Verify semantic search fallback mechanism"""
        test_queries = [
            "how to manage chest pain",
            "treatment for acute stroke",
            "emergency cardiac care"
        ]
        
        for query in test_queries:
            result = self.processor._semantic_search_fallback(query)
            
            # Result can be None if no match found
            if result is not None:
                assert 'condition' in result
                assert 'emergency_keywords' in result
                assert 'treatment_keywords' in result

    def test_validate_keywords(self):
        """Test keyword validation functionality"""
        valid_keywords = {
            'emergency_keywords': 'urgent|critical',
            'treatment_keywords': 'medication|therapy'
        }
        
        invalid_keywords = {
            'emergency_keywords': '',
            'treatment_keywords': ''
        }
        
        assert self.processor.validate_keywords(valid_keywords) is True
        assert self.processor.validate_keywords(invalid_keywords) is False

def main():
    """Run comprehensive test suite with detailed reporting"""
    print("\n" + "="*60)
    print("OnCall.ai: User Prompt Processor Test Suite")
    print("="*60)
    
    # Run pytest with verbose output
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == "__main__":
    main() 