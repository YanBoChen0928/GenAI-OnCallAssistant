"""
OnCall.ai Medical Advice Generation Module

This module handles:  
1. RAG prompt construction from retrieval results
2. Medical advice generation using Med42-70B
3. Response formatting and confidence assessment
4. Integration with multi-dataset architecture
5. Fallback generation mechanisms for reliability

Author: OnCall.ai Team
Date: 2025-07-31
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import re

# Import existing LLM client
from llm_clients import llm_Med42_70BClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fallback Generation Configuration
FALLBACK_TIMEOUTS = {
    "primary": 30.0,        # Primary Med42-70B with full RAG context
    "fallback_1": 15.0,     # Simplified Med42-70B without RAG
    "fallback_2": 1.0       # RAG template generation (instant)
}

FALLBACK_TOKEN_LIMITS = {
    "primary": 800,         # Full comprehensive medical advice
    "fallback_1": 300,      # Concise medical guidance
    "fallback_2": 0         # Template-based, no LLM tokens
}

FALLBACK_CONFIDENCE_SCORES = {
    "fallback_1": 0.6,      # Med42-70B without RAG context
    "fallback_2": 0.4       # RAG template only
}

FALLBACK_ERROR_TRIGGERS = {
    "timeout_errors": ["TimeoutError", "RequestTimeout"],
    "connection_errors": ["ConnectionError", "HTTPError", "APIError"], 
    "processing_errors": ["TokenLimitError", "JSONDecodeError", "ValidationError"],
    "content_errors": ["EmptyResponse", "MalformedResponse"]
}

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
        
        # Select chunks based on intention or intelligent defaults
        selected_chunks = self._select_chunks_by_intention(
            intention=intention,
            emergency_chunks=emergency_chunks,
            treatment_chunks=treatment_chunks,
            symptom_chunks=symptom_chunks,
            diagnosis_chunks=diagnosis_chunks
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
            "diagnosis_subset": []     # Reserved for Dataset B
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
        
        # TODO: Future integration point for Dataset B
        # When Dataset B team provides symptom/diagnosis data:
        # classified["symptom_subset"] = process_dataset_b_symptoms(retrieval_results)
        # classified["diagnosis_subset"] = process_dataset_b_diagnosis(retrieval_results)
        
        logger.info(f"Classified chunks: Emergency={len(classified['emergency_subset'])}, "
                   f"Treatment={len(classified['treatment_subset'])}")
        
        return classified

    def _select_chunks_by_intention(self, intention: Optional[str], 
                                   emergency_chunks: List, treatment_chunks: List,
                                   symptom_chunks: List, diagnosis_chunks: List) -> List:
        """
        Select optimal chunk combination based on query intention
        
        Args:
            intention: Detected or specified intention  
            *_chunks: Chunks from different dataset sources
            
        Returns:
            List of selected chunks for prompt construction
        """
        if intention and intention in self.dataset_priorities:
            # Use predefined priorities for known intentions
            priorities = self.dataset_priorities[intention]
            selected_chunks = []
            
            # Add chunks according to priority allocation
            selected_chunks.extend(emergency_chunks[:priorities["emergency_subset"]])
            selected_chunks.extend(treatment_chunks[:priorities["treatment_subset"]])
            
            # TODO: Future Dataset B integration
            # selected_chunks.extend(symptom_chunks[:priorities["symptom_subset"]])
            # selected_chunks.extend(diagnosis_chunks[:priorities["diagnosis_subset"]])
            
            logger.info(f"Selected chunks by intention '{intention}': {len(selected_chunks)} total")
            
        else:
            # No specific intention - let LLM judge from best available chunks
            all_chunks = emergency_chunks + treatment_chunks + symptom_chunks + diagnosis_chunks
            
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
        Generate medical advice using Med42-70B with comprehensive fallback support
        
        This method implements the complete 3-tier fallback system:
        1. Primary: Med42-70B with full RAG context
        2. Fallback 1: Med42-70B with simplified prompt  
        3. Fallback 2: RAG template response
        4. Final: Error response
        
        Args:
            prompt: Complete RAG prompt
            
        Returns:
            Generation result with metadata and fallback information
        """
        try:
            logger.info("🤖 GENERATION: Attempting Med42-70B with RAG context")
            
            result = self.llm_client.analyze_medical_query(
                query=prompt,
                max_tokens=FALLBACK_TOKEN_LIMITS["primary"],  # Use configured token limit
                timeout=FALLBACK_TIMEOUTS["primary"]         # Use configured timeout
            )
            
            # Check for API errors in response
            if result.get('error'):
                logger.warning(f"⚠️  Med42-70B returned error: {result['error']}")
                # Attempt fallback instead of raising exception
                return self._attempt_fallback_generation(prompt, result['error'])
            
            # Check for empty response
            if not result.get('raw_response', '').strip():
                logger.warning("⚠️  Med42-70B returned empty response")
                return self._attempt_fallback_generation(prompt, "Empty response from primary generation")
            
            # Primary generation successful
            logger.info("✅ GENERATION: Med42-70B with RAG successful")
            # Mark as primary method for tracking
            result['fallback_method'] = 'primary'
            return result
            
        except Exception as e:
            logger.error(f"❌ GENERATION: Med42-70B with RAG failed: {e}")
            # Attempt fallback chain instead of raising exception
            return self._attempt_fallback_generation(prompt, str(e))

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

    def _attempt_fallback_generation(self, original_prompt: str, primary_error: str) -> Dict[str, Any]:
        """
        Orchestrate fallback generation attempts with detailed logging
        
        This function coordinates the fallback chain when primary Med42-70B generation fails.
        It attempts progressively simpler generation methods while maintaining medical value.
        
        Args:
            original_prompt: The complete RAG prompt that failed in primary generation
            primary_error: Error details from the primary generation attempt
            
        Returns:
            Dict containing successful fallback response or final error response
        """
        logger.info("🔄 FALLBACK: Attempting fallback generation strategies")
        
        # Fallback 1: Simplified Med42-70B without RAG context
        try:
            logger.info("📍 FALLBACK 1: Med42-70B without RAG context")
            fallback_1_result = self._attempt_simplified_med42(original_prompt, primary_error)
            
            if not fallback_1_result.get('error'):
                logger.info("✅ FALLBACK 1: Success - Med42-70B without RAG")
                # Mark response as fallback method 1
                fallback_1_result['fallback_method'] = 'med42_simplified'
                fallback_1_result['primary_error'] = primary_error
                return fallback_1_result
            else:
                logger.warning(f"❌ FALLBACK 1: Failed - {fallback_1_result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ FALLBACK 1: Exception - {e}")
        
        # Fallback 2: RAG-only template response
        try:
            logger.info("📍 FALLBACK 2: RAG-only template response")
            fallback_2_result = self._attempt_rag_template(original_prompt, primary_error)
            
            if not fallback_2_result.get('error'):
                logger.info("✅ FALLBACK 2: Success - RAG template response")
                # Mark response as fallback method 2
                fallback_2_result['fallback_method'] = 'rag_template'
                fallback_2_result['primary_error'] = primary_error
                return fallback_2_result
            else:
                logger.warning(f"❌ FALLBACK 2: Failed - {fallback_2_result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ FALLBACK 2: Exception - {e}")
        
        # All fallbacks failed - return comprehensive error response
        logger.error("🚫 ALL FALLBACKS FAILED: Returning final error response")
        return self._generate_final_error_response(original_prompt, primary_error)

    def _generate_final_error_response(self, original_prompt: str, primary_error: str) -> Dict[str, Any]:
        """
        Generate final error response when all fallback methods fail
        
        Args:
            original_prompt: Original RAG prompt that failed
            primary_error: Primary generation error details  
            
        Returns:
            Comprehensive error response with fallback attempt details
        """
        return {
            'extracted_condition': '',
            'confidence': '0',
            'raw_response': 'All generation methods failed. Please try rephrasing your query or contact technical support.',
            'error': f"Primary: {primary_error}. All fallback methods failed.",
            'fallback_method': 'none',
            'latency': 0.0
        }

    def _attempt_simplified_med42(self, original_prompt: str, primary_error: str) -> Dict[str, Any]:
        """
        Attempt Med42-70B generation with simplified prompt (Fallback 1)
        
        This method retries generation using the same Med42-70B model but with:
        - Simplified prompt (user query only, no RAG context)
        - Reduced timeout (15 seconds)
        - Reduced token limit (300 tokens)
        - Higher success probability due to reduced complexity
        
        Args:
            original_prompt: Original RAG prompt that failed
            primary_error: Error from primary generation attempt
            
        Returns:
            Dict with generation result or error details
        """
        logger.info("📍 FALLBACK 1: Med42-70B without RAG context")
        
        try:
            # Extract user query from complex RAG prompt
            user_query = self._extract_user_query_from_prompt(original_prompt)
            
            if not user_query:
                logger.error("❌ FALLBACK 1: Failed to extract user query from prompt")
                return {
                    'error': 'Unable to extract user query from original prompt',
                    'fallback_method': 'med42_simplified'
                }
            
            # Create simplified prompt for Med42-70B
            simplified_prompt = f"As a medical professional, provide concise clinical guidance for the following case: {user_query}"
            
            logger.info(f"🔄 FALLBACK 1: Calling Med42-70B with simplified prompt (max_tokens={FALLBACK_TOKEN_LIMITS['fallback_1']}, timeout={FALLBACK_TIMEOUTS['fallback_1']}s)")
            
            # Call Med42-70B with reduced parameters
            result = self.llm_client.analyze_medical_query(
                query=simplified_prompt,
                max_tokens=FALLBACK_TOKEN_LIMITS["fallback_1"],  # 300 tokens
                timeout=FALLBACK_TIMEOUTS["fallback_1"]         # 15 seconds
            )
            
            # Check for API errors
            if result.get('error'):
                logger.warning(f"❌ FALLBACK 1: API error - {result['error']}")
                return {
                    'error': f"Med42-70B API error: {result['error']}",
                    'fallback_method': 'med42_simplified',
                    'primary_error': primary_error
                }
            
            # Check for empty response
            raw_response = result.get('raw_response', '').strip()
            if not raw_response:
                logger.warning("❌ FALLBACK 1: Empty response from Med42-70B")
                return {
                    'error': 'Empty response from simplified Med42-70B call',
                    'fallback_method': 'med42_simplified'
                }
            
            # Success - format response with fallback metadata
            logger.info("✅ FALLBACK 1: Success - Med42-70B without RAG")
            
            # Adjust confidence score for fallback method
            original_confidence = float(result.get('confidence', '0.5'))
            fallback_confidence = min(original_confidence, FALLBACK_CONFIDENCE_SCORES['fallback_1'])
            
            return {
                'extracted_condition': result.get('extracted_condition', 'simplified_med42_response'),
                'confidence': str(fallback_confidence),
                'raw_response': raw_response,
                'fallback_method': 'med42_simplified',
                'primary_error': primary_error,
                'latency': result.get('latency', 0),
                'simplified_prompt_used': True
            }
            
        except Exception as e:
            logger.error(f"❌ FALLBACK 1: Exception during simplified Med42-70B call - {e}")
            return {
                'error': f"Exception in simplified Med42-70B: {str(e)}",
                'fallback_method': 'med42_simplified',
                'primary_error': primary_error
            }

    def _attempt_rag_template(self, original_prompt: str, primary_error: str) -> Dict[str, Any]:
        """
        Generate template-based response using available RAG context (Fallback 2)
        
        This method creates a structured response using retrieved medical guidelines
        without LLM processing:
        - Instant response (no API calls)
        - Template-based formatting
        - Uses extracted RAG context from original prompt
        - Lower confidence score (0.4)
        
        Args:
            original_prompt: Original RAG prompt that failed
            primary_error: Error from primary generation attempt
            
        Returns:
            Dict with template response or error details
        """
        logger.info("📍 FALLBACK 2: RAG-only template response")
        
        try:
            # Extract user query and RAG context from original prompt
            user_query = self._extract_user_query_from_prompt(original_prompt)
            rag_context = self._extract_rag_context_from_prompt(original_prompt)
            
            if not user_query:
                logger.error("❌ FALLBACK 2: Failed to extract user query")
                return {
                    'error': 'Unable to extract user query for template response',
                    'fallback_method': 'rag_template'
                }
            
            if not rag_context:
                logger.warning("⚠️  FALLBACK 2: No RAG context available, using minimal template")
                # Create minimal response without RAG context
                template_response = self._generate_minimal_template_response(user_query)
            else:
                # Create full template response with RAG context
                template_response = self._generate_rag_template_response(user_query, rag_context)
            
            logger.info("✅ FALLBACK 2: Success - RAG template response")
            
            return {
                'extracted_condition': 'rag_template_response',
                'confidence': str(FALLBACK_CONFIDENCE_SCORES['fallback_2']),  # 0.4
                'raw_response': template_response,
                'fallback_method': 'rag_template',
                'primary_error': primary_error,
                'latency': 0.1,  # Nearly instant
                'template_based': True
            }
            
        except Exception as e:
            logger.error(f"❌ FALLBACK 2: Exception during template generation - {e}")
            return {
                'error': f"Exception in RAG template generation: {str(e)}",
                'fallback_method': 'rag_template',
                'primary_error': primary_error
            }

    def _generate_rag_template_response(self, user_query: str, rag_context: str) -> str:
        """
        Create structured template response from RAG content
        
        Args:
            user_query: Original user medical question
            rag_context: Retrieved medical guideline text
            
        Returns:
            Formatted template response string
        """
        # Format RAG content for better readability
        formatted_context = self._format_rag_content(rag_context)
        
        template = f"""Based on available medical guidelines for your query: "{user_query}"

CLINICAL GUIDANCE:
{formatted_context}

IMPORTANT CLINICAL NOTES:
• This guidance is based on standard medical protocols and guidelines
• Individual patient factors may require modifications to these recommendations
• Consider patient-specific contraindications and comorbidities
• Consult with senior physician or specialist for complex cases
• Follow local institutional protocols and policies

SYSTEM NOTE:
This response was generated using medical guidelines only, without advanced clinical reasoning, due to technical limitations with the primary system. For complex cases requiring detailed clinical analysis, please consult directly with medical professionals.

Please ensure appropriate clinical oversight and use professional medical judgment in applying these guidelines."""

        return template

    def _generate_minimal_template_response(self, user_query: str) -> str:
        """
        Create minimal template response when no RAG context is available
        
        Args:
            user_query: Original user medical question
            
        Returns:
            Minimal template response string
        """
        template = f"""Regarding your medical query: "{user_query}"

SYSTEM STATUS:
Due to technical difficulties with our medical guidance system, we cannot provide specific clinical recommendations at this time.

RECOMMENDED ACTIONS:
• Please consult with qualified healthcare providers for immediate clinical guidance
• Contact your primary care physician or relevant specialist
• For emergency situations, seek immediate medical attention
• Consider consulting medical literature or clinical decision support tools

IMPORTANT:
This system experienced technical limitations that prevented access to our medical guideline database. Professional medical consultation is strongly recommended for this query.

Please try rephrasing your question or contact our technical support if the issue persists."""

        return template

    def _format_rag_content(self, rag_context: str) -> str:
        """
        Format RAG context content for better readability in template responses
        
        Args:
            rag_context: Raw RAG context text
            
        Returns:
            Formatted and structured RAG content
        """
        try:
            # Clean up the content
            lines = rag_context.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:  # Skip very short lines
                    # Add bullet points for better structure
                    if not line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                        line = f"• {line}"
                    formatted_lines.append(line)
            
            # Limit to reasonable length
            if len(formatted_lines) > 10:
                formatted_lines = formatted_lines[:10]
                formatted_lines.append("• [Additional guidelines available - truncated for brevity]")
            
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            logger.error(f"Error formatting RAG content: {e}")
            return f"• {rag_context[:500]}..."  # Fallback formatting

    def _extract_user_query_from_prompt(self, rag_prompt: str) -> str:
        """
        Extract original user query from complex RAG prompt structure
        
        This function parses the structured RAG prompt to extract the original
        user medical query, which is needed for simplified Med42-70B calls.
        
        Args:
            rag_prompt: Complete RAG prompt with structure like:
                       'You are an experienced physician...
                        Clinical Question: {user_query}
                        Relevant Medical Guidelines: {context}...'
        
        Returns:
            Extracted user query string, or empty string if extraction fails
        """
        try:
            # Method 1: Look for "Clinical Question:" section
            clinical_question_pattern = r"Clinical Question:\s*\n?\s*(.+?)(?:\n\s*\n|\nRelevant Medical Guidelines|$)"
            match = re.search(clinical_question_pattern, rag_prompt, re.DOTALL | re.IGNORECASE)
            
            if match:
                extracted_query = match.group(1).strip()
                logger.info(f"🎯 Extracted user query via 'Clinical Question' pattern: {extracted_query[:50]}...")
                return extracted_query
            
            # Method 2: Look for common medical query patterns at the start
            # This handles cases where the prompt might be simpler
            lines = rag_prompt.split('\n')
            for line in lines:
                line = line.strip()
                # Skip system instructions and headers
                if (line and 
                    not line.startswith('You are') and 
                    not line.startswith('Provide') and
                    not line.startswith('Instructions') and
                    not line.startswith('Relevant Medical') and
                    len(line) > 10):
                    logger.info(f"🎯 Extracted user query via line parsing: {line[:50]}...")
                    return line
            
            # Method 3: Fallback - return the first substantial line
            for line in lines:
                line = line.strip()
                if len(line) > 20 and not line.startswith(('You are', 'As a', 'Provide')):
                    logger.warning(f"⚠️  Using fallback extraction method: {line[:50]}...")
                    return line
                    
            logger.error("❌ Failed to extract user query from prompt")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error extracting user query: {e}")
            return ""

    def _extract_rag_context_from_prompt(self, rag_prompt: str) -> str:
        """
        Extract RAG context/guidelines from complex RAG prompt structure
        
        This function extracts the medical guideline content for use in
        template-based responses (Fallback 2).
        
        Args:
            rag_prompt: Complete RAG prompt containing medical guidelines
        
        Returns:
            Extracted RAG context string, or empty string if extraction fails
        """
        try:
            # Look for "Relevant Medical Guidelines:" section
            guidelines_pattern = r"Relevant Medical Guidelines:\s*\n?\s*(.+?)(?:\n\s*Instructions:|$)"
            match = re.search(guidelines_pattern, rag_prompt, re.DOTALL | re.IGNORECASE)
            
            if match:
                extracted_context = match.group(1).strip()
                logger.info(f"🎯 Extracted RAG context: {len(extracted_context)} characters")
                return extracted_context
            
            # Fallback: look for any substantial medical content
            lines = rag_prompt.split('\n')
            context_lines = []
            in_context_section = False
            
            for line in lines:
                line = line.strip()
                # Start collecting after finding medical content indicators
                if any(indicator in line.lower() for indicator in ['guideline', 'protocol', 'treatment', 'management', 'clinical']):
                    in_context_section = True
                
                if in_context_section and len(line) > 20:
                    context_lines.append(line)
            
            if context_lines:
                extracted_context = '\n'.join(context_lines)
                logger.info(f"🎯 Extracted RAG context via fallback method: {len(extracted_context)} characters")
                return extracted_context
                
            logger.warning("⚠️  No RAG context found in prompt")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error extracting RAG context: {e}")
            return ""

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
