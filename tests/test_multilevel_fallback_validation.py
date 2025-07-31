#!/usr/bin/env python3
"""
Multi-Level Fallback Validation Test Suite for OnCall.ai

This test specifically validates the 5-level fallback mechanism:
Level 1: Predefined Mapping (Fast Path)
Level 2: Llama3-Med42-70B Extraction
Level 3: Semantic Search Fallback
Level 4: Medical Query Validation
Level 5: Generic Medical Search

Author: OnCall.ai Team
Date: 2025-07-30
"""

import sys
import os
from pathlib import Path
import logging
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import our modules
try:
    from user_prompt import UserPromptProcessor
    from retrieval import BasicRetrievalSystem
    from llm_clients import llm_Med42_70BClient
    from medical_conditions import CONDITION_KEYWORD_MAPPING
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'tests' / 'multilevel_fallback_test.log')
    ]
)
logger = logging.getLogger(__name__)

class MultilevelFallbackTest:
    """Test suite specifically for the 5-level fallback mechanism"""
    
    def __init__(self):
        """Initialize test suite"""
        self.start_time = datetime.now()
        self.results = []
        self.components_initialized = False
        
        # Component references
        self.llm_client = None
        self.retrieval_system = None
        self.user_prompt_processor = None
        
    def initialize_components(self):
        """Initialize all pipeline components"""
        print("🔧 Initializing Components for Multilevel Fallback Test...")
        print("-" * 60)
        
        try:
            # Initialize LLM client
            print("1. Initializing Llama3-Med42-70B Client...")
            self.llm_client = llm_Med42_70BClient()
            print("   ✅ LLM client initialized")
            
            # Initialize retrieval system
            print("2. Initializing Retrieval System...")
            self.retrieval_system = BasicRetrievalSystem()
            print("   ✅ Retrieval system initialized")
            
            # Initialize user prompt processor
            print("3. Initializing User Prompt Processor...")
            self.user_prompt_processor = UserPromptProcessor(
                llm_client=self.llm_client,
                retrieval_system=self.retrieval_system
            )
            print("   ✅ User prompt processor initialized")
            
            self.components_initialized = True
            print("\n🎉 All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            print(f"❌ Component initialization failed: {e}")
            traceback.print_exc()
            self.components_initialized = False
    
    def get_multilevel_test_cases(self) -> List[Dict[str, Any]]:
        """Define test cases specifically targeting each fallback level"""
        return [
            # Level 1: Predefined Mapping Tests
            {
                "id": "level1_001",
                "query": "acute myocardial infarction treatment",
                "description": "Level 1: Direct predefined condition match",
                "expected_level": 1,
                "expected_condition": "acute myocardial infarction",
                "expected_source": "predefined_mapping",
                "category": "level1_predefined"
            },
            {
                "id": "level1_002", 
                "query": "how to manage acute stroke?",
                "description": "Level 1: Predefined stroke condition",
                "expected_level": 1,
                "expected_condition": "acute stroke",
                "expected_source": "predefined_mapping",
                "category": "level1_predefined"
            },
            {
                "id": "level1_003",
                "query": "pulmonary embolism emergency protocol",
                "description": "Level 1: Predefined PE condition",
                "expected_level": 1,
                "expected_condition": "pulmonary embolism",
                "expected_source": "predefined_mapping",
                "category": "level1_predefined"
            },
            
            # Level 2: LLM Extraction Tests
            {
                "id": "level2_001",
                "query": "patient with severe crushing chest pain radiating to left arm",
                "description": "Level 2: Symptom-based query requiring LLM analysis",
                "expected_level": 2,
                "expected_condition": ["acute myocardial infarction", "acute coronary syndrome"],
                "expected_source": "llm_extraction",
                "category": "level2_llm"
            },
            {
                "id": "level2_002",
                "query": "sudden onset weakness on right side with speech difficulty",
                "description": "Level 2: Neurological symptoms requiring LLM",
                "expected_level": 2,
                "expected_condition": ["acute stroke", "cerebrovascular accident"],
                "expected_source": "llm_extraction",
                "category": "level2_llm"
            },
            
            # Level 3: Semantic Search Tests
            {
                "id": "level3_001",
                "query": "emergency management of cardiovascular crisis",
                "description": "Level 3: Generic medical terms requiring semantic search",
                "expected_level": 3,
                "expected_source": "semantic_search",
                "category": "level3_semantic"
            },
            {
                "id": "level3_002",
                "query": "urgent neurological intervention protocols",
                "description": "Level 3: Medical terminology requiring semantic fallback",
                "expected_level": 3,
                "expected_source": "semantic_search",
                "category": "level3_semantic"
            },
            
            # Level 4a: Non-Medical Query Rejection
            {
                "id": "level4a_001",
                "query": "how to cook pasta properly?",
                "description": "Level 4a: Non-medical query should be rejected",
                "expected_level": 4,
                "expected_result": "invalid_query",
                "expected_source": "validation_rejection",
                "category": "level4a_rejection"
            },
            {
                "id": "level4a_002",
                "query": "best programming language to learn in 2025",
                "description": "Level 4a: Technology query should be rejected",
                "expected_level": 4,
                "expected_result": "invalid_query",
                "expected_source": "validation_rejection",
                "category": "level4a_rejection"
            },
            {
                "id": "level4a_003",
                "query": "weather forecast for tomorrow",
                "description": "Level 4a: Weather query should be rejected",
                "expected_level": 4,
                "expected_result": "invalid_query",
                "expected_source": "validation_rejection",
                "category": "level4a_rejection"
            },
            
            # Level 4b + 5: Obscure Medical Terms → Generic Search
            {
                "id": "level4b_001",
                "query": "rare hematologic malignancy treatment approaches",
                "description": "Level 4b→5: Obscure medical query passing validation to generic search",
                "expected_level": 5,
                "expected_condition": "generic medical query",
                "expected_source": "generic_search",
                "category": "level4b_to_5"
            },
            {
                "id": "level4b_002",
                "query": "idiopathic thrombocytopenic purpura management guidelines",
                "description": "Level 4b→5: Rare condition requiring generic medical search",
                "expected_level": 5,
                "expected_condition": "generic medical query",
                "expected_source": "generic_search",
                "category": "level4b_to_5"
            },
            {
                "id": "level4b_003",
                "query": "necrotizing fasciitis surgical intervention protocols",
                "description": "Level 4b→5: Rare emergency condition → generic search",
                "expected_level": 5,
                "expected_condition": "generic medical query",
                "expected_source": "generic_search",
                "category": "level4b_to_5"
            }
        ]
    
    def run_single_fallback_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single fallback test case with level detection"""
        test_id = test_case["id"]
        query = test_case["query"]
        
        print(f"\n🔍 {test_id}: {test_case['description']}")
        print(f"Query: '{query}'")
        print(f"Expected Level: {test_case.get('expected_level', 'Unknown')}")
        print("-" * 70)
        
        result = {
            "test_id": test_id,
            "test_case": test_case,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "execution_time": 0,
            "detected_level": None,
            "condition_result": {}
        }
        
        start_time = datetime.now()
        
        try:
            # Execute condition extraction with level detection
            print("🎯 Executing multilevel fallback...")
            condition_start = datetime.now()
            
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            condition_time = (datetime.now() - condition_start).total_seconds()
            
            # Detect which level was used
            detected_level = self._detect_fallback_level(condition_result)
            
            result["condition_result"] = condition_result
            result["detected_level"] = detected_level
            result["execution_time"] = condition_time
            
            print(f"   ✅ Detected Level: {detected_level}")
            print(f"   Condition: {condition_result.get('condition', 'None')}")
            print(f"   Emergency Keywords: {condition_result.get('emergency_keywords', 'None')}")
            print(f"   Treatment Keywords: {condition_result.get('treatment_keywords', 'None')}")
            print(f"   Execution Time: {condition_time:.3f}s")
            
            # Validate expected behavior
            validation_result = self._validate_expected_behavior(test_case, detected_level, condition_result)
            result.update(validation_result)
            
            if result["success"]:
                print("   🎉 Test PASSED - Expected behavior achieved")
            else:
                print(f"   ⚠️  Test PARTIAL - {result.get('validation_message', 'Unexpected behavior')}")
                
        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = total_time
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            
            logger.error(f"Test {test_id} failed: {e}")
            print(f"   ❌ Test FAILED: {e}")
            
        return result
    
    def _detect_fallback_level(self, condition_result: Dict[str, Any]) -> int:
        """Detect which fallback level was used based on the result"""
        if not condition_result:
            return 0  # No result
        
        # Check for validation rejection (Level 4a)
        if condition_result.get('type') == 'invalid_query':
            return 4
        
        # Check for generic search (Level 5)
        if condition_result.get('condition') == 'generic medical query':
            return 5
        
        # Check for semantic search (Level 3)
        if 'semantic_confidence' in condition_result:
            return 3
        
        # Check for predefined mapping (Level 1)
        condition = condition_result.get('condition', '')
        if condition and condition in CONDITION_KEYWORD_MAPPING:
            return 1
        
        # Otherwise assume LLM extraction (Level 2)
        if condition:
            return 2
        
        return 0  # Unknown
    
    def _validate_expected_behavior(self, test_case: Dict[str, Any], detected_level: int, 
                                  condition_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if the test behaved as expected"""
        expected_level = test_case.get('expected_level')
        validation_result = {
            "level_match": detected_level == expected_level,
            "condition_match": False,
            "success": False,
            "validation_message": ""
        }
        
        # Check level match
        if validation_result["level_match"]:
            validation_result["validation_message"] += f"✅ Level {detected_level} as expected. "
        else:
            validation_result["validation_message"] += f"⚠️ Level {detected_level} != expected {expected_level}. "
        
        # Check condition/result match based on test type
        if test_case["category"] == "level4a_rejection":
            # Should be rejected
            validation_result["condition_match"] = condition_result.get('type') == 'invalid_query'
            if validation_result["condition_match"]:
                validation_result["validation_message"] += "✅ Query correctly rejected. "
            else:
                validation_result["validation_message"] += "⚠️ Query should have been rejected. "
                
        elif test_case["category"] == "level4b_to_5":
            # Should result in generic medical query
            validation_result["condition_match"] = condition_result.get('condition') == 'generic medical query'
            if validation_result["condition_match"]:
                validation_result["validation_message"] += "✅ Generic medical search triggered. "
            else:
                validation_result["validation_message"] += "⚠️ Should trigger generic medical search. "
                
        else:
            # Check expected condition
            expected_conditions = test_case.get('expected_condition', [])
            if isinstance(expected_conditions, str):
                expected_conditions = [expected_conditions]
            
            actual_condition = condition_result.get('condition', '')
            validation_result["condition_match"] = any(
                expected.lower() in actual_condition.lower() 
                for expected in expected_conditions
            )
            
            if validation_result["condition_match"]:
                validation_result["validation_message"] += f"✅ Condition '{actual_condition}' matches expected. "
            else:
                validation_result["validation_message"] += f"⚠️ Condition '{actual_condition}' != expected {expected_conditions}. "
        
        # Overall success
        validation_result["success"] = validation_result["level_match"] or validation_result["condition_match"]
        
        return validation_result
    
    def run_all_fallback_tests(self):
        """Execute all fallback tests and generate report"""
        if not self.components_initialized:
            print("❌ Cannot run tests: components not initialized")
            return
        
        test_cases = self.get_multilevel_test_cases()
        
        print(f"\n🚀 Starting Multilevel Fallback Test Suite")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Test started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Execute all tests
        for test_case in test_cases:
            result = self.run_single_fallback_test(test_case)
            self.results.append(result)
        
        # Generate report
        self.generate_fallback_report()
        self.save_fallback_results()
    
    def generate_fallback_report(self):
        """Generate detailed fallback analysis report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        partial_tests = [r for r in self.results if not r['success'] and not r.get('error')]
        
        print("\n" + "=" * 80)
        print("📊 MULTILEVEL FALLBACK TEST REPORT")
        print("=" * 80)
        
        # Overall Statistics
        print(f"🕐 Execution Summary:")
        print(f"   Total duration: {total_duration:.3f}s")
        print(f"   Average per test: {total_duration/len(self.results):.3f}s")
        
        print(f"\n📈 Test Results:")
        print(f"   Total tests: {len(self.results)}")
        print(f"   Passed: {len(successful_tests)} ✅")
        print(f"   Partial: {len(partial_tests)} ⚠️")
        print(f"   Failed: {len(failed_tests)} ❌")
        print(f"   Success rate: {len(successful_tests)/len(self.results)*100:.1f}%")
        
        # Level Distribution Analysis
        level_distribution = {}
        level_performance = {}
        
        for result in self.results:
            if not result.get('error'):
                level = result.get('detected_level', 0)
                level_distribution[level] = level_distribution.get(level, 0) + 1
                
                if level not in level_performance:
                    level_performance[level] = []
                level_performance[level].append(result['execution_time'])
        
        print(f"\n🎯 Level Distribution Analysis:")
        for level in sorted(level_distribution.keys()):
            count = level_distribution[level]
            avg_time = sum(level_performance[level]) / len(level_performance[level])
            level_name = {
                1: "Predefined Mapping",
                2: "LLM Extraction", 
                3: "Semantic Search",
                4: "Validation Rejection",
                5: "Generic Search"
            }.get(level, f"Unknown ({level})")
            
            print(f"   Level {level} ({level_name}): {count} tests, avg {avg_time:.3f}s")
        
        # Category Analysis
        categories = {}
        for result in self.results:
            category = result['test_case']['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        print(f"\n📋 Category Analysis:")
        for category, stats in categories.items():
            success_rate = stats['passed'] / stats['total'] * 100
            print(f"   {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Detailed Results
        print(f"\n📝 Detailed Test Results:")
        for result in self.results:
            test_case = result['test_case']
            status = "✅ PASS" if result['success'] else ("❌ FAIL" if result.get('error') else "⚠️ PARTIAL")
            
            print(f"\n   {result['test_id']}: {status}")
            print(f"      Query: '{test_case['query']}'")
            print(f"      Expected Level: {test_case.get('expected_level', 'N/A')}")
            print(f"      Detected Level: {result.get('detected_level', 'N/A')}")
            print(f"      Condition: {result.get('condition_result', {}).get('condition', 'None')}")
            print(f"      Time: {result['execution_time']:.3f}s")
            
            if result.get('validation_message'):
                print(f"      Validation: {result['validation_message']}")
            
            if result.get('error'):
                print(f"      Error: {result['error']}")
        
        print("\n" + "=" * 80)
    
    def save_fallback_results(self):
        """Save detailed test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = project_root / 'tests' / f'multilevel_fallback_results_{timestamp}.json'
        
        try:
            comprehensive_results = {
                "test_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "multilevel_fallback_validation",
                    "total_duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                    "total_tests": len(self.results),
                    "passed_tests": len([r for r in self.results if r['success']]),
                    "failed_tests": len([r for r in self.results if not r['success']])
                },
                "fallback_results": self.results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Multilevel fallback results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            print(f"⚠️ Failed to save test results: {e}")

def main():
    """Main execution function"""
    print("🏥 OnCall.ai Multilevel Fallback Validation Test")
    print("=" * 60)
    
    # Initialize test suite
    test_suite = MultilevelFallbackTest()
    
    # Initialize components
    test_suite.initialize_components()
    
    if not test_suite.components_initialized:
        print("❌ Test suite initialization failed. Exiting.")
        return 1
    
    # Run all fallback tests
    test_suite.run_all_fallback_tests()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
