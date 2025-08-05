#!/usr/bin/env python3
"""
OnCall.ai System - Retrieval Relevance Evaluator (Metric 3)
===========================================================

Evaluates retrieval relevance using cosine similarity from retrieval.py
Automatic evaluation based on existing similarity scores with optional LLM sampling

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
import numpy as np

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


class RelevanceEvaluator:
    """Retrieval relevance evaluator using cosine similarity - automatic evaluation"""
    
    def __init__(self):
        """Initialize system components for relevance testing"""
        print("🔧 Initializing Relevance Evaluator...")
        
        # Initialize required components
        self.llm_client = llm_Med42_70BClient()
        self.retrieval_system = BasicRetrievalSystem()
        self.user_prompt_processor = UserPromptProcessor(
            llm_client=self.llm_client,
            retrieval_system=self.retrieval_system
        )
        
        # Results accumulation
        self.relevance_results = []
        
        print("✅ Relevance Evaluator initialization complete")
    
    def evaluate_single_relevance(self, query: str, category: str = "unknown") -> Dict[str, Any]:
        """
        Evaluate retrieval relevance for a single query
        
        Uses existing cosine similarity scores from retrieval.py
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"🔍 Testing relevance for: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        try:
            # Step 1: Extract condition for search query construction
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            
            # Step 2: Perform retrieval (same as latency_evaluator.py)
            search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
            if not search_query:
                search_query = condition_result.get('condition', query)
            
            retrieval_start = datetime.now()
            retrieval_results = self.retrieval_system.search(search_query, top_k=5)
            retrieval_time = (datetime.now() - retrieval_start).total_seconds()
            
            # Step 3: Extract similarity scores from retrieval results
            processed_results = retrieval_results.get('processed_results', [])
            
            if not processed_results:
                result = {
                    "query": query,
                    "category": category,
                    "search_query": search_query,
                    "retrieval_success": False,
                    "average_relevance": 0.0,
                    "relevance_scores": [],
                    "retrieved_count": 0,
                    "retrieval_time": retrieval_time,
                    "error": "No retrieval results",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.relevance_results.append(result)
                print(f"   ❌ No retrieval results found")
                return result
            
            # Extract cosine similarity scores
            similarity_scores = []
            retrieval_details = []
            
            for i, doc_result in enumerate(processed_results):
                # Get similarity score (may be stored as 'distance', 'similarity_score', or 'score')
                similarity = (
                    doc_result.get('distance', 0.0) or 
                    doc_result.get('similarity_score', 0.0) or
                    doc_result.get('score', 0.0)
                )
                
                similarity_scores.append(similarity)
                
                retrieval_details.append({
                    "doc_index": i,
                    "similarity_score": similarity,
                    "content_snippet": doc_result.get('content', '')[:100] + "...",
                    "doc_type": doc_result.get('type', 'unknown'),
                    "source": doc_result.get('source', 'unknown')
                })
            
            # Calculate relevance metrics
            average_relevance = sum(similarity_scores) / len(similarity_scores)
            max_relevance = max(similarity_scores)
            min_relevance = min(similarity_scores)
            
            # Count high-relevance results (threshold: 0.2 based on evaluation_instruction.md)
            high_relevance_count = sum(1 for score in similarity_scores if score >= 0.2)
            high_relevance_ratio = high_relevance_count / len(similarity_scores)
            
            result = {
                "query": query,
                "category": category,
                "search_query": search_query,
                "retrieval_success": True,
                "average_relevance": average_relevance,
                "max_relevance": max_relevance,
                "min_relevance": min_relevance,
                "relevance_scores": similarity_scores,
                "high_relevance_count": high_relevance_count,
                "high_relevance_ratio": high_relevance_ratio,
                "retrieved_count": len(processed_results),
                "retrieval_time": retrieval_time,
                "retrieval_details": retrieval_details,
                "meets_threshold": average_relevance >= 0.2,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store result
            self.relevance_results.append(result)
            
            print(f"   ✅ Retrieval: {len(processed_results)} documents")
            print(f"   📊 Average Relevance: {average_relevance:.3f}")
            print(f"   📈 High Relevance (≥0.2): {high_relevance_count}/{len(processed_results)} ({high_relevance_ratio:.1%})")
            print(f"   🎯 Threshold: {'✅ Met' if result['meets_threshold'] else '❌ Not Met'}")
            print(f"   ⏱️ Retrieval Time: {retrieval_time:.3f}s")
            
            return result
            
        except Exception as e:
            error_result = {
                "query": query,
                "category": category,
                "retrieval_success": False,
                "average_relevance": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.relevance_results.append(error_result)
            print(f"   ❌ Relevance evaluation failed: {e}")
            
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
    
    def calculate_relevance_statistics(self) -> Dict[str, Any]:
        """Calculate relevance statistics by category"""
        category_stats = {}
        all_successful_results = []
        
        # Group results by category
        results_by_category = {
            "diagnosis": [],
            "treatment": [],
            "mixed": []
        }
        
        for result in self.relevance_results:
            category = result.get('category', 'unknown')
            if category in results_by_category:
                results_by_category[category].append(result)
                if result.get('retrieval_success'):
                    all_successful_results.append(result)
        
        # Calculate statistics for each category
        for category, results in results_by_category.items():
            successful_results = [r for r in results if r.get('retrieval_success')]
            
            if successful_results:
                avg_relevance = sum(r['average_relevance'] for r in successful_results) / len(successful_results)
                relevance_scores = [r['average_relevance'] for r in successful_results]
                avg_retrieval_time = sum(r.get('retrieval_time', 0) for r in successful_results) / len(successful_results)
                
                category_stats[category] = {
                    "average_relevance": avg_relevance,
                    "max_relevance": max(relevance_scores),
                    "min_relevance": min(relevance_scores),
                    "successful_retrievals": len(successful_results),
                    "total_queries": len(results),
                    "success_rate": len(successful_results) / len(results),
                    "average_retrieval_time": avg_retrieval_time,
                    "meets_threshold": avg_relevance >= 0.2,
                    "individual_relevance_scores": relevance_scores
                }
            else:
                category_stats[category] = {
                    "average_relevance": 0.0,
                    "max_relevance": 0.0,
                    "min_relevance": 0.0,
                    "successful_retrievals": 0,
                    "total_queries": len(results),
                    "success_rate": 0.0,
                    "average_retrieval_time": 0.0,
                    "meets_threshold": False,
                    "individual_relevance_scores": []
                }
        
        # Calculate overall statistics
        if all_successful_results:
            all_relevance_scores = [r['average_relevance'] for r in all_successful_results]
            overall_stats = {
                "average_relevance": sum(all_relevance_scores) / len(all_relevance_scores),
                "max_relevance": max(all_relevance_scores),
                "min_relevance": min(all_relevance_scores),
                "successful_retrievals": len(all_successful_results),
                "total_queries": len(self.relevance_results),
                "success_rate": len(all_successful_results) / len(self.relevance_results),
                "meets_threshold": (sum(all_relevance_scores) / len(all_relevance_scores)) >= 0.2,
                "target_compliance": (sum(all_relevance_scores) / len(all_relevance_scores)) >= 0.25
            }
        else:
            overall_stats = {
                "average_relevance": 0.0,
                "max_relevance": 0.0,
                "min_relevance": 0.0,
                "successful_retrievals": 0,
                "total_queries": len(self.relevance_results),
                "success_rate": 0.0,
                "meets_threshold": False,
                "target_compliance": False
            }
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_relevance_statistics(self, filename: str = None) -> str:
        """Save relevance statistics for chart generation"""
        stats = self.calculate_relevance_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relevance_statistics_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Relevance statistics saved to: {filepath}")
        return str(filepath)
    
    def save_relevance_details(self, filename: str = None) -> str:
        """Save detailed relevance results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relevance_details_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create comprehensive relevance data
        relevance_data = {
            "evaluation_metadata": {
                "total_queries": len(self.relevance_results),
                "successful_retrievals": len([r for r in self.relevance_results if r.get('retrieval_success')]),
                "timestamp": datetime.now().isoformat(),
                "evaluator_type": "retrieval_relevance",
                "threshold_used": 0.2
            },
            "relevance_results": self.relevance_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(relevance_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Relevance details saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent relevance evaluation interface"""
    
    print("📊 OnCall.ai Relevance Evaluator - Retrieval Relevance Analysis")
    
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
    else:
        # Default to evaluation/pre_user_query_evaluate.txt
        query_file = Path(__file__).parent / "pre_user_query_evaluate.txt"
    
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        print("Usage: python relevance_evaluator.py [query_file.txt]")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = RelevanceEvaluator()
    
    # Parse queries from file
    queries_by_category = evaluator.parse_queries_from_file(str(query_file))
    
    if "error" in queries_by_category:
        print(f"❌ Failed to parse queries: {queries_by_category['error']}")
        sys.exit(1)
    
    # Test relevance for each query
    print(f"\n🧪 Retrieval Relevance Testing")
    
    for category, queries in queries_by_category.items():
        if not queries:
            continue
            
        print(f"\n📂 Testing {category.upper()} relevance:")
        
        for i, query_info in enumerate(queries):
            query_text = query_info['text']
            
            # Test relevance
            result = evaluator.evaluate_single_relevance(query_text, category)
            
            # Pause between queries to avoid rate limits
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
    print(f"\n📊 Generating relevance analysis...")
    
    # Save statistics and details
    stats_path = evaluator.save_relevance_statistics()
    details_path = evaluator.save_relevance_details()
    
    # Print final summary
    stats = evaluator.calculate_relevance_statistics()
    category_results = stats['category_results']
    overall_results = stats['overall_results']
    
    print(f"\n📊 === RELEVANCE EVALUATION SUMMARY ===")
    print(f"Overall Performance:")
    print(f"   Average Relevance: {overall_results['average_relevance']:.3f}")
    print(f"   Retrieval Success Rate: {overall_results['success_rate']:.1%}")
    print(f"   0.2 Threshold: {'✅ Met' if overall_results['meets_threshold'] else '❌ Not Met'}")
    print(f"   0.25 Target: {'✅ Met' if overall_results['target_compliance'] else '❌ Not Met'}")
    
    print(f"\nCategory Breakdown:")
    for category, cat_stats in category_results.items():
        if cat_stats['total_queries'] > 0:
            print(f"   {category.capitalize()}: {cat_stats['average_relevance']:.3f} "
                  f"({cat_stats['successful_retrievals']}/{cat_stats['total_queries']}) "
                  f"[{cat_stats['average_retrieval_time']:.3f}s avg]")
    
    print(f"\n✅ Relevance evaluation complete!")
    print(f"📊 Statistics: {stats_path}")
    print(f"📝 Details: {details_path}")
