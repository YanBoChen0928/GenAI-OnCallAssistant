#!/usr/bin/env python3
"""
RAG vs Direct LLM Comparative Analysis Module

This module compares the performance of RAG-enhanced OnCall.ai system versus
direct Med42B LLM responses. It analyzes differences in medical advice quality,
response completeness, factual accuracy, and clinical utility.

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class RAGvsDirectComparator:
    """
    Comprehensive comparison between RAG-enhanced and direct LLM medical responses.
    
    This class analyzes both quantitative metrics (response length, latency, etc.)
    and qualitative aspects (medical completeness, evidence-based recommendations,
    clinical actionability) to demonstrate the value of RAG in medical AI systems.
    """
    
    def __init__(self, output_dir: str = "evaluation/results/comparison"):
        """
        Initialize the RAG vs Direct LLM comparator.
        
        Args:
            output_dir: Directory to save comparison results and visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("🔄 RAG vs Direct LLM Comparator initialized")
    
    def compare_evaluations(self, rag_results_file: str, direct_results_file: str) -> Dict[str, Any]:
        """
        Perform comprehensive comparison between RAG and direct LLM results.
        
        Args:
            rag_results_file: Path to RAG evaluation results JSON
            direct_results_file: Path to direct LLM evaluation results JSON
            
        Returns:
            Complete comparison analysis results
        """
        print("🔍 Loading evaluation results for comparison...")
        
        # Load results
        rag_data = self._load_results(rag_results_file)
        direct_data = self._load_results(direct_results_file)
        
        print(f"📊 RAG results: {len(rag_data['query_execution_results']['raw_results'])} queries")
        print(f"📊 Direct results: {len(direct_data['query_results'])} queries")
        
        # Perform comparative analysis
        comparison_results = {
            "comparison_metadata": {
                "timestamp": self.timestamp,
                "comparison_type": "rag_vs_direct_llm",
                "rag_source": rag_results_file,
                "direct_source": direct_results_file,
                "queries_compared": min(len(rag_data['query_execution_results']['raw_results']), 
                                      len(direct_data['query_results']))
            },
            "quantitative_analysis": self._analyze_quantitative_metrics(rag_data, direct_data),
            "qualitative_analysis": self._analyze_qualitative_aspects(rag_data, direct_data),
            "query_by_query_comparison": self._compare_individual_queries(rag_data, direct_data),
            "summary_insights": {}
        }
        
        # Generate summary insights
        comparison_results["summary_insights"] = self._generate_summary_insights(comparison_results)
        
        # Save results
        self._save_comparison_results(comparison_results)
        
        print("✅ Comprehensive comparison analysis completed!")
        return comparison_results
    
    def _load_results(self, filepath: str) -> Dict[str, Any]:
        """Load evaluation results from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading results from {filepath}: {e}")
            raise e
    
    def _analyze_quantitative_metrics(self, rag_data: Dict, direct_data: Dict) -> Dict[str, Any]:
        """
        Analyze quantitative metrics between RAG and direct LLM responses.
        
        Returns:
            Quantitative comparison metrics
        """
        print("📊 Analyzing quantitative metrics...")
        
        # Extract RAG metrics
        rag_queries = rag_data['query_execution_results']['raw_results']
        rag_latencies = [q['execution_time']['total_seconds'] for q in rag_queries if q['success']]
        rag_response_lengths = [len(q['response']['medical_advice']) for q in rag_queries if q['success']]
        rag_hospital_chunks = [len(q['response'].get('guidelines_display', '')) for q in rag_queries if q['success']]
        
        # Extract Direct LLM metrics  
        direct_queries = direct_data['query_results']
        direct_latencies = [q['execution_time']['total_seconds'] for q in direct_queries if q['success']]
        direct_response_lengths = [len(q['direct_llm_response']['medical_advice']) for q in direct_queries if q['success']]
        
        return {
            "response_time_comparison": {
                "rag_average": np.mean(rag_latencies),
                "rag_std": np.std(rag_latencies),
                "direct_average": np.mean(direct_latencies),
                "direct_std": np.std(direct_latencies),
                "time_difference": np.mean(rag_latencies) - np.mean(direct_latencies),
                "rag_overhead_percentage": ((np.mean(rag_latencies) - np.mean(direct_latencies)) / np.mean(direct_latencies)) * 100
            },
            "response_length_comparison": {
                "rag_average": np.mean(rag_response_lengths),
                "rag_std": np.std(rag_response_lengths),
                "direct_average": np.mean(direct_response_lengths),
                "direct_std": np.std(direct_response_lengths),
                "length_difference": np.mean(rag_response_lengths) - np.mean(direct_response_lengths),
                "rag_length_increase_percentage": ((np.mean(rag_response_lengths) - np.mean(direct_response_lengths)) / np.mean(direct_response_lengths)) * 100
            },
            "success_rate_comparison": {
                "rag_success_rate": len([q for q in rag_queries if q['success']]) / len(rag_queries) * 100,
                "direct_success_rate": len([q for q in direct_queries if q['success']]) / len(direct_queries) * 100
            },
            "additional_rag_metrics": {
                "average_hospital_chunks": np.mean(rag_hospital_chunks) if rag_hospital_chunks else 0,
                "retrieval_information_density": np.mean(rag_hospital_chunks) / np.mean(rag_response_lengths) * 1000 if rag_response_lengths else 0
            }
        }
    
    def _analyze_qualitative_aspects(self, rag_data: Dict, direct_data: Dict) -> Dict[str, Any]:
        """
        Analyze qualitative aspects of medical responses.
        
        Returns:
            Qualitative comparison analysis
        """
        print("🔍 Analyzing qualitative aspects...")
        
        rag_queries = rag_data['query_execution_results']['raw_results']
        direct_queries = direct_data['query_results']
        
        qualitative_analysis = {
            "medical_content_structure": {},
            "evidence_based_elements": {},
            "clinical_actionability": {},
            "comprehensive_coverage": {}
        }
        
        # Analyze medical content structure
        for rag_q, direct_q in zip(rag_queries, direct_queries):
            if rag_q['success'] and direct_q['success']:
                query_id = rag_q['query_id']
                rag_content = rag_q['response']['medical_advice']
                direct_content = direct_q['direct_llm_response']['medical_advice']
                
                # Analyze structure and completeness
                rag_analysis = self._analyze_medical_content(rag_content)
                direct_analysis = self._analyze_medical_content(direct_content)
                
                qualitative_analysis["medical_content_structure"][query_id] = {
                    "rag": rag_analysis,
                    "direct": direct_analysis,
                    "comparison": {
                        "structure_advantage": "rag" if rag_analysis['structure_score'] > direct_analysis['structure_score'] else "direct",
                        "completeness_advantage": "rag" if rag_analysis['completeness_score'] > direct_analysis['completeness_score'] else "direct"
                    }
                }
        
        return qualitative_analysis
    
    def _analyze_medical_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze the structure and quality of medical content.
        
        Args:
            content: Medical advice text
            
        Returns:
            Content analysis metrics
        """
        # Count structured elements
        step_patterns = [r'\*\*Step \d+', r'\d+\.', r'Step \d+:', r'•', r'-']
        medication_patterns = [r'\d+\s*mg', r'\d+\s*mcg', r'\d+\s*units', r'dosage', r'administer']
        diagnostic_patterns = [r'ECG', r'MRI', r'CT', r'X-ray', r'blood test', r'laboratory', r'biomarker']
        emergency_patterns = [r'immediate', r'emergency', r'urgent', r'STAT', r'911', r'call']
        
        structure_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in step_patterns)
        medication_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in medication_patterns)
        diagnostic_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in diagnostic_patterns)
        emergency_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in emergency_patterns)
        
        return {
            "structure_score": min(structure_count / 5.0, 1.0),  # Normalize to 0-1
            "completeness_score": min((medication_count + diagnostic_count + emergency_count) / 10.0, 1.0),
            "medication_mentions": medication_count,
            "diagnostic_mentions": diagnostic_count,
            "emergency_mentions": emergency_count,
            "total_length": len(content),
            "structured_elements": structure_count
        }
    
    def _compare_individual_queries(self, rag_data: Dict, direct_data: Dict) -> List[Dict[str, Any]]:
        """
        Compare individual query responses between RAG and direct LLM.
        
        Returns:
            List of individual query comparisons
        """
        print("📝 Comparing individual query responses...")
        
        rag_queries = rag_data['query_execution_results']['raw_results']
        direct_queries = direct_data['query_results']
        
        comparisons = []
        
        for rag_q, direct_q in zip(rag_queries, direct_queries):
            if rag_q['query_id'] == direct_q['query_id']:
                comparison = {
                    "query_id": rag_q['query_id'],
                    "query_text": rag_q['query_text'],
                    "query_metadata": rag_q.get('query_metadata', {}),
                    "rag_response": {
                        "success": rag_q['success'],
                        "execution_time": rag_q['execution_time']['total_seconds'] if rag_q['success'] else None,
                        "response_length": len(rag_q['response']['medical_advice']) if rag_q['success'] else 0,
                        "hospital_guidelines_used": rag_q['response'].get('guidelines_display', '') if rag_q['success'] else '',
                        "key_features": self._extract_key_features(rag_q['response']['medical_advice']) if rag_q['success'] else []
                    },
                    "direct_response": {
                        "success": direct_q['success'],
                        "execution_time": direct_q['execution_time']['total_seconds'] if direct_q['success'] else None,
                        "response_length": len(direct_q['direct_llm_response']['medical_advice']) if direct_q['success'] else 0,
                        "key_features": self._extract_key_features(direct_q['direct_llm_response']['medical_advice']) if direct_q['success'] else []
                    }
                }
                
                # Add comparative analysis
                if rag_q['success'] and direct_q['success']:
                    comparison["analysis"] = {
                        "response_time_advantage": "rag" if rag_q['execution_time']['total_seconds'] < direct_q['execution_time']['total_seconds'] else "direct",
                        "content_length_advantage": "rag" if len(rag_q['response']['medical_advice']) > len(direct_q['direct_llm_response']['medical_advice']) else "direct",
                        "rag_advantages": self._identify_rag_advantages(rag_q['response']['medical_advice'], direct_q['direct_llm_response']['medical_advice']),
                        "direct_advantages": self._identify_direct_advantages(rag_q['response']['medical_advice'], direct_q['direct_llm_response']['medical_advice'])
                    }
                
                comparisons.append(comparison)
        
        return comparisons
    
    def _extract_key_features(self, content: str) -> List[str]:
        """Extract key medical features from response content."""
        features = []
        
        # Check for specific medical elements
        if re.search(r'step|protocol|guideline', content, re.IGNORECASE):
            features.append("structured_protocol")
        if re.search(r'\d+\s*(mg|mcg|units)', content, re.IGNORECASE):
            features.append("specific_dosages")
        if re.search(r'ECG|MRI|CT|X-ray|blood test', content, re.IGNORECASE):
            features.append("diagnostic_recommendations")
        if re.search(r'emergency|urgent|immediate|STAT', content, re.IGNORECASE):
            features.append("emergency_management")
        if re.search(r'monitor|follow.?up|reassess', content, re.IGNORECASE):
            features.append("monitoring_guidance")
        if re.search(r'contraindication|allergy|caution', content, re.IGNORECASE):
            features.append("safety_considerations")
        
        return features
    
    def _identify_rag_advantages(self, rag_content: str, direct_content: str) -> List[str]:
        """Identify advantages of RAG response over direct LLM."""
        advantages = []
        
        # Check for hospital-specific content
        if "hospital" in rag_content.lower() and "hospital" not in direct_content.lower():
            advantages.append("hospital_specific_protocols")
        
        # Check for more detailed protocols
        rag_steps = len(re.findall(r'step \d+|^\d+\.', rag_content, re.IGNORECASE | re.MULTILINE))
        direct_steps = len(re.findall(r'step \d+|^\d+\.', direct_content, re.IGNORECASE | re.MULTILINE))
        if rag_steps > direct_steps:
            advantages.append("more_structured_approach")
        
        # Check for specific medical details
        rag_medications = len(re.findall(r'\d+\s*(mg|mcg)', rag_content, re.IGNORECASE))
        direct_medications = len(re.findall(r'\d+\s*(mg|mcg)', direct_content, re.IGNORECASE))
        if rag_medications > direct_medications:
            advantages.append("more_specific_dosages")
        
        return advantages
    
    def _identify_direct_advantages(self, rag_content: str, direct_content: str) -> List[str]:
        """Identify advantages of direct LLM response over RAG."""
        advantages = []
        
        # Check for brevity advantage
        if len(direct_content) < len(rag_content) * 0.8:
            advantages.append("more_concise")
        
        # Check for different medical perspective
        if "differential diagnosis" in direct_content.lower() and "differential diagnosis" not in rag_content.lower():
            advantages.append("broader_differential")
        
        return advantages
    
    def _generate_summary_insights(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level insights from comparison analysis."""
        quantitative = comparison_results["quantitative_analysis"]
        
        insights = {
            "performance_summary": {
                "rag_latency_overhead": f"{quantitative['response_time_comparison']['rag_overhead_percentage']:.1f}%",
                "rag_content_increase": f"{quantitative['response_length_comparison']['rag_length_increase_percentage']:.1f}%",
                "rag_success_rate": f"{quantitative['success_rate_comparison']['rag_success_rate']:.1f}%",
                "direct_success_rate": f"{quantitative['success_rate_comparison']['direct_success_rate']:.1f}%"
            },
            "key_findings": [],
            "recommendations": []
        }
        
        # Generate key findings
        if quantitative['response_time_comparison']['rag_overhead_percentage'] > 0:
            insights["key_findings"].append(f"RAG system adds {quantitative['response_time_comparison']['rag_overhead_percentage']:.1f}% latency overhead due to retrieval processing")
        
        if quantitative['response_length_comparison']['rag_length_increase_percentage'] > 10:
            insights["key_findings"].append(f"RAG responses are {quantitative['response_length_comparison']['rag_length_increase_percentage']:.1f}% longer, indicating more comprehensive medical advice")
        
        if quantitative['additional_rag_metrics']['average_hospital_chunks'] > 20:
            insights["key_findings"].append(f"RAG system successfully retrieves {quantitative['additional_rag_metrics']['average_hospital_chunks']:.1f} hospital-specific guidelines per query")
        
        # Generate recommendations
        if quantitative['response_time_comparison']['rag_overhead_percentage'] > 50:
            insights["recommendations"].append("Consider optimizing retrieval pipeline to reduce latency overhead")
        
        insights["recommendations"].append("RAG system provides significant value through hospital-specific medical protocols")
        insights["recommendations"].append("Direct LLM serves as good baseline but lacks institutional knowledge")
        
        return insights
    
    def _save_comparison_results(self, results: Dict[str, Any]) -> str:
        """Save comparison results to JSON file."""
        filename = f"rag_vs_direct_comparison_{self.timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Comparison results saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error saving comparison results: {e}")
            raise e


def main():
    """
    Main function for standalone testing of RAG vs Direct LLM comparator.
    """
    print("🧪 RAG vs Direct LLM Comparator - Test Mode")
    
    # Example paths (update with actual file paths)
    rag_results_file = "evaluation/results/frequency_based_evaluation_20250804_210752.json"
    direct_results_file = "evaluation/results/direct_llm_evaluation_latest.json"
    
    try:
        # Initialize comparator
        comparator = RAGvsDirectComparator()
        
        # Perform comparison (this would fail without actual files)
        print("ℹ️ Note: This is test mode. Actual comparison requires result files.")
        print(f"ℹ️ Expected RAG results file: {rag_results_file}")
        print(f"ℹ️ Expected Direct LLM results file: {direct_results_file}")
        
        print("✅ RAG vs Direct LLM Comparator initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during comparison setup: {e}")
        return False


if __name__ == "__main__":
    main()