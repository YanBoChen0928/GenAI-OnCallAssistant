#!/usr/bin/env python3
"""
OnCall.ai System - Relevance Chart Generator
============================================

Generates retrieval relevance charts from saved statistics.
Shows cosine similarity analysis and threshold compliance.

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


class RelevanceChartGenerator:
    """Generate charts for retrieval relevance metrics"""
    
    def __init__(self):
        """Initialize chart generator"""
        print("📈 Initializing Relevance Chart Generator...")
        plt.style.use('default')
        sns.set_palette("husl")
        print("✅ Chart Generator ready")
    
    def load_latest_relevance_statistics(self, results_dir: str = None) -> Dict[str, Any]:
        """Load the most recent relevance statistics file"""
        if results_dir is None:
            results_dir = Path(__file__).parent / "results"
        
        pattern = str(results_dir / "relevance_statistics_*.json")
        stat_files = glob.glob(pattern)
        
        if not stat_files:
            raise FileNotFoundError(f"No relevance statistics files found in {results_dir}")
        
        latest_file = max(stat_files, key=os.path.getmtime)
        print(f"📊 Loading relevance statistics from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        return stats
    
    def generate_relevance_charts(self, stats: Dict[str, Any]) -> str:
        """Generate relevance analysis charts"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('OnCall.ai Retrieval Relevance Analysis', fontsize=16, fontweight='bold')
            
            category_results = stats['category_results']
            overall_results = stats['overall_results']
            
            # Chart 1: Average Relevance by Category
            ax1 = axes[0, 0]
            categories = []
            avg_relevances = []
            
            for category, cat_stats in category_results.items():
                if cat_stats['successful_retrievals'] > 0:
                    categories.append(category.replace('_', ' ').title())
                    avg_relevances.append(cat_stats['average_relevance'])
            
            categories.append('Overall')
            avg_relevances.append(overall_results['average_relevance'])
            
            bars = ax1.bar(categories, avg_relevances, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c'])
            ax1.set_title('Average Relevance Score by Category', fontweight='bold')
            ax1.set_ylabel('Relevance Score (Cosine Similarity)')
            ax1.set_xlabel('Query Category')
            ax1.grid(True, alpha=0.3)
            
            # Add threshold lines
            ax1.axhline(y=0.2, color='orange', linestyle='--', alpha=0.7, label='0.2 Threshold')
            ax1.axhline(y=0.25, color='red', linestyle='--', alpha=0.7, label='0.25 Target')
            ax1.legend()
            
            # Add value labels
            for bar, relevance in zip(bars, avg_relevances):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{relevance:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # Chart 2: Relevance Distribution
            ax2 = axes[0, 1]
            
            # Collect all individual relevance scores
            all_scores = []
            category_labels = []
            
            for category, cat_stats in category_results.items():
                if cat_stats.get('individual_relevance_scores'):
                    all_scores.extend(cat_stats['individual_relevance_scores'])
                    category_labels.extend([category] * len(cat_stats['individual_relevance_scores']))
            
            if all_scores:
                # Create histogram
                ax2.hist(all_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                ax2.axvline(x=0.2, color='orange', linestyle='--', alpha=0.7, label='0.2 Threshold')
                ax2.axvline(x=0.25, color='red', linestyle='--', alpha=0.7, label='0.25 Target')
                ax2.axvline(x=np.mean(all_scores), color='green', linestyle='-', alpha=0.8, label=f'Mean: {np.mean(all_scores):.3f}')
                
                ax2.set_title('Relevance Score Distribution', fontweight='bold')
                ax2.set_xlabel('Relevance Score')
                ax2.set_ylabel('Frequency')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'No relevance data available', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Relevance Score Distribution', fontweight='bold')
            
            # Chart 3: Statistical Summary Table
            ax3 = axes[1, 0]
            ax3.axis('tight')
            ax3.axis('off')
            
            table_data = []
            headers = ['Category', 'Avg Relevance', 'Min/Max', 'Success/Total', 'Threshold Met']
            
            for category, cat_stats in category_results.items():
                if cat_stats['total_queries'] > 0:
                    table_data.append([
                        category.replace('_', ' ').title(),
                        f"{cat_stats['average_relevance']:.3f}",
                        f"{cat_stats['min_relevance']:.3f}/{cat_stats['max_relevance']:.3f}",
                        f"{cat_stats['successful_retrievals']}/{cat_stats['total_queries']}",
                        '✅' if cat_stats.get('meets_threshold', False) else '❌'
                    ])
            
            table_data.append([
                'Overall',
                f"{overall_results['average_relevance']:.3f}",
                f"{overall_results['min_relevance']:.3f}/{overall_results['max_relevance']:.3f}",
                f"{overall_results['successful_queries']}/{overall_results['total_queries']}",
                '✅' if overall_results.get('target_compliance', False) else '❌'
            ])
            
            if table_data:
                table = ax3.table(cellText=table_data, colLabels=headers,
                                cellLoc='center', loc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 2)
                
                # Style header
                for i in range(len(headers)):
                    table[(0, i)].set_text_props(weight='bold', color='white')
                    table[(0, i)].set_facecolor('#2E7D32')
            
            ax3.set_title('Relevance Statistics Summary', fontweight='bold', pad=20)
            
            # Chart 4: Category Comparison Box Plot
            ax4 = axes[1, 1]
            
            box_data = []
            box_labels = []
            
            for category, cat_stats in category_results.items():
                if cat_stats.get('individual_relevance_scores'):
                    box_data.append(cat_stats['individual_relevance_scores'])
                    box_labels.append(category.replace('_', ' ').title())
            
            if box_data:
                box_plot = ax4.boxplot(box_data, labels=box_labels, patch_artist=True)
                colors = ['#1f77b4', '#ff7f0e', '#d62728']
                for patch, color in zip(box_plot['boxes'], colors[:len(box_plot['boxes'])]):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                
                ax4.axhline(y=0.2, color='orange', linestyle='--', alpha=0.7, label='0.2 Threshold')
                ax4.axhline(y=0.25, color='red', linestyle='--', alpha=0.7, label='0.25 Target')
                ax4.set_title('Relevance Distribution by Category', fontweight='bold')
                ax4.set_ylabel('Relevance Score')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'Insufficient data for box plot', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Relevance Distribution by Category', fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"relevance_analysis_charts_{timestamp}.png"
            
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            chart_path = results_dir / chart_filename
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"📈 Relevance charts saved to: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"❌ Relevance chart generation failed: {e}")
            return ""


if __name__ == "__main__":
    """Independent relevance chart generation"""
    
    print("📈 OnCall.ai Relevance Chart Generator")
    
    chart_gen = RelevanceChartGenerator()
    
    try:
        stats = chart_gen.load_latest_relevance_statistics()
        chart_path = chart_gen.generate_relevance_charts(stats)
        
        print(f"\n✅ Relevance chart generation complete!")
        print(f"📈 Charts saved to: {chart_path}")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Please run latency_evaluator.py first to generate relevance statistics data")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
