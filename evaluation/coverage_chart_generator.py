#!/usr/bin/env python3
"""
OnCall.ai System - Coverage Chart Generator
===========================================

Generates retrieval coverage charts from saved statistics.
Shows how well generated advice utilizes retrieved content.

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


class CoverageChartGenerator:
    """Generate charts for retrieval coverage metrics"""
    
    def __init__(self):
        """Initialize chart generator"""
        print("📈 Initializing Coverage Chart Generator...")
        plt.style.use('default')
        sns.set_palette("husl")
        print("✅ Chart Generator ready")
    
    def load_latest_coverage_statistics(self, results_dir: str = None) -> Dict[str, Any]:
        """Load the most recent coverage statistics file"""
        if results_dir is None:
            results_dir = Path(__file__).parent / "results"
        
        pattern = str(results_dir / "coverage_statistics_*.json")
        stat_files = glob.glob(pattern)
        
        if not stat_files:
            raise FileNotFoundError(f"No coverage statistics files found in {results_dir}")
        
        latest_file = max(stat_files, key=os.path.getmtime)
        print(f"📊 Loading coverage statistics from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        return stats
    
    def generate_coverage_charts(self, stats: Dict[str, Any]) -> str:
        """Generate coverage analysis charts"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('OnCall.ai Retrieval Coverage Analysis', fontsize=16, fontweight='bold')
            
            category_results = stats['category_results']
            overall_results = stats['overall_results']
            
            # Chart 1: Average Coverage by Category
            ax1 = axes[0, 0]
            categories = []
            avg_coverages = []
            
            for category, cat_stats in category_results.items():
                if cat_stats['successful_evaluations'] > 0:
                    categories.append(category.replace('_', ' ').title())
                    avg_coverages.append(cat_stats['average_coverage'] * 100)  # Convert to percentage
            
            categories.append('Overall')
            avg_coverages.append(overall_results['average_coverage'] * 100)
            
            bars = ax1.bar(categories, avg_coverages, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c'])
            ax1.set_title('Average Coverage Score by Category', fontweight='bold')
            ax1.set_ylabel('Coverage Score (%)')
            ax1.set_xlabel('Query Category')
            ax1.grid(True, alpha=0.3)
            
            # Add target line
            ax1.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='60% Target')
            ax1.legend()
            
            # Add value labels
            for bar, coverage in zip(bars, avg_coverages):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{coverage:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Chart 2: Coverage Distribution
            ax2 = axes[0, 1]
            
            # Collect all individual coverage scores
            all_scores = []
            
            for category, cat_stats in category_results.items():
                if cat_stats.get('individual_coverage_scores'):
                    all_scores.extend([score * 100 for score in cat_stats['individual_coverage_scores']])
            
            if all_scores:
                # Create histogram
                ax2.hist(all_scores, bins=15, alpha=0.7, color='lightcoral', edgecolor='black')
                ax2.axvline(x=60, color='red', linestyle='--', alpha=0.7, label='60% Target')
                ax2.axvline(x=np.mean(all_scores), color='green', linestyle='-', alpha=0.8, label=f'Mean: {np.mean(all_scores):.1f}%')
                
                ax2.set_title('Coverage Score Distribution', fontweight='bold')
                ax2.set_xlabel('Coverage Score (%)')
                ax2.set_ylabel('Frequency')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'No coverage data available', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Coverage Score Distribution', fontweight='bold')
            
            # Chart 3: Statistical Summary Table
            ax3 = axes[1, 0]
            ax3.axis('tight')
            ax3.axis('off')
            
            table_data = []
            headers = ['Category', 'Avg Coverage', 'Min/Max', 'Success/Total', 'Target Met']
            
            for category, cat_stats in category_results.items():
                if cat_stats['total_queries'] > 0:
                    table_data.append([
                        category.replace('_', ' ').title(),
                        f"{cat_stats['average_coverage']:.3f}",
                        f"{cat_stats['min_coverage']:.3f}/{cat_stats['max_coverage']:.3f}",
                        f"{cat_stats['successful_evaluations']}/{cat_stats['total_queries']}",
                        '✅' if cat_stats.get('meets_threshold', False) else '❌'
                    ])
            
            table_data.append([
                'Overall',
                f"{overall_results['average_coverage']:.3f}",
                f"{overall_results['min_coverage']:.3f}/{overall_results['max_coverage']:.3f}",
                f"{overall_results['successful_queries']}/{overall_results['total_queries']}",
                '✅' if overall_results.get('meets_threshold', False) else '❌'
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
            
            ax3.set_title('Coverage Statistics Summary', fontweight='bold', pad=20)
            
            # Chart 4: Coverage Performance Radar/Gauge
            ax4 = axes[1, 1]
            
            # Create gauge-like visualization for overall coverage
            overall_coverage_pct = overall_results['average_coverage'] * 100
            
            # Pie chart as gauge
            sizes = [overall_coverage_pct, 100 - overall_coverage_pct]
            colors = ['#2ca02c' if overall_coverage_pct >= 60 else '#ff7f0e', '#f0f0f0']
            
            wedges, texts, autotexts = ax4.pie(sizes, labels=['Covered', 'Not Covered'],
                                              autopct='%1.1f%%',
                                              colors=colors,
                                              startangle=90,
                                              counterclock=False)
            
            # Add center text
            ax4.text(0, 0, f'{overall_coverage_pct:.1f}%\nCoverage', 
                    ha='center', va='center', fontsize=14, fontweight='bold')
            
            ax4.set_title(f'Overall Coverage Performance\n{"✅ Target Met" if overall_coverage_pct >= 60 else "❌ Below Target"}', 
                         fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"coverage_analysis_charts_{timestamp}.png"
            
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            chart_path = results_dir / chart_filename
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"📈 Coverage charts saved to: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"❌ Coverage chart generation failed: {e}")
            return ""


if __name__ == "__main__":
    """Independent coverage chart generation"""
    
    print("📈 OnCall.ai Coverage Chart Generator")
    
    chart_gen = CoverageChartGenerator()
    
    try:
        stats = chart_gen.load_latest_coverage_statistics()
        chart_path = chart_gen.generate_coverage_charts(stats)
        
        print(f"\n✅ Coverage chart generation complete!")
        print(f"📈 Charts saved to: {chart_path}")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Please run latency_evaluator.py first to generate coverage statistics data")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
