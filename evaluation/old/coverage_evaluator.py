#!/usr/bin/env python3
"""
OnCall.ai System - Retrieval Coverage Evaluator (Metric 4)
==========================================================

Evaluates how well generated medical advice utilizes retrieved content
Automatic evaluation using keyword overlap analysis with optional LLM sampling

Author: YanBo Chen  
Date: 2025-08-04
"""

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


class CoverageEvaluator:
    """Retrieval coverage evaluator using keyword overlap analysis"""
    
    def __init__(self):
        """Initialize system components for coverage testing"""
        print("🔧 Initializing Coverage Evaluator...")
        
        # Initialize full pipeline components (needed for advice generation)
        self.llm_client = llm_Med42_70BClient()
        self.retrieval_system = BasicRetrievalSystem()
        self.user_prompt_processor = UserPromptProcessor(
            llm_client=self.llm_client,
            retrieval_system=self.retrieval_system
        )
        self.medical_generator = MedicalAdviceGenerator(llm_client=self.llm_client)
        
        # Results accumulation
        self.coverage_results = []
        
        print("✅ Coverage Evaluator initialization complete")
    
    def extract_medical_keywords(self, text: str) -> Set[str]:
        """
        Extract medical keywords from text for coverage analysis
        
        Uses medical terminology patterns and common medical terms
        """
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
    
    def calculate_coverage_score(self, generated_advice: str, retrieval_results: List[Dict]) -> Dict[str, Any]:
        """
        Calculate coverage score based on keyword overlap between advice and retrieved docs
        
        Args:
            generated_advice: Generated medical advice text
            retrieval_results: List of retrieved documents
        """
        if not generated_advice or not retrieval_results:
            return {
                "coverage_score": 0.0,
                "matched_keywords": [],
                "advice_keywords": [],
                "source_keywords": [],
                "coverage_details": []
            }
        
        # Extract keywords from generated advice
        advice_keywords = self.extract_medical_keywords(generated_advice)
        
        # Extract keywords from all retrieved documents
        all_source_keywords = set()
        coverage_details = []
        
        for i, doc in enumerate(retrieval_results):
            doc_content = doc.get('content', '') or doc.get('text', '')
            doc_keywords = self.extract_medical_keywords(doc_content)
            all_source_keywords.update(doc_keywords)
            
            # Calculate overlap for this specific document
            doc_overlap = advice_keywords.intersection(doc_keywords)
            doc_coverage = len(doc_overlap) / len(doc_keywords) if doc_keywords else 0.0
            
            coverage_details.append({
                "doc_index": i,
                "doc_snippet": doc_content[:100] + "...",
                "doc_keywords_count": len(doc_keywords),
                "matched_keywords_count": len(doc_overlap),
                "doc_coverage_ratio": doc_coverage,
                "matched_keywords": list(doc_overlap)[:10]  # Limit for readability
            })
        
        # Calculate overall coverage
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
            "meets_threshold": coverage_score >= 0.6,
            "coverage_details": coverage_details
        }
    
    def evaluate_single_coverage(self, query: str, category: str = "unknown") -> Dict[str, Any]:
        """
        Evaluate retrieval coverage for a single query
        
        Requires full pipeline: extraction → retrieval → generation → coverage analysis
        
        Args:
            query: Medical query to test
            category: Query category (diagnosis/treatment/mixed)
        """
        print(f"🔍 Testing coverage for: {query[:50]}...")
        print(f"📋 Category: {category}")
        
        try:
            # Step 1: Extract condition
            condition_result = self.user_prompt_processor.extract_condition_keywords(query)
            
            # Step 2: Perform retrieval
            search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
            if not search_query:
                search_query = condition_result.get('condition', query)
            
            retrieval_start = datetime.now()
            retrieval_results = self.retrieval_system.search(search_query, top_k=5)
            retrieval_time = (datetime.now() - retrieval_start).total_seconds()
            
            processed_results = retrieval_results.get('processed_results', [])
            
            if not processed_results:
                result = {
                    "query": query,
                    "category": category,
                    "search_query": search_query,
                    "pipeline_success": False,
                    "coverage_score": 0.0,
                    "error": "No retrieval results",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.coverage_results.append(result)
                print(f"   ❌ No retrieval results for coverage analysis")
                return result
            
            # Step 3: Generate medical advice
            generation_start = datetime.now()
            intention = self._detect_query_intention(query)
            medical_advice_result = self.medical_generator.generate_medical_advice(
                user_query=query,
                retrieval_results=retrieval_results,
                intention=intention
            )
            generation_time = (datetime.now() - generation_start).total_seconds()
            
            generated_advice = medical_advice_result.get('medical_advice', '')
            
            if not generated_advice:
                result = {
                    "query": query,
                    "category": category,
                    "search_query": search_query,
                    "pipeline_success": False,
                    "coverage_score": 0.0,
                    "error": "No generated advice",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.coverage_results.append(result)
                print(f"   ❌ No generated advice for coverage analysis")
                return result
            
            # Step 4: Calculate coverage
            coverage_analysis = self.calculate_coverage_score(generated_advice, processed_results)
            
            result = {
                "query": query,
                "category": category,
                "search_query": search_query,
                "pipeline_success": True,
                "retrieval_time": retrieval_time,
                "generation_time": generation_time,
                "retrieved_docs_count": len(processed_results),
                "generated_advice_length": len(generated_advice),
                "coverage_analysis": coverage_analysis,
                "coverage_score": coverage_analysis['coverage_score'],
                "meets_threshold": coverage_analysis['meets_threshold'],
                "timestamp": datetime.now().isoformat()
            }
            
            # Store result
            self.coverage_results.append(result)
            
            print(f"   ✅ Pipeline: Complete")
            print(f"   📊 Coverage Score: {coverage_analysis['coverage_score']:.3f} ({coverage_analysis['coverage_percentage']:.1f}%)")
            print(f"   📝 Keywords: {coverage_analysis['matched_keywords_count']}/{coverage_analysis['source_keywords_count']} matched")
            print(f"   🎯 Threshold: {'✅ Met' if result['meets_threshold'] else '❌ Not Met'}")
            print(f"   ⏱️ Times: Retrieval={retrieval_time:.2f}s, Generation={generation_time:.2f}s")
            
            return result
            
        except Exception as e:
            error_result = {
                "query": query,
                "category": category,
                "pipeline_success": False,
                "coverage_score": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.coverage_results.append(error_result)
            print(f"   ❌ Coverage evaluation failed: {e}")
            
            return error_result
    
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
    
    def calculate_coverage_statistics(self) -> Dict[str, Any]:
        """Calculate coverage statistics by category"""
        category_stats = {}
        all_successful_results = []
        
        # Group results by category
        results_by_category = {
            "diagnosis": [],
            "treatment": [],
            "mixed": []
        }
        
        for result in self.coverage_results:
            category = result.get('category', 'unknown')
            if category in results_by_category:
                results_by_category[category].append(result)
                if result.get('pipeline_success'):
                    all_successful_results.append(result)
        
        # Calculate statistics for each category
        for category, results in results_by_category.items():
            successful_results = [r for r in results if r.get('pipeline_success')]
            
            if successful_results:
                coverage_scores = [r['coverage_score'] for r in successful_results]
                avg_coverage = sum(coverage_scores) / len(coverage_scores)
                avg_retrieval_time = sum(r.get('retrieval_time', 0) for r in successful_results) / len(successful_results)
                avg_generation_time = sum(r.get('generation_time', 0) for r in successful_results) / len(successful_results)
                
                category_stats[category] = {
                    "average_coverage": avg_coverage,
                    "max_coverage": max(coverage_scores),
                    "min_coverage": min(coverage_scores),
                    "successful_evaluations": len(successful_results),
                    "total_queries": len(results),
                    "success_rate": len(successful_results) / len(results),
                    "average_retrieval_time": avg_retrieval_time,
                    "average_generation_time": avg_generation_time,
                    "meets_threshold": avg_coverage >= 0.6,
                    "individual_coverage_scores": coverage_scores
                }
            else:
                category_stats[category] = {
                    "average_coverage": 0.0,
                    "max_coverage": 0.0,
                    "min_coverage": 0.0,
                    "successful_evaluations": 0,
                    "total_queries": len(results),
                    "success_rate": 0.0,
                    "average_retrieval_time": 0.0,
                    "average_generation_time": 0.0,
                    "meets_threshold": False,
                    "individual_coverage_scores": []
                }
        
        # Calculate overall statistics
        if all_successful_results:
            all_coverage_scores = [r['coverage_score'] for r in all_successful_results]
            overall_stats = {
                "average_coverage": sum(all_coverage_scores) / len(all_coverage_scores),
                "max_coverage": max(all_coverage_scores),
                "min_coverage": min(all_coverage_scores),
                "successful_evaluations": len(all_successful_results),
                "total_queries": len(self.coverage_results),
                "success_rate": len(all_successful_results) / len(self.coverage_results),
                "meets_threshold": (sum(all_coverage_scores) / len(all_coverage_scores)) >= 0.6,
                "target_compliance": (sum(all_coverage_scores) / len(all_coverage_scores)) >= 0.6
            }
        else:
            overall_stats = {
                "average_coverage": 0.0,
                "max_coverage": 0.0,
                "min_coverage": 0.0,
                "successful_evaluations": 0,
                "total_queries": len(self.coverage_results),
                "success_rate": 0.0,
                "meets_threshold": False,
                "target_compliance": False
            }
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_coverage_statistics(self, filename: str = None) -> str:
        """Save coverage statistics for chart generation"""
        stats = self.calculate_coverage_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coverage_statistics_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Coverage statistics saved to: {filepath}")
        return str(filepath)
    
    def save_coverage_details(self, filename: str = None) -> str:
        """Save detailed coverage results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coverage_details_{timestamp}.json"
        
        # Ensure results directory exists
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        # Create comprehensive coverage data
        coverage_data = {
            "evaluation_metadata": {
                "total_queries": len(self.coverage_results),
                "successful_evaluations": len([r for r in self.coverage_results if r.get('pipeline_success')]),
                "timestamp": datetime.now().isoformat(),
                "evaluator_type": "retrieval_coverage",
                "threshold_used": 0.6
            },
            "coverage_results": self.coverage_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(coverage_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Coverage details saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent coverage evaluation interface"""
    
    print("📈 OnCall.ai Coverage Evaluator - Retrieval Coverage Analysis")
    
    if len(sys.argv) > 1:
        query_file = sys.argv[1]
    else:
        # Default to evaluation/pre_user_query_evaluate.txt
        query_file = Path(__file__).parent / "pre_user_query_evaluate.txt"
    
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        print("Usage: python coverage_evaluator.py [query_file.txt]")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = CoverageEvaluator()
    
    # Parse queries from file
    queries_by_category = evaluator.parse_queries_from_file(str(query_file))
    
    if "error" in queries_by_category:
        print(f"❌ Failed to parse queries: {queries_by_category['error']}")
        sys.exit(1)
    
    # Test coverage for each query (requires full pipeline)
    print(f"\n🧪 Retrieval Coverage Testing (Full Pipeline Required)")
    print(f"⚠️ Note: This evaluator requires LLM calls for advice generation")
    
    for category, queries in queries_by_category.items():
        if not queries:
            continue
            
        print(f"\n📂 Testing {category.upper()} coverage:")
        
        for i, query_info in enumerate(queries):
            query_text = query_info['text']
            
            # Test coverage (requires full pipeline)
            result = evaluator.evaluate_single_coverage(query_text, category)
            
            # Pause between queries to avoid rate limits
            if i < len(queries) - 1:
                print(f"   ⏳ Pausing 5s before next query...")
                import time
                time.sleep(5)
        
        # Longer pause between categories
        if category != list(queries_by_category.keys())[-1]:
            print(f"\n⏳ Pausing 10s before next category...")
            import time
            time.sleep(10)
    
    # Generate and save results
    print(f"\n📊 Generating coverage analysis...")
    
    # Save statistics and details
    stats_path = evaluator.save_coverage_statistics()
    details_path = evaluator.save_coverage_details()
    
    # Print final summary
    stats = evaluator.calculate_coverage_statistics()
    category_results = stats['category_results']
    overall_results = stats['overall_results']
    
    print(f"\n📊 === COVERAGE EVALUATION SUMMARY ===")
    print(f"Overall Performance:")
    print(f"   Average Coverage: {overall_results['average_coverage']:.3f} ({overall_results['average_coverage']*100:.1f}%)")
    print(f"   Pipeline Success Rate: {overall_results['success_rate']:.1%}")
    print(f"   60% Threshold: {'✅ Met' if overall_results['meets_threshold'] else '❌ Not Met'}")
    
    print(f"\nCategory Breakdown:")
    for category, cat_stats in category_results.items():
        if cat_stats['total_queries'] > 0:
            print(f"   {category.capitalize()}: {cat_stats['average_coverage']:.3f} "
                  f"({cat_stats['successful_evaluations']}/{cat_stats['total_queries']}) "
                  f"[R:{cat_stats['average_retrieval_time']:.2f}s, G:{cat_stats['average_generation_time']:.2f}s]")
    
    print(f"\n✅ Coverage evaluation complete!")
    print(f"📊 Statistics: {stats_path}")
    print(f"📝 Details: {details_path}")
