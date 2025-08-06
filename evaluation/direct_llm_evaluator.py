#!/usr/bin/env python3
"""
OnCall.ai System - Direct LLM Evaluator (Med42-70B Only)
========================================================

Tests Med42-70B directly without RAG pipeline.
Only applicable metrics: 1 (Latency), 5 (Actionability), 6 (Evidence Quality)

Metrics 2-4 (Extraction, Relevance, Coverage) are not applicable for direct LLM.

Author: YanBo Chen  
Date: 2025-08-04
"""

import time
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

# Import LLM client only (no retrieval system needed)
try:
    from llm_clients import llm_Med42_70BClient
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure running from project root directory")
    sys.exit(1)


class DirectLLMEvaluator:
    """Direct LLM evaluation without RAG pipeline"""
    
    def __init__(self):
        """Initialize direct LLM client only"""
        print("🔧 Initializing Direct LLM Evaluator...")
        
        # Initialize only LLM client (no retrieval, no user_prompt processing)
        self.llm_client = llm_Med42_70BClient()
        
        # Results accumulation
        self.direct_results = []
        self.medical_outputs = []
        
        print("✅ Direct LLM Evaluator initialization complete")
    
    def evaluate_direct_llm_query(self, query: str, category: str = "unknown") -> Dict[str, Any]:
        """
        Direct LLM evaluation for single query
        
        Only tests direct LLM response without RAG pipeline
        Applicable metrics: 1 (Latency), 5-6 (via medical output)
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"🔍 Direct LLM evaluation: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        overall_start = time.time()
        
        try:
            # Direct LLM call without any RAG processing
            llm_start = time.time()
            
            # Create direct medical consultation prompt
            direct_prompt = f"""
You are a medical expert providing clinical guidance.

Patient Query: {query}

Please provide comprehensive medical advice including:
1. Differential diagnosis (if applicable)
2. Immediate assessment steps
3. Treatment recommendations
4. Clinical considerations

Provide evidence-based, actionable medical guidance.
"""
            
            # Direct LLM generation (same parameters as RAG system for fair comparison)
            response = self.llm_client.analyze_medical_query(
                query=direct_prompt,
                max_tokens=1600,  # Same as RAG system primary setting  
                timeout=60.0      # Increased timeout for stable evaluation
            )
            # Extract medical advice from response (Med42 client returns dict with 'raw_response')
            if isinstance(response, dict):
                medical_advice = response.get('raw_response', '') or response.get('content', '')
            else:
                medical_advice = str(response)
            
            llm_time = time.time() - llm_start
            total_time = time.time() - overall_start
            
            # Check if response is valid (not empty) - focus on content, not timeout
            if not medical_advice or len(medical_advice.strip()) == 0:
                print(f"❌ Direct LLM returned empty response after {total_time:.2f}s")
                raise ValueError("Empty response from LLM - no content generated")
            
            # Create result
            result = {
                "query": query,
                "category": category,
                
                # Metric 1: Total Latency (direct LLM call time)
                "latency_metrics": {
                    "total_latency": total_time,
                    "llm_generation_time": llm_time,
                    "meets_target": total_time <= 60.0
                },
                
                # Metrics 2-4: Not applicable for direct LLM
                "extraction_metrics": {
                    "not_applicable": True,
                    "reason": "No extraction pipeline in direct LLM"
                },
                "relevance_metrics": {
                    "not_applicable": True,
                    "reason": "No retrieval pipeline in direct LLM"
                },
                "coverage_metrics": {
                    "not_applicable": True,
                    "reason": "No retrieval content to cover"
                },
                
                # Medical advice for metrics 5-6 evaluation
                "medical_advice": medical_advice,
                "advice_length": len(medical_advice),
                
                "overall_success": True,
                "model_type": "Med42-70B_direct",
                "timestamp": datetime.now().isoformat()
            }
            
            # Store result
            self.direct_results.append(result)
            
            # Store medical output for LLM judge evaluation
            medical_output = {
                "query": query,
                "category": category,
                "medical_advice": medical_advice,
                "query_id": f"{category}_query_direct",
                "model_type": "Med42-70B_direct",
                "processing_time": total_time,
                "timestamp": datetime.now().isoformat()
            }
            self.medical_outputs.append(medical_output)
            
            print(f"✅ Direct LLM completed in {total_time:.2f}s")
            print(f"📝 Generated advice: {len(medical_advice)} characters")
            
            return result
            
        except Exception as e:
            total_time = time.time() - overall_start
            print(f"❌ Direct LLM evaluation failed after {total_time:.2f}s: {e}")
            
            error_result = {
                "query": query,
                "category": category,
                "latency_metrics": {
                    "total_latency": total_time,
                    "meets_target": False
                },
                "overall_success": False,
                "error": str(e),
                "model_type": "Med42-70B_direct",
                "timestamp": datetime.now().isoformat()
            }
            
            self.direct_results.append(error_result)
            
            # Do NOT add failed queries to medical_outputs for judge evaluation
            # Only successful queries with valid medical advice should be evaluated
            
            return error_result
    
    def parse_queries_from_file(self, filepath: str) -> Dict[str, List[Dict]]:
        """Parse queries from file with category labels"""
        print(f"📁 Reading queries from file: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
                
                match = re.match(r'^\d+\.(diagnosis|treatment|mixed/complicated|mixed):\s*(.+)', line, re.IGNORECASE)
                if match:
                    category_raw = match.group(1).lower()
                    query_text = match.group(2).strip()
                    
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
    
    def calculate_direct_llm_statistics(self) -> Dict[str, Any]:
        """Calculate statistics for direct LLM evaluation"""
        successful_results = [r for r in self.direct_results if r.get('overall_success')]
        
        if successful_results:
            latencies = [r['latency_metrics']['total_latency'] for r in successful_results]
            
            # Category-wise statistics
            category_stats = {}
            results_by_category = {"diagnosis": [], "treatment": [], "mixed": []}
            
            for result in successful_results:
                category = result.get('category', 'unknown')
                if category in results_by_category:
                    results_by_category[category].append(result)
            
            for category, results in results_by_category.items():
                if results:
                    cat_latencies = [r['latency_metrics']['total_latency'] for r in results]
                    category_stats[category] = {
                        "average_latency": sum(cat_latencies) / len(cat_latencies),
                        "query_count": len(cat_latencies),
                        "target_compliance": sum(1 for lat in cat_latencies if lat <= 60.0) / len(cat_latencies)
                    }
                else:
                    category_stats[category] = {
                        "average_latency": 0.0,
                        "query_count": 0,
                        "target_compliance": 0.0
                    }
            
            # Overall statistics
            overall_stats = {
                "average_latency": sum(latencies) / len(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "successful_queries": len(successful_results),
                "total_queries": len(self.direct_results),
                "success_rate": len(successful_results) / len(self.direct_results),
                "target_compliance": sum(1 for lat in latencies if lat <= 60.0) / len(latencies)
            }
        else:
            category_stats = {cat: {"average_latency": 0.0, "query_count": 0, "target_compliance": 0.0} 
                            for cat in ["diagnosis", "treatment", "mixed"]}
            overall_stats = {
                "average_latency": 0.0,
                "successful_queries": 0,
                "total_queries": len(self.direct_results),
                "success_rate": 0.0,
                "target_compliance": 0.0
            }
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "model_type": "Med42-70B_direct",
            "timestamp": datetime.now().isoformat()
        }
    
    def save_direct_llm_statistics(self, filename: str = None) -> str:
        """Save direct LLM statistics"""
        stats = self.calculate_direct_llm_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"direct_llm_statistics_{timestamp}.json"
        
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Direct LLM statistics saved to: {filepath}")
        return str(filepath)
    
    def save_direct_medical_outputs(self, filename: str = None) -> str:
        """Save medical outputs for LLM judge evaluation"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"medical_outputs_direct_{timestamp}.json"
        
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        filepath = results_dir / filename
        
        output_data = {
            "evaluation_metadata": {
                "total_outputs": len(self.medical_outputs),
                "categories": list(set(output['category'] for output in self.medical_outputs)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "Med42-70B_direct"
            },
            "medical_outputs": self.medical_outputs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Direct medical outputs saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent direct LLM evaluation interface"""
    
    print("🚀 OnCall.ai Direct LLM Evaluator - Med42-70B Only")
    
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
    else:
        # Default to evaluation/single_test_query.txt for consistency
        # TODO: Change to pre_user_query_evaluate.txt for full evaluation
        query_file = Path(__file__).parent / "pre_user_query_evaluate.txt"
    
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        print("Usage: python direct_llm_evaluator.py [query_file.txt]")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = DirectLLMEvaluator()
    
    # Parse queries
    queries_by_category = evaluator.parse_queries_from_file(str(query_file))
    
    if "error" in queries_by_category:
        print(f"❌ Failed to parse queries: {queries_by_category['error']}")
        sys.exit(1)
    
    # Test direct LLM for each query
    print(f"\n🧪 Direct LLM Testing (No RAG Pipeline)")
    
    for category, queries in queries_by_category.items():
        if not queries:
            continue
            
        print(f"\n📂 Testing {category.upper()} with direct Med42-70B:")
        
        for i, query_info in enumerate(queries):
            query_text = query_info['text']
            
            # Direct LLM evaluation
            result = evaluator.evaluate_direct_llm_query(query_text, category)
            
            # Pause between queries
            if i < len(queries) - 1:
                print(f"   ⏳ Pausing 5s before next query...")
                time.sleep(5)
        
        # Pause between categories
        if category != list(queries_by_category.keys())[-1]:
            print(f"\n⏳ Pausing 10s before next category...")
            time.sleep(10)
    
    # Save results
    print(f"\n📊 Generating direct LLM analysis...")
    
    stats_path = evaluator.save_direct_llm_statistics()
    outputs_path = evaluator.save_direct_medical_outputs()
    
    # Print summary
    stats = evaluator.calculate_direct_llm_statistics()
    overall_results = stats['overall_results']
    
    print(f"\n📊 === DIRECT LLM EVALUATION SUMMARY ===")
    print(f"Overall Performance:")
    print(f"   Average Latency: {overall_results['average_latency']:.2f}s")
    print(f"   Success Rate: {overall_results['successful_queries']}/{overall_results['total_queries']}")
    print(f"   60s Target Compliance: {overall_results['target_compliance']:.1%}")
    
    print(f"\nApplicable Metrics:")
    print(f"   ✅ Metric 1 (Latency): Measured")
    print(f"   ❌ Metric 2 (Extraction): Not applicable - no extraction pipeline")
    print(f"   ❌ Metric 3 (Relevance): Not applicable - no retrieval pipeline")
    print(f"   ❌ Metric 4 (Coverage): Not applicable - no retrieval content")
    print(f"   🔄 Metric 5 (Actionability): Requires LLM judge evaluation")
    print(f"   🔄 Metric 6 (Evidence): Requires LLM judge evaluation")
    
    print(f"\n✅ Direct LLM evaluation complete!")
    print(f"📊 Statistics: {stats_path}")
    print(f"📝 Medical Outputs: {outputs_path}")
    print(f"\n💡 Next step: Run python metric5_6_llm_judge_evaluator.py rag,direct for metrics 5-6")
