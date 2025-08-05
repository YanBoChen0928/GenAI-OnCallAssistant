#!/usr/bin/env python3
"""
Hospital Customization Evaluator

This script provides comprehensive evaluation of hospital customization performance
in the OnCall.ai RAG system. It runs all test queries in Hospital Only mode,
calculates detailed metrics, generates visualization charts, and saves comprehensive results.

Features:
- Executes all 6 test queries with Hospital Only retrieval mode
- Calculates Metric 1 (Latency), Metric 3 (Relevance), and Metric 4 (Coverage)
- Generates comprehensive visualization charts (bar charts, scatter plots, etc.)
- Saves detailed results and metrics to JSON files
- Creates a comprehensive evaluation report

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))
sys.path.insert(0, str(current_dir / "evaluation" / "modules"))

from modules.query_executor import QueryExecutor
from modules.metrics_calculator import HospitalCustomizationMetrics
from modules.chart_generator import HospitalCustomizationChartGenerator


class HospitalCustomizationEvaluator:
    """
    Comprehensive evaluator for hospital customization performance.
    
    This class orchestrates the complete evaluation process including query execution,
    metrics calculation, chart generation, and result compilation.
    """
    
    def __init__(self, output_dir: str = "evaluation/results"):
        """
        Initialize the hospital customization evaluator.
        
        Args:
            output_dir: Directory to save evaluation results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize components
        self.query_executor = None
        self.metrics_calculator = None
        self.chart_generator = None
        self.evaluation_data = {}
        
        print("🏥 Hospital Customization Evaluator Initialized")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🕒 Evaluation timestamp: {self.timestamp}")
    
    def initialize_components(self) -> bool:
        """
        Initialize all evaluation components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        print("\n🔧 Initializing evaluation components...")
        
        try:
            # Initialize query executor
            print("  📋 Initializing query executor...")
            self.query_executor = QueryExecutor()
            if not self.query_executor.oncall_interface or not self.query_executor.oncall_interface.initialized:
                raise Exception(f"Query executor initialization failed: {self.query_executor.initialization_error}")
            print("  ✅ Query executor ready")
            
            # Initialize metrics calculator
            print("  📊 Initializing metrics calculator...")
            self.metrics_calculator = HospitalCustomizationMetrics()
            print("  ✅ Metrics calculator ready")
            
            # Initialize chart generator
            print("  📈 Initializing chart generator...")
            charts_dir = self.output_dir / "charts"
            self.chart_generator = HospitalCustomizationChartGenerator(str(charts_dir))
            print("  ✅ Chart generator ready")
            
            print("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False
    
    def load_test_queries(self, queries_file: str = "evaluation/queries/test_queries.json") -> List[Dict[str, Any]]:
        """
        Load test queries for evaluation.
        
        Args:
            queries_file: Path to test queries JSON file
            
        Returns:
            List of query dictionaries
        """
        print(f"\n📋 Loading test queries from {queries_file}...")
        
        try:
            queries = self.query_executor.load_queries(queries_file)
            print(f"✅ Loaded {len(queries)} test queries")
            
            # Display query summary
            query_types = {}
            for query in queries:
                specificity = query["specificity"]
                query_types[specificity] = query_types.get(specificity, 0) + 1
            
            print("📊 Query distribution:")
            for query_type, count in query_types.items():
                print(f"  • {query_type.capitalize()}: {count} queries")
            
            return queries
            
        except Exception as e:
            print(f"❌ Failed to load test queries: {e}")
            raise
    
    def execute_hospital_only_evaluation(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute all queries with Hospital Only retrieval mode.
        
        Args:
            queries: List of test queries
            
        Returns:
            List of execution results
        """
        print(f"\n🏥 Starting Hospital Only evaluation of {len(queries)} queries...")
        
        try:
            # Execute queries with Hospital Only mode
            results = self.query_executor.execute_batch(queries, retrieval_mode="Hospital Only")
            
            # Analyze results
            successful_queries = sum(1 for r in results if r["success"])
            failed_queries = len(queries) - successful_queries
            
            print(f"\n📊 Execution Summary:")
            print(f"  ✅ Successful: {successful_queries}/{len(queries)}")
            print(f"  ❌ Failed: {failed_queries}/{len(queries)}")
            
            if failed_queries > 0:
                print("⚠️  Warning: Some queries failed - this may affect metrics accuracy")
                
                # Display failed queries
                for result in results:
                    if not result["success"]:
                        print(f"  • Failed: {result['query_id']} - {result.get('error', {}).get('message', 'Unknown error')}")
            
            return results
            
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            raise
    
    def calculate_comprehensive_metrics(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive hospital customization metrics.
        
        Args:
            query_results: Results from query execution
            
        Returns:
            Dictionary containing all calculated metrics
        """
        print(f"\n📊 Calculating comprehensive metrics for {len(query_results)} queries...")
        
        try:
            # Calculate metrics using the metrics calculator
            metrics = self.metrics_calculator.calculate_comprehensive_metrics(query_results)
            
            # Display key metrics summary
            print("\n📈 Key Metrics Summary:")
            summary = metrics.get("summary", {})
            
            print(f"  🚀 Latency Performance: {summary.get('latency_performance', 'Unknown')}")
            print(f"  🎯 Relevance Quality: {summary.get('relevance_quality', 'Unknown')}")
            print(f"  📋 Coverage Effectiveness: {summary.get('coverage_effectiveness', 'Unknown')}")
            print(f"  🏆 Overall Assessment: {summary.get('overall_assessment', 'Unknown')}")
            
            # Display detailed statistics
            print("\n📊 Detailed Statistics:")
            
            # Latency metrics
            latency_data = metrics.get("metric_1_latency", {})
            if latency_data.get("total_execution", {}).get("mean"):
                avg_time = latency_data["total_execution"]["mean"]
                customization_pct = latency_data.get("customization_percentage", {}).get("percentage", 0)
                print(f"  ⏱️  Average execution time: {avg_time:.2f}s")
                print(f"  🏥 Hospital customization overhead: {customization_pct:.1f}%")
            
            # Relevance metrics
            relevance_data = metrics.get("metric_3_relevance", {})
            if relevance_data.get("hospital_content", {}).get("mean"):
                hospital_relevance = relevance_data["hospital_content"]["mean"]
                print(f"  🎯 Average hospital content relevance: {hospital_relevance:.3f}")
            
            # Coverage metrics
            coverage_data = metrics.get("metric_4_coverage", {})
            if coverage_data.get("keyword_overlap", {}).get("mean"):
                keyword_coverage = coverage_data["keyword_overlap"]["mean"]
                advice_completeness = coverage_data.get("advice_completeness", {}).get("mean", 0)
                print(f"  📋 Keyword coverage: {keyword_coverage:.1f}%")
                print(f"  ✅ Advice completeness: {advice_completeness:.1f}%")
            
            return metrics
            
        except Exception as e:
            print(f"❌ Metrics calculation failed: {e}")
            raise
    
    def generate_visualization_charts(self, metrics: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate comprehensive visualization charts.
        
        Args:
            metrics: Calculated metrics dictionary
            
        Returns:
            Dictionary mapping chart types to file paths
        """
        print(f"\n📈 Generating visualization charts...")
        
        try:
            chart_files = {
                "latency_charts": [],
                "relevance_charts": [],
                "coverage_charts": [],
                "dashboard": None
            }
            
            # Generate latency charts
            print("  📊 Generating latency analysis charts...")
            latency_files = self.chart_generator.generate_latency_charts(metrics, self.timestamp)
            chart_files["latency_charts"] = latency_files
            print(f"    ✅ Generated {len(latency_files)} latency charts")
            
            # Generate relevance charts
            print("  🎯 Generating relevance analysis charts...")
            relevance_files = self.chart_generator.generate_relevance_charts(metrics, self.timestamp)
            chart_files["relevance_charts"] = relevance_files
            print(f"    ✅ Generated {len(relevance_files)} relevance charts")
            
            # Generate coverage charts
            print("  📋 Generating coverage analysis charts...")
            coverage_files = self.chart_generator.generate_coverage_charts(metrics, self.timestamp)
            chart_files["coverage_charts"] = coverage_files
            print(f"    ✅ Generated {len(coverage_files)} coverage charts")
            
            # Generate comprehensive dashboard
            print("  🏆 Generating comprehensive dashboard...")
            dashboard_file = self.chart_generator.generate_comprehensive_dashboard(metrics, self.timestamp)
            chart_files["dashboard"] = dashboard_file
            print(f"    ✅ Generated dashboard: {Path(dashboard_file).name}")
            
            total_charts = len(latency_files) + len(relevance_files) + len(coverage_files) + 1
            print(f"✅ Generated {total_charts} visualization files")
            
            return chart_files
            
        except Exception as e:
            print(f"❌ Chart generation failed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            # Return partial results if available
            return chart_files
    
    def save_comprehensive_results(self, query_results: List[Dict[str, Any]], 
                                 metrics: Dict[str, Any], 
                                 chart_files: Dict[str, List[str]]) -> str:
        """
        Save comprehensive evaluation results to JSON file.
        
        Args:
            query_results: Raw query execution results
            metrics: Calculated metrics
            chart_files: Generated chart file paths
            
        Returns:
            Path to saved results file
        """
        print(f"\n💾 Saving comprehensive evaluation results...")
        
        try:
            # Compile comprehensive results
            comprehensive_results = {
                "evaluation_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "evaluation_type": "hospital_customization",
                    "retrieval_mode": "Hospital Only",
                    "total_queries": len(query_results),
                    "successful_queries": sum(1 for r in query_results if r["success"]),
                    "failed_queries": sum(1 for r in query_results if not r["success"]),
                    "evaluator_version": "1.0.0"
                },
                "query_execution_results": {
                    "raw_results": query_results,
                    "execution_summary": {
                        "total_execution_time": sum(r["execution_time"]["total_seconds"] for r in query_results if r["success"]),
                        "average_execution_time": sum(r["execution_time"]["total_seconds"] for r in query_results if r["success"]) / max(1, sum(1 for r in query_results if r["success"])),
                        "query_type_performance": self._analyze_query_type_performance(query_results)
                    }
                },
                "hospital_customization_metrics": metrics,
                "visualization_charts": {
                    "chart_files": chart_files,
                    "charts_directory": str(self.chart_generator.output_dir),
                    "total_charts_generated": sum(len(files) if isinstance(files, list) else 1 for files in chart_files.values() if files)
                },
                "evaluation_insights": self._generate_evaluation_insights(metrics, query_results),
                "recommendations": self._generate_recommendations(metrics)
            }
            
            # Save to JSON file
            results_file = self.output_dir / f"hospital_customization_evaluation_{self.timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to: {results_file}")
            
            # Save a summary report
            summary_file = self._create_summary_report(comprehensive_results)
            print(f"📋 Summary report saved to: {summary_file}")
            
            return str(results_file)
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            raise
    
    def run_complete_evaluation(self) -> Dict[str, Any]:
        """
        Run the complete hospital customization evaluation pipeline.
        
        Returns:
            Dictionary containing evaluation results and file paths
        """
        print("🚀 Starting Complete Hospital Customization Evaluation")
        print("=" * 60)
        
        evaluation_summary = {
            "success": False,
            "results_file": None,
            "chart_files": {},
            "metrics": {},
            "error": None
        }
        
        try:
            # Step 1: Initialize components
            if not self.initialize_components():
                raise Exception("Component initialization failed")
            
            # Step 2: Load test queries
            queries = self.load_test_queries()
            
            # Step 3: Execute Hospital Only evaluation
            query_results = self.execute_hospital_only_evaluation(queries)
            
            # Step 4: Calculate comprehensive metrics
            metrics = self.calculate_comprehensive_metrics(query_results)
            
            # Step 5: Generate visualization charts
            chart_files = self.generate_visualization_charts(metrics)
            
            # Step 6: Save comprehensive results
            results_file = self.save_comprehensive_results(query_results, metrics, chart_files)
            
            # Update evaluation summary
            evaluation_summary.update({
                "success": True,
                "results_file": results_file,
                "chart_files": chart_files,
                "metrics": metrics.get("summary", {}),
                "total_queries": len(queries),
                "successful_queries": sum(1 for r in query_results if r["success"])
            })
            
            print("\n" + "=" * 60)
            print("🎉 Hospital Customization Evaluation Completed Successfully!")
            print("=" * 60)
            
            # Display final summary
            print(f"\n📊 Final Evaluation Summary:")
            print(f"  📋 Queries processed: {evaluation_summary['total_queries']}")
            print(f"  ✅ Successful executions: {evaluation_summary['successful_queries']}")
            print(f"  🏆 Overall assessment: {evaluation_summary['metrics'].get('overall_assessment', 'Unknown')}")
            print(f"  📁 Results file: {Path(results_file).name}")
            print(f"  📈 Charts generated: {sum(len(files) if isinstance(files, list) else 1 for files in chart_files.values() if files)}")
            
            return evaluation_summary
            
        except Exception as e:
            error_msg = f"Evaluation failed: {e}"
            print(f"\n❌ {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            
            evaluation_summary["error"] = error_msg
            return evaluation_summary
    
    def _analyze_query_type_performance(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by query type."""
        performance = {"broad": [], "medium": [], "specific": []}
        
        for result in query_results:
            if result["success"]:
                query_type = result["query_metadata"]["specificity"]
                execution_time = result["execution_time"]["total_seconds"]
                if query_type in performance:
                    performance[query_type].append(execution_time)
        
        # Calculate averages
        return {
            query_type: {
                "count": len(times),
                "average_time": sum(times) / len(times) if times else 0,
                "total_time": sum(times)
            }
            for query_type, times in performance.items()
        }
    
    def _generate_evaluation_insights(self, metrics: Dict[str, Any], query_results: List[Dict[str, Any]]) -> List[str]:
        """Generate key insights from the evaluation."""
        insights = []
        
        # Latency insights
        latency_data = metrics.get("metric_1_latency", {})
        avg_time = latency_data.get("total_execution", {}).get("mean", 0)
        customization_pct = latency_data.get("customization_percentage", {}).get("percentage", 0)
        
        if avg_time > 0:
            if avg_time < 30:
                insights.append("Excellent response time - under 30 seconds average")
            elif avg_time < 60:
                insights.append("Good response time - under 1 minute average")
            else:
                insights.append("Response time may benefit from optimization")
            
            if customization_pct > 25:
                insights.append(f"Hospital customization represents {customization_pct:.1f}% of total processing time")
        
        # Relevance insights
        relevance_data = metrics.get("metric_3_relevance", {})
        hospital_relevance = relevance_data.get("hospital_content", {}).get("mean", 0)
        
        if hospital_relevance > 0.7:
            insights.append("High relevance scores indicate effective hospital content matching")
        elif hospital_relevance > 0.4:
            insights.append("Moderate relevance scores - room for improvement in content matching")
        else:
            insights.append("Low relevance scores suggest need for hospital content optimization")
        
        # Coverage insights
        coverage_data = metrics.get("metric_4_coverage", {})
        keyword_coverage = coverage_data.get("keyword_overlap", {}).get("mean", 0)
        
        if keyword_coverage > 70:
            insights.append("Comprehensive keyword coverage demonstrates thorough content analysis")
        elif keyword_coverage > 40:
            insights.append("Adequate keyword coverage with potential for enhancement")
        else:
            insights.append("Limited keyword coverage indicates need for content enrichment")
        
        # Success rate insights
        successful_queries = sum(1 for r in query_results if r["success"])
        total_queries = len(query_results)
        success_rate = (successful_queries / total_queries) * 100 if total_queries > 0 else 0
        
        if success_rate == 100:
            insights.append("Perfect execution success rate achieved")
        elif success_rate >= 90:
            insights.append("High execution success rate with minimal failures")
        else:
            insights.append("Execution reliability may need attention")
        
        return insights
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []
        
        # Performance recommendations
        summary = metrics.get("summary", {})
        
        if summary.get("latency_performance") == "Needs Improvement":
            recommendations.append("Consider optimizing hospital customization processing for better latency")
        
        if summary.get("relevance_quality") == "Low":
            recommendations.append("Review hospital document indexing and embedding quality")
            recommendations.append("Consider tuning similarity thresholds for better content matching")
        
        if summary.get("coverage_effectiveness") == "Limited":
            recommendations.append("Expand medical keyword dictionary for better coverage analysis")
            recommendations.append("Review advice generation templates for completeness")
        
        # Specific metric recommendations
        latency_data = metrics.get("metric_1_latency", {})
        customization_pct = latency_data.get("customization_percentage", {}).get("percentage", 0)
        
        if customization_pct > 30:
            recommendations.append("Hospital customization overhead is high - consider caching strategies")
        
        # Add general recommendations
        recommendations.append("Continue monitoring performance metrics over time")
        recommendations.append("Consider A/B testing different retrieval strategies")
        
        return recommendations
    
    def _create_summary_report(self, comprehensive_results: Dict[str, Any]) -> str:
        """Create a human-readable summary report."""
        summary_file = self.output_dir / f"hospital_customization_summary_{self.timestamp}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Hospital Customization Evaluation Summary Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Metadata
            metadata = comprehensive_results["evaluation_metadata"]
            f.write(f"Evaluation Date: {metadata['timestamp']}\n")
            f.write(f"Evaluation Type: {metadata['evaluation_type']}\n")
            f.write(f"Retrieval Mode: {metadata['retrieval_mode']}\n")
            f.write(f"Total Queries: {metadata['total_queries']}\n")
            f.write(f"Successful Queries: {metadata['successful_queries']}\n\n")
            
            # Metrics Summary
            metrics_summary = comprehensive_results["hospital_customization_metrics"]["summary"]
            f.write("Performance Summary:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Latency Performance: {metrics_summary.get('latency_performance', 'Unknown')}\n")
            f.write(f"Relevance Quality: {metrics_summary.get('relevance_quality', 'Unknown')}\n")
            f.write(f"Coverage Effectiveness: {metrics_summary.get('coverage_effectiveness', 'Unknown')}\n")
            f.write(f"Overall Assessment: {metrics_summary.get('overall_assessment', 'Unknown')}\n\n")
            
            # Key Insights
            insights = comprehensive_results["evaluation_insights"]
            f.write("Key Insights:\n")
            f.write("-" * 12 + "\n")
            for insight in insights:
                f.write(f"• {insight}\n")
            f.write("\n")
            
            # Recommendations
            recommendations = comprehensive_results["recommendations"]
            f.write("Recommendations:\n")
            f.write("-" * 15 + "\n")
            for recommendation in recommendations:
                f.write(f"• {recommendation}\n")
            
        return str(summary_file)


def main():
    """
    Main function for running hospital customization evaluation.
    """
    print("🏥 Hospital Customization Evaluator")
    print("OnCall.ai RAG System Performance Analysis")
    print("=" * 50)
    
    try:
        # Initialize evaluator
        evaluator = HospitalCustomizationEvaluator()
        
        # Run complete evaluation
        results = evaluator.run_complete_evaluation()
        
        if results["success"]:
            print(f"\n🎉 Evaluation completed successfully!")
            print(f"📁 Results available at: {results['results_file']}")
            return 0
        else:
            print(f"\n❌ Evaluation failed: {results['error']}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)