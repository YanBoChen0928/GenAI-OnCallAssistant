"""
OnCall.ai User Prompt Processing Module

This module handles:
1. Condition extraction from user queries
2. Keyword mapping
3. User confirmation workflow
4. Fallback mechanisms

Author: OnCall.ai Team
Date: 2025-07-29
"""

import logging
from typing import Dict, Optional, Any, List
from sentence_transformers import SentenceTransformer
import numpy as np # Added missing import for numpy
import os # Added missing import for os
import json # Added missing import for json
import re # Added missing import for re

# Import our centralized medical conditions configuration
from medical_conditions import (
    CONDITION_KEYWORD_MAPPING, 
    CONDITION_REGEX_MAPPING,
    get_condition_details, 
    validate_condition
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserPromptProcessor:
    def __init__(self, llm_client=None, retrieval_system=None):
        """
        Initialize UserPromptProcessor with optional LLM and retrieval system
        
        Args:
            llm_client: Optional Llama3-Med42-70B client for advanced condition extraction
            retrieval_system: Optional retrieval system for semantic search
        """
        self.llm_client = llm_client
        self.retrieval_system = retrieval_system
        self.embedding_model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
        
        # Add embeddings directory path
        self.embeddings_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'embeddings')
        
        logger.info("UserPromptProcessor initialized")

    def _extract_condition_from_query(self, user_query: str) -> Optional[str]:
        """
        Unified condition extraction with flexible matching
        
        Args:
            user_query: User's medical query
        
        Returns:
            Standardized condition name or None
        """
        if not user_query:
            return None
        
        query_lower = user_query.lower().strip()
        
        # Level 1: Direct exact matching (fastest)
        for condition in CONDITION_KEYWORD_MAPPING.keys():
            if condition.lower() in query_lower:
                logger.info(f"🎯 Direct match found: {condition}")
                return condition
        
        # Level 2: Regular expression matching (flexible)
        for regex_pattern, mapped_condition in CONDITION_REGEX_MAPPING.items():
            if re.search(regex_pattern, query_lower, re.IGNORECASE):
                logger.info(f"🎯 Regex match found: {regex_pattern} → {mapped_condition}")
                return mapped_condition
        
        # Level 3: Partial keyword matching (fallback)
        medical_keywords_mapping = {
            'coronary': 'acute_coronary_syndrome',
            'myocardial': 'acute myocardial infarction',
            'stroke': 'acute stroke',
            'embolism': 'pulmonary embolism'
        }
        
        for keyword, condition in medical_keywords_mapping.items():
            if keyword in query_lower:
                logger.info(f"🎯 Keyword match found: {keyword} → {condition}")
                return condition
        
        return None

    def extract_condition_keywords(self, user_query: str) -> Dict[str, str]:
        """
        Extract condition keywords with multi-level fallback
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with condition and keywords
        """
        logger.info(f"🔍 Starting condition extraction for query: '{user_query}'")
 
        # Level 1: Predefined Mapping (Fast Path)
        logger.info("📍 LEVEL 1: Attempting predefined mapping...")
        predefined_result = self._predefined_mapping(user_query)
        if predefined_result:
            logger.info("✅ LEVEL 1: SUCCESS - Found predefined mapping")
            return predefined_result
        logger.info("❌ LEVEL 1: FAILED - No predefined mapping found")
        
        # Level 2: Llama3-Med42-70B Extraction (if available)
        logger.info("📍 LEVEL 2: Attempting LLM extraction...")
        if self.llm_client:
            llm_result = self._extract_with_llm(user_query)
            if llm_result:
                logger.info("✅ LEVEL 2: SUCCESS - LLM extraction successful")
                return llm_result
            logger.info("❌ LEVEL 2: FAILED - LLM extraction failed")
        else:
            logger.info("⏭️  LEVEL 2: SKIPPED - No LLM client available")
        
        # Level 3: Semantic Search Fallback
        logger.info("📍 LEVEL 3: Attempting semantic search...")
        semantic_result = self._semantic_search_fallback(user_query)
        if semantic_result:
            logger.info("✅ LEVEL 3: SUCCESS - Semantic search successful")
            return semantic_result
        logger.info("❌ LEVEL 3: FAILED - Semantic search failed")
        
        # Level 4: Medical Query Validation
        logger.info("📍 LEVEL 4: Validating medical query...")
        # Only validate if previous levels failed - speed optimization
        validation_result = self.validate_medical_query(user_query)
        if validation_result:  # If validation fails (returns non-None)
            logger.info("❌ LEVEL 4: FAILED - Query identified as non-medical")
            return validation_result
        logger.info("✅ LEVEL 4: PASSED - Query validated as medical, continuing...")
        
        # Level 5: Generic Medical Search (after validation passes)
        logger.info("📍 LEVEL 5: Attempting generic medical search...")
        generic_result = self._generic_medical_search(user_query)
        if generic_result:
            logger.info("✅ LEVEL 5: SUCCESS - Generic medical search successful")
            return generic_result
        logger.info("❌ LEVEL 5: FAILED - Generic medical search failed")
        
        # No match found
        logger.warning("🚫 ALL LEVELS FAILED - Returning empty result")
        return {
            'condition': '',
            'emergency_keywords': '',
            'treatment_keywords': ''
        }

    def _predefined_mapping(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Fast predefined condition mapping using unified extraction
        
        Args:
            user_query: User's medical query
        
        Returns:
            Mapped condition keywords or None
        """
        # Use unified condition extraction
        condition = self._extract_condition_from_query(user_query)
        
        if condition:
            # Get condition details using the flexible matching
            condition_details = get_condition_details(condition)
            if condition_details:
                logger.info(f"✅ Level 1 matched condition: {condition}")
                return {
                    'condition': condition,
                    'emergency_keywords': condition_details['emergency'],
                    'treatment_keywords': condition_details['treatment']
                }
        
        return None

    def _extract_with_llm(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Use Llama3-Med42-70B for advanced condition extraction
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with condition and keywords, or None
        """
        if not self.llm_client:
            return None
        
        try:
            llama_response = self.llm_client.analyze_medical_query(
                query=user_query,
                max_tokens=100,
                timeout=2.0
            )
            
            llm_extracted_condition = llama_response.get('extracted_condition', '')
            logger.info(f"🤖 LLM extracted condition: {llm_extracted_condition}")
            
            if llm_extracted_condition:
                # Use unified condition extraction for validation and standardization
                standardized_condition = self._extract_condition_from_query(llm_extracted_condition)
                
                if standardized_condition:
                    condition_details = get_condition_details(standardized_condition)
                    if condition_details:
                        logger.info(f"✅ Level 2 standardized condition: {standardized_condition}")
                        return {
                            'condition': standardized_condition,
                            'emergency_keywords': condition_details['emergency'],
                            'treatment_keywords': condition_details['treatment']
                        }
            
            return None
        
        except Exception as e:
            logger.error(f"Llama3-Med42-70B condition extraction error: {e}")
            return None

    def _semantic_search_fallback(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Perform semantic search for condition extraction using sliding window chunks
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with condition and keywords, or None
        """
        logger.info(f"Starting semantic search fallback for query: '{user_query}'")
        
        if not self.retrieval_system:
            logger.warning("No retrieval system available for semantic search")
            return None
        
        try:
            # Perform semantic search on sliding window chunks
            semantic_results = self.retrieval_system.search_sliding_window_chunks(user_query)
            
            logger.info(f"Semantic search returned {len(semantic_results)} results")
            
            if semantic_results:
                # Extract condition from top semantic result
                top_result = semantic_results[0]
                condition = self._infer_condition_from_text(top_result['text'])
                
                logger.info(f"Inferred condition: {condition}")
                
                if condition and validate_condition(condition):
                    condition_details = get_condition_details(condition)
                    if condition_details:
                        result = {
                            'condition': condition,
                            'emergency_keywords': condition_details.get('emergency', ''),
                            'treatment_keywords': condition_details.get('treatment', ''),
                            'semantic_confidence': top_result.get('distance', 0)
                        }
                    
                    logger.info(f"Semantic search successful. Condition: {condition}, "
                                f"Confidence: {result['semantic_confidence']}")
                    return result
                else:
                    logger.warning(f"Condition validation failed for: {condition}")
            
            logger.info("No suitable condition found in semantic search")
            return None
        
        except Exception as e:
            logger.error(f"Semantic search fallback error: {e}", exc_info=True)
            return None

    def _generic_medical_search(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Perform generic medical search as final fallback
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with generic medical keywords
        """
        generic_medical_terms = [
            "medical", "treatment", "management", "protocol",
            "guidelines", "emergency", "acute", "chronic"
        ]
        
        generic_query = f"{user_query} medical treatment"
        
        try:
            # Check if query contains any generic medical terms
            if not any(term in generic_query.lower() for term in generic_medical_terms):
                logger.info("No generic medical terms found in query")
                return None
            
            # Check if retrieval system is available
            if not self.retrieval_system:
                logger.warning("No retrieval system available for generic search")
                return None

            # Perform generic medical search
            generic_results = self.retrieval_system.search_generic_medical_content(generic_query)
            
            if generic_results:
                return {
                    'condition': 'generic medical query',
                    'emergency_keywords': 'medical|emergency',
                    'treatment_keywords': 'treatment|management',
                    'generic_confidence': 0.5
                }

            return None 
        except Exception as e:
            logger.error(f"Generic medical search error: {e}")
            return None

    def _infer_condition_from_text(self, text: str) -> Optional[str]:
        """
        Infer medical condition from text using angular distance
        
        Args:
            text: Input medical text
        
        Returns:
            Inferred condition or None
        """
        # Implement condition inference using angular distance (consistent with retrieval system)
        conditions = list(CONDITION_KEYWORD_MAPPING.keys())
        text_embedding = self.embedding_model.encode(text)
        condition_embeddings = [self.embedding_model.encode(condition) for condition in conditions]
        
        # Calculate cosine similarities first
        similarities = [
            np.dot(text_embedding, condition_emb) / 
            (np.linalg.norm(text_embedding) * np.linalg.norm(condition_emb))
            for condition_emb in condition_embeddings
        ]
        
        # Convert to angular distances
        angular_distances = [np.arccos(np.clip(sim, -1, 1)) for sim in similarities]
        
        # Find minimum angular distance (most similar)
        min_distance_index = np.argmin(angular_distances)
        min_distance = angular_distances[min_distance_index]
        
        # Use angular distance threshold of 1.0 (approximately 57 degrees)
        if min_distance < 1.0:
            logger.info(f"Condition inferred: {conditions[min_distance_index]}, angular distance: {min_distance:.3f}")
            return conditions[min_distance_index]
        else:
            logger.info(f"No condition found within angular distance threshold. Min distance: {min_distance:.3f}")
            return None

    def validate_keywords(self, keywords: Dict[str, str]) -> bool:
        """
        Validate if extracted keywords exist in our medical indices
        
        Args:
            keywords: Dict of emergency and treatment keywords
        
        Returns:
            Boolean indicating keyword validity
        """
        emergency_kws = keywords.get('emergency_keywords', '').split('|')
        treatment_kws = keywords.get('treatment_keywords', '').split('|')
        
        # Basic validation: check if any keyword is non-empty
        return any(kw.strip() for kw in emergency_kws + treatment_kws)

    def _check_keyword_in_index(self, keyword: str, index_type: str) -> bool:
        """
        Check if a keyword exists in the specified medical index
        
        Args:
            keyword: Keyword to check
            index_type: Type of index ('emergency' or 'treatment')
        
        Returns:
            Boolean indicating keyword existence in the index
        """
        # Validate input parameters
        if not keyword or not index_type:
            logger.warning(f"Invalid input: keyword='{keyword}', index_type='{index_type}'")
            return False
        
        # Supported index types
        valid_index_types = ['emergency', 'treatment']
        if index_type not in valid_index_types:
            logger.error(f"Unsupported index type: {index_type}")
            return False
        
        try:
            # Construct path to chunks file
            chunks_path = os.path.join(self.embeddings_dir, f"{index_type}_chunks.json")
            
            # Check file existence
            if not os.path.exists(chunks_path):
                logger.error(f"Index file not found: {chunks_path}")
                return False
            
            # Load chunks with error handling
            with open(chunks_path, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            # Normalize keyword for flexible matching
            keyword_lower = keyword.lower().strip()
            
            # Advanced keyword matching
            for chunk in chunks:
                chunk_text = chunk.get('text', '').lower()
                
                # Exact match
                if keyword_lower in chunk_text:
                    logger.info(f"Exact match found for '{keyword}' in {index_type} index")
                    return True
                
                # Partial match with word boundaries
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', chunk_text):
                    logger.info(f"Partial match found for '{keyword}' in {index_type} index")
                    return True
            
            # No match found
            logger.info(f"No match found for '{keyword}' in {index_type} index")
            return False
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {chunks_path}")
            return False
        except IOError as e:
            logger.error(f"IO error reading {chunks_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in _check_keyword_in_index: {e}")
            return False

    def handle_user_confirmation(self, extracted_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Handle user confirmation for extracted condition and keywords
        
        Args:
            extracted_info: Dict with condition and keyword information
        
        Returns:
            Dict with confirmation status and options
        """
        # If no condition found, request user to rephrase
        if not extracted_info.get('condition'):
            return {
                'type': 'rephrase_needed',
                'message': "Could not identify a specific medical condition. Please rephrase your query.",
                'suggestions': [
                    "Try: 'how to treat chest pain'",
                    "Try: 'acute stroke management'",
                    "Try: 'pulmonary embolism treatment'"
                ]
            }
        
        # Prepare confirmation message
        confirmation_message = f"""
I understand you're asking about: "{extracted_info.get('condition', 'Unknown Condition')}"

Extracted Keywords:
- Emergency: {extracted_info.get('emergency_keywords', 'None')}
- Treatment: {extracted_info.get('treatment_keywords', 'None')}

Please confirm:
1) Yes, proceed with search
2) No, please rephrase my query
3) Modify keywords
        """
        
        return {
            'type': 'confirmation_needed',
            'message': confirmation_message,
            'extracted_info': extracted_info
        }

    def _handle_matching_failure_level1(self, condition: str) -> Optional[Dict[str, Any]]:
        """
        Level 1 Fallback: Loose keyword matching for medical conditions
        
        Args:
            condition: The condition to match loosely
        
        Returns:
            Dict with matched keywords or None
        """
        # Predefined loose matching keywords for different medical domains
        loose_medical_keywords = {
            'emergency': [
                'urgent', 'critical', 'severe', 'acute', 
                'immediate', 'life-threatening', 'emergency'
            ],
            'treatment': [
                'manage', 'cure', 'heal', 'recover', 
                'therapy', 'medication', 'intervention'
            ]
        }
        
        # Normalize condition
        condition_lower = condition.lower().strip()
        
        # Check emergency keywords
        emergency_matches = [
            kw for kw in loose_medical_keywords['emergency'] 
            if kw in condition_lower
        ]
        
        # Check treatment keywords
        treatment_matches = [
            kw for kw in loose_medical_keywords['treatment'] 
            if kw in condition_lower
        ]
        
        # If matches found, return result
        if emergency_matches or treatment_matches:
            logger.info(f"Loose keyword match for condition: {condition}")
            return {
                'type': 'loose_keyword_match',
                'condition': condition,
                'emergency_keywords': '|'.join(emergency_matches),
                'treatment_keywords': '|'.join(treatment_matches),
                'confidence': 0.5  # Lower confidence due to loose matching
            }
        
        # No loose matches found
        logger.info(f"No loose keyword match for condition: {condition}")
        return None

    def validate_medical_query(self, user_query: str) -> Dict[str, Any]:
        """
        Validate if the query is a medical-related query using Llama3-Med42-70B multi-layer verification
        
        Args:
            user_query: User's input query
        
        Returns:
            Dict with validation result or None if medical query
        """
        # Expanded medical keywords covering comprehensive medical terminology
        predefined_medical_keywords = {
            # Symptoms and signs
            'pain', 'symptom', 'ache', 'fever', 'inflammation', 
            'bleeding', 'swelling', 'rash', 'bruise', 'wound',
            
            # Medical professional terms
            'disease', 'condition', 'syndrome', 'disorder', 
            'medical', 'health', 'diagnosis', 'treatment', 
            'therapy', 'medication', 'prescription',
            
            # Body systems and organs
            'heart', 'lung', 'brain', 'kidney', 'liver', 
            'blood', 'nerve', 'muscle', 'bone', 'joint',
            
            # Medical actions
            'examine', 'check', 'test', 'scan', 'surgery', 
            'operation', 'emergency', 'urgent', 'critical',
            
            # Specific medical fields
            'cardiology', 'neurology', 'oncology', 'pediatrics', 
            'psychiatry', 'dermatology', 'orthopedics'
        }
        
        # Check if query contains predefined medical keywords
        query_lower = user_query.lower()
        if any(kw in query_lower for kw in predefined_medical_keywords):
            return None  # Validated by predefined keywords
        
        try:
            # Ensure Llama3-Med42-70B client is properly initialized
            if not hasattr(self, 'llm_client') or self.llm_client is None:
                self.logger.warning("Llama3-Med42-70B client not initialized")
                return self._generate_invalid_query_response()
            
            # Use Llama3-Med42-70B for final medical query determination
            llama_result = self.llm_client.analyze_medical_query(
                query=user_query,
                max_tokens=100  # Limit tokens for efficiency
            )
            
            # If Llama3-Med42-70B successfully extracts a medical condition
            if llama_result.get('extracted_condition'):
                return None  # Validated by Llama3-Med42-70B
            
        except Exception as e:
            # Log Llama3-Med42-70B analysis failure without blocking the process
            self.logger.warning(f"Llama3-Med42-70B query validation failed: {e}")
        
        # If no medical relevance is found
        return self._generate_invalid_query_response()

    def _generate_invalid_query_response(self) -> Dict[str, Any]:
        """
        Generate response for non-medical queries
        
        Returns:
            Dict with invalid query guidance
        """
        return {
            'type': 'invalid_query',
            'message': "This is OnCall.AI, a clinical medical assistance platform. "
                       "Please input a medical problem you need help resolving. "
                       "\n\nExamples:\n"
                       "- 'I'm experiencing chest pain'\n"
                       "- 'What are symptoms of stroke?'\n"
                       "- 'How to manage acute asthma?'\n"
                       "- 'I have a persistent headache'"
        }

def main():
    """
    Example usage and testing of UserPromptProcessor with Llama3-Med42-70B
    Demonstrates condition extraction and query validation
    """
    from .retrieval import BasicRetrievalSystem

    # use relative import to avoid circular import
    from .llm_clients import llm_Med42_70BClient
    
    # Initialize LLM client
    llm_client = llm_Med42_70BClient()
    retrieval_system = BasicRetrievalSystem()
    
    # Initialize UserPromptProcessor with the LLM client
    processor = UserPromptProcessor(
        llm_client=llm_client, retrieval_system=retrieval_system
    )
    
    # Update test cases with more representative medical queries
    test_queries = [
        "patient with severe chest pain and shortness of breath",
        "sudden neurological symptoms suggesting stroke",
        "persistent headache with vision changes"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = processor.extract_condition_keywords(query)
        print("Extracted Keywords:", result)
        
        confirmation = processor.handle_user_confirmation(result)
        print("Confirmation:", confirmation['message'])

if __name__ == "__main__":
    main() 