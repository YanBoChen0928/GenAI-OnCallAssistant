#!/usr/bin/env python3
"""
Fixed version of metric5_6_llm_judge_evaluator.py with batch processing
Splits large evaluation requests into smaller batches to avoid API limits
"""

import sys
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_clients import llm_Llama3_70B_JudgeClient

class FixedLLMJudgeEvaluator:
    """
    Fixed LLM Judge Evaluator with batch processing for large evaluations
    """
    
    def __init__(self, batch_size: int = 2):
        """
        Initialize with configurable batch size
        
        Args:
            batch_size: Number of queries to evaluate per batch (default: 2)
        """
        self.judge_llm = llm_Llama3_70B_JudgeClient()
        self.evaluation_results = []
        self.batch_size = batch_size
        print(f"✅ Fixed LLM Judge Evaluator initialized with batch_size={batch_size}")
    
    def load_systems_outputs(self, systems: List[str]) -> Dict[str, List[Dict]]:
        """Load outputs from multiple systems for comparison"""
        results_dir = Path(__file__).parent / "results"
        system_files = {}
        
        for system in systems:
            if system == "rag":
                pattern = str(results_dir / "medical_outputs_[0-9]*.json")
            elif system == "direct":
                pattern = str(results_dir / "medical_outputs_direct_*.json")
            else:
                pattern = str(results_dir / f"medical_outputs_{system}_*.json")
            
            print(f"🔍 Searching for {system} with pattern: {pattern}")
            output_files = glob.glob(pattern)
            print(f"🔍 Found files for {system}: {output_files}")
            
            if not output_files:
                raise FileNotFoundError(f"No output files found for system: {system}")
            
            # Use most recent file
            latest_file = max(output_files, key=os.path.getctime)
            print(f"📁 Using latest file for {system}: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                system_files[system] = data['medical_outputs']
        
        return system_files
    
    def create_batch_evaluation_prompt(self, batch_queries: List[Dict], system_names: List[str]) -> str:
        """
        Create evaluation prompt for a small batch of queries
        
        Args:
            batch_queries: Small batch of queries (2-3 queries)
            system_names: Names of systems being compared
            
        Returns:
            Formatted evaluation prompt
        """
        prompt_parts = [
            "MEDICAL AI EVALUATION - BATCH ASSESSMENT",
            "",
            f"You are evaluating {len(system_names)} medical AI systems on {len(batch_queries)} queries.",
            "Rate each response on a scale of 1-10 for:",
            "1. Clinical Actionability: Can healthcare providers immediately act on this advice?",
            "2. Clinical Evidence Quality: Is the advice evidence-based and follows medical standards?",
            "",
            "SYSTEMS:"
        ]
        
        for i, system in enumerate(system_names, 1):
            if system == "rag":
                prompt_parts.append(f"SYSTEM {i} (RAG): Uses medical guidelines + LLM")
            elif system == "direct":
                prompt_parts.append(f"SYSTEM {i} (Direct): Uses LLM only without external guidelines")
            else:
                prompt_parts.append(f"SYSTEM {i} ({system.upper()}): {system} medical AI system")
        
        prompt_parts.extend([
            "",
            "QUERIES TO EVALUATE:",
            ""
        ])
        
        # Add each query with all system responses
        for i, query_batch in enumerate(batch_queries, 1):
            query = query_batch['query']
            category = query_batch['category']
            
            prompt_parts.extend([
                f"=== QUERY {i} ({category.upper()}) ===",
                f"Patient Query: {query}",
                ""
            ])
            
            # Add each system's response
            for j, system in enumerate(system_names, 1):
                advice = query_batch[f'{system}_advice']
                
                # Truncate very long advice to avoid token limits
                if len(advice) > 1500:
                    advice = advice[:1500] + "... [truncated for evaluation]"
                
                prompt_parts.extend([
                    f"SYSTEM {j} Response: {advice}",
                    ""
                ])
        
        prompt_parts.extend([
            "RESPONSE FORMAT (provide exactly this format):",
            ""
        ])
        
        # Add response format template
        for i in range(1, len(batch_queries) + 1):
            for j, system in enumerate(system_names, 1):
                prompt_parts.append(f"Query {i} System {j}: Actionability=X, Evidence=Y")
        
        return '\n'.join(prompt_parts)
    
    def parse_batch_evaluation_response(self, response_text: str, batch_queries: List[Dict], system_names: List[str]) -> List[Dict]:
        """Parse evaluation response for a batch of queries"""
        results = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            # Parse format: "Query X System Y: Actionability=Z, Evidence=W"
            match = re.search(r'Query\s+(\d+)\s+System\s+(\d+):\s*Actionability\s*=\s*(\d+(?:\.\d+)?),?\s*Evidence\s*=\s*(\d+(?:\.\d+)?)', line, re.IGNORECASE)
            
            if match:
                query_num = int(match.group(1)) - 1
                system_num = int(match.group(2)) - 1
                actionability = float(match.group(3))
                evidence = float(match.group(4))
                
                if (0 <= query_num < len(batch_queries) and 
                    0 <= system_num < len(system_names) and
                    1 <= actionability <= 10 and
                    1 <= evidence <= 10):
                    
                    result = {
                        "query": batch_queries[query_num]['query'],
                        "category": batch_queries[query_num]['category'],
                        "system_type": system_names[system_num],
                        "actionability_score": actionability / 10,  # Normalize to 0-1
                        "evidence_score": evidence / 10,  # Normalize to 0-1
                        "evaluation_success": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    results.append(result)
        
        return results
    
    def evaluate_systems_in_batches(self, systems: List[str]) -> Dict[str, List[Dict]]:
        """
        Evaluate multiple systems using batch processing
        
        Args:
            systems: List of system names to compare
            
        Returns:
            Dict with results for each system
        """
        print(f"🚀 Starting batch evaluation for systems: {systems}")
        
        # Load system outputs
        systems_outputs = self.load_systems_outputs(systems)
        
        # Verify all systems have same number of queries
        query_counts = [len(outputs) for outputs in systems_outputs.values()]
        if len(set(query_counts)) > 1:
            print(f"⚠️ Warning: Systems have different query counts: {dict(zip(systems, query_counts))}")
        
        total_queries = min(query_counts)
        print(f"📊 Evaluating {total_queries} queries across {len(systems)} systems...")
        
        # Prepare combined queries for batching
        combined_queries = []
        system_outputs_list = list(systems_outputs.values())
        
        for i in range(total_queries):
            batch_query = {
                'query': system_outputs_list[0][i]['query'],
                'category': system_outputs_list[0][i]['category']
            }
            
            # Add advice from each system
            for j, system_name in enumerate(systems):
                batch_query[f'{system_name}_advice'] = systems_outputs[system_name][i]['medical_advice']
            
            combined_queries.append(batch_query)
        
        # Process in small batches
        all_results = []
        num_batches = (total_queries + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(num_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_queries)
            batch_queries = combined_queries[start_idx:end_idx]
            
            print(f"\n📦 Processing batch {batch_num + 1}/{num_batches} (queries {start_idx + 1}-{end_idx})...")
            
            try:
                # Create batch evaluation prompt
                batch_prompt = self.create_batch_evaluation_prompt(batch_queries, systems)
                
                print(f"📝 Batch prompt created ({len(batch_prompt)} characters)")
                print(f"🔄 Calling judge LLM for batch {batch_num + 1}...")
                
                # Call LLM for this batch
                eval_start = time.time()
                response = self.judge_llm.batch_evaluate(batch_prompt)
                eval_time = time.time() - eval_start
                
                # Extract response text
                response_text = response.get('content', '') if isinstance(response, dict) else str(response)
                
                print(f"✅ Batch {batch_num + 1} completed in {eval_time:.2f}s")
                print(f"📄 Response length: {len(response_text)} characters")
                
                # Parse batch response
                batch_results = self.parse_batch_evaluation_response(response_text, batch_queries, systems)
                all_results.extend(batch_results)
                
                print(f"📊 Batch {batch_num + 1}: {len(batch_results)} evaluations parsed")
                
                # Small delay between batches to avoid rate limiting
                if batch_num < num_batches - 1:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Batch {batch_num + 1} failed: {e}")
                # Continue with next batch rather than stopping
                continue
        
        # Group results by system
        results_by_system = {}
        for system in systems:
            results_by_system[system] = [r for r in all_results if r['system_type'] == system]
        
        self.evaluation_results.extend(all_results)
        
        return results_by_system
    
    def save_comparison_results(self, systems: List[str], filename: str = None) -> str:
        """Save comparison evaluation results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            systems_str = "_vs_".join(systems)
            filename = f"judge_evaluation_comparison_{systems_str}_{timestamp}.json"
        
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        filepath = results_dir / filename
        
        # Calculate statistics
        successful_results = [r for r in self.evaluation_results if r['evaluation_success']]
        
        if successful_results:
            actionability_scores = [r['actionability_score'] for r in successful_results]
            evidence_scores = [r['evidence_score'] for r in successful_results]
            
            overall_stats = {
                "average_actionability": sum(actionability_scores) / len(actionability_scores),
                "average_evidence": sum(evidence_scores) / len(evidence_scores),
                "successful_evaluations": len(successful_results),
                "total_queries": len(self.evaluation_results)
            }
        else:
            overall_stats = {
                "average_actionability": 0.0,
                "average_evidence": 0.0,
                "successful_evaluations": 0,
                "total_queries": len(self.evaluation_results)
            }
        
        # System-specific results
        detailed_system_results = {}
        for system in systems:
            system_results = [r for r in successful_results if r.get('system_type') == system]
            if system_results:
                detailed_system_results[system] = {
                    "results": system_results,
                    "query_count": len(system_results),
                    "avg_actionability": sum(r['actionability_score'] for r in system_results) / len(system_results),
                    "avg_evidence": sum(r['evidence_score'] for r in system_results) / len(system_results)
                }
            else:
                detailed_system_results[system] = {
                    "results": [],
                    "query_count": 0,
                    "avg_actionability": 0.0,
                    "avg_evidence": 0.0
                }
        
        # Save results
        results_data = {
            "category_results": {},  # Would need category analysis
            "overall_results": overall_stats,
            "timestamp": datetime.now().isoformat(),
            "comparison_metadata": {
                "systems_compared": systems,
                "comparison_type": "multi_system_batch",
                "batch_size": self.batch_size,
                "timestamp": datetime.now().isoformat()
            },
            "detailed_system_results": detailed_system_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Comparison evaluation results saved to: {filepath}")
        return str(filepath)


def main():
    """Main execution function"""
    print("🧠 Fixed OnCall.ai LLM Judge Evaluator - Batch Processing Version")
    
    if len(sys.argv) < 2:
        print("Usage: python fixed_judge_evaluator.py [system1,system2,...]")
        print("Examples:")
        print("  python fixed_judge_evaluator.py rag,direct")
        print("  python fixed_judge_evaluator.py rag,direct --batch-size 3")
        return 1
    
    # Parse systems
    systems_arg = sys.argv[1]
    systems = [s.strip() for s in systems_arg.split(',')]
    
    # Parse batch size
    batch_size = 2
    if "--batch-size" in sys.argv:
        batch_idx = sys.argv.index("--batch-size")
        if batch_idx + 1 < len(sys.argv):
            batch_size = int(sys.argv[batch_idx + 1])
    
    print(f"🎯 Systems to evaluate: {systems}")
    print(f"📦 Batch size: {batch_size}")
    
    try:
        # Initialize evaluator
        evaluator = FixedLLMJudgeEvaluator(batch_size=batch_size)
        
        # Run batch evaluation
        results = evaluator.evaluate_systems_in_batches(systems)
        
        # Save results
        results_file = evaluator.save_comparison_results(systems)
        
        # Print summary
        print(f"\n✅ Fixed batch evaluation completed!")
        print(f"📊 Results saved to: {results_file}")
        
        # Show system comparison
        for system, system_results in results.items():
            if system_results:
                avg_actionability = sum(r['actionability_score'] for r in system_results) / len(system_results)
                avg_evidence = sum(r['evidence_score'] for r in system_results) / len(system_results)
                print(f"  🏥 {system.upper()}: Actionability={avg_actionability:.3f}, Evidence={avg_evidence:.3f} ({len(system_results)} queries)")
            else:
                print(f"  ❌ {system.upper()}: No successful evaluations")
        
        return 0
        
    except Exception as e:
        print(f"❌ Fixed judge evaluation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
