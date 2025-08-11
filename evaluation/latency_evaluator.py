#!/usr/bin/env python3
"""
OnCall.ai System - Comprehensive Evaluator (Metrics 1-8)
========================================================

Single execution to collect all metrics 1-4 data from app.py pipeline.
Generates foundation data for metrics 5-8 evaluation in downstream processors.

COMPLETE METRICS OVERVIEW:

PIPELINE PERFORMANCE METRICS (Collected by this evaluator):
1. Total Latency (總處理時長) - Complete pipeline processing time from query to response
2. Condition Extraction Success Rate (條件抽取成功率) - Success rate of user_prompt.py condition extraction
3. Retrieval Relevance (檢索相關性) - Average cosine similarity scores from retrieval.py results
4. Retrieval Coverage (檢索覆蓋率) - Medical keyword utilization rate between retrieved content and generated advice

LLM JUDGE METRICS (Processed by metric5_6_llm_judge_evaluator.py):
5. Clinical Actionability (臨床可操作性) - Third-party LLM evaluation of medical advice actionability (1-10 scale)
   * Uses batch evaluation strategy with Llama3-70B as judge
   * Measures: Can healthcare providers immediately act on this advice?
   * Target threshold: ≥7.0/10 for acceptable actionability
   
6. Clinical Evidence Quality (臨床證據品質) - Third-party LLM evaluation of evidence-based quality (1-10 scale)
   * Uses same batch evaluation call as metric 5 for efficiency
   * Measures: Is the advice evidence-based and follows medical standards?
   * Target threshold: ≥7.5/10 for acceptable evidence quality

RETRIEVAL PRECISION METRICS (Processed by metric7_8_precision_MRR.py):
7. Precision@K (檢索精確率) - Proportion of relevant results in top-K retrieval results
   * Uses adaptive threshold based on query complexity (0.15 for complex, 0.25 for simple queries)
   * Query complexity determined by unique emergency keywords count (≥4 = complex)
   * Measures: relevant_results / total_retrieved_results
   
8. Mean Reciprocal Rank (平均倒數排名) - Average reciprocal rank of first relevant result
   * Uses same adaptive threshold as Precision@K
   * Measures: 1 / rank_of_first_relevant_result (0 if no relevant results)
   * Higher MRR indicates relevant results appear earlier in ranking

DATA FLOW ARCHITECTURE:
1. latency_evaluator.py → comprehensive_details_*.json (metrics 1-4 + pipeline data)
2. latency_evaluator.py → medical_outputs_*.json (medical advice for judge evaluation)
3. metric5_6_llm_judge_evaluator.py → judge_evaluation_*.json (metrics 5-6)
4. metric7_8_precision_MRR.py → precision_mrr_analysis_*.json (metrics 7-8)

Note: This evaluator focuses on metrics 1-4 collection. Metrics 5-8 require separate downstream evaluation.

Author: YanBo Chen  
Date: 2025-08-04
"""

import time
import json
import os
import sys
from typing import Dict, List, Any, Set
from datetime import datetime
from pathlib import Path
import re

# Add project path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import existing system components
try:
    from user_prompt import UserPromptProcessor
    from retrieval import BasicRetrievalSystem
    from llm_clients import llm_Med42_70BClient
    from generation import MedicalAdviceGenerator
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure running from project root directory")
    sys.exit(1)


class ComprehensiveEvaluator:
    """Comprehensive evaluator for metrics 1-4 - single execution approach"""
    
    def __init__(self):
        """Initialize system components (identical to app.py)"""
        print("🔧 Initializing Comprehensive Evaluator...")
        
        # Initialize existing system components (same as app.py)
        self.llm_client = llm_Med42_70BClient()
        self.retrieval_system = BasicRetrievalSystem()
        self.user_prompt_processor = UserPromptProcessor(
            llm_client=self.llm_client,
            retrieval_system=self.retrieval_system
        )
        self.medical_generator = MedicalAdviceGenerator(llm_client=self.llm_client)
        
        # Results accumulation for all metrics
        self.comprehensive_results = []
        self.medical_outputs = []
        
        print("✅ Comprehensive Evaluator initialization complete")
    
    def extract_medical_keywords(self, text: str) -> Set[str]:
        """Extract medical keywords for coverage analysis"""
        if not text:
            return set()
        
        medical_keywords = set()
        text_lower = text.lower()
        
        # Medical terminology patterns
        patterns = [
            r'\b[a-z]+(?:osis|itis|pathy|emia|uria|gram|scopy)\b',  # Medical suffixes
            r'\b(?:cardio|neuro|pulmo|gastro|hepato|nephro)[a-z]+\b',  # Medical prefixes
            r'\b(?:diagnosis|treatment|therapy|intervention|management)\b',  # Medical actions
            r'\b(?:patient|symptom|condition|disease|disorder|syndrome)\b',  # Medical entities
            r'\b(?:acute|chronic|severe|mild|moderate|emergency)\b',  # Medical descriptors
            r'\b[a-z]+(?:al|ic|ous|ive)\s+(?:pain|failure|infection|injury)\b',  # Compound terms
            r'\b(?:ecg|ekg|ct|mri|x-ray|ultrasound|biopsy)\b',  # Medical procedures
            r'\b\d+\s*(?:mg|ml|units|hours|days|minutes)\b',  # Dosages and timeframes
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            medical_keywords.update(match.strip() for match in matches)
        
        # Additional common medical terms
        common_medical_terms = [
            'blood', 'pressure', 'heart', 'chest', 'pain', 'stroke', 'seizure',
            'emergency', 'hospital', 'monitor', 'assess', 'evaluate', 'immediate',
            'protocol', 'guideline', 'recommendation', 'risk', 'factor'
        ]
        
        for term in common_medical_terms:
            if term in text_lower:
                medical_keywords.add(term)
        
        # Filter out very short terms and common words
        filtered_keywords = {
            kw for kw in medical_keywords 
            if len(kw) > 2 and kw not in ['the', 'and', 'for', 'with', 'are', 'can', 'may']
        }
        
        return filtered_keywords
    
    def calculate_coverage_metrics(self, generated_advice: str, retrieval_results: List[Dict]) -> Dict[str, Any]:
        """Calculate coverage metrics from generated advice and retrieval results"""
        if not generated_advice or not retrieval_results:
            return {
                "coverage_score": 0.0,
                "matched_keywords": [],
                "advice_keywords": [],
                "source_keywords": [],
                "coverage_percentage": 0.0,
                "meets_threshold": False
            }
        
        # Extract keywords from generated advice
        advice_keywords = self.extract_medical_keywords(generated_advice)
        
        # Extract keywords from all retrieved documents
        all_source_keywords = set()
        for doc in retrieval_results:
            doc_content = doc.get('content', '') or doc.get('text', '')
            doc_keywords = self.extract_medical_keywords(doc_content)
            all_source_keywords.update(doc_keywords)
        
        # Calculate coverage
        matched_keywords = advice_keywords.intersection(all_source_keywords)
        coverage_score = len(matched_keywords) / len(all_source_keywords) if all_source_keywords else 0.0
        
        return {
            "coverage_score": coverage_score,
            "matched_keywords": list(matched_keywords),
            "advice_keywords": list(advice_keywords),
            "source_keywords": list(all_source_keywords),
            "advice_keywords_count": len(advice_keywords),
            "source_keywords_count": len(all_source_keywords),
            "matched_keywords_count": len(matched_keywords),
            "coverage_percentage": coverage_score * 100,
            "meets_threshold": coverage_score >= 0.4
        }
    
    def evaluate_single_query_comprehensive(self, query: str, category: str = "unknown") -> Dict[str, Any]:
        """
        Comprehensive evaluation for single query - collects all metrics 1-4 data
        
        Replicates app.py's process_medical_query pipeline exactly
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"🔍 Comprehensive evaluation: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        overall_start = time.time()
        timing_details = {}
        
        try:
            # STEP 1: Query Processing and Condition Extraction (identical to app.py)
            step1_start = time.time()
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            step1_time = time.time() - step1_start
            timing_details['step1_condition_extraction'] = step1_time
            
            print(f"   Step 1 - Condition extraction: {step1_time:.3f}s")
            print(f"   Extracted condition: {condition_result.get('condition', 'None')}")
            
            # Check if valid medical query
            if condition_result.get('query_status') in ['invalid_query', 'non_medical']:
                total_time = time.time() - overall_start
                return self._create_failed_result(query, category, total_time, timing_details, 
                                                "non_medical", condition_result)
            
            # STEP 2: User Confirmation (simulate auto-confirmation)
            step2_start = time.time()
            confirmation = self.user_prompt_processor.handle_user_confirmation(condition_result)
            step2_time = time.time() - step2_start
            timing_details['step2_confirmation'] = step2_time
            
            if not condition_result.get('condition'):
                total_time = time.time() - overall_start
                return self._create_failed_result(query, category, total_time, timing_details,
                                                "no_condition", condition_result)
            
            # STEP 3: Medical Guidelines Retrieval (identical to app.py)
            step3_start = time.time()
            
            search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
            if not search_query:
                search_query = condition_result.get('condition', query)
            
            retrieval_results = self.retrieval_system.search(search_query, top_k=5)
            step3_time = time.time() - step3_start
            timing_details['step3_retrieval'] = step3_time
            
            processed_results = retrieval_results.get('processed_results', [])
            print(f"   Step 3 - Retrieval: {step3_time:.3f}s ({len(processed_results)} results)")
            
            # STEP 4: Medical Advice Generation (identical to app.py)
            step4_start = time.time()
            
            intention = self._detect_query_intention(query)
            medical_advice_result = self.medical_generator.generate_medical_advice(
                user_query=query,
                retrieval_results=retrieval_results,
                intention=intention
            )
            step4_time = time.time() - step4_start
            timing_details['step4_generation'] = step4_time
            
            generated_advice = medical_advice_result.get('medical_advice', '')
            confidence_score = medical_advice_result.get('confidence_score', 0.0)
            
            print(f"   Step 4 - Generation: {step4_time:.3f}s")
            
            total_time = time.time() - overall_start
            
            # METRIC 2: Condition Extraction Analysis
            extraction_success = (
                condition_result.get('condition') and
                condition_result.get('condition') != "unknown" and
                condition_result.get('query_status') not in ['invalid_query', 'non_medical']
            )
            
            extraction_metrics = {
                "extraction_success": extraction_success,
                "extracted_condition": condition_result.get('condition'),
                "query_status": condition_result.get('query_status'),
                "emergency_keywords": condition_result.get('emergency_keywords', []),
                "treatment_keywords": condition_result.get('treatment_keywords', []),
                "fallback_level": condition_result.get('fallback_level', 'unknown'),
                "extraction_time": step1_time
            }
            
            # METRIC 3: Retrieval Relevance Analysis
            if processed_results:
                relevance_scores = []
                for doc_result in processed_results:
                    # Get angular distance and convert to relevance using correct formula
                    distance = doc_result.get('distance', 1.0)
                    relevance = 1.0 - (distance**2) / 2.0  # Correct mathematical conversion
                    relevance_scores.append(relevance)
                
                average_relevance = sum(relevance_scores) / len(relevance_scores)
                high_relevance_count = sum(1 for score in relevance_scores if score >= 0.85)
                
                relevance_metrics = {
                    "average_relevance": average_relevance,
                    "max_relevance": max(relevance_scores),
                    "min_relevance": min(relevance_scores),
                    "relevance_scores": relevance_scores,
                    "high_relevance_count": high_relevance_count,
                    "high_relevance_ratio": high_relevance_count / len(relevance_scores),
                    "retrieved_count": len(processed_results),
                    "meets_threshold": average_relevance >= 0.85,
                    "retrieval_time": step3_time
                }
            else:
                relevance_metrics = {
                    "average_relevance": 0.0,
                    "max_relevance": 0.0,
                    "min_relevance": 0.0,
                    "similarity_scores": [],
                    "high_relevance_count": 0,
                    "high_relevance_ratio": 0.0,
                    "retrieved_count": 0,
                    "meets_threshold": False,
                    "retrieval_time": step3_time
                }
            
            # METRIC 4: Retrieval Coverage Analysis
            coverage_metrics = self.calculate_coverage_metrics(generated_advice, processed_results)
            coverage_metrics["generation_time"] = step4_time
            
            # Create comprehensive result
            comprehensive_result = {
                "query": query,
                "category": category,
                
                # Metric 1: Total Latency - Complete pipeline processing time
                "latency_metrics": {
                    "total_latency": total_time,
                    "timing_details": timing_details,
                    "meets_target": total_time <= 60.0
                },
                
                # Metric 2: Condition Extraction - Success rate from user_prompt.py
                "extraction_metrics": extraction_metrics,
                
                # Metric 3: Retrieval Relevance - Cosine similarity from retrieval.py  
                "relevance_metrics": relevance_metrics,
                
                # Metric 4: Retrieval Coverage - Advice utilization of retrieved content
                "coverage_metrics": coverage_metrics,
                
                # Complete pipeline data (for debugging and detailed analysis)
                "pipeline_data": {
                    "condition_result": condition_result,
                    "retrieval_results": retrieval_results,
                    "medical_advice_result": medical_advice_result,
                    "search_query": search_query,
                    "intention": intention
                },
                
                "overall_success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Validate data completeness for metrics 7-8 analysis
            ready = True
            data = comprehensive_result.get('pipeline_data', {})
            
            # 1. Check retrieval results completeness for precision/MRR calculation
            retr = data.get('retrieval_results', {}).get('processed_results', [])
            if not retr or 'distance' not in retr[0]:
                ready = False
            
            # 2. Check condition extraction completeness for complexity analysis
            cond = data.get('condition_result', {}).get('condition')
            if not cond:
                ready = False
            
            # 3. Check overall execution status
            if not comprehensive_result.get('overall_success', False):
                ready = False
            
            # 4. Check retrieval timing data completeness
            if 'retrieval_time' not in comprehensive_result.get('relevance_metrics', {}):
                ready = False
            
            # Set metrics 7-8 readiness flag for downstream precision/MRR analysis
            comprehensive_result['precision_mrr_ready'] = ready
            
            # Store result
            self.comprehensive_results.append(comprehensive_result)
            
            # Store medical output for model comparison
            medical_output = {
                "query": query,
                "category": category,
                "medical_advice": generated_advice,
                "confidence_score": confidence_score,
                "query_id": f"{category}_query",
                "processing_time": total_time,
                "timestamp": datetime.now().isoformat()
            }
            self.medical_outputs.append(medical_output)
            
            print(f"✅ Comprehensive evaluation completed in {total_time:.2f}s")
            print(f"   📊 Metrics: Latency={total_time:.2f}s, Extraction={'✅' if extraction_success else '❌'}, "
                  f"Relevance={average_relevance:.3f}, Coverage={coverage_metrics['coverage_score']:.3f}")
            
            return comprehensive_result
            
        except Exception as e:
            total_time = time.time() - overall_start
            print(f"❌ Comprehensive evaluation failed after {total_time:.2f}s: {e}")
            
            return self._create_failed_result(query, category, total_time, timing_details, "error", None, str(e))
    
    def _create_failed_result(self, query: str, category: str, total_time: float, 
                            timing_details: Dict, status: str, condition_result: Dict = None, 
                            error: str = None) -> Dict[str, Any]:
        """Create standardized failed result"""
        failed_result = {
            "query": query,
            "category": category,
            
            # Metric 1: Total Latency - Always measurable even on failure
            "latency_metrics": {
                "total_latency": total_time,
                "timing_details": timing_details,
                "meets_target": total_time <= 60.0
            },
            
            # Metric 2: Condition Extraction - Partial data may be available before failure
            "extraction_metrics": {
                "extraction_success": False,
                "extracted_condition": condition_result.get('condition') if condition_result else None,
                "query_status": condition_result.get('query_status') if condition_result else status,
                "extraction_time": timing_details.get('step1_condition_extraction', 0.0)
            },
            
            # Metric 3: Retrieval Relevance - Failed due to pipeline failure
            "relevance_metrics": {
                "average_relevance": 0.0,
                "retrieved_count": 0,
                "meets_threshold": False,
                "retrieval_time": timing_details.get('step3_retrieval', 0.0)
            },
            
            # Metric 4: Retrieval Coverage - Failed due to pipeline failure  
            "coverage_metrics": {
                "coverage_score": 0.0,
                "meets_threshold": False,
                "generation_time": timing_details.get('step4_generation', 0.0)
            },
            
            # Note: Metrics 5-6 (Clinical Actionability & Evidence Quality) 
            # are collected by metric5_6_llm_judge_evaluator.py using medical_outputs
            # Metrics 7-8 (Precision@K & MRR) are collected by metric7_8_precision_MRR.py 
            # using comprehensive_details pipeline data
            
            "overall_success": False,
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        # For failed results, precision/MRR analysis data is not ready
        failed_result['precision_mrr_ready'] = False
        
        self.comprehensive_results.append(failed_result)
        return failed_result
    
    def _detect_query_intention(self, query: str) -> str:
        """Simplified query intention detection (from app.py)"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['diagnos', 'differential', 'possible', 'causes']):
            return 'diagnosis'
        elif any(word in query_lower for word in ['treat', 'manage', 'therapy', 'intervention']):
            return 'treatment'
        else:
            return 'mixed'    
    def parse_queries_from_file(self, filepath: str) -> Dict[str, List[Dict]]:
        """Parse queries from file with category labels"""
        print(f"📁 Reading queries from file: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse queries with category labels
            queries_by_category = {
                "diagnosis": [],
                "treatment": [], 
                "mixed": []
            }
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse format: "1.diagnosis: query text"
                match = re.match(r'^\d+\.(diagnosis|treatment|mixed/complicated|mixed):\s*(.+)', line, re.IGNORECASE)
                if match:
                    category_raw = match.group(1).lower()
                    query_text = match.group(2).strip()
                    
                    # Normalize category name
                    if category_raw in ['mixed/complicated', 'mixed']:
                        category = 'mixed'
                    else:
                        category = category_raw
                    
                    if category in queries_by_category and len(query_text) > 15:
                        queries_by_category[category].append({
                            "text": query_text,
                            "category": category
                        })
            
            print(f"📋 Parsed queries by category:")
            for category, category_queries in queries_by_category.items():
                print(f"  {category.capitalize()}: {len(category_queries)} queries")
            
            return queries_by_category
            
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return {"error": f"Failed to read file: {e}"}
    
    def calculate_metric_statistics(self, metric_name: str) -> Dict[str, Any]:
        """Calculate statistics for a specific metric across all results"""
        category_stats = {}
        all_successful_results = []
        
        # Group results by category
        results_by_category = {
            "diagnosis": [],
            "treatment": [],
            "mixed": []
        }
        
        for result in self.comprehensive_results:
            category = result.get('category', 'unknown')
            if category in results_by_category:
                results_by_category[category].append(result)
                if result.get('overall_success'):
                    all_successful_results.append(result)
        
        # Calculate statistics for each category based on metric type
        for category, results in results_by_category.items():
            successful_results = [r for r in results if r.get('overall_success')]
            
            if metric_name == "latency":
                if successful_results:
                    latencies = [r['latency_metrics']['total_latency'] for r in successful_results]
                    category_stats[category] = {
                        "average_latency": sum(latencies) / len(latencies),
                        "std_deviation": self._calculate_std(latencies),
                        "min_latency": min(latencies),
                        "max_latency": max(latencies),
                        "query_count": len(latencies),
                        "target_compliance": sum(1 for lat in latencies if lat <= 60.0) / len(latencies),
                        "individual_latencies": latencies
                    }
                else:
                    category_stats[category] = self._get_empty_latency_stats()
            
            elif metric_name == "extraction":
                extraction_successes = [r['extraction_metrics']['extraction_success'] for r in results]
                successful_extractions = sum(extraction_successes)
                
                category_stats[category] = {
                    "success_rate": successful_extractions / len(results) if results else 0.0,
                    "successful_count": successful_extractions,
                    "total_count": len(results),
                    "average_extraction_time": sum(r['extraction_metrics']['extraction_time'] for r in results) / len(results) if results else 0.0,
                    "meets_threshold": (successful_extractions / len(results)) >= 0.8 if results else False
                }
            
            elif metric_name == "relevance":
                if successful_results:
                    relevance_scores = [r['relevance_metrics']['average_relevance'] for r in successful_results]
                    category_stats[category] = {
                        "average_relevance": sum(relevance_scores) / len(relevance_scores),
                        "max_relevance": max(relevance_scores),
                        "min_relevance": min(relevance_scores),
                        "successful_retrievals": len(successful_results),
                        "total_queries": len(results),
                        "meets_threshold": (sum(relevance_scores) / len(relevance_scores)) >= 0.85,
                        "individual_relevance_scores": relevance_scores
                    }
                else:
                    category_stats[category] = self._get_empty_relevance_stats(len(results))
            
            elif metric_name == "coverage":
                if successful_results:
                    coverage_scores = [r['coverage_metrics']['coverage_score'] for r in successful_results]
                    category_stats[category] = {
                        "average_coverage": sum(coverage_scores) / len(coverage_scores),
                        "max_coverage": max(coverage_scores),
                        "min_coverage": min(coverage_scores),
                        "successful_evaluations": len(successful_results),
                        "total_queries": len(results),
                        "meets_threshold": (sum(coverage_scores) / len(coverage_scores)) >= 0.4,
                        "individual_coverage_scores": coverage_scores
                    }
                else:
                    category_stats[category] = self._get_empty_coverage_stats(len(results))
        
        # Calculate overall statistics
        overall_stats = self._calculate_overall_stats(metric_name, all_successful_results)
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _get_empty_latency_stats(self) -> Dict[str, Any]:
        """Return empty latency statistics"""
        return {
            "average_latency": 0.0,
            "std_deviation": 0.0,
            "min_latency": 0.0,
            "max_latency": 0.0,
            "query_count": 0,
            "target_compliance": 0.0,
            "individual_latencies": []
        }
    
    def _get_empty_relevance_stats(self, total_queries: int) -> Dict[str, Any]:
        """Return empty relevance statistics"""
        return {
            "average_relevance": 0.0,
            "max_relevance": 0.0,
            "min_relevance": 0.0,
            "successful_retrievals": 0,
            "total_queries": total_queries,
            "meets_threshold": False,
            "individual_relevance_scores": []
        }
    
    def _get_empty_coverage_stats(self, total_queries: int) -> Dict[str, Any]:
        """Return empty coverage statistics"""
        return {
            "average_coverage": 0.0,
            "max_coverage": 0.0,
            "min_coverage": 0.0,
            "successful_evaluations": 0,
            "total_queries": total_queries,
            "meets_threshold": False,
            "individual_coverage_scores": []
        }
    
    def _calculate_overall_stats(self, metric_name: str, all_successful_results: List[Dict]) -> Dict[str, Any]:
        """Calculate overall statistics for a specific metric"""
        total_queries = len(self.comprehensive_results)
        
        if metric_name == "latency" and all_successful_results:
            latencies = [r['latency_metrics']['total_latency'] for r in all_successful_results]
            return {
                "average_latency": sum(latencies) / len(latencies),
                "std_deviation": self._calculate_std(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "successful_queries": len(all_successful_results),
                "total_queries": total_queries,
                "target_compliance": sum(1 for lat in latencies if lat <= 60.0) / len(latencies)
            }
        
        elif metric_name == "extraction":
            all_extractions = [r['extraction_metrics']['extraction_success'] for r in self.comprehensive_results]
            successful_extractions = sum(all_extractions)
            return {
                "success_rate": successful_extractions / len(all_extractions) if all_extractions else 0.0,
                "successful_count": successful_extractions,
                "total_count": len(all_extractions),
                "target_compliance": (successful_extractions / len(all_extractions)) >= 0.8 if all_extractions else False
            }
        
        elif metric_name == "relevance" and all_successful_results:
            relevance_scores = [r['relevance_metrics']['average_relevance'] for r in all_successful_results]
            return {
                "average_relevance": sum(relevance_scores) / len(relevance_scores),
                "max_relevance": max(relevance_scores),
                "min_relevance": min(relevance_scores),
                "successful_queries": len(all_successful_results),
                "total_queries": total_queries,
                "meets_threshold": (sum(relevance_scores) / len(relevance_scores)) >= 0.85,
                "target_compliance": (sum(relevance_scores) / len(relevance_scores)) >= 0.7
            }
        
        elif metric_name == "coverage" and all_successful_results:
            coverage_scores = [r['coverage_metrics']['coverage_score'] for r in all_successful_results]
            return {
                "average_coverage": sum(coverage_scores) / len(coverage_scores),
                "max_coverage": max(coverage_scores),
                "min_coverage": min(coverage_scores),
                "successful_queries": len(all_successful_results),
                "total_queries": total_queries,
                "meets_threshold": (sum(coverage_scores) / len(coverage_scores)) >= 0.4
            }
        
        # Return empty stats for failed cases
        return {
            "average_value": 0.0,
            "successful_queries": len(all_successful_results),
            "total_queries": total_queries,
            "meets_threshold": False
        }    
    def save_all_metric_statistics(self) -> Dict[str, str]:
        """Save separate statistics files for each metric"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        saved_files = {}
        
        # Save statistics for each metric
        for metric_name in ["latency", "extraction", "relevance", "coverage"]:
            stats = self.calculate_metric_statistics(metric_name)
            filename = f"{metric_name}_statistics_{timestamp}.json"
            filepath = results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            saved_files[metric_name] = str(filepath)
            print(f"📊 {metric_name.capitalize()} statistics saved to: {filepath}")
        
        return saved_files
    
    def save_medical_outputs(self, filename: str = None) -> str:
        """Save medical advice outputs for model comparison"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"medical_outputs_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create comprehensive output data
        output_data = {
            "evaluation_metadata": {
                "total_outputs": len(self.medical_outputs),
                "categories": list(set(output['category'] for output in self.medical_outputs)),
                "timestamp": datetime.now().isoformat(),
                "model_type": "Med42-70B_RAG_enhanced"  # For future comparison
            },
            "medical_outputs": self.medical_outputs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Medical outputs saved to: {filepath}")
        return str(filepath)
    
    def save_comprehensive_details(self, filename: str = None) -> str:
        """Save comprehensive detailed results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_details_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create comprehensive evaluation data
        comprehensive_data = {
            "evaluation_metadata": {
                "total_queries": len(self.comprehensive_results),
                "successful_queries": len([r for r in self.comprehensive_results if r.get('overall_success')]),
                "timestamp": datetime.now().isoformat(),
                "evaluator_type": "comprehensive_metrics_1_to_4",
                "metrics_evaluated": ["latency", "extraction", "relevance", "coverage"]
            },
            "comprehensive_results": self.comprehensive_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Comprehensive details saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent comprehensive evaluation interface"""
    
    print("🚀 OnCall.ai Comprehensive Evaluator - Metrics 1-4 in Single Run")
    
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
    else:
        # Default to evaluation/single_test_query.txt for initial testing
        # TODO: Change to pre_user_query_evaluate.txt for full evaluation, user_query.txt for formal evaluation
        query_file = Path(__file__).parent / "user_query.txt"
    
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        print("Usage: python latency_evaluator.py [query_file.txt]")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = ComprehensiveEvaluator()
    
    # Parse queries from file
    queries_by_category = evaluator.parse_queries_from_file(str(query_file))
    
    if "error" in queries_by_category:
        print(f"❌ Failed to parse queries: {queries_by_category['error']}")
        sys.exit(1)
    
    # Test each query comprehensively
    print(f"\n🧪 Comprehensive Evaluation - All Metrics in Single Run")
    print(f"📊 Collecting metrics 1-4 from single app.py pipeline execution")
    
    for category, queries in queries_by_category.items():
        if not queries:
            continue
            
        print(f"\n📂 Testing {category.upper()} queries:")
        
        for i, query_info in enumerate(queries):
            query_text = query_info['text']
            print(f"\n🔍 Query {i+1}/{len(queries)} in {category} category:")
            print(f"   Text: {query_text}")
            
            # Comprehensive evaluation (collects all metrics 1-4)
            result = evaluator.evaluate_single_query_comprehensive(query_text, category)
            
            # Pause between queries to avoid rate limits
            if i < len(queries) - 1:
                print(f"   ⏳ Pausing 5s before next query...")
                time.sleep(5)
        
        # Longer pause between categories
        if category != list(queries_by_category.keys())[-1]:
            print(f"\n⏳ Pausing 10s before next category...")
            time.sleep(10)
    
    # Generate and save all metric statistics
    print(f"\n📊 Generating comprehensive analysis for all metrics...")
    
    # Save separate statistics for each metric
    saved_stats = evaluator.save_all_metric_statistics()
    
    # Save medical outputs for model comparison
    outputs_path = evaluator.save_medical_outputs()
    
    # Save comprehensive details
    details_path = evaluator.save_comprehensive_details()
    
    # Print comprehensive summary
    print(f"\n📊 === COMPREHENSIVE EVALUATION SUMMARY ===")
    
    for metric_name in ["latency", "extraction", "relevance", "coverage"]:
        stats = evaluator.calculate_metric_statistics(metric_name)
        overall_results = stats['overall_results']
        
        print(f"\n{metric_name.upper()} METRICS:")
        
        if metric_name == "latency":
            print(f"   Average: {overall_results['average_latency']:.2f}s (±{overall_results['std_deviation']:.2f})")
            print(f"   60s Target: {'✅ Met' if overall_results['target_compliance'] >= 0.8 else '❌ Not Met'}")
        
        elif metric_name == "extraction":
            print(f"   Success Rate: {overall_results['success_rate']:.1%}")
            print(f"   80% Target: {'✅ Met' if overall_results['target_compliance'] else '❌ Not Met'}")
        
        elif metric_name == "relevance":
            print(f"   Average Relevance: {overall_results['average_relevance']:.3f}")
            print(f"   0.70 Target: {'✅ Met' if overall_results.get('target_compliance', False) else '❌ Not Met'}")
        
        elif metric_name == "coverage":
            print(f"   Average Coverage: {overall_results['average_coverage']:.3f} ({overall_results['average_coverage']*100:.1f}%)")
            print(f"   40% Target: {'✅ Met' if overall_results['meets_threshold'] else '❌ Not Met'}")
    
    print(f"\n✅ Comprehensive evaluation complete! Files saved:")
    for metric_name, filepath in saved_stats.items():
        print(f"   📊 {metric_name.capitalize()}: {filepath}")
    print(f"   📝 Medical Outputs: {outputs_path}")
    print(f"   📋 Comprehensive Details: {details_path}")
    print(f"\n💡 Next step: Run downstream evaluators for metrics 5-8")
    print(f"   python metric5_6_llm_judge_evaluator.py rag")
    print(f"   python metric7_8_precision_MRR.py {details_path}")
    print(f"   python latency_chart_generator.py")
    print(f"   python extraction_chart_generator.py  # (create separately)")
    print(f"   python relevance_chart_generator.py   # (create separately)")
    print(f"   python coverage_chart_generator.py    # (create separately)")
