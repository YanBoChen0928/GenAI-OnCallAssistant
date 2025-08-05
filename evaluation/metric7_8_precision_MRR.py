#!/usr/bin/env python3
"""
OnCall.ai System - Precision & MRR Analyzer (Metrics 7-8)
========================================================

Specialized analyzer for calculating Precision@K and Mean Reciprocal Rank (MRR)
using data collected from latency_evaluator.py comprehensive evaluation.

IMPORTANT CHANGES - Angular Distance & Relevance Calculation:
- DISTANCE METRIC: Uses Angular Distance from Annoy index (range: 0.0-1.0, smaller = more relevant)
- RELEVANCE CONVERSION: relevance = 1.0 - (angular_distance²) / 2.0 (mathematical correct formula)
- THRESHOLD ALIGNMENT: Aligned with Metric 3 relevance calculation standards
- DISPLAY UPDATE: Changed from "Relevance: X" to "Angular Distance: X" for clarity

METRICS CALCULATED:
7. Precision@K (檢索精確率) - Proportion of relevant results in top-K retrieval
8. Mean Reciprocal Rank (平均倒數排名) - Average reciprocal rank of first relevant result

DESIGN PRINCIPLE:
- Reuses comprehensive_details_*.json from latency_evaluator.py
- Implements adaptive threshold based on query complexity
- Query complexity determined by actual matched emergency keywords count
- No additional LLM calls required

Author: YanBo Chen  
Date: 2025-08-04
Updated: 2025-08-04 (Angular Distance alignment)
"""

import json
import os
import sys
from typing import Dict, List, Any, Set
from datetime import datetime
from pathlib import Path
import re
import statistics

# Relevance threshold constants for adaptive query complexity handling
COMPLEX_QUERY_RELEVANCE_THRESHOLD = 0.65  # For queries with multiple emergency keywords
SIMPLE_QUERY_RELEVANCE_THRESHOLD = 0.75   # For straightforward diagnostic queries

class PrecisionMRRAnalyzer:
    """Specialized analyzer for metrics 7-8 using existing comprehensive evaluation data"""
    
    def __init__(self):
        """Initialize analyzer"""
        print("🔧 Initializing Precision & MRR Analyzer...")
        self.analysis_results = []
        print("✅ Analyzer initialization complete")
    
    def load_comprehensive_data(self, filepath: str) -> List[Dict]:
        """
        Load comprehensive evaluation data from latency_evaluator.py output
        
        Args:
            filepath: Path to comprehensive_details_*.json file
            
        Returns:
            List of comprehensive evaluation results
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            comprehensive_results = data.get('comprehensive_results', [])
            
            print(f"📁 Loaded {len(comprehensive_results)} comprehensive evaluation results")
            print(f"📊 Ready for precision/MRR analysis: {sum(1 for r in comprehensive_results if r.get('precision_mrr_ready'))}")
            
            return comprehensive_results
            
        except Exception as e:
            print(f"❌ Failed to load comprehensive data: {e}")
            return []
    
    def _is_complex_query(self, query: str, processed_results: List[Dict]) -> bool:
        """
        Determine query complexity based on actual matched emergency keywords
        
        Args:
            query: Original query text
            processed_results: Retrieval results with matched keywords
            
        Returns:
            True if query is complex (should use lenient threshold)
        """
        # Collect unique emergency keywords actually found in retrieval results
        unique_emergency_keywords = set()
        
        for result in processed_results:
            if result.get('type') == 'emergency':
                matched_keywords = result.get('matched', '')
                if matched_keywords:
                    keywords = [kw.strip() for kw in matched_keywords.split('|') if kw.strip()]
                    unique_emergency_keywords.update(keywords)
        
        keyword_count = len(unique_emergency_keywords)
        
        # Business logic: 4+ different emergency keywords indicate complex case
        is_complex = keyword_count >= 4
        
        print(f"   🧠 Query complexity: {'Complex' if is_complex else 'Simple'} ({keyword_count} emergency keywords)")
        print(f"   🔑 Found keywords: {', '.join(list(unique_emergency_keywords)[:5])}")
        
        return is_complex
    
    def calculate_precision_mrr_single(self, query_data: Dict) -> Dict[str, Any]:
        """
        Calculate precision@K and MRR for single query
        
        Args:
            query_data: Single query's comprehensive evaluation result
            
        Returns:
            Precision and MRR metrics for this query
        """
        query = query_data['query']
        category = query_data['category']
        
        # Extract processed results from pipeline data
        pipeline_data = query_data.get('pipeline_data', {})
        retrieval_results = pipeline_data.get('retrieval_results', {})
        processed_results = retrieval_results.get('processed_results', [])
        
        print(f"🔍 Analyzing precision/MRR for: {query[:50]}...")
        print(f"📋 Category: {category}, Results: {len(processed_results)}")
        
        if not processed_results:
            return self._create_empty_precision_mrr_result(query, category)
        
        # Step 1: Determine query complexity
        is_complex = self._is_complex_query(query, processed_results)
        
        # Step 2: Choose adaptive threshold (aligned with Metric 3 relevance standards)
        threshold = COMPLEX_QUERY_RELEVANCE_THRESHOLD if is_complex else SIMPLE_QUERY_RELEVANCE_THRESHOLD  # Updated thresholds for complex/simple queries
        
        print(f"   🎯 Using relevance threshold: {threshold} ({'lenient' if is_complex else 'strict'})")
        
        # Step 3: Calculate relevance scores using correct angular distance formula
        relevance_scores = []
        for result in processed_results:
            distance = result.get('distance', 1.0)
            relevance = 1.0 - (distance**2) / 2.0  # Correct mathematical conversion
            relevance_scores.append(relevance)
        
        # Step 4: Calculate Precision@K (aligned with Metric 3 thresholds)
        relevant_count = sum(1 for score in relevance_scores if score >= threshold)
        precision_at_k = relevant_count / len(processed_results)
        
        # Step 5: Calculate MRR
        first_relevant_rank = None
        for i, score in enumerate(relevance_scores, 1):
            if score >= threshold:
                first_relevant_rank = i
                break
        
        mrr_score = (1.0 / first_relevant_rank) if first_relevant_rank else 0.0
        
        # Detailed analysis
        result = {
            "query": query,
            "category": category,
            "query_complexity": "complex" if is_complex else "simple",
            "threshold_used": threshold,
            
            # Metric 7: Precision@K
            "precision_at_k": precision_at_k,
            "relevant_count": relevant_count,
            "total_results": len(processed_results),
            
            # Metric 8: MRR
            "mrr_score": mrr_score,
            "first_relevant_rank": first_relevant_rank,
            
            # Supporting data
            "relevance_scores": relevance_scores,
            "avg_relevance": sum(relevance_scores) / len(relevance_scores),
            "max_relevance": max(relevance_scores),
            "min_relevance": min(relevance_scores),
            
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   📊 Precision@{len(processed_results)}: {precision_at_k:.3f} ({relevant_count}/{len(processed_results)} relevant)")
        print(f"   📊 MRR: {mrr_score:.3f} (first relevant at rank {first_relevant_rank})")
        
        return result
    
    def _create_empty_precision_mrr_result(self, query: str, category: str) -> Dict[str, Any]:
        """Create empty result for failed queries"""
        return {
            "query": query,
            "category": category,
            "query_complexity": "unknown",
            "threshold_used": 0.0,
            "precision_at_k": 0.0,
            "relevant_count": 0,
            "total_results": 0,
            "mrr_score": 0.0,
            "first_relevant_rank": None,
            "relevance_scores": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_all_queries(self, comprehensive_results: List[Dict]) -> List[Dict]:
        """
        Analyze precision/MRR for all queries in comprehensive evaluation
        
        Args:
            comprehensive_results: Results from latency_evaluator.py
            
        Returns:
            List of precision/MRR analysis results
        """
        print(f"\n📊 Analyzing Precision@K and MRR for {len(comprehensive_results)} queries...")
        
        analysis_results = []
        
        for i, query_data in enumerate(comprehensive_results):
            if not query_data.get('precision_mrr_ready'):
                print(f"⏭️  Skipping query {i+1}: Not ready for precision/MRR analysis")
                continue
            
            if not query_data.get('overall_success'):
                print(f"⏭️  Skipping query {i+1}: Pipeline failed")
                analysis_results.append(self._create_empty_precision_mrr_result(
                    query_data['query'], 
                    query_data['category']
                ))
                continue
            
            # Analyze this query
            result = self.calculate_precision_mrr_single(query_data)
            analysis_results.append(result)
            
            print("")  # Spacing between queries
        
        self.analysis_results = analysis_results
        return analysis_results
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive statistics for metrics 7-8"""
        
        if not self.analysis_results:
            return {"error": "No analysis results available"}
        
        # Separate by complexity and category
        stats = {
            "overall_statistics": {},
            "by_complexity": {"simple": {}, "complex": {}},
            "by_category": {"diagnosis": {}, "treatment": {}, "mixed": {}},
            "timestamp": datetime.now().isoformat()
        }
        
        # Overall statistics
        all_precision = [r['precision_at_k'] for r in self.analysis_results]
        all_mrr = [r['mrr_score'] for r in self.analysis_results]
        
        stats["overall_statistics"] = {
            "total_queries": len(self.analysis_results),
            "avg_precision": statistics.mean(all_precision),
            "avg_mrr": statistics.mean(all_mrr),
            "precision_std": statistics.stdev(all_precision) if len(all_precision) > 1 else 0.0,
            "mrr_std": statistics.stdev(all_mrr) if len(all_mrr) > 1 else 0.0
        }
        
        # By complexity
        for complexity in ["simple", "complex"]:
            complexity_results = [r for r in self.analysis_results if r['query_complexity'] == complexity]
            if complexity_results:
                precision_scores = [r['precision_at_k'] for r in complexity_results]
                mrr_scores = [r['mrr_score'] for r in complexity_results]
                
                stats["by_complexity"][complexity] = {
                    "query_count": len(complexity_results),
                    "avg_precision": statistics.mean(precision_scores),
                    "avg_mrr": statistics.mean(mrr_scores),
                    "avg_threshold": statistics.mean([r['threshold_used'] for r in complexity_results])
                }
        
        # By category
        for category in ["diagnosis", "treatment", "mixed"]:
            category_results = [r for r in self.analysis_results if r['category'] == category]
            if category_results:
                precision_scores = [r['precision_at_k'] for r in category_results]
                mrr_scores = [r['mrr_score'] for r in category_results]
                
                stats["by_category"][category] = {
                    "query_count": len(category_results),
                    "avg_precision": statistics.mean(precision_scores),
                    "avg_mrr": statistics.mean(mrr_scores)
                }
        
        return stats
    
    def save_results(self, filename: str = None) -> str:
        """Save precision/MRR analysis results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"precision_mrr_analysis_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create output data
        output_data = {
            "analysis_metadata": {
                "total_queries": len(self.analysis_results),
                "analysis_type": "precision_mrr_metrics_7_8",
                "timestamp": datetime.now().isoformat(),
                "adaptive_threshold": True
            },
            "detailed_results": self.analysis_results,
            "statistics": self.calculate_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Precision/MRR analysis saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent precision/MRR analysis interface"""
    
    print("📊 OnCall.ai Precision & MRR Analyzer - Metrics 7-8")
    
    if len(sys.argv) > 1:
        comprehensive_file = sys.argv[1]
    else:
        # Look for latest comprehensive_details file
        results_dir = Path(__file__).parent / "results"
        if results_dir.exists():
            comprehensive_files = list(results_dir.glob("comprehensive_details_*.json"))
            if comprehensive_files:
                comprehensive_file = str(sorted(comprehensive_files)[-1])  # Latest file
                print(f"📁 Using latest comprehensive file: {comprehensive_file}")
            else:
                print("❌ No comprehensive_details_*.json files found")
                print("Please run latency_evaluator.py first to generate comprehensive data")
                sys.exit(1)
        else:
            print("❌ Results directory not found")
            sys.exit(1)
    
    if not os.path.exists(comprehensive_file):
        print(f"❌ Comprehensive file not found: {comprehensive_file}")
        print("Usage: python precision_MRR.py [comprehensive_details_file.json]")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = PrecisionMRRAnalyzer()
    
    # Load comprehensive data from latency_evaluator.py
    comprehensive_results = analyzer.load_comprehensive_data(comprehensive_file)
    
    if not comprehensive_results:
        print("❌ No comprehensive data loaded")
        sys.exit(1)
    
    # Analyze precision/MRR for all queries
    analysis_results = analyzer.analyze_all_queries(comprehensive_results)
    
    # Calculate and display statistics
    statistics_result = analyzer.calculate_statistics()
    
    print(f"\n📊 === PRECISION & MRR ANALYSIS SUMMARY ===")
    
    overall_stats = statistics_result['overall_statistics']
    print(f"\nOVERALL METRICS:")
    print(f"   Precision@K: {overall_stats['avg_precision']:.3f} (±{overall_stats['precision_std']:.3f})")
    print(f"   MRR: {overall_stats['avg_mrr']:.3f} (±{overall_stats['mrr_std']:.3f})")
    print(f"   Total Queries: {overall_stats['total_queries']}")
    
    # Complexity-based statistics
    complexity_stats = statistics_result['by_complexity']
    print(f"\nBY COMPLEXITY:")
    for complexity, stats in complexity_stats.items():
        if stats:
            print(f"   {complexity.title()}: Precision={stats['avg_precision']:.3f}, MRR={stats['avg_mrr']:.3f} "
                  f"(threshold={stats['avg_threshold']:.2f}, n={stats['query_count']})")
    
    # Category-based statistics  
    category_stats = statistics_result['by_category']
    print(f"\nBY CATEGORY:")
    for category, stats in category_stats.items():
        if stats:
            print(f"   {category.title()}: Precision={stats['avg_precision']:.3f}, MRR={stats['avg_mrr']:.3f} "
                  f"(n={stats['query_count']})")
    
    # Save results
    saved_path = analyzer.save_results()
    
    print(f"\n✅ Precision & MRR analysis complete!")
    print(f"📁 Results saved to: {saved_path}")
    print(f"\n💡 Next step: Create precision_mrr_chart_generator.py for visualization")
