#!/usr/bin/env python3
"""
Test script for OnCall.ai retrieval pipeline

This script tests the complete flow:
user_input → user_prompt.py → retrieval.py

Author: OnCall.ai Team
Date: 2025-07-30
"""

import sys
import os
from pathlib import Path
import logging
import json
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our modules
from user_prompt import UserPromptProcessor
from retrieval import BasicRetrievalSystem
from llm_clients import llm_Med42_70BClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_retrieval_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

def test_retrieval_pipeline():
    """
    Test the complete retrieval pipeline
    """
    print("="*60)
    print("OnCall.ai Retrieval Pipeline Test")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        
        # Initialize LLM client
        llm_client = llm_Med42_70BClient()
        print("✅ LLM client initialized")
        
        # Initialize retrieval system
        retrieval_system = BasicRetrievalSystem()
        print("✅ Retrieval system initialized")
        
        # Initialize user prompt processor
        user_prompt_processor = UserPromptProcessor(
            llm_client=llm_client,
            retrieval_system=retrieval_system
        )
        print("✅ User prompt processor initialized")
        print()
        
        # Test queries
        test_queries = [
            "how to treat acute MI?",
            "patient with chest pain and shortness of breath",
            "sudden neurological symptoms suggesting stroke",
            "acute stroke management protocol"
        ]
        
        results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 Test {i}/{len(test_queries)}: Testing query: '{query}'")
            print("-" * 50)
            
            try:
                # Step 1: Extract condition keywords
                print("Step 1: Extracting condition keywords...")
                condition_result = user_prompt_processor.extract_condition_keywords(query)
                
                print(f"  Condition: {condition_result.get('condition', 'None')}")
                print(f"  Emergency keywords: {condition_result.get('emergency_keywords', 'None')}")
                print(f"  Treatment keywords: {condition_result.get('treatment_keywords', 'None')}")
                
                if not condition_result.get('condition'):
                    print("  ⚠️  No condition extracted, skipping retrieval")
                    continue
                
                # Step 2: User confirmation (simulated)
                print("\nStep 2: User confirmation (simulated as 'yes')")
                confirmation = user_prompt_processor.handle_user_confirmation(condition_result)
                print(f"  Confirmation type: {confirmation.get('type', 'Unknown')}")
                
                # Step 3: Perform retrieval
                print("\nStep 3: Performing retrieval...")
                search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
                
                if not search_query:
                    search_query = condition_result.get('condition', query)
                
                print(f"  Search query: '{search_query}'")
                
                retrieval_results = retrieval_system.search(search_query, top_k=5)
                
                # Display results
                print(f"\n📊 Retrieval Results:")
                print(f"  Total results: {retrieval_results.get('total_results', 0)}")
                
                emergency_results = retrieval_results.get('emergency_results', [])
                treatment_results = retrieval_results.get('treatment_results', [])
                
                print(f"  Emergency results: {len(emergency_results)}")
                print(f"  Treatment results: {len(treatment_results)}")
                
                # Show top results
                if 'processed_results' in retrieval_results:
                    processed_results = retrieval_results['processed_results'][:3]  # Show top 3
                    print(f"\n  Top {len(processed_results)} results:")
                    for j, result in enumerate(processed_results, 1):
                        print(f"    {j}. Type: {result.get('type', 'Unknown')}")
                        print(f"       Distance: {result.get('distance', 'Unknown'):.4f}")
                        print(f"       Text preview: {result.get('text', '')[:100]}...")
                        print(f"       Matched: {result.get('matched', 'None')}")
                        print(f"       Treatment matched: {result.get('matched_treatment', 'None')}")
                        print()
                
                # Store results for summary
                test_result = {
                    'query': query,
                    'condition_extracted': condition_result.get('condition', ''),
                    'emergency_keywords': condition_result.get('emergency_keywords', ''),
                    'treatment_keywords': condition_result.get('treatment_keywords', ''),
                    'search_query': search_query,
                    'total_results': retrieval_results.get('total_results', 0),
                    'emergency_count': len(emergency_results),
                    'treatment_count': len(treatment_results),
                    'success': True
                }
                results.append(test_result)
                
                print("✅ Test completed successfully")
                
            except Exception as e:
                logger.error(f"Error in test {i}: {e}", exc_info=True)
                test_result = {
                    'query': query,
                    'error': str(e),
                    'success': False
                }
                results.append(test_result)
                print(f"❌ Test failed: {e}")
            
            print("\n" + "="*60 + "\n")
        
        # Print summary
        print_test_summary(results)
        
        # Save results to file
        save_test_results(results)
        
        return results
        
    except Exception as e:
        logger.error(f"Critical error in pipeline test: {e}", exc_info=True)
        print(f"❌ Critical error: {e}")
        return []

def print_test_summary(results):
    """Print test summary"""
    print("📋 TEST SUMMARY")
    print("="*60)
    
    successful_tests = [r for r in results if r.get('success', False)]
    failed_tests = [r for r in results if not r.get('success', False)]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {len(successful_tests)/len(results)*100:.1f}%")
    print()
    
    if successful_tests:
        print("✅ Successful tests:")
        for result in successful_tests:
            print(f"  - '{result['query']}'")
            print(f"    Condition: {result.get('condition_extracted', 'None')}")
            print(f"    Results: {result.get('total_results', 0)} total "
                  f"({result.get('emergency_count', 0)} emergency, "
                  f"{result.get('treatment_count', 0)} treatment)")
            print()
    
    if failed_tests:
        print("❌ Failed tests:")
        for result in failed_tests:
            print(f"  - '{result['query']}': {result.get('error', 'Unknown error')}")
        print()

def save_test_results(results):
    """Save test results to JSON file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'test_results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Test results saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to save test results: {e}")
        print(f"⚠️  Failed to save test results: {e}")

if __name__ == "__main__":
    test_retrieval_pipeline()
