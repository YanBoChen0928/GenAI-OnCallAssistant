#!/usr/bin/env python3
"""
OnCall.ai System - LLM Judge Evaluator (Metrics 5-6)
====================================================

Uses Llama3-70B as third-party judge to evaluate medical advice quality.
Batch evaluation strategy: 1 call evaluates all queries for maximum efficiency.

Metrics evaluated:
5. Clinical Actionability (臨床可操作性)
6. Clinical Evidence Quality (臨床證據品質)

EVALUATION RUBRICS:

Metric 5: Clinical Actionability (1-10 scale)
  1-2 points: Almost no actionable advice; extremely abstract or empty responses.
  3-4 points: Provides some directional suggestions but too vague, lacks clear steps.
  5-6 points: Offers basic executable steps but lacks details or insufficient explanation for key aspects.
  7-8 points: Clear and complete steps that clinicians can follow, with occasional gaps needing supplementation.
  9-10 points: Extremely actionable with precise, step-by-step executable guidance; can be used "as-is" immediately.

Metric 6: Clinical Evidence Quality (1-10 scale)
  1-2 points: Almost no evidence support; cites completely irrelevant or unreliable sources.
  3-4 points: References lower quality literature or guidelines, or sources lack authority.
  5-6 points: Uses general quality literature/guidelines but lacks depth or currency.
  7-8 points: References reliable, authoritative sources (renowned journals or authoritative guidelines) with accurate explanations.
  9-10 points: Rich and high-quality evidence sources (systematic reviews, RCTs, etc.) combined with latest research; enhances recommendation credibility.

Author: YanBo Chen  
Date: 2025-08-04
"""

import json
import os
import sys
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path
import glob
import re

# Evaluation Rubrics as programmable constants
ACTIONABILITY_RUBRIC = {
    (1, 2): "Almost no actionable advice; extremely abstract or empty responses.",
    (3, 4): "Provides some directional suggestions but too vague, lacks clear steps.",
    (5, 6): "Offers basic executable steps but lacks details or insufficient explanation for key aspects.",
    (7, 8): "Clear and complete steps that clinicians can follow, with occasional gaps needing supplementation.",
    (9, 10): "Extremely actionable with precise, step-by-step executable guidance; can be used 'as-is' immediately."
}

EVIDENCE_RUBRIC = {
    (1, 2): "Almost no evidence support; cites completely irrelevant or unreliable sources.",
    (3, 4): "References lower quality literature or guidelines, or sources lack authority.",
    (5, 6): "Uses general quality literature/guidelines but lacks depth or currency.",
    (7, 8): "References reliable, authoritative sources (renowned journals or authoritative guidelines) with accurate explanations.",
    (9, 10): "Rich and high-quality evidence sources (systematic reviews, RCTs, etc.) combined with latest research; enhances recommendation credibility."
}

def print_evaluation_rubrics():
    """Print detailed evaluation rubrics for reference"""
    print("=" * 60)
    print("CLINICAL EVALUATION RUBRICS")
    print("=" * 60)
    
    print("\n🎯 METRIC 5: Clinical Actionability (1-10 scale)")
    print("-" * 50)
    for score_range, description in ACTIONABILITY_RUBRIC.items():
        print(f"{score_range[0]}–{score_range[1]} points: {description}")
    
    print("\n📚 METRIC 6: Clinical Evidence Quality (1-10 scale)")
    print("-" * 50)
    for score_range, description in EVIDENCE_RUBRIC.items():
        print(f"{score_range[0]}–{score_range[1]} points: {description}")
    
    print("\n" + "=" * 60)
    print("TARGET THRESHOLDS:")
    print("• Actionability: ≥7.0 (Acceptable clinical utility)")
    print("• Evidence Quality: ≥7.5 (Reliable evidence support)")
    print("=" * 60)

def get_rubric_description(score: int, metric_type: str) -> str:
    """Get rubric description for a given score and metric type"""
    rubric = ACTIONABILITY_RUBRIC if metric_type == "actionability" else EVIDENCE_RUBRIC
    
    for score_range, description in rubric.items():
        if score_range[0] <= score <= score_range[1]:
            return description
    
    return "Score out of valid range (1-10)"

# Add project path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import LLM client for judge evaluation
try:
    from llm_clients import llm_Llama3_70B_JudgeClient
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Please ensure running from project root directory")
    sys.exit(1)


class LLMJudgeEvaluator:
    """LLM judge evaluator using batch evaluation strategy"""
    
    def __init__(self):
        """Initialize judge LLM client"""
        print("🔧 Initializing LLM Judge Evaluator...")
        
        # Initialize Llama3-70B as judge LLM
        self.judge_llm = llm_Llama3_70B_JudgeClient()
        
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
    
    def find_medical_outputs_for_systems(self, systems: List[str]) -> Dict[str, str]:
        """Find medical outputs files for multiple systems"""
        results_dir = Path(__file__).parent / "results"
        system_files = {}
        
        for system in systems:
            if system == "rag":
                # Use more specific pattern to exclude direct files
                pattern = str(results_dir / "medical_outputs_[0-9]*.json")
            elif system == "direct":
                pattern = str(results_dir / "medical_outputs_direct_*.json")
            else:
                # Future extension: support other systems
                pattern = str(results_dir / f"medical_outputs_{system}_*.json")
            
            print(f"🔍 Searching for {system} with pattern: {pattern}")
            output_files = glob.glob(pattern)
            print(f"🔍 Found files for {system}: {output_files}")
            
            if not output_files:
                raise FileNotFoundError(f"No medical outputs files found for {system} system")
            
            latest_file = max(output_files, key=os.path.getmtime)
            system_files[system] = latest_file
            print(f"📊 Found {system} outputs: {latest_file}")
        
        return system_files
    
    def create_comparison_evaluation_prompt(self, systems_outputs: Dict[str, List[Dict]]) -> str:
        """
        Create comparison evaluation prompt for multiple systems
        
        Args:
            systems_outputs: Dict mapping system names to their medical outputs
        """
        system_names = list(systems_outputs.keys())
        
        prompt_parts = [
            "You are a medical expert evaluating and comparing AI systems for clinical advice quality.",
            f"Please evaluate {len(system_names)} different systems using the detailed rubrics below:",
            "",
            "EVALUATION RUBRICS:",
            "",
            "METRIC 1: Clinical Actionability (1-10 scale)",
            "Question: Can healthcare providers immediately act on this advice?",
            "1-2 points: Almost no actionable advice; extremely abstract or empty responses.",
            "3-4 points: Provides directional suggestions but too vague, lacks clear steps.",
            "5-6 points: Offers basic executable steps but lacks details for key aspects.",
            "7-8 points: Clear and complete steps that clinicians can follow with occasional gaps.",
            "9-10 points: Extremely actionable with precise, step-by-step executable guidance.",
            "",
            "METRIC 2: Clinical Evidence Quality (1-10 scale)", 
            "Question: Is the advice evidence-based and follows medical standards?",
            "1-2 points: Almost no evidence support; cites irrelevant or unreliable sources.",
            "3-4 points: References lower quality literature or sources lack authority.",
            "5-6 points: Uses general quality literature/guidelines but lacks depth or currency.",
            "7-8 points: References reliable, authoritative sources with accurate explanations.",
            "9-10 points: Rich, high-quality evidence sources combined with latest research.",
            "",
            "TARGET THRESHOLDS: Actionability ≥7.0, Evidence Quality ≥7.5",
            ""
        ]
        
        # Add system descriptions
        for i, system in enumerate(system_names, 1):
            if system == "rag":
                prompt_parts.append(f"SYSTEM {i} (RAG): Uses medical guidelines + LLM for evidence-based advice")
            elif system == "direct":
                prompt_parts.append(f"SYSTEM {i} (Direct): Uses LLM only without external guidelines")
            else:
                prompt_parts.append(f"SYSTEM {i} ({system.upper()}): {system} medical AI system")
        
        prompt_parts.extend([
            "",
            "EVALUATION CRITERIA:",
            "1. Clinical Actionability (1-10): Can healthcare providers immediately act on this advice?",
            "2. Clinical Evidence Quality (1-10): Is the advice evidence-based and follows medical standards?",
            "",
            "QUERIES TO EVALUATE:",
            ""
        ])
        
        # Get all queries (assuming all systems processed same queries)
        first_system = system_names[0]
        queries = systems_outputs[first_system]
        
        # Add each query with all system responses
        for i, query_data in enumerate(queries, 1):
            query = query_data.get('query', '')
            category = query_data.get('category', 'unknown')
            
            prompt_parts.extend([
                f"=== QUERY {i} ({category.upper()}) ===",
                f"Patient Query: {query}",
                ""
            ])
            
            # Add each system's response
            for j, system in enumerate(system_names, 1):
                system_query = systems_outputs[system][i-1]  # Get corresponding query from this system
                advice = system_query.get('medical_advice', '')
                
                prompt_parts.extend([
                    f"SYSTEM {j} Response: {advice}",
                    ""
                ])
        
        prompt_parts.extend([
            "RESPONSE FORMAT (provide exactly this format):",
            ""
        ])
        
        # Add response format template
        for i in range(1, len(queries) + 1):
            for j, system in enumerate(system_names, 1):
                prompt_parts.append(f"Query {i} System {j}: Actionability=X, Evidence=Y")
        
        prompt_parts.extend([
            "",
            "Replace X and Y with numeric scores 1-10.",
            "Provide only the scores in the exact format above.",
            f"Note: System 1={system_names[0]}, System 2={system_names[1] if len(system_names) > 1 else 'N/A'}"
        ])
        
        return "\n".join(prompt_parts)
    
    def parse_comparison_evaluation_response(self, response: str, systems_outputs: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Parse comparison evaluation response into results by system"""
        results_by_system = {}
        system_names = list(systems_outputs.keys())
        
        # Initialize results for each system
        for system in system_names:
            results_by_system[system] = []
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse format: "Query X System Y: Actionability=A, Evidence=B"
            match = re.match(r'Query\s+(\d+)\s+System\s+(\d+):\s*Actionability\s*=\s*(\d+)\s*,\s*Evidence\s*=\s*(\d+)', line, re.IGNORECASE)
            
            if match:
                query_num = int(match.group(1)) - 1  # 0-based index
                system_num = int(match.group(2)) - 1  # 0-based index
                actionability_score = int(match.group(3))
                evidence_score = int(match.group(4))
                
                if system_num < len(system_names) and query_num < len(systems_outputs[system_names[system_num]]):
                    system_name = system_names[system_num]
                    output = systems_outputs[system_name][query_num]
                    
                    result = {
                        "query": output.get('query', ''),
                        "category": output.get('category', 'unknown'),
                        "system_type": system_name,
                        "medical_advice": output.get('medical_advice', ''),
                        
                        # Metric 5: Clinical Actionability
                        "actionability_score": actionability_score / 10.0,
                        "actionability_raw": actionability_score,
                        
                        # Metric 6: Clinical Evidence Quality
                        "evidence_score": evidence_score / 10.0,
                        "evidence_raw": evidence_score,
                        
                        "evaluation_success": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    results_by_system[system_name].append(result)
        
        return results_by_system
    
    def evaluate_multiple_systems(self, systems_outputs: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Evaluate multiple systems using single LLM call for comparison
        
        Args:
            systems_outputs: Dict mapping system names to their medical outputs
        """
        system_names = list(systems_outputs.keys())
        total_queries = len(systems_outputs[system_names[0]])
        
        print(f"🧠 Multi-system comparison: {', '.join(system_names)}")
        print(f"📊 Evaluating {total_queries} queries across {len(system_names)} systems...")
        
        try:
            # Create comparison evaluation prompt
            comparison_prompt = self.create_comparison_evaluation_prompt(systems_outputs)
            
            print(f"📝 Comparison prompt created ({len(comparison_prompt)} characters)")
            print(f"🔄 Calling judge LLM for multi-system comparison...")
            
            # Single LLM call for all systems comparison
            eval_start = time.time()
            response = self.judge_llm.batch_evaluate(comparison_prompt)
            eval_time = time.time() - eval_start
            
            # Extract response text
            response_text = response.get('content', '') if isinstance(response, dict) else str(response)
            
            print(f"✅ Judge LLM completed comparison evaluation in {eval_time:.2f}s")
            print(f"📄 Response length: {len(response_text)} characters")
            
            # Parse comparison response
            results_by_system = self.parse_comparison_evaluation_response(response_text, systems_outputs)
            
            # Combine all results for storage
            all_results = []
            for system_name, system_results in results_by_system.items():
                all_results.extend(system_results)
                print(f"📊 {system_name.upper()}: {len(system_results)} evaluations parsed")
            
            self.evaluation_results.extend(all_results)
            
            return results_by_system
            
        except Exception as e:
            print(f"❌ Multi-system evaluation failed: {e}")
            
            # Create error results for all systems
            error_results = {}
            for system_name, outputs in systems_outputs.items():
                error_results[system_name] = []
                for output in outputs:
                    error_result = {
                        "query": output.get('query', ''),
                        "category": output.get('category', 'unknown'),
                        "system_type": system_name,
                        "actionability_score": 0.0,
                        "evidence_score": 0.0,
                        "evaluation_success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    error_results[system_name].append(error_result)
                self.evaluation_results.extend(error_results[system_name])
            
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
    
    def save_comparison_statistics(self, systems: List[str], filename: str = None) -> str:
        """Save comparison evaluation statistics for multiple systems"""
        stats = self.calculate_judge_statistics()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            systems_str = "_vs_".join(systems)
            filename = f"judge_evaluation_comparison_{systems_str}_{timestamp}.json"
        
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        filepath = results_dir / filename
        
        # Add comparison metadata
        stats["comparison_metadata"] = {
            "systems_compared": systems,
            "comparison_type": "multi_system",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add detailed system-specific results for chart generation
        stats["detailed_system_results"] = {}
        for system in systems:
            system_results = [r for r in self.evaluation_results if r.get('system_type') == system and r.get('evaluation_success')]
            stats["detailed_system_results"][system] = {
                "results": system_results,
                "query_count": len(system_results),
                "avg_actionability": sum(r['actionability_score'] for r in system_results) / len(system_results) if system_results else 0.0,
                "avg_evidence": sum(r['evidence_score'] for r in system_results) / len(system_results) if system_results else 0.0
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Comparison evaluation statistics saved to: {filepath}")
        return str(filepath)


# Independent execution interface
if __name__ == "__main__":
    """Independent LLM judge evaluation interface with multi-system support"""
    
    print("🧠 OnCall.ai LLM Judge Evaluator - Metrics 5-6 Multi-System Evaluation")
    
    # Print evaluation rubrics for reference
    print_evaluation_rubrics()
    
    if len(sys.argv) < 2:
        print("Usage: python metric5_6_llm_judge_evaluator.py [system1] or [system1,system2,...]")
        print("  rag         - Evaluate RAG system medical outputs")
        print("  direct      - Evaluate direct LLM medical outputs") 
        print("  rag,direct  - Compare RAG vs Direct systems")
        print("  system1,system2,system3  - Compare multiple systems")
        sys.exit(1)
    
    # Parse systems from command line
    systems_input = sys.argv[1]
    systems = [s.strip() for s in systems_input.split(',')]
    
    # Initialize evaluator
    evaluator = LLMJudgeEvaluator()
    
    try:
        if len(systems) == 1:
            # Single system evaluation (legacy mode)
            system = systems[0]
            print(f"\n🧪 Single System LLM Judge Evaluation: {system.upper()}")
            
            # Find and load medical outputs for single system
            system_files = evaluator.find_medical_outputs_for_systems([system])
            medical_outputs = evaluator.load_medical_outputs(system_files[system])
            
            if not medical_outputs:
                print(f"❌ No medical outputs found for {system}")
                sys.exit(1)
            
            print(f"📊 Evaluating {len(medical_outputs)} medical advice outputs")
            print(f"🎯 Metrics: 5 (Actionability) + 6 (Evidence Quality)")
            
            # Convert to multi-system format for consistency
            systems_outputs = {system: medical_outputs}
            results_by_system = evaluator.evaluate_multiple_systems(systems_outputs)
            
            # Save results
            stats_path = evaluator.save_comparison_statistics([system])
            
        else:
            # Multi-system comparison evaluation  
            print(f"\n🧪 Multi-System Comparison: {' vs '.join([s.upper() for s in systems])}")
            
            # Find and load medical outputs for all systems
            system_files = evaluator.find_medical_outputs_for_systems(systems)
            systems_outputs = {}
            
            for system in systems:
                outputs = evaluator.load_medical_outputs(system_files[system])
                if not outputs:
                    print(f"❌ No medical outputs found for {system}")
                    sys.exit(1)
                systems_outputs[system] = outputs
            
            # Validate all systems have same number of queries
            query_counts = [len(outputs) for outputs in systems_outputs.values()]
            if len(set(query_counts)) > 1:
                print(f"⚠️ Warning: Systems have different query counts: {dict(zip(systems, query_counts))}")
            
            # Validate systems processed same queries (for scientific comparison)
            print(f"🔍 Validating query consistency across systems...")
            if len(systems) > 1:
                first_system_queries = [q['query'] for q in systems_outputs[systems[0]]]
                for i, system in enumerate(systems[1:], 1):
                    system_queries = [q['query'] for q in systems_outputs[system]]
                    
                    if first_system_queries != system_queries:
                        print(f"⚠️ Warning: {systems[0]} and {system} processed different queries!")
                        # Show first difference
                        for j, (q1, q2) in enumerate(zip(first_system_queries, system_queries)):
                            if q1 != q2:
                                print(f"   Query {j+1} differs:")
                                print(f"   {systems[0]}: {q1[:50]}...")
                                print(f"   {system}: {q2[:50]}...")
                                break
                    else:
                        print(f"✅ {systems[0]} and {system} processed identical queries")
            
            # Validate systems have different model types
            model_types = set()
            for system, outputs in systems_outputs.items():
                if outputs:
                    model_type = outputs[0].get('model_type', 'unknown')
                    model_types.add(model_type)
                    print(f"🏷️ {system.upper()} system model_type: {model_type}")
            
            if len(model_types) == 1:
                print(f"⚠️ Warning: All systems have same model_type - this may not be a valid comparison!")
            else:
                print(f"✅ Systems have different model_types: {model_types}")
            
            print(f"📊 Comparing {len(systems)} systems with {min(query_counts)} queries each")
            print(f"🎯 Metrics: 5 (Actionability) + 6 (Evidence Quality)")
            print(f"⚡ Strategy: Single comparison call for maximum consistency")
            
            # Multi-system comparison evaluation
            results_by_system = evaluator.evaluate_multiple_systems(systems_outputs)
            
            # Save comparison results
            stats_path = evaluator.save_comparison_statistics(systems)
        
        # Print summary
        print(f"\n📊 Generating evaluation analysis...")
        stats = evaluator.calculate_judge_statistics()
        overall_results = stats['overall_results']
        
        print(f"\n📊 === LLM JUDGE EVALUATION SUMMARY ===")
        
        if len(systems) == 1:
            print(f"System: {systems[0].upper()}")
        else:
            print(f"Systems Compared: {' vs '.join([s.upper() for s in systems])}")
        
        print(f"Overall Performance:")
        actionability_raw = overall_results['average_actionability'] * 10
        evidence_raw = overall_results['average_evidence'] * 10
        
        print(f"   Average Actionability: {overall_results['average_actionability']:.3f} ({actionability_raw:.1f}/10)")
        print(f"   • {get_rubric_description(int(actionability_raw), 'actionability')}")
        print(f"   Average Evidence Quality: {overall_results['average_evidence']:.3f} ({evidence_raw:.1f}/10)")
        print(f"   • {get_rubric_description(int(evidence_raw), 'evidence')}")
        print(f"   Actionability Target (≥7.0): {'✅ Met' if overall_results['actionability_target_met'] else '❌ Not Met'}")
        print(f"   Evidence Target (≥7.5): {'✅ Met' if overall_results['evidence_target_met'] else '❌ Not Met'}")
        
        # System-specific breakdown for multi-system comparison
        if len(systems) > 1:
            print(f"\nSystem Breakdown:")
            for system in systems:
                system_results = [r for r in evaluator.evaluation_results if r.get('system_type') == system and r.get('evaluation_success')]
                if system_results:
                    avg_action = sum(r['actionability_score'] for r in system_results) / len(system_results)
                    avg_evidence = sum(r['evidence_score'] for r in system_results) / len(system_results)
                    print(f"   {system.upper()}: Actionability={avg_action:.3f}, Evidence={avg_evidence:.3f} [{len(system_results)} queries]")
        
        print(f"\n✅ LLM judge evaluation complete!")
        print(f"📊 Statistics: {stats_path}")
        print(f"⚡ Efficiency: {overall_results['total_queries']} evaluations in 1 LLM call")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print(f"💡 Please run evaluators first:")
        for system in systems:
            if system == "rag":
                print("   python latency_evaluator.py single_test_query.txt")
            elif system == "direct":
                print("   python direct_llm_evaluator.py single_test_query.txt")
            else:
                print(f"   python {system}_evaluator.py single_test_query.txt")
    except Exception as e:
        print(f"❌ Judge evaluation failed: {e}")
