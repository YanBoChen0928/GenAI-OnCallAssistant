#!/usr/bin/env python3
"""
OnCall.ai System - LLM Judge Chart Generator (Metrics 5-6)
==========================================================

Generates comprehensive comparison charts for LLM judge evaluation results.
Supports both single-system and multi-system visualization with professional layouts.

Metrics visualized:
5. Clinical Actionability (臨床可操作性) - 1-10 scale
6. Clinical Evidence Quality (臨床證據品質) - 1-10 scale

Author: YanBo Chen  
Date: 2025-08-04
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path
import glob
import numpy as np

# Visualization imports
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.patches import Rectangle


class LLMJudgeChartGenerator:
    """Generate professional comparison charts for LLM judge evaluation results"""
    
    def __init__(self):
        """Initialize chart generator with professional styling"""
        print("📈 Initializing LLM Judge Chart Generator...")
        
        # Set up professional chart style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Professional color scheme for medical evaluation
        self.colors = {
            'rag': '#2E8B57',      # Sea Green - represents evidence-based
            'direct': '#4682B4',   # Steel Blue - represents direct approach
            'claude': '#9370DB',   # Medium Purple - future extension
            'gpt4': '#DC143C',     # Crimson - future extension
            'actionability': '#FF6B6B',  # Coral Red
            'evidence': '#4ECDC4',        # Turquoise
            'target_line': '#FF4444',     # Red for target thresholds
            'grid': '#E0E0E0'             # Light gray for grid
        }
        
        print("✅ Chart Generator ready with professional medical styling")
    
    def load_latest_statistics(self, results_dir: str = None) -> Dict[str, Any]:
        """
        Load the most recent judge evaluation statistics file
        
        Args:
            results_dir: Directory containing statistics files
        """
        if results_dir is None:
            results_dir = Path(__file__).parent / "results"
        
        # Find latest comparison statistics file
        pattern = str(results_dir / "judge_evaluation_comparison_*.json")
        stat_files = glob.glob(pattern)
        
        if not stat_files:
            raise FileNotFoundError(f"No judge evaluation comparison files found in {results_dir}")
        
        # Get the most recent file
        latest_file = max(stat_files, key=os.path.getmtime)
        
        print(f"📊 Loading statistics from: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_comparison_charts(self, stats: Dict[str, Any], save_path: str = None) -> str:
        """
        Generate comprehensive 4-panel comparison visualization
        
        Creates professional charts showing:
        1. System comparison radar chart
        2. Grouped bar chart comparison
        3. Actionability vs Evidence scatter plot
        4. Category-wise heatmap
        """
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(
                'Medical AI Systems Comparison - Clinical Quality Assessment\n'
                'Actionability (1-10): Can healthcare providers act immediately? | '
                'Evidence Quality (1-10): Is advice evidence-based?',
                fontsize=14, fontweight='bold', y=0.95
            )
            
            # Extract comparison metadata
            comparison_meta = stats.get('comparison_metadata', {})
            systems = comparison_meta.get('systems_compared', ['rag', 'direct'])
            
            overall_results = stats['overall_results']
            category_results = stats['category_results']
            
            # Chart 1: System Comparison Radar Chart
            self._create_radar_chart(axes[0, 0], stats, systems)
            
            # Chart 2: Grouped Bar Chart Comparison
            self._create_grouped_bar_chart(axes[0, 1], stats, systems)
            
            # Chart 3: Actionability vs Evidence Scatter Plot
            self._create_scatter_plot(axes[1, 0], stats, systems)
            
            # Chart 4: Category-wise Performance Heatmap
            self._create_heatmap(axes[1, 1], stats, systems)
            
            # Add method annotation at bottom
            method_text = (
                f"Evaluation: Llama3-70B judge | Targets: Actionability ≥7.0, Evidence ≥7.5 | "
                f"Systems: {', '.join([s.upper() for s in systems])} | "
                f"Queries: {overall_results.get('total_queries', 'N/A')}"
            )
            fig.text(0.5, 0.02, method_text, ha='center', fontsize=10, 
                    style='italic', color='gray')
            
            # Adjust layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.88, bottom=0.08)
            
            # Save the chart
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                systems_str = "_vs_".join(systems)
                save_path = f"judge_comparison_charts_{systems_str}_{timestamp}.png"
            
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(exist_ok=True)
            full_path = results_dir / save_path
            
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"📊 Comparison charts saved to: {full_path}")
            return str(full_path)
            
        except Exception as e:
            print(f"❌ Chart generation failed: {e}")
            raise
    
    def _create_radar_chart(self, ax, stats: Dict, systems: List[str]):
        """Create radar chart for multi-dimensional system comparison"""
        ax.set_title('Multi-Dimensional System Comparison', fontweight='bold', pad=20)
        
        # Prepare data for radar chart using real system-specific data
        categories = ['Overall Actionability', 'Overall Evidence', 'Diagnosis', 'Treatment', 'Mixed']
        
        # Extract real system-specific metrics
        detailed_results = stats.get('detailed_system_results', {})
        system_data = {}
        
        for system in systems:
            if system in detailed_results:
                system_info = detailed_results[system]
                system_results = system_info['results']
                
                # Calculate category-specific performance
                category_performance = {}
                for result in system_results:
                    category = result.get('category', 'unknown').lower()
                    if category not in category_performance:
                        category_performance[category] = {'actionability': [], 'evidence': []}
                    category_performance[category]['actionability'].append(result['actionability_score'])
                    category_performance[category]['evidence'].append(result['evidence_score'])
                
                # Build radar chart data
                system_scores = [
                    system_info['avg_actionability'],  # Overall Actionability
                    system_info['avg_evidence'],       # Overall Evidence
                    # Category-specific scores (average of actionability and evidence)
                    (sum(category_performance.get('diagnosis', {}).get('actionability', [0])) / 
                     len(category_performance.get('diagnosis', {}).get('actionability', [1])) + 
                     sum(category_performance.get('diagnosis', {}).get('evidence', [0])) / 
                     len(category_performance.get('diagnosis', {}).get('evidence', [1]))) / 2 if 'diagnosis' in category_performance else 0.5,
                    
                    (sum(category_performance.get('treatment', {}).get('actionability', [0])) / 
                     len(category_performance.get('treatment', {}).get('actionability', [1])) + 
                     sum(category_performance.get('treatment', {}).get('evidence', [0])) / 
                     len(category_performance.get('treatment', {}).get('evidence', [1]))) / 2 if 'treatment' in category_performance else 0.5,
                    
                    (sum(category_performance.get('mixed', {}).get('actionability', [0])) / 
                     len(category_performance.get('mixed', {}).get('actionability', [1])) + 
                     sum(category_performance.get('mixed', {}).get('evidence', [0])) / 
                     len(category_performance.get('mixed', {}).get('evidence', [1]))) / 2 if 'mixed' in category_performance else 0.5
                ]
                system_data[system] = system_scores
            else:
                # Fallback to overall stats if detailed results not available
                overall_results = stats['overall_results']
                system_data[system] = [
                    overall_results['average_actionability'],
                    overall_results['average_evidence'],
                    0.7, 0.6, 0.5  # Placeholder for missing category data
                ]
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        for system in systems:
            values = system_data[system] + [system_data[system][0]]  # Complete the circle
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=f'{system.upper()} System', color=self.colors.get(system, 'gray'))
            ax.fill(angles, values, alpha=0.1, color=self.colors.get(system, 'gray'))
        
        # Customize radar chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['2.0', '4.0', '6.0', '8.0', '10.0'])
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        
        # Add target threshold circle
        target_circle = [0.7] * (len(categories) + 1)  # 7.0 threshold
        ax.plot(angles, target_circle, '--', color=self.colors['target_line'], 
               alpha=0.7, label='Target (7.0)')
    
    def _create_grouped_bar_chart(self, ax, stats: Dict, systems: List[str]):
        """Create grouped bar chart for direct metric comparison"""
        ax.set_title('Direct Metric Comparison', fontweight='bold', pad=20)
        
        # Prepare data using real system-specific metrics
        metrics = ['Actionability', 'Evidence Quality']
        detailed_results = stats.get('detailed_system_results', {})
        
        # Extract real system-specific data
        system_scores = {}
        for system in systems:
            if system in detailed_results:
                system_info = detailed_results[system]
                system_scores[system] = [
                    system_info['avg_actionability'],
                    system_info['avg_evidence']
                ]
            else:
                # Fallback to overall results
                overall_results = stats['overall_results']
                system_scores[system] = [
                    overall_results['average_actionability'],
                    overall_results['average_evidence']
                ]
        
        # Create grouped bar chart
        x = np.arange(len(metrics))
        width = 0.35 if len(systems) == 2 else 0.25
        
        for i, system in enumerate(systems):
            offset = (i - len(systems)/2 + 0.5) * width
            bars = ax.bar(x + offset, system_scores[system], width,
                         label=f'{system.upper()}', color=self.colors.get(system, 'gray'),
                         alpha=0.8)
            
            # Add value labels on bars
            for bar, value in zip(bars, system_scores[system]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Add target threshold lines
        ax.axhline(y=0.7, color=self.colors['target_line'], linestyle='--', 
                  alpha=0.7, label='Actionability Target (7.0)')
        ax.axhline(y=0.75, color=self.colors['target_line'], linestyle=':', 
                  alpha=0.7, label='Evidence Target (7.5)')
        
        # Customize chart
        ax.set_xlabel('Evaluation Metrics')
        ax.set_ylabel('Score (0-1 scale)')
        ax.set_title('System Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(0, 1.0)
    
    def _create_scatter_plot(self, ax, stats: Dict, systems: List[str]):
        """Create scatter plot for actionability vs evidence quality analysis"""
        ax.set_title('Actionability vs Evidence Quality Analysis', fontweight='bold', pad=20)
        
        # Extract real query-level data from detailed results
        detailed_results = stats.get('detailed_system_results', {})
        
        for system in systems:
            if system in detailed_results:
                system_results = detailed_results[system]['results']
                
                # Extract real actionability and evidence scores for each query
                actionability_scores = [r['actionability_score'] for r in system_results]
                evidence_scores = [r['evidence_score'] for r in system_results]
                
                ax.scatter(actionability_scores, evidence_scores, 
                          label=f'{system.upper()}', color=self.colors.get(system, 'gray'),
                          alpha=0.7, s=100, edgecolors='white', linewidth=1)
            else:
                # Fallback: create single point from overall averages
                overall_results = stats['overall_results']
                ax.scatter([overall_results['average_actionability']], 
                          [overall_results['average_evidence']], 
                          label=f'{system.upper()}', color=self.colors.get(system, 'gray'),
                          alpha=0.7, s=100, edgecolors='white', linewidth=1)
        
        # Add target threshold lines
        ax.axvline(x=0.7, color=self.colors['target_line'], linestyle='--', 
                  alpha=0.7, label='Actionability Target')
        ax.axhline(y=0.75, color=self.colors['target_line'], linestyle='--', 
                  alpha=0.7, label='Evidence Target')
        
        # Add target zone
        target_rect = Rectangle((0.7, 0.75), 0.3, 0.25, linewidth=1, 
                               edgecolor=self.colors['target_line'], facecolor='green', 
                               alpha=0.1, label='Target Zone')
        ax.add_patch(target_rect)
        
        # Customize chart
        ax.set_xlabel('Clinical Actionability (0-1 scale)')
        ax.set_ylabel('Clinical Evidence Quality (0-1 scale)')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    def _create_heatmap(self, ax, stats: Dict, systems: List[str]):
        """Create heatmap for category-wise performance matrix"""
        ax.set_title('Category-wise Performance Matrix', fontweight='bold', pad=20)
        
        # Prepare data
        categories = ['Diagnosis', 'Treatment', 'Mixed']
        metrics = ['Actionability', 'Evidence']
        category_results = stats['category_results']
        
        # Create data matrix
        data_matrix = []
        row_labels = []
        
        for system in systems:
            for metric in metrics:
                row_data = []
                for category in categories:
                    cat_key = category.lower()
                    if cat_key in category_results and category_results[cat_key]['query_count'] > 0:
                        if metric == 'Actionability':
                            value = category_results[cat_key]['average_actionability']
                        else:
                            value = category_results[cat_key]['average_evidence']
                    else:
                        value = 0.5  # Placeholder for missing data
                    row_data.append(value)
                
                data_matrix.append(row_data)
                row_labels.append(f'{system.upper()}\n{metric}')
        
        # Create heatmap
        im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(categories)))
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_xticklabels(categories)
        ax.set_yticklabels(row_labels, fontsize=9)
        
        # Add text annotations
        for i in range(len(row_labels)):
            for j in range(len(categories)):
                text = ax.text(j, i, f'{data_matrix[i][j]:.3f}',
                             ha='center', va='center', fontweight='bold',
                             color='white' if data_matrix[i][j] < 0.5 else 'black')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.6)
        cbar.set_label('Performance Score (0-1)', rotation=270, labelpad=15)
        
        ax.set_xlabel('Query Categories')
        ax.set_ylabel('System × Metric')


# Independent execution interface
if __name__ == "__main__":
    """Independent chart generation interface"""
    
    print("📊 OnCall.ai LLM Judge Chart Generator - Metrics 5-6 Visualization")
    
    # Initialize generator
    generator = LLMJudgeChartGenerator()
    
    try:
        # Load latest statistics
        stats = generator.load_latest_statistics()
        
        print(f"📈 Generating comparison charts...")
        
        # Generate comprehensive comparison charts
        chart_path = generator.generate_comparison_charts(stats)
        
        # Print summary
        comparison_meta = stats.get('comparison_metadata', {})
        systems = comparison_meta.get('systems_compared', ['rag', 'direct'])
        overall_results = stats['overall_results']
        
        print(f"\n📊 === CHART GENERATION SUMMARY ===")
        print(f"Systems Visualized: {' vs '.join([s.upper() for s in systems])}")
        print(f"Overall Actionability: {overall_results['average_actionability']:.3f}")
        print(f"Overall Evidence Quality: {overall_results['average_evidence']:.3f}")
        print(f"Total Queries: {overall_results['total_queries']}")
        print(f"Chart Components: Radar Chart, Bar Chart, Scatter Plot, Heatmap")
        
        print(f"\n✅ Comprehensive visualization complete!")
        print(f"📊 Charts saved to: {chart_path}")
        print(f"💡 Tip: Charts optimized for research presentations and publications")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print(f"💡 Please run judge evaluation first:")
        print("   python metric5_6_llm_judge_evaluator.py rag,direct")
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
