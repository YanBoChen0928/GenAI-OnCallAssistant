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
from huggingface_hub import InferenceClient

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
        Direct LLM evaluation for single query with retry mechanism for 504 timeouts
        
        Only tests direct LLM response without RAG pipeline
        Applicable metrics: 1 (Latency), 5-6 (via medical output)
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"🔍 Direct LLM evaluation: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        overall_start = time.time()
        
        # Retry configuration
        max_retries = 3
        retry_delay = 30  # seconds
        base_timeout = 120.0  # Increased base timeout for complex medical advice generation
        
        for attempt in range(max_retries):
            try:
                print(f"   🔄 Attempt {attempt + 1}/{max_retries}")
                
                # Direct LLM call without any RAG processing
                llm_start = time.time()
                
                # Create direct medical consultation prompt (matching generation.py format)
                direct_prompt = f"""You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
{query}

Instructions:
Provide comprehensive medical guidance covering both diagnostic and treatment aspects as appropriate.

Provide guidance with:
• Prioritize your medical knowledge and clinical experience
• Use numbered points (1. 2. 3.) for key steps
• Line breaks between major sections
• Highlight medications with dosages and routes
• Emphasize clinical judgment for individual patient factors

IMPORTANT: Keep response under 1000 words. Use concise numbered points. For complex cases with multiple conditions, address the most urgent condition first, then relevant comorbidities. Prioritize actionable clinical steps over theoretical explanations.

Your response should provide practical clinical guidance suitable for immediate bedside application with appropriate medical caution."""
                
                # Direct LLM generation with extended timeout - bypass analyze_medical_query to avoid system prompt conflict
                current_timeout = 120.0 + (attempt * 60)  # 120s, 180s, 240s
                print(f"   ⏱️ Using read timeout = {current_timeout}s")
                
                # Create a new client with appropriate timeout for this attempt
                hf_token = os.getenv('HF_TOKEN')
                if not hf_token:
                    raise ValueError("HF_TOKEN not found in environment variables")
                
                timeout_client = InferenceClient(
                    provider="featherless-ai",
                    api_key=hf_token,
                    timeout=current_timeout
                )
                
                # Call LLM directly to avoid system prompt conflicts
                response = timeout_client.chat.completions.create(
                    model="m42-health/Llama3-Med42-70B",
                    messages=[
                        {
                            "role": "user",
                            "content": direct_prompt  # Our complete prompt as user message
                        }
                    ],
                    max_tokens=1600,
                    temperature=0.1  # Low temperature for consistent medical advice
                )
                # Extract medical advice from direct API response (not Med42 client wrapper)
                medical_advice = response.choices[0].message.content or ""
                
                llm_time = time.time() - llm_start
                total_time = time.time() - overall_start
                
                # Check if response is valid (not empty)
                if not medical_advice or len(medical_advice.strip()) == 0:
                    raise ValueError("Empty response from LLM - no content generated")
                
                # Success - create result and return
                if attempt > 0:
                    print(f"   ✅ Succeeded on attempt {attempt + 1}")
                
                result = {
                    "query": query,
                    "category": category,
                    
                    # Metric 1: Total Latency (direct LLM call time)
                    "latency_metrics": {
                        "total_latency": total_time,
                        "llm_generation_time": llm_time,
                        "meets_target": total_time <= 60.0,
                        "attempts_needed": attempt + 1
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
                error_str = str(e)
                
                # CRITICAL: Check for timeout/connectivity errors FIRST (before any response processing)
                if any(keyword in error_str.lower() for keyword in ['504', 'timeout', 'gateway', 'connection', 'time-out', 'empty response']):
                    if attempt < max_retries - 1:
                        print(f"   ⏳ Timeout/connectivity/empty response error detected, retrying in {retry_delay}s...")
                        print(f"      Error: {error_str}")
                        time.sleep(retry_delay)
                        continue  # Continue to next retry attempt
                    else:
                        print(f"   ❌ All {max_retries} attempts failed with timeouts/empty responses")
                        total_time = time.time() - overall_start
                        return self._create_timeout_failure_result(query, category, error_str, total_time)
                else:
                    # Non-timeout error (e.g., ValueError for empty response), don't retry
                    print(f"   ❌ Non-retry error: {error_str}")
                    total_time = time.time() - overall_start
                    return self._create_general_failure_result(query, category, error_str, total_time)
        
        # Should not reach here
        total_time = time.time() - overall_start
        return self._create_timeout_failure_result(query, category, "Max retries exceeded", total_time)
    
    def _create_timeout_failure_result(self, query: str, category: str, error: str, total_time: float) -> Dict[str, Any]:
        """Create standardized result for timeout failures after all retries"""
        error_result = {
            "query": query,
            "category": category,
            "latency_metrics": {
                "total_latency": total_time,
                "llm_generation_time": 0.0,
                "meets_target": False,
                "failure_type": "timeout_after_retries"
            },
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
            "overall_success": False,
            "error": f"API timeout after retries: {error}",
            "model_type": "Med42-70B_direct",
            "timestamp": datetime.now().isoformat()
        }
        
        self.direct_results.append(error_result)
        print(f"❌ Direct LLM failed after {total_time:.2f}s with retries: {error}")
        return error_result
    
    def _create_general_failure_result(self, query: str, category: str, error: str, total_time: float) -> Dict[str, Any]:
        """Create standardized result for general failures (non-timeout)"""
        error_result = {
            "query": query,
            "category": category,
            "latency_metrics": {
                "total_latency": total_time,
                "llm_generation_time": 0.0,
                "meets_target": False,
                "failure_type": "general_error"
            },
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
            "overall_success": False,
            "error": str(error),
            "model_type": "Med42-70B_direct",
            "timestamp": datetime.now().isoformat()
        }
        
        self.direct_results.append(error_result)
        print(f"❌ Direct LLM failed after {total_time:.2f}s: {error}")
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
