#!/usr/bin/env python3
"""
OnCall.ai System - Precision & MRR Chart Generator (Metrics 7-8)
===============================================================

Generates comprehensive Precision@K and MRR analysis charts from saved analysis results.
Reads JSON files produced by metric7_8_precision_MRR.py and creates visualizations.

Charts generated:
1. Precision@K comparison by category and complexity
2. MRR comparison by category and complexity  
3. Combined metrics heatmap
4. Threshold impact analysis
5. Detailed statistics tables

No LLM calls - pure data visualization.

Author: YanBo Chen  
Date: 2025-08-04
"""

import json
import os
import sys
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import glob

# Visualization imports
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class PrecisionMRRChartGenerator:
    """Generate charts from precision/MRR analysis results - no LLM dependency"""
    
    def __init__(self):
        """Initialize chart generator"""
        print("📈 Initializing Precision & MRR Chart Generator...")
        
        # Set up professional chart style
        plt.style.use('default')
        sns.set_palette("husl")
        
        print("✅ Chart Generator ready")
    
    def load_latest_analysis(self, results_dir: str = None) -> Dict[str, Any]:
        """
        Load the most recent precision/MRR analysis file
        
        Args:
            results_dir: Directory containing analysis files
        """
        if results_dir is None:
            results_dir = Path(__file__).parent / "results"
        
        analysis_files = glob.glob(str(results_dir / "precision_mrr_analysis_*.json"))
        
        if not analysis_files:
            raise FileNotFoundError("No precision_mrr_analysis_*.json files found. Run metric7_8_precision_MRR.py first.")
        
        latest_file = max(analysis_files, key=os.path.getctime)
        print(f"📁 Loading latest analysis: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_precision_comparison_chart(self, analysis_data: Dict, save_path: str = None) -> str:
        """Create Precision@K comparison chart"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Chart 1: Precision by Category
        category_stats = analysis_data['statistics']['by_category']
        categories = []
        precisions = []
        
        for category, stats in category_stats.items():
            if stats:
                categories.append(category.title())
                precisions.append(stats['avg_precision'])
        
        if categories:
            bars1 = ax1.bar(categories, precisions, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#d62728'])
            ax1.set_title('Precision@K by Query Category', fontweight='bold')
            ax1.set_ylabel('Precision@K')
            ax1.set_xlabel('Query Category')
            ax1.set_ylim(0, 1.0)
            ax1.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, precision in zip(bars1, precisions):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{precision:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: Precision by Complexity
        complexity_stats = analysis_data['statistics']['by_complexity']
        complexities = []
        comp_precisions = []
        
        for complexity, stats in complexity_stats.items():
            if stats:
                complexities.append(complexity.title())
                comp_precisions.append(stats['avg_precision'])
        
        if complexities:
            bars2 = ax2.bar(complexities, comp_precisions, alpha=0.8, color=['#2ca02c', '#d62728'])
            ax2.set_title('Precision@K by Query Complexity', fontweight='bold')
            ax2.set_ylabel('Precision@K')
            ax2.set_xlabel('Query Complexity')
            ax2.set_ylim(0, 1.0)
            ax2.grid(True, alpha=0.3)
            
            # Add value labels and threshold info
            for bar, precision, complexity in zip(bars2, comp_precisions, complexities):
                height = bar.get_height()
                threshold = 0.15 if complexity.lower() == 'complex' else 0.25
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{precision:.3f}\n(T={threshold})', ha='center', va='bottom', 
                        fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = Path(__file__).parent / "charts" / f"precision_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Precision comparison chart saved: {save_path}")
        return str(save_path)
    
    def create_mrr_comparison_chart(self, analysis_data: Dict, save_path: str = None) -> str:
        """Create MRR comparison chart"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Chart 1: MRR by Category
        category_stats = analysis_data['statistics']['by_category']
        categories = []
        mrr_scores = []
        
        for category, stats in category_stats.items():
            if stats:
                categories.append(category.title())
                mrr_scores.append(stats['avg_mrr'])
        
        if categories:
            bars1 = ax1.bar(categories, mrr_scores, alpha=0.8, color=['#9467bd', '#8c564b', '#e377c2'])
            ax1.set_title('Mean Reciprocal Rank by Query Category', fontweight='bold')
            ax1.set_ylabel('MRR Score')
            ax1.set_xlabel('Query Category')
            ax1.set_ylim(0, 1.0)
            ax1.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, mrr in zip(bars1, mrr_scores):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{mrr:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: MRR by Complexity
        complexity_stats = analysis_data['statistics']['by_complexity']
        complexities = []
        comp_mrr = []
        
        for complexity, stats in complexity_stats.items():
            if stats:
                complexities.append(complexity.title())
                comp_mrr.append(stats['avg_mrr'])
        
        if complexities:
            bars2 = ax2.bar(complexities, comp_mrr, alpha=0.8, color=['#17becf', '#bcbd22'])
            ax2.set_title('MRR by Query Complexity', fontweight='bold')
            ax2.set_ylabel('MRR Score')
            ax2.set_xlabel('Query Complexity')
            ax2.set_ylim(0, 1.0)
            ax2.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, mrr in zip(bars2, comp_mrr):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{mrr:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = Path(__file__).parent / "charts" / f"mrr_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 MRR comparison chart saved: {save_path}")
        return str(save_path)
    
    def create_combined_metrics_heatmap(self, analysis_data: Dict, save_path: str = None) -> str:
        """Create combined precision/MRR heatmap"""
        
        # Prepare data for heatmap
        detailed_results = analysis_data.get('detailed_results', [])
        
        if not detailed_results:
            print("⚠️ No detailed results for heatmap")
            return ""
        
        # Create DataFrame for heatmap
        heatmap_data = []
        for result in detailed_results:
            heatmap_data.append({
                'Category': result['category'].title(),
                'Complexity': result['query_complexity'].title(),
                'Precision@K': result['precision_at_k'],
                'MRR': result['mrr_score'],
                'Threshold': result['threshold_used']
            })
        
        df = pd.DataFrame(heatmap_data)
        
        # Create pivot table for heatmap
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Precision heatmap
        precision_pivot = df.pivot_table(values='Precision@K', index='Category', columns='Complexity', aggfunc='mean')
        sns.heatmap(precision_pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax1, 
                   cbar_kws={'label': 'Precision@K'}, vmin=0, vmax=1)
        ax1.set_title('Precision@K Heatmap\n(Category vs Complexity)', fontweight='bold')
        
        # MRR heatmap  
        mrr_pivot = df.pivot_table(values='MRR', index='Category', columns='Complexity', aggfunc='mean')
        sns.heatmap(mrr_pivot, annot=True, fmt='.3f', cmap='YlGnBu', ax=ax2,
                   cbar_kws={'label': 'MRR Score'}, vmin=0, vmax=1)
        ax2.set_title('MRR Heatmap\n(Category vs Complexity)', fontweight='bold')
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = Path(__file__).parent / "charts" / f"precision_mrr_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Combined metrics heatmap saved: {save_path}")
        return str(save_path)
    
    def create_threshold_impact_chart(self, analysis_data: Dict, save_path: str = None) -> str:
        """Create threshold impact analysis chart"""
        
        detailed_results = analysis_data.get('detailed_results', [])
        
        if not detailed_results:
            print("⚠️ No detailed results for threshold analysis")
            return ""
        
        # Group by complexity and calculate average relevance
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Prepare data
        simple_queries = [r for r in detailed_results if r['query_complexity'] == 'simple']
        complex_queries = [r for r in detailed_results if r['query_complexity'] == 'complex']
        
        # Chart 1: Relevance distribution for different complexities
        if simple_queries:
            simple_relevances = []
            for query in simple_queries:
                simple_relevances.extend(query.get('relevance_scores', []))
            
            ax1.hist(simple_relevances, bins=10, alpha=0.7, label=f'Simple (T=0.25)', color='#2ca02c', density=True)
            ax1.axvline(x=0.25, color='#2ca02c', linestyle='--', linewidth=2, label='Simple Threshold')
        
        if complex_queries:
            complex_relevances = []
            for query in complex_queries:
                complex_relevances.extend(query.get('relevance_scores', []))
            
            ax1.hist(complex_relevances, bins=10, alpha=0.7, label=f'Complex (T=0.15)', color='#d62728', density=True)
            ax1.axvline(x=0.15, color='#d62728', linestyle='--', linewidth=2, label='Complex Threshold')
        
        ax1.set_title('Relevance Score Distribution\nby Query Complexity', fontweight='bold')
        ax1.set_xlabel('Relevance Score')
        ax1.set_ylabel('Density')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Metrics comparison
        complexity_stats = analysis_data['statistics']['by_complexity']
        
        complexities = []
        precisions = []
        mrrs = []
        thresholds = []
        
        for complexity, stats in complexity_stats.items():
            if stats:
                complexities.append(complexity.title())
                precisions.append(stats['avg_precision'])
                mrrs.append(stats['avg_mrr'])
                thresholds.append(stats['avg_threshold'])
        
        x = np.arange(len(complexities))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, precisions, width, label='Precision@K', alpha=0.8, color='#ff7f0e')
        bars2 = ax2.bar(x + width/2, mrrs, width, label='MRR', alpha=0.8, color='#1f77b4')
        
        ax2.set_title('Metrics Comparison by Complexity\n(with Adaptive Thresholds)', fontweight='bold')
        ax2.set_ylabel('Score')
        ax2.set_xlabel('Query Complexity')
        ax2.set_xticks(x)
        ax2.set_xticklabels(complexities)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1.0)
        
        # Add value labels
        for bars, values, thresholds_vals in [(bars1, precisions, thresholds), (bars2, mrrs, thresholds)]:
            for bar, value, threshold in zip(bars, values, thresholds_vals):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = Path(__file__).parent / "charts" / f"threshold_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Threshold impact chart saved: {save_path}")
        return str(save_path)
    
    def create_detailed_analysis_table(self, analysis_data: Dict, save_path: str = None) -> str:
        """Create detailed statistics table"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        table_data = []
        
        # Overall statistics
        overall_stats = analysis_data['statistics']['overall_statistics']
        table_data.append(['OVERALL METRICS', '', '', '', ''])
        table_data.append(['Total Queries', str(overall_stats['total_queries']), '', '', ''])
        table_data.append(['Avg Precision@K', f"{overall_stats['avg_precision']:.3f}", 
                          f"±{overall_stats['precision_std']:.3f}", '', ''])
        table_data.append(['Avg MRR', f"{overall_stats['avg_mrr']:.3f}", 
                          f"±{overall_stats['mrr_std']:.3f}", '', ''])
        table_data.append(['', '', '', '', ''])
        
        # By category
        table_data.append(['BY CATEGORY', 'Queries', 'Precision@K', 'MRR', 'Notes'])
        category_stats = analysis_data['statistics']['by_category']
        for category, stats in category_stats.items():
            if stats:
                table_data.append([
                    category.title(),
                    str(stats['query_count']),
                    f"{stats['avg_precision']:.3f}",
                    f"{stats['avg_mrr']:.3f}",
                    ''
                ])
        
        table_data.append(['', '', '', '', ''])
        
        # By complexity
        table_data.append(['BY COMPLEXITY', 'Queries', 'Precision@K', 'MRR', 'Threshold'])
        complexity_stats = analysis_data['statistics']['by_complexity']
        for complexity, stats in complexity_stats.items():
            if stats:
                table_data.append([
                    complexity.title(),
                    str(stats['query_count']),
                    f"{stats['avg_precision']:.3f}",
                    f"{stats['avg_mrr']:.3f}",
                    f"{stats['avg_threshold']:.2f}"
                ])
        
        # Create table
        table = ax.table(cellText=table_data,
                        colLabels=['Metric', 'Value 1', 'Value 2', 'Value 3', 'Value 4'],
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Header styling
        for i in range(5):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Section headers styling
        for i, row in enumerate(table_data):
            if row[0] in ['OVERALL METRICS', 'BY CATEGORY', 'BY COMPLEXITY']:
                table[(i+1, 0)].set_facecolor('#1f77b4')
                table[(i+1, 0)].set_text_props(weight='bold', color='white')
        
        plt.title('Precision@K & MRR Detailed Analysis\nMetrics 7-8 Statistics', 
                 fontweight='bold', fontsize=14, pad=20)
        
        # Save chart
        if save_path is None:
            save_path = Path(__file__).parent / "charts" / f"precision_mrr_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Detailed analysis table saved: {save_path}")
        return str(save_path)
    
    def create_individual_query_analysis(self, analysis_data: Dict, save_path: str = None) -> str:
        """Create individual query analysis chart"""
        
        detailed_results = analysis_data.get('detailed_results', [])
        
        if not detailed_results:
            print("⚠️ No detailed results for individual analysis")
            return ""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Prepare data
        query_indices = []
        precisions = []
        mrrs = []
        colors = []
        labels = []
        
        for i, result in enumerate(detailed_results):
            query_indices.append(i + 1)
            precisions.append(result['precision_at_k'])
            mrrs.append(result['mrr_score'])
            
            # Color by complexity
            if result['query_complexity'] == 'complex':
                colors.append('#d62728')  # Red for complex
            else:
                colors.append('#2ca02c')  # Green for simple
            
            # Create short label
            query_short = result['query'][:30] + "..." if len(result['query']) > 30 else result['query']
            category = result['category'][:4].upper()
            labels.append(f"{category}\n{query_short}")
        
        # Chart 1: Precision@K for each query
        bars1 = ax1.bar(query_indices, precisions, color=colors, alpha=0.8)
        ax1.set_title('Precision@K by Individual Query', fontweight='bold')
        ax1.set_ylabel('Precision@K')
        ax1.set_xlabel('Query Index')
        ax1.set_ylim(0, 1.0)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, precision in zip(bars1, precisions):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{precision:.2f}', ha='center', va='bottom', fontsize=8)
        
        # Chart 2: MRR for each query
        bars2 = ax2.bar(query_indices, mrrs, color=colors, alpha=0.8)
        ax2.set_title('MRR by Individual Query', fontweight='bold')
        ax2.set_ylabel('MRR Score')
        ax2.set_xlabel('Query Index')
        ax2.set_ylim(0, 1.0)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, mrr in zip(bars2, mrrs):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{mrr:.2f}', ha='center', va='bottom', fontsize=8)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ca02c', alpha=0.8, label='Simple Query (T=0.25)'),
            Patch(facecolor='#d62728', alpha=0.8, label='Complex Query (T=0.15)')
        ]
        ax1.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        # Save chart
        if save_path is None:
            save_path = Path(__file__).parent / "charts" / f"individual_query_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Individual query analysis saved: {save_path}")
        return str(save_path)
    
    def generate_all_charts(self, analysis_data: Dict = None) -> Dict[str, str]:
        """Generate all precision/MRR charts"""
        
        if analysis_data is None:
            analysis_data = self.load_latest_analysis()
        
        print(f"\n📈 Generating all Precision & MRR charts...")
        
        saved_charts = {}
        
        # Generate all chart types
        try:
            saved_charts['precision_comparison'] = self.create_precision_comparison_chart(analysis_data)
            saved_charts['mrr_comparison'] = self.create_mrr_comparison_chart(analysis_data)
            saved_charts['combined_heatmap'] = self.create_combined_metrics_heatmap(analysis_data)
            saved_charts['threshold_impact'] = self.create_threshold_impact_chart(analysis_data)
            saved_charts['individual_analysis'] = self.create_individual_query_analysis(analysis_data)
            
        except Exception as e:
            print(f"❌ Error generating charts: {e}")
            return {"error": str(e)}
        
        print(f"\n✅ All precision/MRR charts generated successfully!")
        print(f"📁 Charts saved to: evaluation/charts/")
        
        return saved_charts


# Independent execution interface
if __name__ == "__main__":
    """Generate precision/MRR charts from analysis results"""
    
    print("📈 OnCall.ai Precision & MRR Chart Generator - Metrics 7-8")
    
    if len(sys.argv) > 1:
        analysis_file = sys.argv[1]
        
        if not os.path.exists(analysis_file):
            print(f"❌ Analysis file not found: {analysis_file}")
            sys.exit(1)
    else:
        analysis_file = None  # Will use latest file
    
    # Initialize generator
    generator = PrecisionMRRChartGenerator()
    
    try:
        # Load analysis data
        if analysis_file:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            print(f"📁 Using specified analysis file: {analysis_file}")
        else:
            analysis_data = generator.load_latest_analysis()
        
        # Generate all charts
        saved_charts = generator.generate_all_charts(analysis_data)
        
        if 'error' not in saved_charts:
            print(f"\n📊 === PRECISION & MRR CHART GENERATION SUMMARY ===")
            for chart_type, filepath in saved_charts.items():
                print(f"   📈 {chart_type.replace('_', ' ').title()}: {filepath}")
            
            print(f"\n💡 Charts ready for analysis and presentation!")
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        sys.exit(1)
