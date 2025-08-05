#!/usr/bin/env python3
"""
OnCall.ai System - LLM Judge Evaluator (Metrics 5-6)
====================================================

Uses Llama3-70B as third-party judge to evaluate medical advice quality.
Batch evaluation strategy: 1 call evaluates all queries for maximum efficiency.

Metrics evaluated:
5. Clinical Actionability (臨床可操作性)
6. Clinical Evidence Quality (臨床證據品質)

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
import re

# Add project path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import LLM client for judge evaluation
try:
    from llm_clients import llm_Med42_70BClient  # Temporarily use Med42 as placeholder
    # TODO: Replace with actual Llama3-70B client when available
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure running from project root directory")
    sys.exit(1)


class LLMJudgeEvaluator:
    """LLM judge evaluator using batch evaluation strategy"""
    
    def __init__(self):
        """Initialize judge LLM client"""
        print("🔧 Initializing LLM Judge Evaluator...")
        
        # TODO: Replace with actual Llama3-70B client
        # For now, using Med42 as placeholder
        self.judge_llm = llm_Med42_70BClient()
        print("⚠️ Note: Using Med42 as placeholder for Llama3-70B judge")
        
        self.evaluation_results = []
        
        print("✅ LLM Judge Evaluator initialization complete")
    
    def load_medical_outputs(self, filepath: str) -> List[Dict[str, Any]]:
        """Load medical outputs from file"""
        print(f"📁 Loading medical outputs from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        medical_outputs = data.get('medical_outputs', [])
        print(f"📋 Loaded {len(medical_outputs)} medical outputs")
        
        return medical_outputs
    
    def find_latest_medical_outputs(self, model_type: str = "rag") -> str:
        """Find the latest medical outputs file"""
        results_dir = Path(__file__).parent / "results"
        
        if model_type == "rag":
            pattern = str(results_dir / "medical_outputs_*.json")
        else:  # direct
            pattern = str(results_dir / "medical_outputs_direct_*.json")
        
        output_files = glob.glob(pattern)
        
        if not output_files:
            raise FileNotFoundError(f"No medical outputs files found for {model_type} model")
        
        latest_file = max(output_files, key=os.path.getmtime)
        print(f"📊 Found latest medical outputs: {latest_file}")
        
        return latest_file
    
    def create_batch_evaluation_prompt(self, medical_outputs: List[Dict[str, Any]]) -> str:
        """
        Create batch evaluation prompt for all queries at once
        
        Maximum efficiency: 1 LLM call evaluates all queries
        """
        prompt_parts = [
            "You are a medical expert evaluating clinical advice quality.",
            "Please evaluate each medical advice response on TWO criteria:",
            "",
            "CRITERIA:",
            "1. Clinical Actionability (1-10): Can healthcare providers immediately act on this advice?",
            "2. Clinical Evidence Quality (1-10): Is the advice evidence-based and follows medical standards?",
            "",
            "QUERIES TO EVALUATE:",
            ""
        ]
        
        # Add each query and advice
        for i, output in enumerate(medical_outputs, 1):
            query = output.get('query', '')
            advice = output.get('medical_advice', '')
            category = output.get('category', 'unknown')
            
            prompt_parts.extend([
                f"=== QUERY {i} ({category.upper()}) ===",
                f"Patient Query: {query}",
                f"Medical Advice: {advice}",
                ""
            ])
        
        prompt_parts.extend([
            "RESPONSE FORMAT (provide exactly this format):",
            ""
        ])
        
        # Add response format template
        for i in range(1, len(medical_outputs) + 1):
            prompt_parts.append(f"Query {i}: Actionability=X, Evidence=Y")
        
        prompt_parts.extend([
            "",
            "Replace X and Y with numeric scores 1-10.",
            "Provide only the scores in the exact format above."
        ])
        
        return "\n".join(prompt_parts)
    
    def parse_batch_evaluation_response(self, response: str, medical_outputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse batch evaluation response into individual scores"""
        results = []
        
        # Parse response format: "Query 1: Actionability=8, Evidence=7"
        lines = response.strip().split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try to match pattern: "Query X: Actionability=Y, Evidence=Z"
            match = re.match(r'Query\s+(\d+):\s*Actionability\s*=\s*(\d+)\s*,\s*Evidence\s*=\s*(\d+)', line, re.IGNORECASE)
            
            if match:
                query_num = int(match.group(1)) - 1  # Convert to 0-based index
                actionability_score = int(match.group(2))
                evidence_score = int(match.group(3))
                
                if query_num < len(medical_outputs):
                    output = medical_outputs[query_num]
                    
                    result = {
                        "query": output.get('query', ''),
                        "category": output.get('category', 'unknown'),
                        "model_type": output.get('model_type', 'unknown'),
                        "medical_advice": output.get('medical_advice', ''),
                        
                        # Metric 5: Clinical Actionability
                        "actionability_score": actionability_score / 10.0,  # Normalize to 0-1
                        "actionability_raw": actionability_score,
                        
                        # Metric 6: Clinical Evidence Quality
                        "evidence_score": evidence_score / 10.0,  # Normalize to 0-1
                        "evidence_raw": evidence_score,
                        
                        "evaluation_success": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    results.append(result)
        
        return results
    
    def evaluate_batch_medical_outputs(self, medical_outputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch evaluate all medical outputs using single LLM call
        
        Args:
            medical_outputs: List of medical advice outputs to evaluate
        """
        print(f"🧠 Batch evaluating {len(medical_outputs)} medical outputs...")
        
        try:
            # Create batch evaluation prompt
            batch_prompt = self.create_batch_evaluation_prompt(medical_outputs)
            
            print(f"📝 Batch prompt created ({len(batch_prompt)} characters)")
            print(f"🔄 Calling judge LLM for batch evaluation...")
            
            # Single LLM call for all evaluations
            eval_start = time.time()
            response = self.judge_llm.generate_completion(batch_prompt)
            eval_time = time.time() - eval_start
            
            # Extract response text
            response_text = response.get('content', '') if isinstance(response, dict) else str(response)
            
            print(f"✅ Judge LLM completed batch evaluation in {eval_time:.2f}s")
            print(f"📄 Response length: {len(response_text)} characters")
            
            # Parse batch response
            parsed_results = self.parse_batch_evaluation_response(response_text, medical_outputs)
            
            if len(parsed_results) != len(medical_outputs):
                print(f"⚠️ Warning: Expected {len(medical_outputs)} results, got {len(parsed_results)}")
            
            self.evaluation_results.extend(parsed_results)
            
            print(f"📊 Successfully parsed {len(parsed_results)} evaluation results")
            
            return parsed_results
            
        except Exception as e:
            print(f"❌ Batch evaluation failed: {e}")
            
            # Create error results for all outputs
            error_results = []
            for output in medical_outputs:
                error_result = {
                    "query": output.get('query', ''),
                    "category": output.get('category', 'unknown'),
                    "model_type": output.get('model_type', 'unknown'),
                    "actionability_score": 0.0,
                    "evidence_score": 0.0,
                    "evaluation_success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                error_results.append(error_result)
            
            self.evaluation_results.extend(error_results)
            return error_results
    
    def calculate_judge_statistics(self) -> Dict[str, Any]:
        """Calculate statistics for LLM judge evaluation"""
        successful_results = [r for r in self.evaluation_results if r.get('evaluation_success')]
        
        if not successful_results:
            return {
                "category_results": {},
                "overall_results": {
                    "average_actionability": 0.0,
                    "average_evidence": 0.0,
                    "successful_evaluations": 0,
                    "total_queries": len(self.evaluation_results)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Group by category
        results_by_category = {"diagnosis": [], "treatment": [], "mixed": []}
        
        for result in successful_results:
            category = result.get('category', 'unknown')
            if category in results_by_category:
                results_by_category[category].append(result)
        
        # Calculate category statistics
        category_stats = {}
        for category, results in results_by_category.items():
            if results:
                actionability_scores = [r['actionability_score'] for r in results]
                evidence_scores = [r['evidence_score'] for r in results]
                
                category_stats[category] = {
                    "average_actionability": sum(actionability_scores) / len(actionability_scores),
                    "average_evidence": sum(evidence_scores) / len(evidence_scores),
                    "query_count": len(results),
                    "actionability_target_met": (sum(actionability_scores) / len(actionability_scores)) >= 0.7,
                    "evidence_target_met": (sum(evidence_scores) / len(evidence_scores)) >= 0.75,
                    "individual_actionability_scores": actionability_scores,
                    "individual_evidence_scores": evidence_scores
                }
            else:
                category_stats[category] = {
                    "average_actionability": 0.0,
                    "average_evidence": 0.0,
                    "query_count": 0,
                    "actionability_target_met": False,
                    "evidence_target_met": False,
                    "individual_actionability_scores": [],
                    "individual_evidence_scores": []
                }
        
        # Calculate overall statistics
        all_actionability = [r['actionability_score'] for r in successful_results]
        all_evidence = [r['evidence_score'] for r in successful_results]
        
        overall_stats = {
            "average_actionability": sum(all_actionability) / len(all_actionability),
            "average_evidence": sum(all_evidence) / len(all_evidence),
            "successful_evaluations": len(successful_results),
            "total_queries": len(self.evaluation_results),
            "actionability_target_met": (sum(all_actionability) / len(all_actionability)) >= 0.7,
            "evidence_target_met": (sum(all_evidence) / len(all_evidence)) >= 0.75
        }
        
        return {
            "category_results": category_stats,
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_judge_statistics(self, model_type: str, filename: str = None) -> str:
        """Save judge evaluation statistics"""
        stats = self.calculate_judge_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"judge_evaluation_{model_type}_{timestamp}.json"
        
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Judge evaluation statistics saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent LLM judge evaluation interface"""
    
    print("🧠 OnCall.ai LLM Judge Evaluator - Metrics 5-6 Batch Evaluation")
    
    if len(sys.argv) > 1 and sys.argv[1] in ['rag', 'direct']:
        model_type = sys.argv[1]
    else:
        print("Usage: python llm_judge_evaluator.py [rag|direct]")
        print("  rag    - Evaluate RAG system medical outputs")
        print("  direct - Evaluate direct LLM medical outputs")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = LLMJudgeEvaluator()
    
    try:
        # Find and load latest medical outputs
        outputs_file = evaluator.find_latest_medical_outputs(model_type)
        medical_outputs = evaluator.load_medical_outputs(outputs_file)
        
        if not medical_outputs:
            print(f"❌ No medical outputs found in {outputs_file}")
            sys.exit(1)
        
        # Batch evaluate all outputs
        print(f"\n🧪 Batch LLM Judge Evaluation for {model_type.upper()} model")
        print(f"📊 Evaluating {len(medical_outputs)} medical advice outputs")
        print(f"🎯 Metrics: 5 (Actionability) + 6 (Evidence Quality)")
        print(f"⚡ Strategy: Single batch call for maximum efficiency")
        
        evaluation_results = evaluator.evaluate_batch_medical_outputs(medical_outputs)
        
        # Save results
        print(f"\n📊 Generating judge evaluation analysis...")
        stats_path = evaluator.save_judge_statistics(model_type)
        
        # Print summary
        stats = evaluator.calculate_judge_statistics()
        overall_results = stats['overall_results']
        category_results = stats['category_results']
        
        print(f"\n📊 === LLM JUDGE EVALUATION SUMMARY ({model_type.upper()}) ===")
        print(f"Overall Performance:")
        print(f"   Average Actionability: {overall_results['average_actionability']:.3f} ({overall_results['average_actionability']*10:.1f}/10)")
        print(f"   Average Evidence Quality: {overall_results['average_evidence']:.3f} ({overall_results['average_evidence']*10:.1f}/10)")
        print(f"   Actionability Target (≥7.0): {'✅ Met' if overall_results['actionability_target_met'] else '❌ Not Met'}")
        print(f"   Evidence Target (≥7.5): {'✅ Met' if overall_results['evidence_target_met'] else '❌ Not Met'}")
        
        print(f"\nCategory Breakdown:")
        for category, cat_stats in category_results.items():
            if cat_stats['query_count'] > 0:
                print(f"   {category.capitalize()}: "
                      f"Actionability={cat_stats['average_actionability']:.2f}, "
                      f"Evidence={cat_stats['average_evidence']:.2f} "
                      f"[{cat_stats['query_count']} queries]")
        
        print(f"\n✅ LLM judge evaluation complete!")
        print(f"📊 Statistics: {stats_path}")
        print(f"⚡ Efficiency: {len(medical_outputs)} evaluations in 1 LLM call")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print(f"💡 Please run evaluator first:")
        if model_type == "rag":
            print("   python latency_evaluator.py pre_user_query_evaluate.txt")
        else:
            print("   python direct_llm_evaluator.py pre_user_query_evaluate.txt")
    except Exception as e:
        print(f"❌ Judge evaluation failed: {e}")
