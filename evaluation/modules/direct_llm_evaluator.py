#!/usr/bin/env python3
"""
Direct LLM Evaluator Module for RAG Comparison

This module evaluates Med42B model without RAG retrieval to establish a baseline
for comparison with the RAG-enhanced system. It provides direct medical advice
generation for the same queries used in hospital customization evaluation.

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from llm_clients import llm_Med42_70BClient


class DirectLLMEvaluator:
    """
    Evaluates Med42B model without RAG retrieval to establish baseline performance.
    
    This class provides direct medical advice generation using only the Med42B LLM,
    without any document retrieval or external knowledge sources. Results can be
    compared with RAG-enhanced responses to measure RAG system value.
    """
    
    def __init__(self, output_dir: str = "evaluation/results"):
        """
        Initialize the direct LLM evaluator.
        
        Args:
            output_dir: Directory to save evaluation results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM client
        try:
            self.llm_client = llm_Med42_70BClient()
            print("✅ Direct LLM evaluator initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize LLM client: {e}")
            raise
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def evaluate_direct_responses(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate queries using direct LLM without RAG.
        
        Args:
            queries: List of query dictionaries with 'id', 'text', and metadata
            
        Returns:
            Complete evaluation results with direct LLM responses
        """
        print("🚀 Starting direct LLM evaluation (no RAG)...")
        print(f"📊 Total queries to evaluate: {len(queries)}")
        
        start_time = time.time()
        results = {
            "evaluation_metadata": {
                "timestamp": self.timestamp,
                "evaluation_type": "direct_llm_baseline",
                "model": "m42-health/Llama3-Med42-70B",
                "retrieval_mode": "none",
                "total_queries": len(queries),
                "successful_queries": 0,
                "failed_queries": 0,
                "total_execution_time": 0
            },
            "query_results": []
        }
        
        for i, query in enumerate(queries):
            print(f"\n📋 Processing query {i+1}/{len(queries)}: {query['id']}")
            print(f"🔍 Query: {query['text']}")
            
            query_start_time = time.time()
            
            try:
                # Generate direct medical advice without RAG
                response = self._generate_direct_medical_advice(query['text'])
                query_end_time = time.time()
                execution_time = query_end_time - query_start_time
                
                query_result = {
                    "query_id": query['id'],
                    "query_text": query['text'],
                    "query_metadata": {
                        "specificity": query.get('specificity', 'unknown'),
                        "category": query.get('category', 'unknown')
                    },
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": {
                        "total_seconds": execution_time,
                        "start_time": datetime.fromtimestamp(query_start_time).isoformat(),
                        "end_time": datetime.fromtimestamp(query_end_time).isoformat()
                    },
                    "direct_llm_response": {
                        "medical_advice": response['content'],
                        "response_length": len(response['content']),
                        "generation_details": response.get('details', {})
                    },
                    "analysis": {
                        "retrieval_used": False,
                        "knowledge_source": "LLM training data only",
                        "response_type": "direct_generation"
                    }
                }
                
                results["evaluation_metadata"]["successful_queries"] += 1
                print(f"✅ Query {query['id']} completed in {execution_time:.2f}s")
                
            except Exception as e:
                query_end_time = time.time()
                execution_time = query_end_time - query_start_time
                
                query_result = {
                    "query_id": query['id'],
                    "query_text": query['text'],
                    "query_metadata": {
                        "specificity": query.get('specificity', 'unknown'),
                        "category": query.get('category', 'unknown')
                    },
                    "success": False,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": {
                        "total_seconds": execution_time,
                        "start_time": datetime.fromtimestamp(query_start_time).isoformat(),
                        "end_time": datetime.fromtimestamp(query_end_time).isoformat()
                    },
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "details": "Failed to generate direct LLM response"
                    }
                }
                
                results["evaluation_metadata"]["failed_queries"] += 1
                print(f"❌ Query {query['id']} failed: {e}")
            
            results["query_results"].append(query_result)
        
        # Calculate total execution time
        end_time = time.time()
        results["evaluation_metadata"]["total_execution_time"] = end_time - start_time
        
        # Save results
        self._save_results(results)
        
        print(f"\n🎉 Direct LLM evaluation completed!")
        print(f"✅ Successful queries: {results['evaluation_metadata']['successful_queries']}")
        print(f"❌ Failed queries: {results['evaluation_metadata']['failed_queries']}")
        print(f"⏱️ Total time: {results['evaluation_metadata']['total_execution_time']:.2f}s")
        
        return results
    
    def _generate_direct_medical_advice(self, query: str) -> Dict[str, Any]:
        """
        Generate medical advice using only the LLM without any retrieval.
        
        Args:
            query: Medical query text
            
        Returns:
            Generated medical advice response
        """
        # Create a comprehensive medical prompt for direct generation
        direct_prompt = f"""You are an experienced emergency medicine physician. A patient presents with the following situation:

{query}

Please provide comprehensive medical advice including:
1. Initial assessment and differential diagnosis
2. Recommended diagnostic tests or procedures
3. Treatment recommendations with specific medications and dosages
4. Risk factors and red flags to monitor
5. When to seek immediate medical attention

Base your response on established medical guidelines and evidence-based medicine. Be specific and actionable while maintaining appropriate medical disclaimers.

Medical Advice:"""

        try:
            # Use the LLM client's direct generation capability
            response = self.llm_client.client.chat.completions.create(
                model="m42-health/Llama3-Med42-70B",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledgeable emergency medicine physician providing evidence-based medical guidance. Your responses should be comprehensive, specific, and actionable while including appropriate medical disclaimers."
                    },
                    {
                        "role": "user", 
                        "content": direct_prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent medical advice
            )
            
            content = response.choices[0].message.content
            
            # Add medical disclaimer
            medical_advice = content + "\n\n**IMPORTANT MEDICAL DISCLAIMER**: This response is generated by an AI system for research purposes only. It should not replace professional medical judgment, clinical examination, or established medical protocols. Always consult with qualified healthcare professionals for actual patient care decisions."
            
            return {
                "content": medical_advice,
                "details": {
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
                    "model": "m42-health/Llama3-Med42-70B",
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating direct medical advice: {e}")
            raise e
    
    def _save_results(self, results: Dict[str, Any]) -> str:
        """
        Save evaluation results to JSON file.
        
        Args:
            results: Complete evaluation results
            
        Returns:
            Path to saved file
        """
        filename = f"direct_llm_evaluation_{self.timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            raise e


def main():
    """
    Main function for standalone testing of direct LLM evaluator.
    """
    print("🧪 Direct LLM Evaluator - Test Mode")
    
    # Load test queries
    queries_file = Path("evaluation/queries/frequency_based_test_queries.json")
    
    if not queries_file.exists():
        print(f"❌ Query file not found: {queries_file}")
        return False
    
    try:
        with open(queries_file, 'r', encoding='utf-8') as f:
            query_data = json.load(f)
        
        queries = query_data['queries']
        print(f"📋 Loaded {len(queries)} test queries")
        
        # Initialize evaluator
        evaluator = DirectLLMEvaluator()
        
        # Run evaluation
        results = evaluator.evaluate_direct_responses(queries)
        
        print(f"\n✅ Direct LLM evaluation completed successfully!")
        print(f"📊 Results: {results['evaluation_metadata']['successful_queries']}/{results['evaluation_metadata']['total_queries']} queries successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return False


if __name__ == "__main__":
    main()