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

# Import our centralized medical conditions configuration
from medical_conditions import (
    CONDITION_KEYWORD_MAPPING, 
    get_condition_keywords, 
    validate_condition
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserPromptProcessor:
    def __init__(self, meditron_client=None, retrieval_system=None):
        """
        Initialize UserPromptProcessor with optional Meditron and retrieval system
        
        Args:
            meditron_client: Optional Meditron client for advanced condition extraction
            retrieval_system: Optional retrieval system for semantic search
        """
        self.meditron_client = meditron_client
        self.retrieval_system = retrieval_system
        self.embedding_model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
        logger.info("UserPromptProcessor initialized")

    def extract_condition_keywords(self, user_query: str) -> Dict[str, str]:
        """
        Extract condition keywords with multi-level fallback
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with condition and keywords
        """
        # Level 1: Predefined Mapping (Fast Path)
        predefined_result = self._predefined_mapping(user_query)
        if predefined_result:
            return predefined_result
        
        # Level 2: Meditron Extraction (if available)
        if self.meditron_client:
            meditron_result = self._extract_with_meditron(user_query)
            if meditron_result:
                return meditron_result
        
        # Level 3: Semantic Search Fallback
        semantic_result = self._semantic_search_fallback(user_query)
        if semantic_result:
            return semantic_result
        
        # Level 4: Generic Medical Search
        generic_result = self._generic_medical_search(user_query)
        if generic_result:
            return generic_result
        
        # No match found
        return {
            'condition': '',
            'emergency_keywords': '',
            'treatment_keywords': ''
        }

    def _predefined_mapping(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Fast predefined condition mapping
        
        Args:
            user_query: User's medical query
        
        Returns:
            Mapped condition keywords or None
        """
        query_lower = user_query.lower()
        
        for condition, mappings in CONDITION_KEYWORD_MAPPING.items():
            if condition.lower() in query_lower:
                logger.info(f"Matched predefined condition: {condition}")
                return {
                    'condition': condition,
                    'emergency_keywords': mappings['emergency'],
                    'treatment_keywords': mappings['treatment']
                }
        
        return None

    def _extract_with_meditron(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Use Meditron for advanced condition extraction
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with condition and keywords, or None
        """
        if not self.meditron_client:
            return None
        
        try:
            meditron_response = self.meditron_client.analyze_medical_query(
                query=user_query,
                max_tokens=100,
                timeout=2.0
            )
            
            extracted_condition = meditron_response.get('extracted_condition', '')
            
            if extracted_condition and validate_condition(extracted_condition):
                condition_details = get_condition_keywords(extracted_condition)
                return {
                    'condition': extracted_condition,
                    'emergency_keywords': condition_details.get('emergency', ''),
                    'treatment_keywords': condition_details.get('treatment', '')
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Meditron condition extraction error: {e}")
            return None

    def _semantic_search_fallback(self, user_query: str) -> Optional[Dict[str, str]]:
        """
        Perform semantic search for condition extraction
        
        Args:
            user_query: User's medical query
        
        Returns:
            Dict with condition and keywords, or None
        """
        if not self.retrieval_system:
            return None
        
        try:
            # Perform semantic search on sliding window chunks
            semantic_results = self.retrieval_system.search_sliding_window_chunks(user_query)
            
            if semantic_results:
                # Extract condition from top semantic result
                top_result = semantic_results[0]
                condition = self._infer_condition_from_text(top_result['text'])
                
                if condition and validate_condition(condition):
                    condition_details = get_condition_keywords(condition)
                    return {
                        'condition': condition,
                        'emergency_keywords': condition_details.get('emergency', ''),
                        'treatment_keywords': condition_details.get('treatment', ''),
                        'semantic_confidence': top_result.get('distance', 0)
                    }
            
            return None
        
        except Exception as e:
            logger.error(f"Semantic search fallback error: {e}")
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
        Infer medical condition from text using embedding similarity
        
        Args:
            text: Input medical text
        
        Returns:
            Inferred condition or None
        """
        # Implement a simple condition inference using embedding similarity
        # This is a placeholder and would need more sophisticated implementation
        conditions = list(CONDITION_KEYWORD_MAPPING.keys())
        text_embedding = self.embedding_model.encode(text)
        condition_embeddings = [self.embedding_model.encode(condition) for condition in conditions]
        
        similarities = [
            np.dot(text_embedding, condition_emb) / 
            (np.linalg.norm(text_embedding) * np.linalg.norm(condition_emb))
            for condition_emb in condition_embeddings
        ]
        
        max_similarity_index = np.argmax(similarities)
        return conditions[max_similarity_index] if similarities[max_similarity_index] > 0.7 else None

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

def main():
    """
    Example usage and testing of UserPromptProcessor
    """
    processor = UserPromptProcessor()
    
    # Test cases
    test_queries = [
        "how to treat acute MI?",
        "patient with stroke symptoms",
        "chest pain and breathing difficulty"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = processor.extract_condition_keywords(query)
        print("Extracted Keywords:", result)
        
        confirmation = processor.handle_user_confirmation(result)
        print("Confirmation:", confirmation['message'])

if __name__ == "__main__":
    main() 