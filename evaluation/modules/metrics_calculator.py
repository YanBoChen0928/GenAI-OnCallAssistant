#!/usr/bin/env python3
"""
Metrics Calculator Module for Hospital Customization Evaluation

This module provides comprehensive metrics calculation for evaluating the performance
of hospital customization in the OnCall.ai RAG system. It focuses on three key metrics:
- Metric 1 (Latency): Total execution time analysis
- Metric 3 (Relevance): Average similarity scores from hospital content
- Metric 4 (Coverage): Keyword overlap between advice and hospital content

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from statistics import mean, median, stdev
from collections import Counter


class HospitalCustomizationMetrics:
    """
    Calculates performance metrics for hospital customization evaluation.
    
    This class provides comprehensive analysis of query execution results,
    focusing on hospital-specific performance indicators.
    """
    
    def __init__(self):
        """Initialize the metrics calculator."""
        self.medical_keywords = self._load_medical_keywords()
    
    def _load_medical_keywords(self) -> List[str]:
        """
        Load medical keywords for coverage analysis.
        
        Returns:
            List of medical keywords and terms
        """
        # Core medical terms for coverage analysis
        keywords = [
            # Symptoms
            "pain", "fever", "nausea", "headache", "fatigue", "weakness", "dyspnea",
            "chest pain", "abdominal pain", "shortness of breath", "dizziness",
            "palpitations", "syncope", "seizure", "confusion", "altered mental status",
            
            # Diagnostics
            "blood pressure", "heart rate", "temperature", "oxygen saturation",
            "blood glucose", "laboratory", "imaging", "ecg", "chest x-ray", "ct scan",
            "mri", "ultrasound", "blood test", "urine test", "culture",
            
            # Treatments
            "medication", "drug", "antibiotic", "analgesic", "antihypertensive",
            "insulin", "oxygen", "iv fluids", "monitoring", "observation",
            "discharge", "admission", "surgery", "procedure", "intervention",
            
            # Medical conditions
            "diabetes", "hypertension", "pneumonia", "sepsis", "myocardial infarction",
            "stroke", "asthma", "copd", "heart failure", "arrhythmia", "pregnancy",
            "trauma", "fracture", "dehydration", "infection", "inflammation",
            
            # Clinical assessment
            "vital signs", "physical examination", "assessment", "diagnosis",
            "differential diagnosis", "risk factors", "contraindications",
            "follow-up", "monitoring", "prognosis", "complications"
        ]
        return keywords
    
    def calculate_latency_metrics(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Metric 1: Latency analysis for hospital customization.
        
        Args:
            query_results: List of query execution results
            
        Returns:
            Dictionary containing comprehensive latency metrics
        """
        latency_data = {
            "total_execution_times": [],
            "customization_times": [],
            "by_query_type": {
                "broad": [],
                "medium": [],
                "specific": []
            },
            "by_category": {}
        }
        
        # Extract latency data from results
        for result in query_results:
            if not result.get("success", False):
                continue
                
            total_time = result["execution_time"]["total_seconds"]
            latency_data["total_execution_times"].append(total_time)
            
            # Extract customization time from processing steps
            customization_time = self._extract_customization_time(result)
            if customization_time is not None:
                latency_data["customization_times"].append(customization_time)
            
            # Group by query specificity
            specificity = result["query_metadata"]["specificity"]
            if specificity in latency_data["by_query_type"]:
                latency_data["by_query_type"][specificity].append(total_time)
            
            # Group by category
            category = result["query_metadata"]["category"]
            if category not in latency_data["by_category"]:
                latency_data["by_category"][category] = []
            latency_data["by_category"][category].append(total_time)
        
        # Calculate statistics
        metrics = {
            "metric_1_latency": {
                "total_execution": self._calculate_statistics(latency_data["total_execution_times"]),
                "customization_only": self._calculate_statistics(latency_data["customization_times"]),
                "by_query_type": {
                    query_type: self._calculate_statistics(times)
                    for query_type, times in latency_data["by_query_type"].items()
                    if times
                },
                "by_category": {
                    category: self._calculate_statistics(times)
                    for category, times in latency_data["by_category"].items()
                    if times
                },
                "customization_percentage": self._calculate_customization_percentage(
                    latency_data["customization_times"], 
                    latency_data["total_execution_times"]
                )
            }
        }
        
        return metrics
    
    def calculate_relevance_metrics(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Metric 3: Relevance analysis based on similarity scores.
        
        Args:
            query_results: List of query execution results
            
        Returns:
            Dictionary containing relevance metrics for hospital content
        """
        relevance_data = {
            "hospital_similarity_scores": [],
            "general_similarity_scores": [],
            "by_query_type": {
                "broad": [],
                "medium": [],
                "specific": []
            },
            "hospital_guidelines_count": [],
            "relevance_distribution": []
        }
        
        # Extract relevance data from results
        for result in query_results:
            if not result.get("success", False):
                continue
            
            # Extract hospital-specific relevance scores
            hospital_scores = self._extract_hospital_relevance_scores(result)
            relevance_data["hospital_similarity_scores"].extend(hospital_scores)
            
            # Extract general guideline scores for comparison
            general_scores = self._extract_general_relevance_scores(result)
            relevance_data["general_similarity_scores"].extend(general_scores)
            
            # Group by query specificity
            specificity = result["query_metadata"]["specificity"]
            if specificity in relevance_data["by_query_type"]:
                relevance_data["by_query_type"][specificity].extend(hospital_scores)
            
            # Count hospital guidelines found
            hospital_count = self._extract_hospital_guidelines_count(result)
            if hospital_count is not None:
                relevance_data["hospital_guidelines_count"].append(hospital_count)
            
            # Collect relevance distribution
            if hospital_scores:
                relevance_data["relevance_distribution"].extend(hospital_scores)
        
        # Calculate metrics
        metrics = {
            "metric_3_relevance": {
                "hospital_content": self._calculate_statistics(relevance_data["hospital_similarity_scores"]),
                "general_content": self._calculate_statistics(relevance_data["general_similarity_scores"]),
                "hospital_vs_general_comparison": self._compare_relevance_scores(
                    relevance_data["hospital_similarity_scores"],
                    relevance_data["general_similarity_scores"]
                ),
                "by_query_type": {
                    query_type: self._calculate_statistics(scores)
                    for query_type, scores in relevance_data["by_query_type"].items()
                    if scores
                },
                "hospital_guidelines_usage": self._calculate_statistics(relevance_data["hospital_guidelines_count"]),
                "relevance_distribution": self._analyze_relevance_distribution(relevance_data["relevance_distribution"])
            }
        }
        
        return metrics
    
    def calculate_coverage_metrics(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate Metric 4: Coverage analysis based on keyword overlap.
        
        Args:
            query_results: List of query execution results
            
        Returns:
            Dictionary containing coverage metrics for hospital customization
        """
        coverage_data = {
            "keyword_overlaps": [],
            "hospital_content_coverage": [],
            "advice_completeness": [],
            "by_query_type": {
                "broad": [],
                "medium": [],
                "specific": []
            },
            "medical_concept_coverage": []
        }
        
        # Analyze coverage for each query result
        for result in query_results:
            if not result.get("success", False):
                continue
            
            # Extract medical advice text
            medical_advice = result["response"].get("medical_advice", "")
            
            # Calculate keyword overlap with hospital content
            hospital_overlap = self._calculate_hospital_keyword_overlap(result, medical_advice)
            coverage_data["keyword_overlaps"].append(hospital_overlap)
            
            # Calculate hospital content coverage
            hospital_coverage = self._calculate_hospital_content_coverage(result)
            if hospital_coverage is not None:
                coverage_data["hospital_content_coverage"].append(hospital_coverage)
            
            # Calculate advice completeness
            completeness = self._calculate_advice_completeness(medical_advice)
            coverage_data["advice_completeness"].append(completeness)
            
            # Group by query specificity
            specificity = result["query_metadata"]["specificity"]
            if specificity in coverage_data["by_query_type"]:
                coverage_data["by_query_type"][specificity].append(hospital_overlap)
            
            # Analyze medical concept coverage
            concept_coverage = self._analyze_medical_concept_coverage(medical_advice)
            coverage_data["medical_concept_coverage"].append(concept_coverage)
        
        # Calculate metrics
        metrics = {
            "metric_4_coverage": {
                "keyword_overlap": self._calculate_statistics(coverage_data["keyword_overlaps"]),
                "hospital_content_coverage": self._calculate_statistics(coverage_data["hospital_content_coverage"]),
                "advice_completeness": self._calculate_statistics(coverage_data["advice_completeness"]),
                "by_query_type": {
                    query_type: self._calculate_statistics(overlaps)
                    for query_type, overlaps in coverage_data["by_query_type"].items()
                    if overlaps
                },
                "medical_concept_coverage": self._calculate_statistics(coverage_data["medical_concept_coverage"]),
                "coverage_analysis": self._analyze_coverage_patterns(coverage_data)
            }
        }
        
        return metrics
    
    def calculate_comprehensive_metrics(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate all metrics for hospital customization evaluation.
        
        Args:
            query_results: List of query execution results
            
        Returns:
            Dictionary containing all calculated metrics
        """
        print("📊 Calculating comprehensive hospital customization metrics...")
        
        # Calculate individual metrics
        latency_metrics = self.calculate_latency_metrics(query_results)
        relevance_metrics = self.calculate_relevance_metrics(query_results)
        coverage_metrics = self.calculate_coverage_metrics(query_results)
        
        # Combine all metrics
        comprehensive_metrics = {
            "evaluation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_queries_analyzed": len(query_results),
                "successful_queries": sum(1 for r in query_results if r.get("success", False)),
                "evaluation_focus": "hospital_customization"
            },
            "metrics": {
                **latency_metrics,
                **relevance_metrics,
                **coverage_metrics
            },
            "summary": self._generate_metrics_summary(latency_metrics, relevance_metrics, coverage_metrics)
        }
        
        return comprehensive_metrics
    
    def _extract_customization_time(self, result: Dict[str, Any]) -> Optional[float]:
        """Extract hospital customization time from processing steps."""
        processing_steps = result["response"].get("processing_steps", "")
        
        # Look for customization time in processing steps
        customization_pattern = r"⏱️ Customization time: ([\d.]+)s"
        match = re.search(customization_pattern, processing_steps)
        
        if match:
            return float(match.group(1))
        return None
    
    def _extract_hospital_relevance_scores(self, result: Dict[str, Any]) -> List[float]:
        """Extract relevance scores specifically from hospital guidelines."""
        scores = []
        
        # Check pipeline analysis for hospital-specific scores
        pipeline_analysis = result.get("pipeline_analysis", {})
        retrieval_info = pipeline_analysis.get("retrieval_info", {})
        
        # Extract scores from confidence_scores if available
        if "confidence_scores" in retrieval_info:
            scores.extend(retrieval_info["confidence_scores"])
        
        # Also parse from guidelines display
        guidelines_display = result["response"].get("guidelines_display", "")
        relevance_pattern = r"Relevance: (\d+)%"
        matches = re.findall(relevance_pattern, guidelines_display)
        
        for match in matches:
            scores.append(float(match) / 100.0)  # Convert percentage to decimal
        
        return scores
    
    def _extract_general_relevance_scores(self, result: Dict[str, Any]) -> List[float]:
        """Extract relevance scores from general (non-hospital) guidelines."""
        # For now, return the same scores - in future this could differentiate
        # between hospital-specific and general guideline scores
        return self._extract_hospital_relevance_scores(result)
    
    def _extract_hospital_guidelines_count(self, result: Dict[str, Any]) -> Optional[int]:
        """Extract the count of hospital guidelines found."""
        pipeline_analysis = result.get("pipeline_analysis", {})
        retrieval_info = pipeline_analysis.get("retrieval_info", {})
        
        return retrieval_info.get("hospital_guidelines", None)
    
    def _calculate_hospital_keyword_overlap(self, result: Dict[str, Any], medical_advice: str) -> float:
        """Calculate keyword overlap between advice and hospital content."""
        if not medical_advice:
            return 0.0
        
        # Convert advice to lowercase for comparison
        advice_lower = medical_advice.lower()
        
        # Count medical keywords present in the advice
        keywords_found = 0
        for keyword in self.medical_keywords:
            if keyword.lower() in advice_lower:
                keywords_found += 1
        
        # Calculate overlap percentage
        total_keywords = len(self.medical_keywords)
        overlap_percentage = (keywords_found / total_keywords) * 100.0
        
        return overlap_percentage
    
    def _calculate_hospital_content_coverage(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate how well hospital content was utilized."""
        pipeline_analysis = result.get("pipeline_analysis", {})
        retrieval_info = pipeline_analysis.get("retrieval_info", {})
        
        hospital_guidelines = retrieval_info.get("hospital_guidelines", 0)
        total_guidelines = retrieval_info.get("guidelines_found", 0)
        
        if total_guidelines == 0:
            return None
        
        # Calculate percentage of hospital guidelines used
        coverage_percentage = (hospital_guidelines / total_guidelines) * 100.0
        return coverage_percentage
    
    def _calculate_advice_completeness(self, medical_advice: str) -> float:
        """Calculate completeness of medical advice based on structure and content."""
        if not medical_advice:
            return 0.0
        
        completeness_score = 0.0
        
        # Check for structured sections (steps, bullet points, etc.)
        if re.search(r"Step \d+:", medical_advice):
            completeness_score += 25.0
        
        # Check for specific medical recommendations
        if any(term in medical_advice.lower() for term in ["recommend", "prescribe", "administer"]):
            completeness_score += 25.0
        
        # Check for diagnostic considerations
        if any(term in medical_advice.lower() for term in ["diagnos", "test", "examination"]):
            completeness_score += 25.0
        
        # Check for follow-up or monitoring instructions
        if any(term in medical_advice.lower() for term in ["follow-up", "monitor", "reassess"]):
            completeness_score += 25.0
        
        return completeness_score
    
    def _analyze_medical_concept_coverage(self, medical_advice: str) -> float:
        """Analyze coverage of key medical concepts in the advice."""
        if not medical_advice:
            return 0.0
        
        advice_lower = medical_advice.lower()
        
        # Key medical concept categories
        concept_categories = {
            "assessment": ["history", "examination", "assessment", "evaluation"],
            "diagnostics": ["test", "laboratory", "imaging", "diagnosis"],
            "treatment": ["treatment", "medication", "intervention", "therapy"],
            "monitoring": ["monitor", "follow-up", "reassess", "observe"]
        }
        
        categories_covered = 0
        for category, terms in concept_categories.items():
            if any(term in advice_lower for term in terms):
                categories_covered += 1
        
        coverage_percentage = (categories_covered / len(concept_categories)) * 100.0
        return coverage_percentage
    
    def _calculate_statistics(self, values: List[float]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for a list of values."""
        if not values:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "sum": 0.0
            }
        
        return {
            "count": len(values),
            "mean": round(mean(values), 3),
            "median": round(median(values), 3),
            "std_dev": round(stdev(values) if len(values) > 1 else 0.0, 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "sum": round(sum(values), 3)
        }
    
    def _calculate_customization_percentage(self, customization_times: List[float], total_times: List[float]) -> Dict[str, Any]:
        """Calculate what percentage of total time is spent on customization."""
        if not customization_times or not total_times:
            return {"percentage": 0.0, "analysis": "No data available"}
        
        avg_customization = mean(customization_times)
        avg_total = mean(total_times)
        
        percentage = (avg_customization / avg_total) * 100.0
        
        return {
            "percentage": round(percentage, 2),
            "avg_customization_time": round(avg_customization, 3),
            "avg_total_time": round(avg_total, 3),
            "analysis": f"Hospital customization accounts for {percentage:.1f}% of total execution time"
        }
    
    def _compare_relevance_scores(self, hospital_scores: List[float], general_scores: List[float]) -> Dict[str, Any]:
        """Compare relevance scores between hospital and general content."""
        if not hospital_scores and not general_scores:
            return {"comparison": "No data available"}
        
        hospital_avg = mean(hospital_scores) if hospital_scores else 0.0
        general_avg = mean(general_scores) if general_scores else 0.0
        
        return {
            "hospital_average": round(hospital_avg, 3),
            "general_average": round(general_avg, 3),
            "difference": round(hospital_avg - general_avg, 3),
            "hospital_better": hospital_avg > general_avg,
            "improvement_percentage": round(((hospital_avg - general_avg) / general_avg * 100), 2) if general_avg > 0 else 0.0
        }
    
    def _analyze_relevance_distribution(self, scores: List[float]) -> Dict[str, Any]:
        """Analyze the distribution of relevance scores."""
        if not scores:
            return {"distribution": "No data available"}
        
        # Create score bins
        bins = {
            "low (0-0.3)": sum(1 for s in scores if 0 <= s <= 0.3),
            "medium (0.3-0.7)": sum(1 for s in scores if 0.3 < s <= 0.7),
            "high (0.7-1.0)": sum(1 for s in scores if 0.7 < s <= 1.0)
        }
        
        total_scores = len(scores)
        distribution = {
            bin_name: {
                "count": count,
                "percentage": round((count / total_scores) * 100, 1)
            }
            for bin_name, count in bins.items()
        }
        
        return {
            "total_scores": total_scores,
            "distribution": distribution,
            "quality_assessment": "High" if bins["high (0.7-1.0)"] > total_scores * 0.5 else "Medium" if bins["medium (0.3-0.7)"] > total_scores * 0.5 else "Low"
        }
    
    def _analyze_coverage_patterns(self, coverage_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze patterns in coverage metrics."""
        patterns = {}
        
        # Analyze keyword overlap patterns
        if coverage_data["keyword_overlaps"]:
            avg_overlap = mean(coverage_data["keyword_overlaps"])
            patterns["keyword_overlap_trend"] = "High" if avg_overlap > 70 else "Medium" if avg_overlap > 40 else "Low"
        
        # Analyze completeness patterns
        if coverage_data["advice_completeness"]:
            avg_completeness = mean(coverage_data["advice_completeness"])
            patterns["completeness_trend"] = "Complete" if avg_completeness > 75 else "Partial" if avg_completeness > 50 else "Incomplete"
        
        return patterns
    
    def _generate_metrics_summary(self, latency_metrics: Dict, relevance_metrics: Dict, coverage_metrics: Dict) -> Dict[str, Any]:
        """Generate a high-level summary of all metrics."""
        summary = {
            "latency_performance": "Unknown",
            "relevance_quality": "Unknown",
            "coverage_effectiveness": "Unknown",
            "overall_assessment": "Unknown",
            "key_findings": []
        }
        
        # Assess latency performance
        if latency_metrics.get("metric_1_latency", {}).get("total_execution", {}).get("mean", 0) < 30:
            summary["latency_performance"] = "Excellent"
        elif latency_metrics.get("metric_1_latency", {}).get("total_execution", {}).get("mean", 0) < 60:
            summary["latency_performance"] = "Good"
        else:
            summary["latency_performance"] = "Needs Improvement"
        
        # Assess relevance quality
        hospital_relevance = relevance_metrics.get("metric_3_relevance", {}).get("hospital_content", {}).get("mean", 0)
        if hospital_relevance > 0.7:
            summary["relevance_quality"] = "High"
        elif hospital_relevance > 0.4:
            summary["relevance_quality"] = "Medium"
        else:
            summary["relevance_quality"] = "Low"
        
        # Assess coverage effectiveness
        coverage_avg = coverage_metrics.get("metric_4_coverage", {}).get("keyword_overlap", {}).get("mean", 0)
        if coverage_avg > 70:
            summary["coverage_effectiveness"] = "Comprehensive"
        elif coverage_avg > 40:
            summary["coverage_effectiveness"] = "Adequate"
        else:
            summary["coverage_effectiveness"] = "Limited"
        
        # Overall assessment
        performance_scores = {
            "Excellent": 3, "High": 3, "Comprehensive": 3,
            "Good": 2, "Medium": 2, "Adequate": 2,
            "Needs Improvement": 1, "Low": 1, "Limited": 1
        }
        
        avg_score = mean([
            performance_scores.get(summary["latency_performance"], 1),
            performance_scores.get(summary["relevance_quality"], 1),
            performance_scores.get(summary["coverage_effectiveness"], 1)
        ])
        
        if avg_score >= 2.5:
            summary["overall_assessment"] = "Strong Performance"
        elif avg_score >= 2.0:
            summary["overall_assessment"] = "Satisfactory Performance"
        else:
            summary["overall_assessment"] = "Performance Improvement Needed"
        
        return summary


def main():
    """
    Main function for standalone testing of metrics calculator.
    """
    print("📊 Hospital Customization Metrics Calculator - Test Mode")
    
    # Load sample results for testing
    results_file = "evaluation/results/single_test_20250804_201434.json"
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        query_results = data.get("query_results", [])
        print(f"📋 Loaded {len(query_results)} query results for analysis")
        
        # Initialize metrics calculator
        calculator = HospitalCustomizationMetrics()
        
        # Calculate comprehensive metrics
        metrics = calculator.calculate_comprehensive_metrics(query_results)
        
        # Display summary
        print("\n📈 Metrics Summary:")
        summary = metrics["summary"]
        print(f"  Latency Performance: {summary['latency_performance']}")
        print(f"  Relevance Quality: {summary['relevance_quality']}")
        print(f"  Coverage Effectiveness: {summary['coverage_effectiveness']}")
        print(f"  Overall Assessment: {summary['overall_assessment']}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Error during metrics calculation: {e}")
        return None


if __name__ == "__main__":
    main()