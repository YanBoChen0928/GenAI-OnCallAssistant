#!/usr/bin/env python3
"""
Chart Generator Module for Hospital Customization Evaluation

This module generates comprehensive visualizations for hospital customization metrics,
including bar charts for latency analysis, scatter plots for relevance scores,
and coverage percentage charts. All charts are saved as PNG files for reports.

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Set matplotlib style
plt.style.use('default')
sns.set_palette("husl")


class HospitalCustomizationChartGenerator:
    """
    Generates comprehensive charts and visualizations for hospital customization metrics.
    
    This class creates publication-ready charts for latency, relevance, and coverage
    analysis of the hospital customization evaluation system.
    """
    
    def __init__(self, output_dir: str = "evaluation/results/charts"):
        """
        Initialize the chart generator.
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up consistent styling
        self.colors = {
            "primary": "#2E86AB",
            "secondary": "#A23B72", 
            "accent": "#F18F01",
            "success": "#C73E1D",
            "info": "#592E83",
            "light": "#F5F5F5",
            "dark": "#2C3E50"
        }
        
        self.figure_size = (12, 8)
        self.dpi = 300
        
    def generate_latency_charts(self, metrics: Dict[str, Any], timestamp: str = None) -> List[str]:
        """
        Generate comprehensive latency analysis charts.
        
        Args:
            metrics: Metrics dictionary containing latency data
            timestamp: Optional timestamp for file naming
            
        Returns:
            List of generated chart file paths
        """
        print("📊 Generating latency analysis charts...")
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        generated_files = []
        latency_data = metrics.get("metric_1_latency", {})
        
        # 1. Bar chart for latency by query type
        latency_by_type_file = self._create_latency_by_query_type_chart(
            latency_data, timestamp
        )
        if latency_by_type_file:
            generated_files.append(latency_by_type_file)
        
        # 2. Customization time breakdown chart
        customization_breakdown_file = self._create_customization_breakdown_chart(
            latency_data, timestamp
        )
        if customization_breakdown_file:
            generated_files.append(customization_breakdown_file)
        
        # 3. Latency distribution histogram
        latency_distribution_file = self._create_latency_distribution_chart(
            latency_data, timestamp
        )
        if latency_distribution_file:
            generated_files.append(latency_distribution_file)
        
        print(f"✅ Generated {len(generated_files)} latency charts")
        return generated_files
    
    def generate_relevance_charts(self, metrics: Dict[str, Any], timestamp: str = None) -> List[str]:
        """
        Generate relevance analysis charts including scatter plots.
        
        Args:
            metrics: Metrics dictionary containing relevance data
            timestamp: Optional timestamp for file naming
            
        Returns:
            List of generated chart file paths
        """
        print("📊 Generating relevance analysis charts...")
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        generated_files = []
        relevance_data = metrics.get("metric_3_relevance", {})
        
        # 1. Scatter plot for relevance scores
        relevance_scatter_file = self._create_relevance_scatter_plot(
            relevance_data, timestamp
        )
        if relevance_scatter_file:
            generated_files.append(relevance_scatter_file)
        
        # 2. Hospital vs General comparison chart
        comparison_chart_file = self._create_hospital_vs_general_chart(
            relevance_data, timestamp
        )
        if comparison_chart_file:
            generated_files.append(comparison_chart_file)
        
        # 3. Relevance distribution pie chart
        distribution_chart_file = self._create_relevance_distribution_chart(
            relevance_data, timestamp
        )
        if distribution_chart_file:
            generated_files.append(distribution_chart_file)
        
        print(f"✅ Generated {len(generated_files)} relevance charts")
        return generated_files
    
    def generate_coverage_charts(self, metrics: Dict[str, Any], timestamp: str = None) -> List[str]:
        """
        Generate coverage analysis charts showing keyword overlap and completeness.
        
        Args:
            metrics: Metrics dictionary containing coverage data
            timestamp: Optional timestamp for file naming
            
        Returns:
            List of generated chart file paths
        """
        print("📊 Generating coverage analysis charts...")
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        generated_files = []
        coverage_data = metrics.get("metric_4_coverage", {})
        
        # 1. Coverage percentage bar chart
        coverage_percentage_file = self._create_coverage_percentage_chart(
            coverage_data, timestamp
        )
        if coverage_percentage_file:
            generated_files.append(coverage_percentage_file)
        
        # 2. Keyword overlap heatmap
        keyword_heatmap_file = self._create_keyword_overlap_heatmap(
            coverage_data, timestamp
        )
        if keyword_heatmap_file:
            generated_files.append(keyword_heatmap_file)
        
        # 3. Advice completeness gauge chart
        completeness_gauge_file = self._create_completeness_gauge_chart(
            coverage_data, timestamp
        )
        if completeness_gauge_file:
            generated_files.append(completeness_gauge_file)
        
        print(f"✅ Generated {len(generated_files)} coverage charts")
        return generated_files
    
    def generate_comprehensive_dashboard(self, metrics: Dict[str, Any], timestamp: str = None) -> str:
        """
        Generate a comprehensive dashboard combining all key metrics.
        
        Args:
            metrics: Comprehensive metrics dictionary
            timestamp: Optional timestamp for file naming
            
        Returns:
            Path to generated dashboard file
        """
        print("📊 Generating comprehensive metrics dashboard...")
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a large figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle("Hospital Customization Evaluation Dashboard", fontsize=20, fontweight='bold')
        
        # Extract metric data
        latency_data = metrics.get("metric_1_latency", {})
        relevance_data = metrics.get("metric_3_relevance", {})
        coverage_data = metrics.get("metric_4_coverage", {})
        
        # 1. Latency by query type (top-left)
        self._add_latency_subplot(axes[0, 0], latency_data)
        
        # 2. Relevance scores (top-center)
        self._add_relevance_subplot(axes[0, 1], relevance_data)
        
        # 3. Coverage percentage (top-right)
        self._add_coverage_subplot(axes[0, 2], coverage_data)
        
        # 4. Performance summary (bottom-left)
        self._add_summary_subplot(axes[1, 0], metrics.get("summary", {}))
        
        # 5. Trend analysis (bottom-center)
        self._add_trend_subplot(axes[1, 1], latency_data, relevance_data, coverage_data)
        
        # 6. Key insights (bottom-right)
        self._add_insights_subplot(axes[1, 2], metrics)
        
        plt.tight_layout()
        
        # Save dashboard
        dashboard_file = self.output_dir / f"hospital_customization_dashboard_{timestamp}.png"
        plt.savefig(dashboard_file, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Generated comprehensive dashboard: {dashboard_file}")
        return str(dashboard_file)
    
    def _create_latency_by_query_type_chart(self, latency_data: Dict, timestamp: str) -> Optional[str]:
        """Create bar chart showing latency by query type."""
        by_query_type = latency_data.get("by_query_type", {})
        if not by_query_type:
            return None
        
        # Prepare data
        query_types = list(by_query_type.keys())
        mean_times = [data.get("mean", 0) for data in by_query_type.values()]
        std_devs = [data.get("std_dev", 0) for data in by_query_type.values()]
        
        # Create chart
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        bars = ax.bar(query_types, mean_times, yerr=std_devs, 
                     capsize=5, color=[self.colors["primary"], self.colors["secondary"], self.colors["accent"]])
        
        ax.set_title("Latency Analysis by Query Type", fontsize=16, fontweight='bold')
        ax.set_xlabel("Query Specificity", fontsize=12)
        ax.set_ylabel("Execution Time (seconds)", fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, mean_time in zip(bars, mean_times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(std_devs) * 0.1,
                   f'{mean_time:.2f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"latency_by_query_type_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_customization_breakdown_chart(self, latency_data: Dict, timestamp: str) -> Optional[str]:
        """Create pie chart showing customization time breakdown."""
        customization_percentage = latency_data.get("customization_percentage", {})
        if not customization_percentage:
            return None
        
        percentage = customization_percentage.get("percentage", 0)
        
        # Prepare data for pie chart
        labels = ['Hospital Customization', 'Other Processing']
        sizes = [percentage, 100 - percentage]
        colors = [self.colors["accent"], self.colors["light"]]
        explode = (0.1, 0)  # explode the customization slice
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                         autopct='%1.1f%%', shadow=True, startangle=90)
        
        # Style the text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title("Hospital Customization Time Breakdown", fontsize=16, fontweight='bold')
        
        # Add analysis text
        analysis_text = customization_percentage.get("analysis", "")
        plt.figtext(0.5, 0.02, analysis_text, ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"customization_breakdown_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_latency_distribution_chart(self, latency_data: Dict, timestamp: str) -> Optional[str]:
        """Create histogram showing latency distribution."""
        total_execution = latency_data.get("total_execution", {})
        if not total_execution or total_execution.get("count", 0) == 0:
            return None
        
        # Create simulated distribution based on statistics
        mean_time = total_execution.get("mean", 0)
        std_dev = total_execution.get("std_dev", 0)
        min_time = total_execution.get("min", 0)
        max_time = total_execution.get("max", 0)
        
        # Generate synthetic data for visualization
        np.random.seed(42)  # For reproducible results
        synthetic_data = np.random.normal(mean_time, std_dev, 100)
        synthetic_data = np.clip(synthetic_data, min_time, max_time)
        
        # Create chart
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        n, bins, patches = ax.hist(synthetic_data, bins=15, alpha=0.7, color=self.colors["primary"])
        
        # Add mean line
        ax.axvline(mean_time, color=self.colors["accent"], linestyle='--', linewidth=2, label=f'Mean: {mean_time:.2f}s')
        
        ax.set_title("Latency Distribution", fontsize=16, fontweight='bold')
        ax.set_xlabel("Execution Time (seconds)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"latency_distribution_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_relevance_scatter_plot(self, relevance_data: Dict, timestamp: str) -> Optional[str]:
        """Create scatter plot for relevance scores."""
        hospital_content = relevance_data.get("hospital_content", {})
        if not hospital_content or hospital_content.get("count", 0) == 0:
            return None
        
        # Generate synthetic scatter data based on statistics
        mean_score = hospital_content.get("mean", 0)
        std_dev = hospital_content.get("std_dev", 0)
        count = hospital_content.get("count", 10)
        
        np.random.seed(42)
        x_values = np.arange(1, count + 1)
        y_values = np.random.normal(mean_score, std_dev, count)
        y_values = np.clip(y_values, 0, 1)  # Relevance scores should be 0-1
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        scatter = ax.scatter(x_values, y_values, c=y_values, cmap='viridis', 
                           s=100, alpha=0.7, edgecolors='black')
        
        # Add trend line
        z = np.polyfit(x_values, y_values, 1)
        p = np.poly1d(z)
        ax.plot(x_values, p(x_values), color=self.colors["accent"], linestyle='--', linewidth=2)
        
        # Add mean line
        ax.axhline(mean_score, color=self.colors["secondary"], linestyle='-', linewidth=2, 
                  label=f'Mean Relevance: {mean_score:.3f}')
        
        ax.set_title("Hospital Guidelines Relevance Scores", fontsize=16, fontweight='bold')
        ax.set_xlabel("Guideline Index", fontsize=12)
        ax.set_ylabel("Relevance Score", fontsize=12)
        ax.set_ylim(0, 1)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Relevance Score', rotation=270, labelpad=15)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"relevance_scatter_plot_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_hospital_vs_general_chart(self, relevance_data: Dict, timestamp: str) -> Optional[str]:
        """Create comparison chart between hospital and general content relevance."""
        comparison = relevance_data.get("hospital_vs_general_comparison", {})
        if not comparison:
            return None
        
        hospital_avg = comparison.get("hospital_average", 0)
        general_avg = comparison.get("general_average", 0)
        
        # Prepare data
        categories = ['Hospital Content', 'General Content']
        averages = [hospital_avg, general_avg]
        colors = [self.colors["primary"], self.colors["secondary"]]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        bars = ax.bar(categories, averages, color=colors)
        
        # Add value labels
        for bar, avg in zip(bars, averages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{avg:.3f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title("Hospital vs General Content Relevance Comparison", fontsize=16, fontweight='bold')
        ax.set_ylabel("Average Relevance Score", fontsize=12)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
        
        # Add improvement indicator
        improvement = comparison.get("improvement_percentage", 0)
        if improvement != 0:
            improvement_text = f"Hospital content shows {abs(improvement):.1f}% {'improvement' if improvement > 0 else 'decrease'}"
            plt.figtext(0.5, 0.02, improvement_text, ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"hospital_vs_general_comparison_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_relevance_distribution_chart(self, relevance_data: Dict, timestamp: str) -> Optional[str]:
        """Create pie chart showing relevance score distribution."""
        distribution_data = relevance_data.get("relevance_distribution", {})
        if not distribution_data or "distribution" not in distribution_data:
            return None
        
        distribution = distribution_data["distribution"]
        
        # Prepare data
        labels = list(distribution.keys())
        sizes = [item["percentage"] for item in distribution.values()]
        colors = [self.colors["success"], self.colors["accent"], self.colors["primary"]]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                         autopct='%1.1f%%', shadow=True, startangle=90)
        
        # Style the text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title("Relevance Score Distribution", fontsize=16, fontweight='bold')
        
        # Add quality assessment
        quality = distribution_data.get("quality_assessment", "Unknown")
        plt.figtext(0.5, 0.02, f"Overall Quality Assessment: {quality}", 
                   ha='center', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"relevance_distribution_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_coverage_percentage_chart(self, coverage_data: Dict, timestamp: str) -> Optional[str]:
        """Create bar chart showing coverage percentages."""
        keyword_overlap = coverage_data.get("keyword_overlap", {})
        completeness = coverage_data.get("advice_completeness", {})
        concept_coverage = coverage_data.get("medical_concept_coverage", {})
        
        if not any([keyword_overlap, completeness, concept_coverage]):
            return None
        
        # Prepare data
        categories = []
        percentages = []
        
        if keyword_overlap.get("mean"):
            categories.append("Keyword\nOverlap")
            percentages.append(keyword_overlap["mean"])
        
        if completeness.get("mean"):
            categories.append("Advice\nCompleteness")
            percentages.append(completeness["mean"])
        
        if concept_coverage.get("mean"):
            categories.append("Medical Concept\nCoverage")
            percentages.append(concept_coverage["mean"])
        
        if not categories:
            return None
        
        # Create chart
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        bars = ax.bar(categories, percentages, 
                     color=[self.colors["primary"], self.colors["secondary"], self.colors["accent"]])
        
        # Add value labels
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{percentage:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title("Coverage Analysis Metrics", fontsize=16, fontweight='bold')
        ax.set_ylabel("Coverage Percentage", fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"coverage_percentage_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_keyword_overlap_heatmap(self, coverage_data: Dict, timestamp: str) -> Optional[str]:
        """Create heatmap showing keyword overlap patterns."""
        by_query_type = coverage_data.get("by_query_type", {})
        if not by_query_type:
            return None
        
        # Prepare data for heatmap
        query_types = list(by_query_type.keys())
        coverage_means = [data.get("mean", 0) for data in by_query_type.values()]
        
        # Create a simple heatmap-style visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create a matrix for the heatmap
        data_matrix = np.array([coverage_means])
        
        im = ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(query_types)))
        ax.set_xticklabels(query_types)
        ax.set_yticks([0])
        ax.set_yticklabels(['Coverage %'])
        
        # Add text annotations
        for i, coverage in enumerate(coverage_means):
            ax.text(i, 0, f'{coverage:.1f}%', ha='center', va='center', 
                   color='white' if coverage > 50 else 'black', fontweight='bold')
        
        ax.set_title("Keyword Overlap Coverage by Query Type", fontsize=16, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Coverage Percentage', rotation=270, labelpad=15)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"keyword_overlap_heatmap_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _create_completeness_gauge_chart(self, coverage_data: Dict, timestamp: str) -> Optional[str]:
        """Create gauge chart showing advice completeness."""
        completeness = coverage_data.get("advice_completeness", {})
        if not completeness:
            return None
        
        mean_completeness = completeness.get("mean", 0)
        
        # Create gauge chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create the gauge
        theta = np.linspace(0, np.pi, 100)
        
        # Background semicircle
        x_bg = np.cos(theta)
        y_bg = np.sin(theta)
        ax.fill_between(x_bg, 0, y_bg, alpha=0.3, color=self.colors["light"])
        
        # Completeness arc
        completeness_theta = np.linspace(0, np.pi * (mean_completeness / 100), 100)
        x_comp = np.cos(completeness_theta)
        y_comp = np.sin(completeness_theta)
        
        # Color based on completeness level
        if mean_completeness >= 75:
            gauge_color = self.colors["primary"]
        elif mean_completeness >= 50:
            gauge_color = self.colors["accent"]
        else:
            gauge_color = self.colors["success"]
        
        ax.fill_between(x_comp, 0, y_comp, alpha=0.8, color=gauge_color)
        
        # Add percentage text
        ax.text(0, 0.5, f'{mean_completeness:.1f}%', ha='center', va='center', 
               fontsize=24, fontweight='bold')
        ax.text(0, 0.3, 'Completeness', ha='center', va='center', fontsize=14)
        
        # Add scale labels
        for i, pct in enumerate([0, 25, 50, 75, 100]):
            angle = np.pi * (pct / 100)
            x_label = 1.1 * np.cos(angle)
            y_label = 1.1 * np.sin(angle)
            ax.text(x_label, y_label, f'{pct}%', ha='center', va='center', fontsize=10)
        
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-0.2, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title("Medical Advice Completeness Gauge", fontsize=16, fontweight='bold', pad=20)
        
        # Save chart
        chart_file = self.output_dir / f"completeness_gauge_{timestamp}.png"
        plt.savefig(chart_file, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def _add_latency_subplot(self, ax, latency_data: Dict):
        """Add latency subplot to dashboard."""
        by_query_type = latency_data.get("by_query_type", {})
        if not by_query_type:
            ax.text(0.5, 0.5, "No latency data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Latency by Query Type")
            return
        
        query_types = list(by_query_type.keys())
        mean_times = [data.get("mean", 0) for data in by_query_type.values()]
        
        bars = ax.bar(query_types, mean_times, color=self.colors["primary"])
        ax.set_title("Latency by Query Type", fontweight='bold')
        ax.set_ylabel("Seconds")
        
        # Add value labels
        for bar, mean_time in zip(bars, mean_times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(mean_times) * 0.05,
                   f'{mean_time:.1f}s', ha='center', va='bottom', fontsize=8)
    
    def _add_relevance_subplot(self, ax, relevance_data: Dict):
        """Add relevance subplot to dashboard."""
        hospital_content = relevance_data.get("hospital_content", {})
        if not hospital_content:
            ax.text(0.5, 0.5, "No relevance data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Relevance Scores")
            return
        
        mean_score = hospital_content.get("mean", 0)
        
        # Create a simple bar showing relevance
        ax.bar(['Hospital Content'], [mean_score], color=self.colors["secondary"])
        ax.set_title("Average Relevance Score", fontweight='bold')
        ax.set_ylabel("Score")
        ax.set_ylim(0, 1)
        
        # Add value label
        ax.text(0, mean_score + 0.05, f'{mean_score:.3f}', ha='center', va='bottom', fontweight='bold')
    
    def _add_coverage_subplot(self, ax, coverage_data: Dict):
        """Add coverage subplot to dashboard."""
        keyword_overlap = coverage_data.get("keyword_overlap", {})
        if not keyword_overlap:
            ax.text(0.5, 0.5, "No coverage data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Coverage Analysis")
            return
        
        mean_coverage = keyword_overlap.get("mean", 0)
        
        # Create a pie chart showing coverage
        sizes = [mean_coverage, 100 - mean_coverage]
        colors = [self.colors["accent"], self.colors["light"]]
        ax.pie(sizes, labels=['Covered', 'Not Covered'], colors=colors, autopct='%1.1f%%')
        ax.set_title("Keyword Coverage", fontweight='bold')
    
    def _add_summary_subplot(self, ax, summary_data: Dict):
        """Add performance summary subplot to dashboard."""
        if not summary_data:
            ax.text(0.5, 0.5, "No summary data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Performance Summary")
            return
        
        # Display key metrics as text
        ax.axis('off')
        ax.set_title("Performance Summary", fontweight='bold')
        
        summary_text = f"""
Latency: {summary_data.get('latency_performance', 'Unknown')}
Relevance: {summary_data.get('relevance_quality', 'Unknown')}
Coverage: {summary_data.get('coverage_effectiveness', 'Unknown')}

Overall: {summary_data.get('overall_assessment', 'Unknown')}
        """
        
        ax.text(0.1, 0.8, summary_text, transform=ax.transAxes, fontsize=10, 
               verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors["light"]))
    
    def _add_trend_subplot(self, ax, latency_data: Dict, relevance_data: Dict, coverage_data: Dict):
        """Add trend analysis subplot to dashboard."""
        ax.set_title("Performance Trends", fontweight='bold')
        
        # Create a simple trend visualization
        metrics = ['Latency', 'Relevance', 'Coverage']
        values = [
            80 if latency_data.get("total_execution", {}).get("mean", 0) < 60 else 60 if latency_data.get("total_execution", {}).get("mean", 0) < 120 else 40,
            relevance_data.get("hospital_content", {}).get("mean", 0) * 100,
            coverage_data.get("keyword_overlap", {}).get("mean", 0)
        ]
        
        colors = [self.colors["primary"], self.colors["secondary"], self.colors["accent"]]
        ax.bar(metrics, values, color=colors)
        ax.set_ylabel("Performance Score")
        ax.set_ylim(0, 100)
    
    def _add_insights_subplot(self, ax, metrics: Dict):
        """Add key insights subplot to dashboard."""
        ax.axis('off')
        ax.set_title("Key Insights", fontweight='bold')
        
        # Generate insights based on metrics
        insights = []
        
        # Latency insights
        latency_data = metrics.get("metric_1_latency", {})
        if latency_data.get("customization_percentage", {}).get("percentage", 0) > 20:
            insights.append("• High customization overhead detected")
        
        # Relevance insights
        relevance_data = metrics.get("metric_3_relevance", {})
        if relevance_data.get("hospital_content", {}).get("mean", 0) > 0.7:
            insights.append("• Strong hospital content relevance")
        
        # Coverage insights
        coverage_data = metrics.get("metric_4_coverage", {})
        if coverage_data.get("keyword_overlap", {}).get("mean", 0) > 70:
            insights.append("• Comprehensive keyword coverage")
        
        if not insights:
            insights = ["• Evaluation complete", "• Review detailed metrics", "• for comprehensive analysis"]
        
        insights_text = "\n".join(insights)
        ax.text(0.1, 0.8, insights_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors["light"]))


def main():
    """
    Main function for standalone testing of chart generator.
    """
    print("📊 Hospital Customization Chart Generator - Test Mode")
    
    # Load sample metrics for testing
    sample_metrics = {
        "metric_1_latency": {
            "total_execution": {"mean": 45.2, "std_dev": 12.3, "count": 6},
            "by_query_type": {
                "broad": {"mean": 35.1, "std_dev": 8.2},
                "medium": {"mean": 48.7, "std_dev": 10.1},
                "specific": {"mean": 51.8, "std_dev": 15.4}
            },
            "customization_percentage": {"percentage": 18.5}
        },
        "metric_3_relevance": {
            "hospital_content": {"mean": 0.745, "std_dev": 0.123, "count": 12},
            "hospital_vs_general_comparison": {
                "hospital_average": 0.745,
                "general_average": 0.681,
                "improvement_percentage": 9.4
            },
            "relevance_distribution": {
                "distribution": {
                    "low (0-0.3)": {"percentage": 15.0},
                    "medium (0.3-0.7)": {"percentage": 35.0},
                    "high (0.7-1.0)": {"percentage": 50.0}
                },
                "quality_assessment": "High"
            }
        },
        "metric_4_coverage": {
            "keyword_overlap": {"mean": 68.3, "std_dev": 12.7},
            "advice_completeness": {"mean": 78.5, "std_dev": 8.9},
            "medical_concept_coverage": {"mean": 82.1, "std_dev": 7.3},
            "by_query_type": {
                "broad": {"mean": 62.1},
                "medium": {"mean": 71.4},
                "specific": {"mean": 75.8}
            }
        },
        "summary": {
            "latency_performance": "Good",
            "relevance_quality": "High",
            "coverage_effectiveness": "Comprehensive",
            "overall_assessment": "Strong Performance"
        }
    }
    
    # Initialize chart generator
    generator = HospitalCustomizationChartGenerator()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Generate all chart types
        latency_files = generator.generate_latency_charts(sample_metrics, timestamp)
        relevance_files = generator.generate_relevance_charts(sample_metrics, timestamp)
        coverage_files = generator.generate_coverage_charts(sample_metrics, timestamp)
        dashboard_file = generator.generate_comprehensive_dashboard(sample_metrics, timestamp)
        
        print(f"\n✅ Chart generation completed!")
        print(f"📊 Generated {len(latency_files + relevance_files + coverage_files) + 1} charts")
        print(f"📁 Charts saved to: {generator.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during chart generation: {e}")
        return False


if __name__ == "__main__":
    main()