#!/usr/bin/env python3
"""
Query Executor Module for OnCall.ai Evaluation Framework

This module provides functionality to execute medical queries through the OnCall.ai
RAG pipeline and collect comprehensive evaluation data including timing, responses,
and retrieval results.

Author: OnCall.ai Evaluation Team
Date: 2025-08-05
Version: 1.0.0
"""

import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sys
import os

# Add project root to path for imports
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

from app import OnCallAIInterface


class QueryExecutor:
    """
    Executes medical queries through the OnCall.ai pipeline and collects evaluation data.
    
    This class provides a modular interface for running evaluation queries,
    collecting timing data, responses, and retrieval information for analysis.
    """
    
    def __init__(self):
        """Initialize the QueryExecutor with OnCall.ai interface."""
        self.oncall_interface = None
        self.initialization_error = None
        self._initialize_interface()
    
    def _initialize_interface(self):
        """Initialize the OnCall.ai interface with error handling."""
        try:
            print("🔧 Initializing OnCall.ai interface for evaluation...")
            self.oncall_interface = OnCallAIInterface()
            if not self.oncall_interface.initialized:
                raise Exception(f"Interface initialization failed: {self.oncall_interface.initialization_error}")
            print("✅ OnCall.ai interface initialized successfully")
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ Failed to initialize OnCall.ai interface: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def load_queries(self, queries_file: str) -> List[Dict[str, Any]]:
        """
        Load test queries from JSON file.
        
        Args:
            queries_file: Path to the JSON file containing test queries
            
        Returns:
            List of query dictionaries with id, text, specificity, and category
            
        Raises:
            FileNotFoundError: If queries file doesn't exist
            json.JSONDecodeError: If queries file is not valid JSON
        """
        try:
            queries_path = Path(queries_file)
            if not queries_path.exists():
                raise FileNotFoundError(f"Queries file not found: {queries_file}")
            
            with open(queries_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            queries = data.get('queries', [])
            print(f"📋 Loaded {len(queries)} test queries from {queries_file}")
            
            # Validate query structure
            for i, query in enumerate(queries):
                required_fields = ['id', 'text', 'specificity', 'category']
                missing_fields = [field for field in required_fields if field not in query]
                if missing_fields:
                    raise ValueError(f"Query {i} missing required fields: {missing_fields}")
            
            return queries
            
        except Exception as e:
            print(f"❌ Error loading queries from {queries_file}: {e}")
            raise
    
    def execute_query(self, query: Dict[str, Any], retrieval_mode: str = "Combine Both") -> Dict[str, Any]:
        """
        Execute a single query through the OnCall.ai pipeline.
        
        Args:
            query: Query dictionary with id, text, specificity, and category
            retrieval_mode: Retrieval strategy ("General Only", "Hospital Only", "Combine Both")
            
        Returns:
            Dictionary containing execution results with timing, response, and metadata
        """
        if not self.oncall_interface or not self.oncall_interface.initialized:
            return {
                "query_id": query.get("id", "unknown"),
                "success": False,
                "error": f"Interface not initialized: {self.initialization_error}",
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"🔍 Executing query: {query['id']} ({query['specificity']})")
        
        # Record start time
        start_time = time.time()
        execution_start = datetime.now()
        
        try:
            # Execute query through OnCall.ai pipeline
            # Note: We set DEBUG_MODE environment variable to get technical details
            original_debug = os.getenv('ONCALL_DEBUG', 'false')
            os.environ['ONCALL_DEBUG'] = 'true'
            
            try:
                result = self.oncall_interface.process_medical_query(
                    user_query=query['text'],
                    retrieval_mode=retrieval_mode
                )
                
                # Handle different return formats based on debug mode
                if len(result) == 4:
                    medical_advice, processing_steps, guidelines_display, technical_details = result
                    technical_details = json.loads(technical_details) if isinstance(technical_details, str) else technical_details
                else:
                    medical_advice, processing_steps, guidelines_display = result
                    technical_details = {}
                
            finally:
                # Restore original debug mode
                os.environ['ONCALL_DEBUG'] = original_debug
            
            # Record end time
            end_time = time.time()
            total_execution_time = end_time - start_time
            
            # Parse processing steps to extract level information
            level_info = self._parse_processing_steps(processing_steps)
            
            # Extract retrieval information
            retrieval_info = self._extract_retrieval_info(guidelines_display, technical_details)
            
            # Build comprehensive result
            execution_result = {
                "query_id": query["id"],
                "query_text": query["text"],
                "query_metadata": {
                    "specificity": query["specificity"],
                    "category": query["category"]
                },
                "success": True,
                "timestamp": execution_start.isoformat(),
                "execution_time": {
                    "total_seconds": total_execution_time,
                    "start_time": execution_start.isoformat(),
                    "end_time": datetime.now().isoformat()
                },
                "retrieval_mode": retrieval_mode,
                "response": {
                    "medical_advice": medical_advice,
                    "processing_steps": processing_steps,
                    "guidelines_display": guidelines_display
                },
                "pipeline_analysis": {
                    "levels_executed": level_info,
                    "retrieval_info": retrieval_info,
                    "technical_details": technical_details
                },
                "error": None
            }
            
            print(f"✅ Query {query['id']} executed successfully in {total_execution_time:.3f}s")
            return execution_result
            
        except Exception as e:
            end_time = time.time()
            total_execution_time = end_time - start_time
            
            error_result = {
                "query_id": query["id"],
                "query_text": query["text"],
                "query_metadata": {
                    "specificity": query["specificity"],
                    "category": query["category"]
                },
                "success": False,
                "timestamp": execution_start.isoformat(),
                "execution_time": {
                    "total_seconds": total_execution_time,
                    "start_time": execution_start.isoformat(),
                    "end_time": datetime.now().isoformat()
                },
                "retrieval_mode": retrieval_mode,
                "response": None,
                "pipeline_analysis": None,
                "error": {
                    "message": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            }
            
            print(f"❌ Query {query['id']} failed: {e}")
            return error_result
    
    def execute_batch(self, queries: List[Dict[str, Any]], retrieval_mode: str = "Combine Both") -> List[Dict[str, Any]]:
        """
        Execute a batch of queries through the OnCall.ai pipeline.
        
        Args:
            queries: List of query dictionaries
            retrieval_mode: Retrieval strategy for all queries
            
        Returns:
            List of execution results for each query
        """
        print(f"🚀 Starting batch execution of {len(queries)} queries with mode: {retrieval_mode}")
        
        results = []
        start_time = time.time()
        
        for i, query in enumerate(queries, 1):
            print(f"\n📋 Processing query {i}/{len(queries)}: {query['id']}")
            
            result = self.execute_query(query, retrieval_mode)
            results.append(result)
            
            # Brief pause between queries to avoid overwhelming the system
            if i < len(queries):
                time.sleep(0.5)
        
        total_time = time.time() - start_time
        successful_queries = sum(1 for r in results if r["success"])
        failed_queries = len(queries) - successful_queries
        
        print(f"\n✅ Batch execution completed in {total_time:.3f}s")
        print(f"📊 Results: {successful_queries} successful, {failed_queries} failed")
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """
        Save execution results to JSON file.
        
        Args:
            results: List of execution results
            output_file: Path to output JSON file
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create comprehensive results structure
            batch_summary = {
                "execution_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_queries": len(results),
                    "successful_queries": sum(1 for r in results if r["success"]),
                    "failed_queries": sum(1 for r in results if not r["success"]),
                    "average_execution_time": sum(r["execution_time"]["total_seconds"] for r in results) / len(results) if results else 0
                },
                "query_results": results
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(batch_summary, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving results to {output_file}: {e}")
            raise
    
    def _parse_processing_steps(self, processing_steps: str) -> Dict[str, Any]:
        """
        Parse processing steps to extract pipeline level information.
        
        Args:
            processing_steps: Processing steps string from pipeline execution
            
        Returns:
            Dictionary containing level execution analysis
        """
        if not processing_steps:
            return {"levels_detected": [], "total_steps": 0}
        
        steps = processing_steps.split('\n')
        levels_detected = []
        step_pattern_map = {
            "Step 1": "condition_extraction",
            "Step 1.5": "hospital_customization", 
            "Step 2": "user_confirmation",
            "Step 3": "guideline_retrieval",
            "Step 4": "advice_generation"
        }
        
        for step in steps:
            for pattern, level_name in step_pattern_map.items():
                if pattern in step and level_name not in levels_detected:
                    levels_detected.append(level_name)
        
        return {
            "levels_detected": levels_detected,
            "total_steps": len([s for s in steps if s.strip()]),
            "step_details": steps
        }
    
    def _extract_retrieval_info(self, guidelines_display: str, technical_details: Dict) -> Dict[str, Any]:
        """
        Extract retrieval information from guidelines display and technical details.
        
        Args:
            guidelines_display: Guidelines display string or JSON
            technical_details: Technical details dictionary
            
        Returns:
            Dictionary containing retrieval analysis
        """
        retrieval_info = {
            "guidelines_found": 0,
            "retrieval_mode_used": "unknown",
            "emergency_guidelines": 0,
            "treatment_guidelines": 0,
            "hospital_guidelines": 0,
            "confidence_scores": []
        }
        
        try:
            # Try to parse as JSON first (debug mode)
            if isinstance(guidelines_display, str) and guidelines_display.strip().startswith('{'):
                guidelines_data = json.loads(guidelines_display)
                if "total_guidelines" in guidelines_data:
                    retrieval_info["guidelines_found"] = guidelines_data["total_guidelines"]
                if "displayed_guidelines" in guidelines_data:
                    for guideline in guidelines_data["displayed_guidelines"]:
                        source_type = guideline.get("source_type", "").lower()
                        if "emergency" in source_type:
                            retrieval_info["emergency_guidelines"] += 1
                        elif "treatment" in source_type:
                            retrieval_info["treatment_guidelines"] += 1
                        
                        # Extract confidence scores
                        relevance = guideline.get("relevance_score", "0")
                        try:
                            score = float(relevance)
                            retrieval_info["confidence_scores"].append(score)
                        except:
                            pass
            
            # Extract from technical details if available
            if technical_details and "retrieval" in technical_details:
                retrieval_data = technical_details["retrieval"]
                retrieval_info["guidelines_found"] = retrieval_data.get("total_results", 0)
                retrieval_info["emergency_guidelines"] = retrieval_data.get("emergency_results", 0)
                retrieval_info["treatment_guidelines"] = retrieval_data.get("treatment_results", 0)
            
            # Check for hospital guidelines in customization results
            if "Hospital Guidelines Found:" in guidelines_display:
                # First extract the count (backward compatibility)
                hospital_count_line = guidelines_display.split("Hospital Guidelines Found:")[1].strip().split('\n')[0]
                hospital_count = hospital_count_line.split()[0] if hospital_count_line else "0"
                try:
                    retrieval_info["hospital_guidelines"] = int(hospital_count)
                except:
                    pass
                
                # Now try to extract similarity scores from embedded JSON
                if "<!--EVAL_DATA:" in guidelines_display:
                    try:
                        import json
                        eval_data_start = guidelines_display.index("<!--EVAL_DATA:") + len("<!--EVAL_DATA:")
                        eval_data_end = guidelines_display.index("-->", eval_data_start)
                        eval_data_json = guidelines_display[eval_data_start:eval_data_end]
                        eval_data = json.loads(eval_data_json)
                        
                        # Extract similarity scores
                        if "similarity_scores" in eval_data:
                            retrieval_info["confidence_scores"] = eval_data["similarity_scores"]
                            print(f"   📊 Extracted {len(eval_data['similarity_scores'])} similarity scores")
                    except Exception as e:
                        print(f"   ⚠️ Could not parse similarity scores: {e}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not fully parse retrieval info: {e}")
        
        return retrieval_info


def main():
    """
    Main function for standalone execution of query evaluation.
    
    Example usage:
        python evaluation/modules/query_executor.py
    """
    print("🏥 OnCall.ai Query Executor - Standalone Mode")
    
    # Initialize executor
    executor = QueryExecutor()
    
    if not executor.oncall_interface or not executor.oncall_interface.initialized:
        print("❌ Cannot run evaluation - OnCall.ai interface initialization failed")
        return 1
    
    # Load queries
    queries_file = "evaluation/queries/test_queries.json"
    try:
        queries = executor.load_queries(queries_file)
    except Exception as e:
        print(f"❌ Failed to load queries: {e}")
        return 1
    
    # Execute queries
    print("\n🚀 Starting evaluation execution...")
    results = executor.execute_batch(queries, retrieval_mode="Combine Both")
    
    # Save results
    output_file = f"evaluation/results/query_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        executor.save_results(results, output_file)
        print(f"\n✅ Evaluation completed successfully!")
        print(f"📊 Results saved to: {output_file}")
        return 0
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)