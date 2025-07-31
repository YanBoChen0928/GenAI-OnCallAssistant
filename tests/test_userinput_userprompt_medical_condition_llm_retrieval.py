#!/usr/bin/env python3
"""
Comprehensive Test Suite for OnCall.ai Medical Query Processing Pipeline

This test validates the complete flow:
User Input → UserPrompt Processing → Medical Condition Extraction → LLM Analysis → Retrieval

Test Components:
- UserPromptProcessor (condition extraction, keyword mapping)
- MedicalConditions (predefined mappings, validation)
- LLM Client (Llama3-Med42-70B condition extraction)
- BasicRetrievalSystem (vector search, result processing)

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
from typing import Dict, List, Any

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
    from medical_conditions import CONDITION_KEYWORD_MAPPING, validate_condition, get_condition_details
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'tests' / 'pipeline_test.log')
    ]
)
logger = logging.getLogger(__name__)

class MedicalQueryPipelineTest:
    """Comprehensive test suite for the medical query processing pipeline"""
    
    def __init__(self):
        """Initialize test suite with all required components"""
        self.start_time = datetime.now()
        self.results = []
        self.components_initialized = False
        
        # Component references
        self.llm_client = None
        self.retrieval_system = None
        self.user_prompt_processor = None
        
    def initialize_components(self):
        """Initialize all pipeline components with error handling"""
        print("🔧 Initializing Pipeline Components...")
        print("-" * 50)
        
        try:
            # Initialize LLM client
            print("1. Initializing Llama3-Med42-70B Client...")
            self.llm_client = llm_Med42_70BClient()
            print("   ✅ LLM client initialized successfully")
            
            # Initialize retrieval system
            print("2. Initializing Retrieval System...")
            self.retrieval_system = BasicRetrievalSystem()
            print("   ✅ Retrieval system initialized successfully")
            
            # Initialize user prompt processor
            print("3. Initializing User Prompt Processor...")
            self.user_prompt_processor = UserPromptProcessor(
                llm_client=self.llm_client,
                retrieval_system=self.retrieval_system
            )
            print("   ✅ User prompt processor initialized successfully")
            
            self.components_initialized = True
            print("\n🎉 All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            print(f"❌ Component initialization failed: {e}")
            traceback.print_exc()
            self.components_initialized = False
            
    def get_test_queries(self) -> List[Dict[str, Any]]:
        """Define comprehensive test queries with expected behavior"""
        return [
            {
                "id": "test_001",
                "query": "how to treat acute MI?",
                "description": "Classic acute myocardial infarction query",
                "expected_condition": "acute myocardial infarction",
                "expected_mechanism": "predefined_mapping",
                "category": "cardiac_emergency"
            },
            {
                "id": "test_002", 
                "query": "patient with severe chest pain and shortness of breath",
                "description": "Symptoms-based query requiring LLM analysis",
                "expected_condition": ["acute myocardial infarction", "pulmonary embolism", "acute coronary syndrome"],
                "expected_mechanism": "llm_extraction",
                "category": "cardiac_pulmonary"
            },
            {
                "id": "test_003",
                "query": "sudden neurological symptoms suggesting stroke",
                "description": "Neurological emergency query",
                "expected_condition": "acute stroke",
                "expected_mechanism": "predefined_mapping",
                "category": "neurological_emergency"
            },
            {
                "id": "test_004",
                "query": "acute stroke management protocol",
                "description": "Protocol-specific stroke query",
                "expected_condition": "acute stroke", 
                "expected_mechanism": "predefined_mapping",
                "category": "neurological_protocol"
            },
            {
                "id": "test_005",
                "query": "patient presenting with acute abdominal pain",
                "description": "General symptom requiring LLM analysis",
                "expected_condition": "unknown",
                "expected_mechanism": "semantic_fallback",
                "category": "general_symptom"
            },
            {
                "id": "test_006",
                "query": "pulmonary embolism treatment guidelines",
                "description": "Specific condition with treatment focus",
                "expected_condition": "pulmonary embolism",
                "expected_mechanism": "predefined_mapping", 
                "category": "pulmonary_emergency"
            }
        ]
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test case with comprehensive analysis"""
        test_id = test_case["id"]
        query = test_case["query"]
        
        print(f"\n🔍 {test_id}: {test_case['description']}")
        print(f"Query: '{query}'")
        print("-" * 60)
        
        result = {
            "test_id": test_id,
            "test_case": test_case,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "execution_time": 0,
            "steps": {}
        }
        
        start_time = datetime.now()
        
        try:
            # Step 1: Condition Extraction
            print("Step 1: Extracting medical condition and keywords...")
            condition_start = datetime.now()
            
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            condition_time = (datetime.now() - condition_start).total_seconds()
            
            result["steps"]["condition_extraction"] = {
                "duration_seconds": condition_time,
                "condition": condition_result.get('condition', ''),
                "emergency_keywords": condition_result.get('emergency_keywords', ''),
                "treatment_keywords": condition_result.get('treatment_keywords', ''),
                "confidence": condition_result.get('confidence', 'unknown'),
                "source": self._determine_extraction_source(condition_result)
            }
            
            print(f"   Condition: {condition_result.get('condition', 'None')}")
            print(f"   Emergency keywords: {condition_result.get('emergency_keywords', 'None')}")
            print(f"   Treatment keywords: {condition_result.get('treatment_keywords', 'None')}")
            print(f"   Source: {result['steps']['condition_extraction']['source']}")
            print(f"   Duration: {condition_time:.3f}s")
            
            # Step 2: User Confirmation (Simulated)
            print("\nStep 2: User confirmation process...")
            confirmation_result = self.user_prompt_processor.handle_user_confirmation(condition_result)
            
            result["steps"]["user_confirmation"] = {
                "confirmation_type": confirmation_result.get('type', 'unknown'),
                "message_length": len(confirmation_result.get('message', '')),
                "actionable": confirmation_result.get('type') == 'confirmation_needed'
            }
            
            print(f"   Confirmation type: {confirmation_result.get('type', 'Unknown')}")
            
            # Step 3: Retrieval Execution
            if condition_result.get('condition'):
                print("\nStep 3: Executing retrieval...")
                retrieval_start = datetime.now()
                
                # Construct search query
                search_query = self._construct_search_query(condition_result)
                
                # Perform retrieval
                retrieval_results = self.retrieval_system.search(search_query, top_k=5)
                retrieval_time = (datetime.now() - retrieval_start).total_seconds()
                
                # Correctly count emergency and treatment results from processed_results
                processed_results = retrieval_results.get('processed_results', [])
                emergency_count = len([r for r in processed_results if r.get('type') == 'emergency'])
                treatment_count = len([r for r in processed_results if r.get('type') == 'treatment'])
                
                result["steps"]["retrieval"] = {
                    "duration_seconds": retrieval_time,
                    "search_query": search_query,
                    "total_results": retrieval_results.get('total_results', 0),
                    "emergency_results": emergency_count,
                    "treatment_results": treatment_count,
                    "processed_results": len(processed_results),
                    "duplicates_removed": retrieval_results.get('processing_info', {}).get('duplicates_removed', 0)
                }
                
                print(f"   Search query: '{search_query}'")
                print(f"   Total results: {result['steps']['retrieval']['total_results']}")
                print(f"   Emergency results: {emergency_count}")
                print(f"   Treatment results: {treatment_count}")
                print(f"   Duration: {retrieval_time:.3f}s")
                
                # Analyze top results
                if 'processed_results' in retrieval_results and retrieval_results['processed_results']:
                    top_results = retrieval_results['processed_results'][:3]
                    result["steps"]["top_results_analysis"] = []
                    
                    print(f"\n   Top {len(top_results)} results:")
                    for i, res in enumerate(top_results, 1):
                        analysis = {
                            "rank": i,
                            "type": res.get('type', 'unknown'),
                            "distance": res.get('distance', 999),
                            "text_length": len(res.get('text', '')),
                            "has_matched_keywords": bool(res.get('matched', '')),
                            "has_treatment_keywords": bool(res.get('matched_treatment', ''))
                        }
                        result["steps"]["top_results_analysis"].append(analysis)
                        
                        print(f"      {i}. Type: {analysis['type']}, Distance: {analysis['distance']:.4f}")
                        print(f"         Text preview: {res.get('text', '')[:100]}...")
                        if res.get('matched'):
                            print(f"         Matched: {res.get('matched')}")
                        if res.get('matched_treatment'):
                            print(f"         Treatment: {res.get('matched_treatment')}")
            
            else:
                print("\nStep 3: Skipping retrieval (no condition extracted)")
                result["steps"]["retrieval"] = {
                    "skipped": True,
                    "reason": "no_condition_extracted"
                }
            
            # Calculate total execution time
            total_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = total_time
            result["success"] = True
            
            print(f"\n✅ Test {test_id} completed successfully ({total_time:.3f}s)")
            
        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = total_time
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            
            logger.error(f"Test {test_id} failed: {e}")
            print(f"❌ Test {test_id} failed: {e}")
            
        return result
    
    def _determine_extraction_source(self, condition_result: Dict) -> str:
        """Determine how the condition was extracted"""
        if condition_result.get('semantic_confidence') is not None:
            return "semantic_search"
        elif condition_result.get('generic_confidence') is not None:
            return "generic_search"
        elif condition_result.get('condition') in CONDITION_KEYWORD_MAPPING:
            return "predefined_mapping"
        else:
            return "llm_extraction"
    
    def _construct_search_query(self, condition_result: Dict) -> str:
        """Construct search query from condition result"""
        emergency_kws = condition_result.get('emergency_keywords', '')
        treatment_kws = condition_result.get('treatment_keywords', '')
        
        search_parts = []
        if emergency_kws:
            search_parts.append(emergency_kws)
        if treatment_kws:
            search_parts.append(treatment_kws)
            
        if search_parts:
            return ' '.join(search_parts)
        else:
            return condition_result.get('condition', 'medical emergency')
    
    def run_all_tests(self):
        """Execute all test cases and generate comprehensive report"""
        if not self.components_initialized:
            print("❌ Cannot run tests: components not initialized")
            return
        
        test_cases = self.get_test_queries()
        
        print(f"\n🚀 Starting Comprehensive Pipeline Test")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Test started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Execute all tests
        for test_case in test_cases:
            result = self.run_single_test(test_case)
            self.results.append(result)
        
        # Generate comprehensive report
        self.generate_test_report()
        self.save_test_results()
    
    def generate_test_report(self):
        """Generate detailed test report with statistics and analysis"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Summary Statistics
        print(f"🕐 Execution Summary:")
        print(f"   Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total duration: {total_duration:.3f}s")
        print(f"   Average per test: {total_duration/len(self.results):.3f}s")
        
        print(f"\n📈 Test Results:")
        print(f"   Total tests: {len(self.results)}")
        print(f"   Successful: {len(successful_tests)} ✅")
        print(f"   Failed: {len(failed_tests)} ❌") 
        print(f"   Success rate: {len(successful_tests)/len(self.results)*100:.1f}%")
        
        # Detailed Analysis
        if successful_tests:
            print(f"\n✅ Successful Tests Analysis:")
            
            # Analyze extraction sources
            source_counts = {}
            total_retrieval_time = 0
            total_condition_time = 0
            retrieval_count = 0
            
            for result in successful_tests:
                if 'condition_extraction' in result['steps']:
                    source = result['steps']['condition_extraction']['source']
                    source_counts[source] = source_counts.get(source, 0) + 1
                    total_condition_time += result['steps']['condition_extraction']['duration_seconds']
                
                if 'retrieval' in result['steps'] and not result['steps']['retrieval'].get('skipped'):
                    total_retrieval_time += result['steps']['retrieval']['duration_seconds']
                    retrieval_count += 1
            
            print(f"   Condition extraction sources:")
            for source, count in source_counts.items():
                print(f"     - {source}: {count} tests")
            
            print(f"   Performance metrics:")
            print(f"     - Avg condition extraction: {total_condition_time/len(successful_tests):.3f}s")
            if retrieval_count > 0:
                print(f"     - Avg retrieval time: {total_retrieval_time/retrieval_count:.3f}s")
            
            # Individual test details
            for result in successful_tests:
                test_case = result['test_case']
                print(f"\n   📋 {result['test_id']}: {test_case['description']}")
                print(f"      Query: '{test_case['query']}'")
                
                if 'condition_extraction' in result['steps']:
                    ce = result['steps']['condition_extraction']
                    print(f"      Condition: {ce['condition']}")
                    print(f"      Source: {ce['source']}")
                
                if 'retrieval' in result['steps'] and not result['steps']['retrieval'].get('skipped'):
                    ret = result['steps']['retrieval']
                    print(f"      Results: {ret['total_results']} total ({ret['emergency_results']} emergency, {ret['treatment_results']} treatment)")
                
                print(f"      Duration: {result['execution_time']:.3f}s")
        
        # Failed Tests Analysis
        if failed_tests:
            print(f"\n❌ Failed Tests Analysis:")
            for result in failed_tests:
                test_case = result['test_case']
                print(f"   {result['test_id']}: {test_case['description']}")
                print(f"      Error: {result['error']}")
                print(f"      Duration: {result['execution_time']:.3f}s")
        
        print("\n" + "=" * 80)
    
    def save_test_results(self):
        """Save detailed test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = project_root / 'tests' / f'pipeline_test_results_{timestamp}.json'
        
        try:
            comprehensive_results = {
                "test_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "start_time": self.start_time.isoformat(),
                    "total_duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                    "total_tests": len(self.results),
                    "successful_tests": len([r for r in self.results if r['success']]),
                    "failed_tests": len([r for r in self.results if not r['success']])
                },
                "test_results": self.results,
                "component_versions": {
                    "user_prompt_processor": "1.0.0",
                    "retrieval_system": "1.0.0", 
                    "llm_client": "1.0.0"
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Comprehensive test results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            print(f"⚠️ Failed to save test results: {e}")

def main():
    """Main execution function"""
    print("🏥 OnCall.ai Medical Query Processing Pipeline Test")
    print("=" * 60)
    
    # Initialize test suite
    test_suite = MedicalQueryPipelineTest()
    
    # Initialize components
    test_suite.initialize_components()
    
    if not test_suite.components_initialized:
        print("❌ Test suite initialization failed. Exiting.")
        return 1
    
    # Run all tests
    test_suite.run_all_tests()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
