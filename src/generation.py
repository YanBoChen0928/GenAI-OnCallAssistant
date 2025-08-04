"""
OnCall.ai Medical Advice Generation Module

This module handles:  
1. RAG prompt construction from retrieval results
2. Medical advice generation using Med42-70B
3. Response formatting and confidence assessment
4. Integration with multi-dataset architecture

Author: OnCall.ai Team
Date: 2025-07-31
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json

# Import existing LLM client
from llm_clients import llm_Med42_70BClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MedicalAdviceGenerator:
    """
    Core generation module for medical advice using RAG approach
    """
    
    def __init__(self, llm_client: Optional[llm_Med42_70BClient] = None):
        """
        Initialize medical advice generator
        
        Args:
            llm_client: Optional Med42-70B client, creates new if None
        """
        self.llm_client = llm_client or llm_Med42_70BClient()
        
        # Dataset source priorities for different intentions
        self.dataset_priorities = {
            "treatment": {
                "emergency_subset": 2,
                "treatment_subset": 4,
                "symptom_subset": 0,      # Reserved for Dataset B
                "diagnosis_subset": 0     # Reserved for Dataset B
            },
            "diagnosis": {
                "emergency_subset": 4,
                "treatment_subset": 2,
                "symptom_subset": 0,      # Reserved for Dataset B  
                "diagnosis_subset": 0     # Reserved for Dataset B
            },
            # "STAT": {
            #     # NOTE: Use when query contains urgent indicators like "NOW", "STAT", "critical"
            #     "emergency_subset": 5,
            #     "treatment_subset": 1,
            #     "symptom_subset": 0,      # Reserved for Dataset B
            #     "diagnosis_subset": 0     # Reserved for Dataset B
            # }
        }
        
        logger.info("MedicalAdviceGenerator initialized")

    def generate_medical_advice(self, user_query: str, retrieval_results: Dict[str, Any], 
                               intention: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete pipeline: construct prompt → generate advice → format response
        
        Args:
            user_query: Original user medical query
            retrieval_results: Results from BasicRetrievalSystem.search()
            intention: Optional query intention ('treatment', 'diagnosis', 'STAT'(tentative))
            
        Returns:
            Dict containing formatted medical advice and metadata
        """
        try:
            logger.info(f"Generating medical advice for query: '{user_query[:50]}...'")
            start_time = datetime.now()
            
            # Step 1: Extract and classify chunks from retrieval results
            classified_chunks = self._classify_retrieval_chunks(retrieval_results)
            
            # Step 2: Build RAG prompt based on intention and chunk classification
            rag_prompt = self.generate_prompt(user_query, classified_chunks, intention)
            
            # Step 3: Generate medical advice using Med42-70B
            generation_result = self._generate_with_med42(rag_prompt)
            
            # Step 4: Format structured response
            formatted_response = self._format_medical_response(
                user_query=user_query,
                generated_advice=generation_result,
                chunks_used=classified_chunks,
                intention=intention,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            processing_duration = formatted_response.get('query_metadata', {}).get('processing_time_seconds', 0)
            logger.info(f"Medical advice generated successfully in {processing_duration:.3f}s")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Medical advice generation failed: {e}")
            return self._generate_error_response(user_query, str(e))

    def generate_prompt(self, user_query: str, classified_chunks: Dict[str, List], 
                       intention: Optional[str] = None) -> str:
        """
        Enhanced prompt generator with flexible dataset integration
        
        Args:
            user_query: User's medical query
            classified_chunks: Chunks classified by dataset source
            intention: Query intention if detected
            
        Returns:
            Structured RAG prompt for Med42-70B
        """
        logger.info(f"Generating prompt with intention: {intention}")
        
        # Extract chunks by dataset source
        emergency_chunks = classified_chunks.get("emergency_subset", [])
        treatment_chunks = classified_chunks.get("treatment_subset", [])
        symptom_chunks = classified_chunks.get("symptom_subset", [])      # Dataset B (future)
        diagnosis_chunks = classified_chunks.get("diagnosis_subset", [])  # Dataset B (future)
        hospital_custom_chunks = classified_chunks.get("hospital_custom", [])  # Hospital customization
        
        # Select chunks based on intention or intelligent defaults
        selected_chunks = self._select_chunks_by_intention(
            intention=intention,
            emergency_chunks=emergency_chunks,
            treatment_chunks=treatment_chunks,
            symptom_chunks=symptom_chunks,
            diagnosis_chunks=diagnosis_chunks,
            hospital_custom_chunks=hospital_custom_chunks
        )
        
        # Build context block from selected chunks
        context_block = self._build_context_block(selected_chunks)
        
        # Construct medical RAG prompt
        prompt = self._construct_medical_prompt(user_query, context_block, intention)
        
        logger.info(f"Generated prompt with {len(selected_chunks)} chunks, {len(context_block)} chars")
        return prompt

    def _classify_retrieval_chunks(self, retrieval_results: Dict[str, Any]) -> Dict[str, List]:
        """
        Classify retrieval chunks by dataset source
        
        Args:
            retrieval_results: Results from BasicRetrievalSystem.search()
            
        Returns:
            Dict mapping dataset sources to chunk lists
        """
        classified = {
            "emergency_subset": [],
            "treatment_subset": [],
            "symptom_subset": [],      # Reserved for Dataset B
            "diagnosis_subset": [],     # Reserved for Dataset B
            "hospital_custom": []      # Hospital-specific customization
        }
        
        # Process results from current dual-index system
        processed_results = retrieval_results.get('processed_results', [])
        
        for chunk in processed_results:
            chunk_type = chunk.get('type', 'unknown')
            
            # Map current system types to dataset sources
            if chunk_type == 'emergency':
                classified["emergency_subset"].append(chunk)
            elif chunk_type == 'treatment':
                classified["treatment_subset"].append(chunk)
            else:
                # Unknown type, classify by content analysis or default to STAT (tentative)
                logger.warning(f"Unknown chunk type: {chunk_type}, defaulting to STAT (tentative)")
                classified["emergency_subset"].append(chunk)
        
        # Process hospital customization results if available
        customization_results = retrieval_results.get('customization_results', [])
        if customization_results:
            for custom_chunk in customization_results:
                # Convert customization format to standard chunk format
                standardized_chunk = {
                    'type': 'hospital_custom',
                    'text': custom_chunk.get('chunk_text', ''),
                    'distance': 1 - custom_chunk.get('score', 0),  # Convert score to distance
                    'matched': f"Hospital Doc: {custom_chunk.get('document', 'Unknown')}",
                    'metadata': custom_chunk.get('metadata', {})
                }
                classified["hospital_custom"].append(standardized_chunk)
            logger.info(f"Added {len(customization_results)} hospital-specific chunks")
        
        # TODO: Future integration point for Dataset B
        # When Dataset B team provides symptom/diagnosis data:
        # classified["symptom_subset"] = process_dataset_b_symptoms(retrieval_results)
        # classified["diagnosis_subset"] = process_dataset_b_diagnosis(retrieval_results)
        
        logger.info(f"Classified chunks: Emergency={len(classified['emergency_subset'])}, "
                   f"Treatment={len(classified['treatment_subset'])}, "
                   f"Hospital Custom={len(classified['hospital_custom'])}")
        
        return classified

    def _select_chunks_by_intention(self, intention: Optional[str], 
                                   emergency_chunks: List, treatment_chunks: List,
                                   symptom_chunks: List, diagnosis_chunks: List,
                                   hospital_custom_chunks: List = None) -> List:
        """
        Select optimal chunk combination based on query intention
        
        Args:
            intention: Detected or specified intention  
            *_chunks: Chunks from different dataset sources
            hospital_custom_chunks: Hospital-specific customization chunks
            
        Returns:
            List of selected chunks for prompt construction
        """
        hospital_custom_chunks = hospital_custom_chunks or []
        
        if intention and intention in self.dataset_priorities:
            # Use predefined priorities for known intentions
            priorities = self.dataset_priorities[intention]
            selected_chunks = []
            
            # Add chunks according to priority allocation
            selected_chunks.extend(emergency_chunks[:priorities["emergency_subset"]])
            selected_chunks.extend(treatment_chunks[:priorities["treatment_subset"]])
            
            # Add hospital custom chunks alongside
            selected_chunks.extend(hospital_custom_chunks)
            
            # TODO: Future Dataset B integration
            # selected_chunks.extend(symptom_chunks[:priorities["symptom_subset"]])
            # selected_chunks.extend(diagnosis_chunks[:priorities["diagnosis_subset"]])
            
            logger.info(f"Selected chunks by intention '{intention}': {len(selected_chunks)} total")
            
        else:
            # No specific intention - let LLM judge from best available chunks
            all_chunks = emergency_chunks + treatment_chunks + symptom_chunks + diagnosis_chunks + hospital_custom_chunks
            
            # Sort by relevance (distance) and take top 6
            all_chunks_sorted = sorted(all_chunks, key=lambda x: x.get("distance", 999))
            selected_chunks = all_chunks_sorted[:6]
            
            logger.info(f"Selected chunks by relevance (no intention): {len(selected_chunks)} total")
        
        return selected_chunks

    def _build_context_block(self, selected_chunks: List) -> str:
        """
        Build formatted context block from selected chunks
        
        Args:
            selected_chunks: List of selected chunks
            
        Returns:
            Formatted context string for prompt
        """
        if not selected_chunks:
            return "No relevant medical guidelines found."
        
        context_parts = []
        
        for i, chunk in enumerate(selected_chunks, 1):
            chunk_text = chunk.get("text", "").strip()
            chunk_type = chunk.get("type", "unknown")
            distance = chunk.get("distance", 0)
            
            # Format each chunk with metadata
            if chunk_type == 'hospital_custom':
                # Special formatting for hospital-specific guidelines
                source_label = "Hospital Protocol"
                context_part = f"""
[Guideline {i}] (Source: {source_label}, Relevance: {1-distance:.3f})
📋 {chunk.get('matched', 'Hospital Document')}
{chunk_text}
                """.strip()
            else:
                context_part = f"""
[Guideline {i}] (Source: {chunk_type.title()}, Relevance: {1-distance:.3f})
{chunk_text}
                """.strip()
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)

    def _construct_medical_prompt(self, user_query: str, context_block: str, 
                                 intention: Optional[str]) -> str:
        """
        Construct final medical RAG prompt with appropriate framing
        
        Args:
            user_query: Original user query
            context_block: Formatted context from selected chunks
            intention: Query intention if detected
            
        Returns:
            Complete RAG prompt for Med42-70B
        """
        # Customize prompt based on intention
        if intention == "treatment":
            focus_guidance = "Focus on providing specific treatment protocols, management steps, and therapeutic interventions."
        elif intention == "diagnosis":  
            focus_guidance = "Focus on differential diagnosis, diagnostic criteria, and assessment approaches."
        elif intention == "STAT(tentative)":
            focus_guidance = "Focus on immediate emergency interventions and critical decision-making steps."
        else:
            focus_guidance = "Provide comprehensive medical guidance covering both diagnostic and treatment aspects as appropriate."
        
        prompt = f"""
        You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

        Clinical Question:
        {user_query}

        Relevant Medical Guidelines:
        {context_block}

        Instructions:
        {focus_guidance}

        Provide guidance with:
        • Numbered points (1. 2. 3.) for key steps
        • Line breaks between major sections
        • Highlight medications with dosages and routes
        • Reference evidence from above sources
        • Emphasize clinical judgment

        IMPORTANT: Keep response within 700 tokens. If approaching this limit, prioritize the most critical steps and conclude with a brief summary of remaining considerations.

        Your response should be concise but comprehensive, suitable for immediate clinical application with appropriate medical caution."""

        return prompt

    def _generate_with_med42(self, prompt: str) -> Dict[str, Any]:
        """
        Generate medical advice using Med42-70B
        
        Args:
            prompt: Complete RAG prompt
            
        Returns:
            Generation result with metadata
        """
        try:
            logger.info("Calling Med42-70B for medical advice generation")
            
            result = self.llm_client.analyze_medical_query(
                query=prompt,
                max_tokens=800,  # Adjust based on needs
                timeout=30.0     # Allow more time for complex medical advice
            )
            
            if result.get('error'):
                raise Exception(f"Med42-70B generation error: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Med42-70B generation failed: {e}")
            raise

    def _format_medical_response(self, user_query: str, generated_advice: Dict[str, Any],
                                chunks_used: Dict[str, List], intention: Optional[str],
                                processing_time: float) -> Dict[str, Any]:
        """
        Format final medical response with metadata and confidence assessment
        
        Args:
            user_query: Original query
            generated_advice: Result from Med42-70B
            chunks_used: Classification of chunks used
            intention: Detected intention
            processing_time: Total processing time
            
        Returns:
            Structured medical advice response
        """
        # Extract generated content - use raw_response for complete medical advice
        advice_content = generated_advice.get('raw_response', '')
        if not advice_content:
            advice_content = generated_advice.get('extracted_condition', 'Unable to generate medical advice.')
        
        # Calculate confidence based on available factors
        confidence_score = self._calculate_confidence_score(generated_advice, chunks_used)
        
        # Count chunks used by source
        chunk_counts = {source: len(chunks) for source, chunks in chunks_used.items()}
        total_chunks = sum(chunk_counts.values())
        
        formatted_response = {
            "medical_advice": advice_content,
            "confidence_score": confidence_score,
            "query_metadata": {
                "original_query": user_query,
                "detected_intention": intention,
                "processing_time_seconds": processing_time,
                "total_chunks_used": total_chunks,
                "chunks_by_source": chunk_counts
            },
            "generation_metadata": {
                "model_used": "m42-health/Llama3-Med42-70B",
                "generation_time": generated_advice.get('latency', 0),
                "model_confidence": generated_advice.get('confidence', 'unknown'),
                "timestamp": datetime.now().isoformat()
            },
            "sources": {
                "emergency_sources": len(chunks_used.get("emergency_subset", [])),
                "treatment_sources": len(chunks_used.get("treatment_subset", [])),
                "total_sources": total_chunks
            },
            "disclaimer": "This advice is for informational purposes only and should not replace professional medical consultation. Always consult with qualified healthcare providers for medical decisions."
        }
        
        return formatted_response

    def _calculate_confidence_score(self, generated_advice: Dict[str, Any], 
                                   chunks_used: Dict[str, List]) -> float:
        """
        Calculate confidence score based on generation quality and source reliability
        
        Args:
            generated_advice: Result from Med42-70B
            chunks_used: Chunks used in generation
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_factors = []
        
        # Factor 1: Model confidence if available
        model_confidence = generated_advice.get('confidence', '0.5')
        try:
            model_conf_value = float(model_confidence)
            confidence_factors.append(model_conf_value)
        except (ValueError, TypeError):
            confidence_factors.append(0.5)  # Default neutral confidence
        
        # Factor 2: Number of sources used (more sources = higher confidence)
        total_chunks = sum(len(chunks) for chunks in chunks_used.values())
        source_confidence = min(total_chunks / 6.0, 1.0)  # Normalize to max 6 chunks
        confidence_factors.append(source_confidence)
        
        # Factor 3: Response length (reasonable length indicates comprehensive advice)
        response_length = len(generated_advice.get('raw_response', ''))
        length_confidence = min(response_length / 500.0, 1.0)  # Normalize to ~500 chars
        confidence_factors.append(length_confidence)
        
        # Factor 4: Processing success (no errors = higher confidence)
        if generated_advice.get('error'):
            confidence_factors.append(0.3)  # Lower confidence if errors occurred
        else:
            confidence_factors.append(0.8)  # Higher confidence for clean generation
        
        # Calculate weighted average
        final_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Ensure confidence is within valid range
        return max(0.1, min(0.95, final_confidence))

    def _generate_error_response(self, user_query: str, error_message: str) -> Dict[str, Any]:
        """
        Generate error response when generation fails
        
        Args:
            user_query: Original query
            error_message: Error details
            
        Returns:
            Error response in standard format
        """
        return {
            "medical_advice": "I apologize, but I encountered an error while processing your medical query. Please try rephrasing your question or contact technical support if the issue persists.",
            "confidence_score": 0.0,
            "query_metadata": {
                "original_query": user_query,
                "detected_intention": None,
                "processing_time_seconds": 0.0,
                "total_chunks_used": 0,
                "chunks_by_source": {}
            },
            "generation_metadata": {
                "model_used": "m42-health/Llama3-Med42-70B",
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            },
            "sources": {
                "emergency_sources": 0,
                "treatment_sources": 0,
                "total_sources": 0
            },
            "disclaimer": "This system experienced a technical error. Please consult with qualified healthcare providers for medical decisions."
        }

# Example usage and testing
def main():
    """
    Test the medical advice generation system
    """
    # Initialize generator 
    generator = MedicalAdviceGenerator()
    
    # Example retrieval results (simulated)
    example_retrieval_results = {
        "processed_results": [
            {
                "type": "emergency", 
                "distance": 0.3,
                "text": "Acute myocardial infarction requires immediate assessment including ECG, cardiac enzymes, and chest X-ray. Time-sensitive condition requiring rapid intervention.",
                "matched": "MI|chest pain"
            },
            {
                "type": "treatment",
                "distance": 0.25, 
                "text": "Treatment protocol for STEMI includes aspirin 325mg, clopidogrel loading dose, and urgent PCI within 90 minutes when available.",
                "matched_treatment": "aspirin|PCI|thrombolytic"
            }
        ]
    }
    
    # Test queries
    test_queries = [
        ("How should I treat a patient with chest pain?", "treatment"),
        ("What are the signs of acute MI?", "diagnosis"),
        # ("Emergency management of cardiac arrest", "STAT(tentative)")
    ]
    
    for query, intention in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: {query}")
        print(f"Intention: {intention}")
        
        try:
            result = generator.generate_medical_advice(
                user_query=query,
                retrieval_results=example_retrieval_results,
                intention=intention
            )
            
            print(f"✅ Success: {result['confidence_score']:.2f} confidence")
            print(f"Advice: {result['medical_advice'][:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
