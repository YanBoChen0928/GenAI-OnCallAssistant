#!/usr/bin/env python3
"""
OnCall.ai System - Extraction Chart Generator
============================================

Generates extraction success rate charts from saved statistics.
Reads JSON files produced by comprehensive evaluator.

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


class ExtractionChartGenerator:
    """Generate charts for condition extraction metrics"""
    
    def __init__(self):
        """Initialize chart generator"""
        print("📈 Initializing Extraction Chart Generator...")
        plt.style.use('default')
        sns.set_palette("husl")
        print("✅ Chart Generator ready")
    
    def load_latest_extraction_statistics(self, results_dir: str = None) -> Dict[str, Any]:
        """Load the most recent extraction statistics file"""
        if results_dir is None:
            results_dir = Path(__file__).parent / "results"
        
        pattern = str(results_dir / "extraction_statistics_*.json")
        stat_files = glob.glob(pattern)
        
        if not stat_files:
            raise FileNotFoundError(f"No extraction statistics files found in {results_dir}")
        
        latest_file = max(stat_files, key=os.path.getmtime)
        print(f"📊 Loading extraction statistics from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        return stats
    
    def generate_extraction_charts(self, stats: Dict[str, Any]) -> str:
        """Generate extraction success rate analysis charts"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('OnCall.ai Extraction Success Rate Analysis', fontsize=16, fontweight='bold')
            
            category_results = stats['category_results']
            overall_results = stats['overall_results']
            
            # Chart 1: Success Rate by Category
            ax1 = axes[0, 0]
            categories = []
            success_rates = []
            
            for category, cat_stats in category_results.items():
                if cat_stats['total_count'] > 0:
                    categories.append(category.replace('_', ' ').title())
                    success_rates.append(cat_stats['success_rate'] * 100)
            
            categories.append('Overall')
            success_rates.append(overall_results['success_rate'] * 100)
            
            bars = ax1.bar(categories, success_rates, alpha=0.8, color=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c'])
            ax1.set_title('Extraction Success Rate by Category', fontweight='bold')
            ax1.set_ylabel('Success Rate (%)')
            ax1.set_xlabel('Query Category')
            ax1.grid(True, alpha=0.3)
            
            # Add target line
            ax1.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='80% Target')
            ax1.legend()
            
            # Add value labels
            for bar, rate in zip(bars, success_rates):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Chart 2: Success Count
            ax2 = axes[0, 1]
            successful_counts = []
            total_counts = []
            
            for category, cat_stats in category_results.items():
                if cat_stats['total_count'] > 0:
                    successful_counts.append(cat_stats['successful_count'])
                    total_counts.append(cat_stats['total_count'])
            
            successful_counts.append(overall_results['successful_count'])
            total_counts.append(overall_results['total_count'])
            
            x = np.arange(len(categories))
            width = 0.35
            
            ax2.bar(x - width/2, successful_counts, width, label='Successful', alpha=0.8)
            ax2.bar(x + width/2, total_counts, width, label='Total', alpha=0.8)
            
            ax2.set_title('Extraction Success Count', fontweight='bold')
            ax2.set_ylabel('Query Count')
            ax2.set_xlabel('Query Category')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categories)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Chart 3: Statistical Summary Table
            ax3 = axes[1, 0]
            ax3.axis('tight')
            ax3.axis('off')
            
            table_data = []
            headers = ['Category', 'Success Rate', 'Success/Total', 'Avg Time (s)', 'Target Met']
            
            for category, cat_stats in category_results.items():
                if cat_stats['total_count'] > 0:
                    table_data.append([
                        category.replace('_', ' ').title(),
                        f"{cat_stats['success_rate']:.1%}",
                        f"{cat_stats['successful_count']}/{cat_stats['total_count']}",
                        f"{cat_stats['average_extraction_time']:.3f}",
                        '✅' if cat_stats.get('meets_threshold', False) else '❌'
                    ])
            
            table_data.append([
                'Overall',
                f"{overall_results['success_rate']:.1%}",
                f"{overall_results['successful_count']}/{overall_results['total_count']}",
                '-',
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
            
            ax3.set_title('Extraction Statistics Summary', fontweight='bold', pad=20)
            
            # Chart 4: Performance visualization
            ax4 = axes[1, 1]
            
            # Simple performance indicator
            overall_rate = overall_results['success_rate'] * 100
            colors = ['#d62728' if overall_rate < 80 else '#2ca02c']
            
            wedges, texts, autotexts = ax4.pie([overall_rate, 100-overall_rate], 
                                              labels=['Successful', 'Failed'],
                                              autopct='%1.1f%%',
                                              colors=['#2ca02c', '#ffcccc'],
                                              startangle=90)
            
            ax4.set_title(f'Overall Extraction Success\n{overall_rate:.1f}% Success Rate', fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"extraction_analysis_charts_{timestamp}.png"
            
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            chart_path = results_dir / chart_filename
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"📈 Extraction charts saved to: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"❌ Extraction chart generation failed: {e}")
            return ""


if __name__ == "__main__":
    """Independent extraction chart generation"""
    
    print("📈 OnCall.ai Extraction Chart Generator")
    
    chart_gen = ExtractionChartGenerator()
    
    try:
        stats = chart_gen.load_latest_extraction_statistics()
        chart_path = chart_gen.generate_extraction_charts(stats)
        
        print(f"\n✅ Extraction chart generation complete!")
        print(f"📈 Charts saved to: {chart_path}")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Please run latency_evaluator.py first to generate extraction statistics data")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
