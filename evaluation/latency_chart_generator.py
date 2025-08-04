#!/usr/bin/env python3
"""
OnCall.ai System - Latency Chart Generator
==========================================

Generates comprehensive latency analysis charts from saved statistics.
Reads JSON files produced by latency_evaluator.py and creates visualizations.

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


class LatencyChartGenerator:
    """Generate charts from latency evaluation statistics - no LLM dependency"""
    
    def __init__(self):
        """Initialize chart generator"""
        print("📈 Initializing Latency Chart Generator...")
        
        # Set up professional chart style
        plt.style.use('default')
        sns.set_palette("husl")
        
        print("✅ Chart Generator ready")
    
    def load_latest_statistics(self, results_dir: str = None) -> Dict[str, Any]:
        """
        Load the most recent latency statistics file
        
        Args:
            results_dir: Directory containing statistics files
        """
        if results_dir is None:
            results_dir = Path(__file__).parent / "results"
        
        # Find latest statistics file
        pattern = str(results_dir / "latency_statistics_*.json")
        stat_files = glob.glob(pattern)
        
        if not stat_files:
            raise FileNotFoundError(f"No latency statistics files found in {results_dir}")
        
        # Get the most recent file
        latest_file = max(stat_files, key=os.path.getmtime)
        
        print(f"📊 Loading statistics from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        return stats
    
    def generate_comprehensive_charts(self, stats: Dict[str, Any]) -> str:
        """
        Generate comprehensive 4-category latency analysis charts
        
        Creates professional charts showing:
        1. Category comparison bar chart
        2. Individual query scatter plot  
        3. Statistical summary table
        4. Performance distribution box plot
        """
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('OnCall.ai Latency Analysis - Category Comparison', 
                        fontsize=16, fontweight='bold')
            
            category_results = stats['category_results']
            overall_results = stats['overall_results']
            
            # Chart 1: Category Comparison Bar Chart
            ax1 = axes[0, 0]
            categories = []
            avg_latencies = []
            std_devs = []
            
            # Collect category data
            for category, cat_stats in category_results.items():
                if cat_stats['query_count'] > 0:
                    categories.append(category.replace('_', ' ').title())
                    avg_latencies.append(cat_stats['average_latency'])
                    std_devs.append(cat_stats['std_deviation'])
            
            # Add overall
            categories.append('Overall')
            avg_latencies.append(overall_results['average_latency'])
            std_devs.append(overall_results['std_deviation'])
            
            # Create bar chart with error bars
            bars = ax1.bar(categories, avg_latencies, capsize=5, alpha=0.8, 
                          color=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c'])
            ax1.errorbar(categories, avg_latencies, yerr=std_devs, fmt='none', 
                        color='black', capsize=3, capthick=1)
            
            ax1.set_title('Average Latency by Category', fontweight='bold')
            ax1.set_ylabel('Latency (seconds)')
            ax1.set_xlabel('Query Category')
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, avg, std in zip(bars, avg_latencies, std_devs):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + std*0.1,
                        f'{avg:.1f}s', ha='center', va='bottom', fontweight='bold')
            
            # Add target line
            ax1.axhline(y=30.0, color='red', linestyle='--', alpha=0.7, label='30s Target')
            ax1.legend()
            
            # Chart 2: Individual Query Performance
            ax2 = axes[0, 1]
            
            query_indices = []
            latencies = []
            colors = []
            
            color_map = {'diagnosis': '#1f77b4', 'treatment': '#ff7f0e', 'mixed': '#d62728'}
            query_idx = 0
            
            for category, cat_stats in category_results.items():
                for latency in cat_stats['individual_latencies']:
                    query_indices.append(query_idx)
                    latencies.append(latency)
                    colors.append(color_map.get(category, 'gray'))
                    query_idx += 1
            
            if latencies:
                ax2.scatter(query_indices, latencies, c=colors, alpha=0.7, s=100)
                ax2.set_title('Individual Query Performance', fontweight='bold')
                ax2.set_ylabel('Latency (seconds)')
                ax2.set_xlabel('Query Index')
                ax2.grid(True, alpha=0.3)
                
                # Add target line
                ax2.axhline(y=30.0, color='red', linestyle='--', alpha=0.7, label='30s Target')
                
                # Add category legend
                from matplotlib.patches import Patch
                legend_elements = [Patch(facecolor=color_map[cat], label=cat.title()) 
                                 for cat in color_map.keys() if cat in category_results.keys()]
                ax2.legend(handles=legend_elements)
            else:
                ax2.text(0.5, 0.5, 'No latency data available', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Individual Query Performance', fontweight='bold')
            
            # Chart 3: Statistical Summary Table
            ax3 = axes[1, 0]
            ax3.axis('tight')
            ax3.axis('off')
            
            # Create summary table
            table_data = []
            headers = ['Category', 'Avg (s)', 'Std (s)', 'Min (s)', 'Max (s)', 'Count']
            
            for category, cat_stats in category_results.items():
                if cat_stats['query_count'] > 0:
                    table_data.append([
                        category.replace('_', ' ').title(),
                        f"{cat_stats['average_latency']:.2f}",
                        f"{cat_stats['std_deviation']:.2f}",
                        f"{cat_stats['min_latency']:.2f}",
                        f"{cat_stats['max_latency']:.2f}",
                        str(cat_stats['query_count'])
                    ])
            
            # Add overall row
            table_data.append([
                'Overall',
                f"{overall_results['average_latency']:.2f}",
                f"{overall_results['std_deviation']:.2f}",
                f"{overall_results['min_latency']:.2f}",
                f"{overall_results['max_latency']:.2f}",
                str(overall_results['successful_queries'])
            ])
            
            if table_data:
                table = ax3.table(cellText=table_data, colLabels=headers,
                                cellLoc='center', loc='center',
                                colWidths=[0.2, 0.15, 0.15, 0.15, 0.15, 0.1])
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 2)
                
                # Style the table header
                for i in range(len(headers)):
                    table[(0, i)].set_text_props(weight='bold', color='white')
                    table[(0, i)].set_facecolor('#2E7D32')
            
            ax3.set_title('Statistical Summary', fontweight='bold', pad=20)
            
            # Chart 4: Performance Distribution
            ax4 = axes[1, 1]
            
            # Create box plot if we have multiple data points
            box_data = []
            box_labels = []
            
            for category, cat_stats in category_results.items():
                if cat_stats['individual_latencies'] and len(cat_stats['individual_latencies']) > 0:
                    box_data.append(cat_stats['individual_latencies'])
                    box_labels.append(category.replace('_', ' ').title())
            
            if box_data and len(box_data) > 0:
                box_plot = ax4.boxplot(box_data, labels=box_labels, patch_artist=True)
                
                # Color the boxes
                colors = ['#1f77b4', '#ff7f0e', '#d62728']
                for patch, color in zip(box_plot['boxes'], colors[:len(box_plot['boxes'])]):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                
                ax4.set_title('Latency Distribution by Category', fontweight='bold')
                ax4.set_ylabel('Latency (seconds)')
                ax4.grid(True, alpha=0.3)
                
                # Add target line
                ax4.axhline(y=30.0, color='red', linestyle='--', alpha=0.7, label='30s Target')
                ax4.legend()
            else:
                # For single data points, show a simple bar chart
                single_categories = []
                single_latencies = []
                
                for category, cat_stats in category_results.items():
                    if cat_stats['query_count'] > 0:
                        single_categories.append(category.replace('_', ' ').title())
                        single_latencies.append(cat_stats['average_latency'])
                
                if single_categories:
                    ax4.bar(single_categories, single_latencies, alpha=0.7, 
                           color=['#1f77b4', '#ff7f0e', '#d62728'][:len(single_categories)])
                    ax4.set_title('Category Latency (Single Query Each)', fontweight='bold')
                    ax4.set_ylabel('Latency (seconds)')
                    ax4.grid(True, alpha=0.3)
                    ax4.axhline(y=30.0, color='red', linestyle='--', alpha=0.7, label='30s Target')
                    ax4.legend()
                else:
                    ax4.text(0.5, 0.5, 'No data available for distribution plot', 
                            ha='center', va='center', transform=ax4.transAxes)
                    ax4.set_title('Latency Distribution', fontweight='bold')
            
            # Adjust layout and save
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"latency_analysis_charts_{timestamp}.png"
            
            # Ensure results directory exists
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            chart_path = results_dir / chart_filename
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"📈 Charts saved to: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"❌ Chart generation failed: {e}")
            return ""
    
    def print_statistics_summary(self, stats: Dict[str, Any]):
        """Print formatted statistics summary to console"""
        category_results = stats['category_results']
        overall_results = stats['overall_results']
        
        print(f"\n📊 === LATENCY ANALYSIS CHART SUMMARY ===")
        print(f"Overall Performance:")
        print(f"   Average Latency: {overall_results['average_latency']:.2f}s (±{overall_results['std_deviation']:.2f})")
        print(f"   Success Rate: {overall_results['successful_queries']}/{overall_results['total_queries']}")
        print(f"   30s Target Compliance: {overall_results['target_compliance']:.1%}")
        
        print(f"\nCategory Breakdown:")
        for category, cat_stats in category_results.items():
            if cat_stats['query_count'] > 0:
                print(f"   {category.capitalize()}: {cat_stats['average_latency']:.2f}s (±{cat_stats['std_deviation']:.2f}) [{cat_stats['query_count']} queries]")


# Independent execution interface
if __name__ == "__main__":
    """Independent chart generation interface"""
    
    print("📈 OnCall.ai Latency Chart Generator")
    
    # Initialize chart generator
    chart_gen = LatencyChartGenerator()
    
    try:
        # Load latest statistics
        stats = chart_gen.load_latest_statistics()
        
        # Generate charts
        chart_path = chart_gen.generate_comprehensive_charts(stats)
        
        # Print summary
        chart_gen.print_statistics_summary(stats)
        
        print(f"\n✅ Chart generation complete!")
        print(f"📈 Charts saved to: {chart_path}")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Please run latency_evaluator.py first to generate statistics data")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
