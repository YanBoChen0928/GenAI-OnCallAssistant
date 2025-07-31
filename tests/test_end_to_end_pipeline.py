#!/usr/bin/env python3
"""
End-to-End Pipeline Script Test for OnCall.ai

Tests the complete pipeline:
User Input → UserPrompt Processing → Retrieval → Generation → Structured Medical Advice

This script validates the entire workflow with realistic medical queries,
simulating the user confirmation process and generating final medical advice.

Author: OnCall.ai Team
Date: 2025-07-31
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

# Import all pipeline modules
try:
    from user_prompt import UserPromptProcessor
    from retrieval import BasicRetrievalSystem
    from llm_clients import llm_Med42_70BClient
    from generation import MedicalAdviceGenerator
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
        logging.FileHandler(project_root / 'tests' / 'end_to_end_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

class EndToEndPipelineTest:
    """Complete pipeline test with realistic medical scenarios"""
    
    def __init__(self):
        """Initialize test suite"""
        self.start_time = datetime.now()
        self.test_results = []
        self.components_initialized = False
        
        # Pipeline components
        self.llm_client = None
        self.retrieval_system = None
        self.user_prompt_processor = None
        self.medical_generator = None
        
    def initialize_complete_pipeline(self):
        """Initialize all pipeline components"""
        print("🔧 Initializing Complete OnCall.ai Pipeline...")
        print("-" * 60)
        
        try:
            # Initialize LLM client
            print("1. Initializing Med42-70B Client...")
            self.llm_client = llm_Med42_70BClient()
            print("   ✅ Med42-70B client ready")
            
            # Initialize retrieval system
            print("2. Initializing Dual-Index Retrieval System...")
            self.retrieval_system = BasicRetrievalSystem()
            print("   ✅ Emergency & Treatment indices loaded")
            
            # Initialize user prompt processor
            print("3. Initializing Multi-Level Prompt Processor...")
            self.user_prompt_processor = UserPromptProcessor(
                llm_client=self.llm_client,
                retrieval_system=self.retrieval_system
            )
            print("   ✅ Fallback validation system ready")
            
            # Initialize medical advice generator
            print("4. Initializing Medical Advice Generator...")
            self.medical_generator = MedicalAdviceGenerator(
                llm_client=self.llm_client
            )
            print("   ✅ RAG generation system ready")
            
            self.components_initialized = True
            print(f"\n🎉 Complete pipeline initialized successfully!")
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            print(f"❌ Initialization failed: {e}")
            traceback.print_exc()
            self.components_initialized = False
    
    def get_realistic_test_queries(self) -> List[Dict[str, Any]]:
        """Define realistic medical queries for end-to-end testing"""
        return [
            {
                "id": "e2e_001",
                "query": "How to treat acute myocardial infarction in emergency department?",
                "description": "Classic cardiac emergency with treatment focus",
                "expected_intention": "treatment",
                "category": "cardiac_emergency",
                "simulated_confirmation": "yes"
            },
            {
                "id": "e2e_002", 
                "query": "Patient presenting with severe chest pain and shortness of breath",
                "description": "Symptom-based emergency requiring assessment and treatment",
                "expected_intention": "diagnosis",
                "category": "multi_symptom",
                "simulated_confirmation": "yes"
            },
            {
                "id": "e2e_003",
                "query": "What are the emergency protocols for acute stroke management?",
                "description": "Neurological emergency with protocol focus",
                "expected_intention": "treatment", 
                "category": "neurological_emergency",
                "simulated_confirmation": "yes"
            },
            {
                "id": "e2e_004",
                "query": "Differential diagnosis for sudden onset chest pain in young adult",
                "description": "Diagnostic reasoning query",
                "expected_intention": "diagnosis",
                "category": "differential_diagnosis",
                "simulated_confirmation": "yes"
            },
            {
                "id": "e2e_005",
                "query": "Emergency management of pulmonary embolism",
                "description": "Pulmonary emergency requiring immediate intervention",
                "expected_intention": "treatment",
                "category": "pulmonary_emergency", 
                "simulated_confirmation": "yes"
            },
            {
                "id": "e2e_006",
                "query": "How to cook pasta properly?",
                "description": "Non-medical query - should be rejected",
                "expected_intention": None,
                "category": "non_medical",
                "simulated_confirmation": "reject_expected"
            }
        ]
    
    def run_scripted_end_to_end_tests(self):
        """Execute complete end-to-end tests with realistic queries"""
        if not self.components_initialized:
            print("❌ Cannot run tests: pipeline not initialized")
            return
            
        test_queries = self.get_realistic_test_queries()
        
        print(f"\n🚀 Starting End-to-End Pipeline Tests")
        print(f"Total test scenarios: {len(test_queries)}")
        print(f"Test started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Execute all tests
        for test_case in test_queries:
            result = self._execute_single_pipeline_test(test_case)
            self.test_results.append(result)
        
        # Generate comprehensive report
        self._generate_end_to_end_report()
        self._save_end_to_end_results()
    
    def _execute_single_pipeline_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single test through complete pipeline"""
        test_id = test_case["id"]
        query = test_case["query"]
        
        print(f"\n🧪 {test_id}: {test_case['description']}")
        print(f"Query: '{query}'")
        print(f"Expected: {test_case['expected_intention']} intention")
        print("-" * 70)
        
        pipeline_start = datetime.now()
        result = {
            "test_id": test_id,
            "test_case": test_case,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "total_pipeline_time": 0,
            "pipeline_steps": {}
        }
        
        try:
            # STEP 1: User Prompt Processing
            print("   🎯 Step 1: Condition extraction and validation...")
            step1_start = datetime.now()
            
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            step1_time = (datetime.now() - step1_start).total_seconds()
            
            result["pipeline_steps"]["condition_extraction"] = {
                "duration": step1_time,
                "result": condition_result,
                "condition_found": bool(condition_result.get('condition'))
            }
            
            print(f"      Condition: {condition_result.get('condition', 'None')}")
            print(f"      Keywords: Emergency='{condition_result.get('emergency_keywords', 'None')}', Treatment='{condition_result.get('treatment_keywords', 'None')}'")
            print(f"      Time: {step1_time:.3f}s")
            
            # Check if this is a non-medical query that should be rejected
            if condition_result.get('type') == 'invalid_query':
                print("      🚫 Non-medical query correctly rejected")
                result["pipeline_steps"]["rejection"] = {
                    "reason": "non_medical_query",
                    "message": condition_result.get('message', '')
                }
                result["success"] = test_case['category'] == 'non_medical'
                return result
            
            # STEP 2: User Confirmation (Simulated)
            print("   🤝 Step 2: User confirmation (simulated as 'yes')...")
            confirmation = self.user_prompt_processor.handle_user_confirmation(condition_result)
            
            result["pipeline_steps"]["confirmation"] = {
                "type": confirmation.get('type', 'unknown'),
                "simulated_response": test_case['simulated_confirmation']
            }
            
            if not condition_result.get('condition'):
                print("      ⚠️  No condition extracted, skipping retrieval and generation")
                result["pipeline_steps"]["pipeline_stopped"] = "no_condition"
                return result
            
            # STEP 3: Retrieval
            print("   🔍 Step 3: Medical guideline retrieval...")
            step3_start = datetime.now()
            
            search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
            if not search_query:
                search_query = condition_result.get('condition', query)
            
            retrieval_results = self.retrieval_system.search(search_query, top_k=5)
            step3_time = (datetime.now() - step3_start).total_seconds()
            
            processed_results = retrieval_results.get('processed_results', [])
            emergency_count = len([r for r in processed_results if r.get('type') == 'emergency'])
            treatment_count = len([r for r in processed_results if r.get('type') == 'treatment'])
            
            result["pipeline_steps"]["retrieval"] = {
                "duration": step3_time,
                "search_query": search_query,
                "total_results": len(processed_results),
                "emergency_results": emergency_count,
                "treatment_results": treatment_count
            }
            
            print(f"      Search Query: '{search_query}'")
            print(f"      Results: {len(processed_results)} total ({emergency_count} emergency, {treatment_count} treatment)")
            print(f"      Time: {step3_time:.3f}s")
            
            # STEP 4: Medical Advice Generation
            print("   🧠 Step 4: Medical advice generation...")
            step4_start = datetime.now()
            
            # Determine intention (simulate intelligent detection)
            intention = test_case.get('expected_intention')
            
            medical_advice = self.medical_generator.generate_medical_advice(
                user_query=query,
                retrieval_results=retrieval_results,
                intention=intention
            )
            step4_time = (datetime.now() - step4_start).total_seconds()
            
            result["pipeline_steps"]["generation"] = {
                "duration": step4_time,
                "intention_used": intention,
                "confidence_score": medical_advice.get('confidence_score', 0.0),
                "advice_length": len(medical_advice.get('medical_advice', '')),
                "chunks_used": medical_advice.get('query_metadata', {}).get('total_chunks_used', 0)
            }
            
            print(f"      Intention: {intention}")
            print(f"      Confidence: {medical_advice.get('confidence_score', 0.0):.2f}")
            print(f"      Advice Length: {len(medical_advice.get('medical_advice', ''))} chars")
            print(f"      Chunks Used: {medical_advice.get('query_metadata', {}).get('total_chunks_used', 0)}")
            print(f"      Time: {step4_time:.3f}s")
            
            # STEP 5: Results Summary
            total_time = (datetime.now() - pipeline_start).total_seconds()
            result["total_pipeline_time"] = total_time
            result["final_medical_advice"] = medical_advice
            result["success"] = True
            
            print(f"\n   ✅ Pipeline completed successfully!")
            print(f"   📊 Total Time: {total_time:.3f}s")
            print(f"   🩺 Medical Advice Preview:")
            print(f"      {medical_advice.get('medical_advice', 'No advice generated')[:150]}...")
            
        except Exception as e:
            total_time = (datetime.now() - pipeline_start).total_seconds()
            result["total_pipeline_time"] = total_time
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            
            logger.error(f"Pipeline test {test_id} failed: {e}")
            print(f"   ❌ Pipeline failed: {e}")
            
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
    
    def _generate_end_to_end_report(self):
        """Generate comprehensive end-to-end test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        successful_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print("\n" + "=" * 80)
        print("📊 END-TO-END PIPELINE TEST REPORT")
        print("=" * 80)
        
        # Overall Statistics
        print(f"🕐 Execution Summary:")
        print(f"   Test session duration: {total_duration:.3f}s")
        print(f"   Average per test: {total_duration/len(self.test_results):.3f}s")
        
        print(f"\n📈 Pipeline Results:")
        print(f"   Total tests: {len(self.test_results)}")
        print(f"   Successful: {len(successful_tests)} ✅")
        print(f"   Failed: {len(failed_tests)} ❌")
        print(f"   Success rate: {len(successful_tests)/len(self.test_results)*100:.1f}%")
        
        # Performance Analysis
        if successful_tests:
            print(f"\n⚡ Performance Analysis:")
            
            # Calculate average times for each step
            step_times = {}
            for result in successful_tests:
                for step_name, step_data in result.get('pipeline_steps', {}).items():
                    if 'duration' in step_data:
                        if step_name not in step_times:
                            step_times[step_name] = []
                        step_times[step_name].append(step_data['duration'])
            
            for step_name, times in step_times.items():
                avg_time = sum(times) / len(times)
                print(f"   {step_name.replace('_', ' ').title()}: {avg_time:.3f}s average")
            
            # Overall pipeline performance
            total_times = [r['total_pipeline_time'] for r in successful_tests]
            avg_total = sum(total_times) / len(total_times)
            print(f"   Complete Pipeline: {avg_total:.3f}s average")
        
        # Detailed Results
        print(f"\n📝 Detailed Test Results:")
        for result in self.test_results:
            test_case = result['test_case']
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            
            print(f"\n   📋 {result['test_id']}: {status}")
            print(f"      Query: '{test_case['query']}'")
            print(f"      Category: {test_case['category']}")
            print(f"      Total Time: {result['total_pipeline_time']:.3f}s")
            
            if result['success']:
                steps = result.get('pipeline_steps', {})
                if 'condition_extraction' in steps:
                    condition = steps['condition_extraction']['result'].get('condition', 'None')
                    print(f"      Condition Extracted: {condition}")
                
                if 'generation' in steps:
                    confidence = steps['generation'].get('confidence_score', 0.0)
                    chunks = steps['generation'].get('chunks_used', 0)
                    print(f"      Generation: {confidence:.2f} confidence, {chunks} chunks")
                
                if 'final_medical_advice' in result:
                    advice = result['final_medical_advice'].get('medical_advice', '')
                    print(f"      Advice Preview: {advice[:100]}...")
            else:
                if result.get('error'):
                    print(f"      Error: {result['error']}")
                elif 'rejection' in result.get('pipeline_steps', {}):
                    print(f"      Rejected: {result['pipeline_steps']['rejection']['reason']}")
        
        print("\n" + "=" * 80)
    
    def _save_end_to_end_results(self):
        """Save detailed test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = project_root / 'tests' / f'end_to_end_pipeline_results_{timestamp}.json'
        
        try:
            comprehensive_results = {
                "test_metadata": {
                    "test_type": "end_to_end_pipeline",
                    "timestamp": datetime.now().isoformat(),
                    "session_start": self.start_time.isoformat(),
                    "total_duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                    "total_tests": len(self.test_results),
                    "successful_tests": len([r for r in self.test_results if r['success']]),
                    "failed_tests": len([r for r in self.test_results if not r['success']])
                },
                "pipeline_results": self.test_results,
                "component_status": {
                    "user_prompt_processor": "operational",
                    "retrieval_system": "operational", 
                    "medical_generator": "operational",
                    "med42_llm_client": "operational"
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
            
            print(f"📁 End-to-end test results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            print(f"⚠️ Failed to save test results: {e}")

def main():
    """Main execution function"""
    print("🏥 OnCall.ai Complete End-to-End Pipeline Test")
    print("Testing: User Input → UserPrompt → Retrieval → Generation")
    print("=" * 70)
    
    # Initialize test suite
    test_suite = EndToEndPipelineTest()
    
    # Initialize complete pipeline
    test_suite.initialize_complete_pipeline()
    
    if not test_suite.components_initialized:
        print("❌ Pipeline initialization failed. Cannot proceed with testing.")
        return 1
    
    # Run scripted end-to-end tests
    test_suite.run_scripted_end_to_end_tests()
    
    print(f"\n🎯 End-to-end testing completed!")
    print("Next step: Create Gradio interface for interactive testing")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
