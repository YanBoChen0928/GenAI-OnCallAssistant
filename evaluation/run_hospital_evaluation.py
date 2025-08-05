#!/usr/bin/env python3
"""
Simple Runner for Hospital Customization Evaluation

This script provides an easy way to run the hospital customization evaluation
without needing to understand the internal components. Simply run this script
to execute the complete evaluation pipeline.

Usage:
    python evaluation/run_hospital_evaluation.py

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def main():
    """Main function to run hospital customization evaluation."""
    print("🏥 OnCall.ai Hospital Customization Evaluation")
    print("=" * 50)
    
    # Check if we can import the evaluator
    try:
        from evaluation.hospital_customization_evaluator import HospitalCustomizationEvaluator
        print("✅ Evaluation modules loaded successfully")
    except ImportError as e:
        print(f"❌ Cannot import evaluator: {e}")
        print("\n📋 This likely means missing dependencies. To run with actual OnCall.ai system:")
        print("1. Make sure you're in the rag_env virtual environment")
        print("2. Ensure all requirements are installed")
        print("3. The OnCall.ai system should be properly initialized")
        return 1
    
    print("\n🚀 Initializing Hospital Customization Evaluator...")
    
    try:
        # Initialize evaluator
        evaluator = HospitalCustomizationEvaluator()
        
        # Run complete evaluation
        print("🏥 Starting complete evaluation with Hospital Only mode...")
        results = evaluator.run_complete_evaluation()
        
        if results["success"]:
            print(f"\n🎉 Evaluation completed successfully!")
            print(f"📊 Processed {results['total_queries']} queries")
            print(f"✅ {results['successful_queries']} successful executions")
            print(f"🏆 Overall assessment: {results['metrics'].get('overall_assessment', 'Unknown')}")
            print(f"📁 Results file: {Path(results['results_file']).name}")
            
            # Display chart information
            chart_info = []
            for chart_type, files in results['chart_files'].items():
                if files:
                    if isinstance(files, list):
                        chart_info.append(f"{len(files)} {chart_type}")
                    else:
                        chart_info.append(f"1 {chart_type}")
            
            if chart_info:
                print(f"📈 Generated: {', '.join(chart_info)}")
            
            return 0
        else:
            print(f"\n❌ Evaluation failed: {results['error']}")
            return 1
            
    except Exception as e:
        print(f"\n💥 Evaluation error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("• Make sure the rag_env virtual environment is activated")
        print("• Ensure OnCall.ai system dependencies are installed")
        print("• Check that the evaluation/queries/test_queries.json file exists")
        print("• Verify the customization pipeline is properly configured")
        return 1


if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("\n📋 Next Steps:")
        print("• Review the generated results file for detailed metrics")
        print("• Examine the visualization charts for insights")
        print("• Use the metrics to optimize hospital customization performance")
    
    sys.exit(exit_code)