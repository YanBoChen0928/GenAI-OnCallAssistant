#!/usr/bin/env python3
"""
OnCall.ai System - RAG vs Direct Latency Comparison Chart Generator
==================================================================

Compares RAG and Direct LLM system latency performance.
Reads statistics from latency_statistics_*.json and direct_llm_statistics_*.json

No LLM calls - pure data visualization.

Author: YanBo Chen  
Date: 2025-08-05
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path
import glob

# Visualization imports
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class RAGvsDirectLatencyChartGenerator:
    """Generate RAG vs Direct latency comparison charts"""
    
    def __init__(self):
        """Initialize chart generator"""
        print("📈 Initializing RAG vs Direct Latency Chart Generator...")
        
        # Set up professional chart style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Define system colors
        self.system_colors = {
            'rag': '#1f77b4',      # Blue
            'direct': '#ff7f0e'    # Orange
        }
        
        print("✅ Chart Generator ready with professional medical styling")
    
    def find_latest_statistics_files(self) -> Tuple[str, str]:
        """
        Find the most recent RAG and Direct statistics files
        
        Returns:
            Tuple of (rag_file_path, direct_file_path)
        """
        results_dir = Path(__file__).parent / "results"
        
        # Find RAG statistics file
        rag_pattern = str(results_dir / "latency_statistics_*.json")
        rag_files = glob.glob(rag_pattern)
        
        if not rag_files:
            raise FileNotFoundError(f"No RAG latency statistics files found with pattern: {rag_pattern}")
        
        latest_rag_file = max(rag_files, key=os.path.getmtime)
        
        # Find Direct statistics file
        direct_pattern = str(results_dir / "direct_llm_statistics_*.json")
        direct_files = glob.glob(direct_pattern)
        
        if not direct_files:
            raise FileNotFoundError(f"No Direct LLM statistics files found with pattern: {direct_pattern}")
        
        latest_direct_file = max(direct_files, key=os.path.getmtime)
        
        print(f"📊 Found RAG statistics: {latest_rag_file}")
        print(f"📊 Found Direct statistics: {latest_direct_file}")
        
        return latest_rag_file, latest_direct_file
    
    def load_statistics(self, rag_file: str, direct_file: str) -> Tuple[Dict, Dict]:
        """
        Load statistics from both files
        
        Args:
            rag_file: Path to RAG statistics file
            direct_file: Path to Direct statistics file
            
        Returns:
            Tuple of (rag_stats, direct_stats)
        """
        print(f"📁 Loading RAG statistics from: {rag_file}")
        with open(rag_file, 'r', encoding='utf-8') as f:
            rag_stats = json.load(f)
        
        print(f"📁 Loading Direct statistics from: {direct_file}")
        with open(direct_file, 'r', encoding='utf-8') as f:
            direct_stats = json.load(f)
        
        return rag_stats, direct_stats
    
    def generate_comparison_charts(self, rag_stats: Dict, direct_stats: Dict) -> str:
        """
        Generate comprehensive RAG vs Direct latency comparison charts
        
        Creates 4-panel comparison:
        1. Category-wise latency comparison
        2. Overall performance comparison
        3. Target compliance comparison
        4. Success rate comparison
        """
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('RAG vs Direct LLM - Latency Performance Comparison', 
                        fontsize=16, fontweight='bold')
            
            # Chart 1: Category-wise Latency Comparison
            ax1 = axes[0, 0]
            categories = ['diagnosis', 'treatment', 'mixed']
            rag_latencies = []
            direct_latencies = []
            
            for category in categories:
                rag_cat = rag_stats['category_results'].get(category, {})
                direct_cat = direct_stats['category_results'].get(category, {})
                
                rag_latencies.append(rag_cat.get('average_latency', 0))
                direct_latencies.append(direct_cat.get('average_latency', 0))
            
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax1.bar(x - width/2, rag_latencies, width, label='RAG', 
                           color=self.system_colors['rag'], alpha=0.8)
            bars2 = ax1.bar(x + width/2, direct_latencies, width, label='Direct LLM', 
                           color=self.system_colors['direct'], alpha=0.8)
            
            ax1.set_title('Latency by Category', fontweight='bold')
            ax1.set_ylabel('Average Latency (seconds)')
            ax1.set_xlabel('Query Category')
            ax1.set_xticks(x)
            ax1.set_xticklabels([cat.capitalize() for cat in categories])
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Add target line
            ax1.axhline(y=60.0, color='red', linestyle='--', alpha=0.7, label='60s Target')
            ax1.legend()
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{height:.1f}s', ha='center', va='bottom', fontsize=9)
            
            # Chart 2: Overall Performance Comparison
            ax2 = axes[0, 1]
            
            systems = ['RAG', 'Direct LLM']
            overall_latencies = [
                rag_stats['overall_results']['average_latency'],
                direct_stats['overall_results']['average_latency']
            ]
            
            bars = ax2.bar(systems, overall_latencies, 
                          color=[self.system_colors['rag'], self.system_colors['direct']], 
                          alpha=0.8)
            
            ax2.set_title('Overall Average Latency', fontweight='bold')
            ax2.set_ylabel('Average Latency (seconds)')
            ax2.grid(True, alpha=0.3)
            
            # Add target line
            ax2.axhline(y=60.0, color='red', linestyle='--', alpha=0.7, label='60s Target')
            ax2.legend()
            
            # Add value labels
            for bar, value in zip(bars, overall_latencies):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{value:.1f}s', ha='center', va='bottom', fontweight='bold')
            
            # Chart 3: Target Compliance Comparison
            ax3 = axes[1, 0]
            
            rag_compliance = rag_stats['overall_results']['target_compliance'] * 100
            direct_compliance = direct_stats['overall_results']['target_compliance'] * 100
            
            compliance_data = [rag_compliance, direct_compliance]
            
            bars = ax3.bar(systems, compliance_data, 
                          color=[self.system_colors['rag'], self.system_colors['direct']], 
                          alpha=0.8)
            
            ax3.set_title('60s Target Compliance Rate', fontweight='bold')
            ax3.set_ylabel('Compliance Rate (%)')
            ax3.set_ylim(0, 105)
            ax3.grid(True, alpha=0.3)
            
            # Add target line at 100%
            ax3.axhline(y=100.0, color='green', linestyle='--', alpha=0.7, label='100% Target')
            ax3.legend()
            
            # Add percentage labels
            for bar, value in zip(bars, compliance_data):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Chart 4: Success Rate Comparison
            ax4 = axes[1, 1]
            
            rag_success_rate = rag_stats['overall_results']['successful_queries'] / rag_stats['overall_results']['total_queries'] * 100
            direct_success_rate = direct_stats['overall_results']['successful_queries'] / direct_stats['overall_results']['total_queries'] * 100
            
            success_data = [rag_success_rate, direct_success_rate]
            
            bars = ax4.bar(systems, success_data, 
                          color=[self.system_colors['rag'], self.system_colors['direct']], 
                          alpha=0.8)
            
            ax4.set_title('Query Success Rate', fontweight='bold')
            ax4.set_ylabel('Success Rate (%)')
            ax4.set_ylim(0, 105)
            ax4.grid(True, alpha=0.3)
            
            # Add target line at 100%
            ax4.axhline(y=100.0, color='green', linestyle='--', alpha=0.7, label='100% Target')
            ax4.legend()
            
            # Add percentage labels
            for bar, value in zip(bars, success_data):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"rag_vs_direct_latency_comparison_{timestamp}.png"
            
            # Ensure results directory exists
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            chart_path = results_dir / chart_filename
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            print(f"📈 RAG vs Direct latency comparison charts saved to: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"❌ Chart generation failed: {e}")
            return ""
    
    def print_comparison_summary(self, rag_stats: Dict, direct_stats: Dict):
        """Print formatted comparison summary to console"""
        print(f"\n📊 === RAG vs DIRECT LATENCY COMPARISON SUMMARY ===")
        
        # Overall comparison
        rag_overall = rag_stats['overall_results']
        direct_overall = direct_stats['overall_results']
        
        print(f"\n🔄 Overall Performance:")
        print(f"   RAG System:")
        print(f"     • Average Latency: {rag_overall['average_latency']:.2f}s")
        print(f"     • Success Rate: {rag_overall['successful_queries']}/{rag_overall['total_queries']} ({rag_overall['successful_queries']/rag_overall['total_queries']*100:.1f}%)")
        print(f"     • 60s Target Compliance: {rag_overall['target_compliance']*100:.1f}%")
        
        print(f"   Direct LLM System:")
        print(f"     • Average Latency: {direct_overall['average_latency']:.2f}s")
        print(f"     • Success Rate: {direct_overall['successful_queries']}/{direct_overall['total_queries']} ({direct_overall['success_rate']*100:.1f}%)")
        print(f"     • 60s Target Compliance: {direct_overall['target_compliance']*100:.1f}%")
        
        # Performance winner
        if direct_overall['average_latency'] < rag_overall['average_latency']:
            latency_winner = "Direct LLM"
            latency_improvement = rag_overall['average_latency'] - direct_overall['average_latency']
        else:
            latency_winner = "RAG"
            latency_improvement = direct_overall['average_latency'] - rag_overall['average_latency']
        
        print(f"\n🏆 Performance Winner:")
        print(f"   • Faster System: {latency_winner}")
        print(f"   • Performance Improvement: {latency_improvement:.2f}s ({latency_improvement/max(rag_overall['average_latency'], direct_overall['average_latency'])*100:.1f}%)")
        
        # Category breakdown
        print(f"\n📋 Category Breakdown:")
        categories = ['diagnosis', 'treatment', 'mixed']
        
        for category in categories:
            rag_cat = rag_stats['category_results'].get(category, {})
            direct_cat = direct_stats['category_results'].get(category, {})
            
            if rag_cat.get('query_count', 0) > 0 and direct_cat.get('query_count', 0) > 0:
                rag_latency = rag_cat.get('average_latency', 0)
                direct_latency = direct_cat.get('average_latency', 0)
                
                winner = "Direct" if direct_latency < rag_latency else "RAG"
                difference = abs(rag_latency - direct_latency)
                
                print(f"   {category.capitalize()}:")
                print(f"     • RAG: {rag_latency:.2f}s")
                print(f"     • Direct: {direct_latency:.2f}s")
                print(f"     • Winner: {winner} (faster by {difference:.2f}s)")


# Independent execution interface
if __name__ == "__main__":
    """Independent chart generation interface"""
    
    print("📈 OnCall.ai RAG vs Direct Latency Comparison Chart Generator")
    
    # Initialize chart generator
    chart_gen = RAGvsDirectLatencyChartGenerator()
    
    try:
        # Find latest statistics files
        rag_file, direct_file = chart_gen.find_latest_statistics_files()
        
        # Load statistics
        rag_stats, direct_stats = chart_gen.load_statistics(rag_file, direct_file)
        
        # Generate comparison charts
        print(f"📈 Generating RAG vs Direct comparison charts...")
        chart_path = chart_gen.generate_comparison_charts(rag_stats, direct_stats)
        
        # Print comparison summary
        chart_gen.print_comparison_summary(rag_stats, direct_stats)
        
        print(f"\n✅ RAG vs Direct latency comparison complete!")
        print(f"📈 Charts saved to: {chart_path}")
        print(f"💡 Charts optimized for research presentations and publications")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Please ensure both evaluators have been run:")
        print("   python latency_evaluator.py  # for RAG statistics")
        print("   python direct_llm_evaluator.py  # for Direct statistics")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
