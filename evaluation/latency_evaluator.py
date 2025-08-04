#!/usr/bin/env python3
"""
OnCall.ai System - Latency Evaluator (Single Query Test Mode)
============================================================

Test latency for individual queries to avoid rate limits.
Based on existing system flow: app.py -> user_prompt.py -> retrieval.py -> generation.py

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

# Import existing system components
try:
    from user_prompt import UserPromptProcessor
    from retrieval import BasicRetrievalSystem
    from llm_clients import llm_Med42_70BClient
    from generation import MedicalAdviceGenerator
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure running from project root directory")
    sys.exit(1)


class LatencyEvaluator:
    """Pure latency measurement and medical advice output recording - no visualization"""
    
    def __init__(self):
        """Initialize existing system components"""
        print("🔧 Initializing Latency Evaluator...")
        
        # Initialize existing system components (same as app.py)
        self.llm_client = llm_Med42_70BClient()
        self.retrieval_system = BasicRetrievalSystem()
        self.user_prompt_processor = UserPromptProcessor(
            llm_client=self.llm_client,
            retrieval_system=self.retrieval_system
        )
        self.medical_generator = MedicalAdviceGenerator(llm_client=self.llm_client)
        
        # Results accumulation for summary statistics
        self.accumulated_results = {
            "diagnosis": [],
            "treatment": [],
            "mixed": []
        }
        
        # Medical advice outputs for model comparison
        self.medical_outputs = []
        
        print("✅ Latency Evaluator initialization complete")
    
    def measure_single_query_latency(self, query: str, category: str = "unknown") -> Dict[str, Any]:
        """
        Measure complete processing time for a single query
        
        Replicates app.py's process_medical_query flow with timing focus
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"⏱️ Measuring query latency: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        overall_start = time.time()
        timing_details = {}
        
        try:
            # STEP 1: Condition extraction (user_prompt.py)
            step1_start = time.time()
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            timing_details['step1_condition_extraction'] = time.time() - step1_start
            
            print(f"   Step 1 - Condition extraction: {timing_details['step1_condition_extraction']:.3f}s")
            print(f"   Extracted condition: {condition_result.get('condition', 'None')}")
            
            # Check if valid medical query
            if condition_result.get('query_status') in ['invalid_query', 'non_medical']:
                total_time = time.time() - overall_start
                print(f"   ⚠️ Non-medical query detected")
                return {
                    "query": query,
                    "category": category,
                    "total_latency": total_time,
                    "timing_details": timing_details,
                    "status": "non_medical",
                    "condition_result": condition_result,
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # STEP 2: User confirmation (simulate auto-confirmation)
            step2_start = time.time()
            confirmation = self.user_prompt_processor.handle_user_confirmation(condition_result)
            timing_details['step2_confirmation'] = time.time() - step2_start
            
            print(f"   Step 2 - User confirmation: {timing_details['step2_confirmation']:.3f}s")
            
            # STEP 3: Retrieve relevant guidelines (retrieval.py)
            step3_start = time.time()
            
            search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
            if not search_query:
                search_query = condition_result.get('condition', query)
            
            retrieval_results = self.retrieval_system.search(search_query, top_k=5)
            timing_details['step3_retrieval'] = time.time() - step3_start
            
            retrieved_count = len(retrieval_results.get('processed_results', []))
            print(f"   Step 3 - Retrieval: {timing_details['step3_retrieval']:.3f}s ({retrieved_count} results)")
            
            # STEP 4: Generate medical advice (generation.py)
            step4_start = time.time()
            
            intention = self._detect_query_intention(query)
            medical_advice_result = self.medical_generator.generate_medical_advice(
                user_query=query,
                retrieval_results=retrieval_results,
                intention=intention
            )
            timing_details['step4_generation'] = time.time() - step4_start
            
            print(f"   Step 4 - Generation: {timing_details['step4_generation']:.3f}s")
            
            total_time = time.time() - overall_start
            
            # Extract medical advice output for future model comparison
            medical_advice_text = medical_advice_result.get('medical_advice', '')
            confidence_score = medical_advice_result.get('confidence_score', 0.0)
            
            result = {
                "query": query,
                "category": category,
                "total_latency": total_time,
                "timing_details": timing_details,
                "condition_result": condition_result,
                "retrieval_results": retrieval_results,
                "medical_advice_result": medical_advice_result,
                "status": "success",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store medical output separately for model comparison
            medical_output = {
                "query": query,
                "category": category,
                "medical_advice": medical_advice_text,
                "confidence_score": confidence_score,
                "query_id": f"{category}_query",
                "processing_time": total_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self.medical_outputs.append(medical_output)
            
            print(f"✅ Query completed successfully in {total_time:.2f}s")
            print(f"📝 Medical advice recorded ({len(medical_advice_text)} characters)")
            
            return result
            
        except Exception as e:
            total_time = time.time() - overall_start
            print(f"❌ Query failed after {total_time:.2f}s: {e}")
            
            return {
                "query": query,
                "category": category,
                "total_latency": total_time,
                "timing_details": timing_details,
                "error": str(e),
                "status": "error",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def test_individual_queries_from_file(self, filepath: str) -> Dict[str, List[Dict]]:
        """
        Parse queries from file and return them for individual testing
        
        Returns categorized queries for separate testing
        """
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
                for i, query_info in enumerate(category_queries):
                    print(f"    {i+1}. {query_info['text'][:60]}...")
            
            return queries_by_category
            
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return {"error": f"Failed to read file: {e}"}
    
    def _detect_query_intention(self, query: str) -> str:
        """Simplified query intention detection (from app.py)"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['diagnos', 'differential', 'possible', 'causes']):
            return 'diagnosis'
        elif any(word in query_lower for word in ['treat', 'manage', 'therapy', 'intervention']):
            return 'treatment'
        else:
            return 'mixed'
    
    def save_single_result(self, result: Dict[str, Any], filename: str = None) -> str:
        """Save single query evaluation result"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            category = result.get('category', 'unknown')
            filename = f"latency_{category}_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Result saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent test interface for single queries"""
    
    print("🚀 OnCall.ai Latency Evaluator - Single Query Test Mode")
    
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
    else:
        # Default to evaluation/pre_user_query_evaluate.txt
        query_file = Path(__file__).parent / "pre_user_query_evaluate.txt"
    
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        print("Usage: python latency_evaluator.py [query_file.txt]")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = LatencyEvaluator()
    
    # Parse queries from file
    queries_by_category = evaluator.test_individual_queries_from_file(str(query_file))
    
    if "error" in queries_by_category:
        print(f"❌ Failed to parse queries: {queries_by_category['error']}")
        sys.exit(1)
    
    # Test each category individually
    print(f"\n🧪 Individual Query Testing Mode with Result Accumulation")
    print(f"📝 Test each query separately to avoid rate limits")
    
    for category, queries in queries_by_category.items():
        if not queries:
            continue
            
        print(f"\n📂 Testing {category.upper()} queries:")
        
        for i, query_info in enumerate(queries):
            query_text = query_info['text']
            print(f"\n🔍 Query {i+1}/{len(queries)} in {category} category:")
            print(f"   Text: {query_text}")
            
            # Test single query
            result = evaluator.measure_single_query_latency(query_text, category)
            
            # Add to accumulator for chart generation
            evaluator.add_result_to_accumulator(result)
            
            # Save individual result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"latency_{category}_query{i+1}_{timestamp}.json"
            saved_path = evaluator.save_single_result(result, filename)
            
            # Show summary
            if result.get('success'):
                print(f"   ✅ Success: {result['total_latency']:.2f}s total")
                print(f"      Breakdown: Extract={result['timing_details']['step1_condition_extraction']:.2f}s, "
                      f"Retrieve={result['timing_details']['step3_retrieval']:.2f}s, "
                      f"Generate={result['timing_details']['step4_generation']:.2f}s")
            else:
                print(f"   ❌ Failed: {result.get('status')} - {result.get('error', 'Unknown error')}")
            
            # Pause between queries to avoid rate limits
            if i < len(queries) - 1:  # Not the last query in category
                print(f"   ⏳ Pausing 5s before next query...")
                time.sleep(5)
        
        # Longer pause between categories
        if category != list(queries_by_category.keys())[-1]:  # Not the last category
            print(f"\n⏳ Pausing 10s before next category...")
            time.sleep(10)
    
    # Generate comprehensive analysis (no charts - pure data)
    print(f"\n📊 Generating comprehensive statistical summary...")
    
    # Calculate category statistics
    final_stats = evaluator.calculate_category_statistics()
    
    # Save statistics for chart generation
    stats_path = evaluator.save_statistics_summary()
    
    # Save medical outputs for model comparison
    outputs_path = evaluator.save_medical_outputs()
    
    # Print final summary
    print(f"\n📊 === FINAL LATENCY ANALYSIS SUMMARY ===")
    category_results = final_stats['category_results']
    overall_results = final_stats['overall_results']
    
    print(f"Overall Performance:")
    print(f"   Average Latency: {overall_results['average_latency']:.2f}s (±{overall_results['std_deviation']:.2f})")
    print(f"   Success Rate: {overall_results['successful_queries']}/{overall_results['total_queries']}")
    print(f"   30s Target Compliance: {overall_results['target_compliance']:.1%}")
    
    print(f"\nCategory Breakdown:")
    for category, stats in category_results.items():
        if stats['query_count'] > 0:
            print(f"   {category.capitalize()}: {stats['average_latency']:.2f}s (±{stats['std_deviation']:.2f}) [{stats['query_count']} queries]")
    
    print(f"\n✅ Data collection complete! Files saved:")
    print(f"   📊 Statistics: {stats_path}")
    print(f"   📝 Medical Outputs: {outputs_path}")
    print(f"   📁 Individual results: {Path(__file__).parent / 'results'}")
    print(f"\n💡 Next step: Run latency_chart_generator.py to create visualizations")
    
    def add_result_to_accumulator(self, result: Dict[str, Any]):
        """Add successful result to category accumulator"""
        if result.get('success') and result.get('category') in self.accumulated_results:
            category = result['category']
            self.accumulated_results[category].append(result)
            print(f"📊 Added result to {category} category. Total: {len(self.accumulated_results[category])}")
    
    def save_statistics_summary(self, filename: str = None) -> str:
        """Save statistical summary for chart generation"""
        stats = self.calculate_category_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"latency_statistics_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Statistics saved to: {filepath}")
        return str(filepath)
    
    def save_medical_outputs(self, filename: str = None) -> str:
        """Save medical advice outputs for model comparison"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"medical_outputs_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create comprehensive output data
        output_data = {
            "evaluation_metadata": {
                "total_outputs": len(self.medical_outputs),
                "categories": list(set(output['category'] for output in self.medical_outputs)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "Med42-70B_RAG_enhanced"  # For future comparison
            },
            "medical_outputs": self.medical_outputs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Medical outputs saved to: {filepath}")
        print(f"    Total outputs: {len(self.medical_outputs)}")
        print(f"    Categories: {', '.join(set(output['category'] for output in self.medical_outputs))}")
        
        return str(filepath)
    
    def calculate_category_statistics(self) -> Dict[str, Any]:
        """Calculate statistics for each category and overall"""
        category_stats = {}
        all_successful_latencies = []
        
        for category, results in self.accumulated_results.items():
            latencies = [r['total_latency'] for r in results if r.get('success')]
            
            if latencies:
                category_stats[category] = {
                    "average_latency": sum(latencies) / len(latencies),
                    "std_deviation": self._calculate_std(latencies),
                    "min_latency": min(latencies),
                    "max_latency": max(latencies),
                    "query_count": len(latencies),
                    "individual_latencies": latencies
                }
                all_successful_latencies.extend(latencies)
            else:
                category_stats[category] = {
                    "average_latency": 0.0,
                    "std_deviation": 0.0,
                    "min_latency": 0.0,
                    "max_latency": 0.0,
                    "query_count": 0,
                    "individual_latencies": []
                }
        
        # Calculate overall statistics
        overall_stats = {
            "average_latency": sum(all_successful_latencies) / len(all_successful_latencies) if all_successful_latencies else 0.0,
            "std_deviation": self._calculate_std(all_successful_latencies),
            "min_latency": min(all_successful_latencies) if all_successful_latencies else 0.0,
            "max_latency": max(all_successful_latencies) if all_successful_latencies else 0.0,
            "total_queries": sum(len(results) for results in self.accumulated_results.values()),
            "successful_queries": len(all_successful_latencies),
            "target_compliance": sum(1 for lat in all_successful_latencies if lat <= 30.0) / len(all_successful_latencies) if all_successful_latencies else 0.0
        }
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5