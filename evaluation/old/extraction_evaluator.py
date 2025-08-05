#!/usr/bin/env python3
"""
OnCall.ai System - Condition Extraction Evaluator (Metric 2)
============================================================

Evaluates condition extraction success rate from user_prompt.py
Pure automatic evaluation based on extract_condition_keywords() results

Author: YanBo Chen  
Date: 2025-08-04
"""

import json
import os
import sys
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import re

# Add project path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import existing system components
try:
    from user_prompt import UserPromptProcessor
    from retrieval import BasicRetrievalSystem
    from llm_clients import llm_Med42_70BClient
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure running from project root directory")
    sys.exit(1)


class ExtractionEvaluator:
    """Condition extraction success rate evaluator - pure automatic evaluation"""
    
    def __init__(self):
        """Initialize system components for extraction testing"""
        print("🔧 Initializing Extraction Evaluator...")
        
        # Initialize required components for extraction
        self.llm_client = llm_Med42_70BClient()
        self.retrieval_system = BasicRetrievalSystem()
        self.user_prompt_processor = UserPromptProcessor(
            llm_client=self.llm_client,
            retrieval_system=self.retrieval_system
        )
        
        # Results accumulation
        self.extraction_results = []
        
        print("✅ Extraction Evaluator initialization complete")
    
    def evaluate_single_extraction(self, query: str, category: str = "unknown") -> Dict[str, Any]:
        """
        Evaluate condition extraction success for a single query
        
        Tests user_prompt.py extract_condition_keywords() method
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"🔍 Testing extraction for: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        try:
            # Call the actual extraction method from user_prompt.py
            extraction_start = datetime.now()
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            extraction_time = (datetime.now() - extraction_start).total_seconds()
            
            # Analyze extraction success
            extracted_condition = condition_result.get('condition')
            query_status = condition_result.get('query_status')
            emergency_keywords = condition_result.get('emergency_keywords', [])
            treatment_keywords = condition_result.get('treatment_keywords', [])
            fallback_level = condition_result.get('fallback_level', 'unknown')
            
            # Define success criteria
            is_successful = (
                extracted_condition and 
                extracted_condition.strip() and 
                extracted_condition != "unknown" and
                query_status not in ['invalid_query', 'non_medical']
            )
            
            result = {
                "query": query,
                "category": category,
                "extraction_success": is_successful,
                "extraction_time": extraction_time,
                "extracted_condition": extracted_condition,
                "query_status": query_status,
                "emergency_keywords": emergency_keywords,
                "treatment_keywords": treatment_keywords,
                "fallback_level": fallback_level,
                "full_condition_result": condition_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store result
            self.extraction_results.append(result)
            
            print(f"   ✅ Extraction: {'Success' if is_successful else 'Failed'}")
            print(f"   📝 Condition: {extracted_condition}")
            print(f"   🎯 Status: {query_status}")
            print(f"   ⏱️ Time: {extraction_time:.3f}s")
            print(f"   🔄 Fallback Level: {fallback_level}")
            
            return result
            
        except Exception as e:
            error_result = {
                "query": query,
                "category": category,
                "extraction_success": False,
                "extraction_time": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.extraction_results.append(error_result)
            print(f"   ❌ Extraction failed: {e}")
            
            return error_result
    
    def parse_queries_from_file(self, filepath: str) -> Dict[str, List[Dict]]:
        """Parse queries from file with category labels"""
        print(f"📁 Reading queries from file: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse queries with category labels
            queries_by_category = {
                "diagnosis": [],
                "treatment": [], 
                "mixed": []
            }
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse format: "1.diagnosis: query text"
                match = re.match(r'^\d+\.(diagnosis|treatment|mixed/complicated|mixed):\s*(.+)', line, re.IGNORECASE)
                if match:
                    category_raw = match.group(1).lower()
                    query_text = match.group(2).strip()
                    
                    # Normalize category name
                    if category_raw in ['mixed/complicated', 'mixed']:
                        category = 'mixed'
                    else:
                        category = category_raw
                    
                    if category in queries_by_category and len(query_text) > 15:
                        queries_by_category[category].append({
                            "text": query_text,
                            "category": category
                        })
            
            print(f"📋 Parsed queries by category:")
            for category, category_queries in queries_by_category.items():
                print(f"  {category.capitalize()}: {len(category_queries)} queries")
            
            return queries_by_category
            
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return {"error": f"Failed to read file: {e}"}
    
    def calculate_extraction_statistics(self) -> Dict[str, Any]:
        """Calculate extraction success statistics by category"""
        category_stats = {}
        all_results = []
        
        # Group results by category
        results_by_category = {
            "diagnosis": [],
            "treatment": [],
            "mixed": []
        }
        
        for result in self.extraction_results:
            category = result.get('category', 'unknown')
            if category in results_by_category:
                results_by_category[category].append(result)
                all_results.append(result)
        
        # Calculate statistics for each category
        for category, results in results_by_category.items():
            if results:
                successful = [r for r in results if r.get('extraction_success')]
                success_rate = len(successful) / len(results)
                avg_time = sum(r.get('extraction_time', 0) for r in results) / len(results)
                
                category_stats[category] = {
                    "success_rate": success_rate,
                    "successful_count": len(successful),
                    "total_count": len(results),
                    "average_extraction_time": avg_time,
                    "fallback_levels": [r.get('fallback_level') for r in results]
                }
            else:
                category_stats[category] = {
                    "success_rate": 0.0,
                    "successful_count": 0,
                    "total_count": 0,
                    "average_extraction_time": 0.0,
                    "fallback_levels": []
                }
        
        # Calculate overall statistics
        if all_results:
            overall_successful = [r for r in all_results if r.get('extraction_success')]
            overall_stats = {
                "success_rate": len(overall_successful) / len(all_results),
                "successful_count": len(overall_successful),
                "total_count": len(all_results),
                "average_extraction_time": sum(r.get('extraction_time', 0) for r in all_results) / len(all_results),
                "target_compliance": len(overall_successful) / len(all_results) >= 0.8
            }
        else:
            overall_stats = {
                "success_rate": 0.0,
                "successful_count": 0,
                "total_count": 0,
                "average_extraction_time": 0.0,
                "target_compliance": False
            }
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_extraction_statistics(self, filename: str = None) -> str:
        """Save extraction statistics for chart generation"""
        stats = self.calculate_extraction_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extraction_statistics_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Extraction statistics saved to: {filepath}")
        return str(filepath)
    
    def save_extraction_details(self, filename: str = None) -> str:
        """Save detailed extraction results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extraction_details_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create comprehensive extraction data
        extraction_data = {
            "evaluation_metadata": {
                "total_queries": len(self.extraction_results),
                "timestamp": datetime.now().isoformat(),
                "evaluator_type": "condition_extraction"
            },
            "extraction_results": self.extraction_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(extraction_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Extraction details saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent extraction evaluation interface"""
    
    print("🔍 OnCall.ai Extraction Evaluator - Condition Extraction Success Rate")
    
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
    else:
        # Default to evaluation/pre_user_query_evaluate.txt
        query_file = Path(__file__).parent / "pre_user_query_evaluate.txt"
    
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        print("Usage: python extraction_evaluator.py [query_file.txt]")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = ExtractionEvaluator()
    
    # Parse queries from file
    queries_by_category = evaluator.parse_queries_from_file(str(query_file))
    
    if "error" in queries_by_category:
        print(f"❌ Failed to parse queries: {queries_by_category['error']}")
        sys.exit(1)
    
    # Test extraction for each query
    print(f"\n🧪 Condition Extraction Testing")
    
    for category, queries in queries_by_category.items():
        if not queries:
            continue
            
        print(f"\n📂 Testing {category.upper()} extraction:")
        
        for i, query_info in enumerate(queries):
            query_text = query_info['text']
            
            # Test extraction
            result = evaluator.evaluate_single_extraction(query_text, category)
            
            # Pause between queries to avoid rate limits (if needed)
            if i < len(queries) - 1:
                print(f"   ⏳ Pausing 3s before next query...")
                import time
                time.sleep(3)
        
        # Pause between categories
        if category != list(queries_by_category.keys())[-1]:
            print(f"\n⏳ Pausing 5s before next category...")
            import time
            time.sleep(5)
    
    # Generate and save results
    print(f"\n📊 Generating extraction analysis...")
    
    # Save statistics and details
    stats_path = evaluator.save_extraction_statistics()
    details_path = evaluator.save_extraction_details()
    
    # Print final summary
    stats = evaluator.calculate_extraction_statistics()
    category_results = stats['category_results']
    overall_results = stats['overall_results']
    
    print(f"\n📊 === EXTRACTION EVALUATION SUMMARY ===")
    print(f"Overall Performance:")
    print(f"   Success Rate: {overall_results['success_rate']:.1%}")
    print(f"   Successful Extractions: {overall_results['successful_count']}/{overall_results['total_count']}")
    print(f"   Average Extraction Time: {overall_results['average_extraction_time']:.3f}s")
    print(f"   80% Target Compliance: {'✅ Met' if overall_results['target_compliance'] else '❌ Not Met'}")
    
    print(f"\nCategory Breakdown:")
    for category, cat_stats in category_results.items():
        if cat_stats['total_count'] > 0:
            print(f"   {category.capitalize()}: {cat_stats['success_rate']:.1%} "
                  f"({cat_stats['successful_count']}/{cat_stats['total_count']}) "
                  f"[{cat_stats['average_extraction_time']:.3f}s avg]")
    
    print(f"\n✅ Extraction evaluation complete!")
    print(f"📊 Statistics: {stats_path}")
    print(f"📝 Details: {details_path}")
