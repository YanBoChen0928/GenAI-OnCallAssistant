"""
OnCall.ai LLM Clients Module

Provides specialized LLM clients for medical query processing.

Author: OnCall.ai Team
Date: 2025-07-29
"""

import logging
import os
from typing import Dict, Optional, Union, List
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class llm_Med42_70BClient:
    def __init__(
        self, 
        model_name: str = "m42-health/Llama3-Med42-70B",
        timeout: float = 30.0
    ):
        """
        Initialize Medical LLM client for query processing.
        
        Args:
            model_name: Hugging Face model name
            timeout: API call timeout duration
        
        Warning: This model should not be used for professional medical advice.
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        
        # Configure logging to show detailed information
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Get Hugging Face token from environment
        hf_token = os.getenv('HF_TOKEN')
        if not hf_token:
            self.logger.error("HF_TOKEN is missing from environment variables.")
            raise ValueError(
                "HF_TOKEN not found in environment variables. "
                "Please set HF_TOKEN in your .env file or environment. "
                "Ensure the token is not empty and is correctly set."
            )
        
        try:
            # Initialize InferenceClient with the new model
            self.client = InferenceClient(
                provider="featherless-ai", 
                api_key=hf_token
            )
            
            self.logger.info(f"Medical LLM client initialized with model: {model_name}")
            self.logger.warning(
                "Medical LLM Model: Research tool only. "
                "Not for professional medical diagnosis."
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize InferenceClient: {str(e)}")
            self.logger.error(f"Error Type: {type(e).__name__}")
            self.logger.error(f"Detailed Error: {repr(e)}")
            raise ValueError(f"Failed to initialize Medical LLM client: {str(e)}") from e

    def analyze_medical_query(
        self, 
        query: str, 
        max_tokens: int = 100, 
        timeout: Optional[float] = None
    ) -> Dict[str, Union[str, float]]:
        """
        Analyze medical query and extract condition.
        
        Args:
            query: Medical query text
            max_tokens: Maximum tokens to generate
            timeout: Specific API call timeout
        
        Returns:
            Extracted medical condition information with latency
        """
        import time
        
        # Start timing
        start_time = time.time()
        
        try:
            self.logger.info(f"Calling Medical LLM with query: {query}")
            
            # Prepare chat completion request with updated system prompt
            response = self.client.chat.completions.create(
                model="m42-health/Llama3-Med42-70B",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a medical assistant trained to extract medical conditions.

                        HANDLING MULTIPLE CONDITIONS:
                        1. If query contains multiple medical conditions, extract the PRIMARY/ACUTE condition
                        2. Priority order: Life-threatening emergencies > Acute conditions > Chronic diseases > Symptoms
                        3. For patient scenarios, focus on the condition requiring immediate medical attention

                        EXAMPLES:
                        - Single: "chest pain" → "Acute Coronary Syndrome"
                        - Multiple: "diabetic patient with chest pain" → "Acute Coronary Syndrome"
                        - Chronic+Acute: "hypertension patient having seizure" → "Seizure Disorder" 
                        - Complex: "20-year-old female, porphyria, sudden seizure" → "Acute Seizure"
                        - Emergency context: "porphyria patient with sudden seizure" → "Seizure Disorder"

                        RESPONSE FORMAT:
                        - Medical queries: Return ONLY the primary condition name
                        - Non-medical queries: Return "NON_MEDICAL_QUERY"

                        DO NOT provide explanations or medical advice."""
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                max_tokens=max_tokens
            )
            
            # Calculate latency
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract the response text
            response_text = response.choices[0].message.content or ""
            
            # Log raw response and latency
            self.logger.info(f"Raw LLM Response: {response_text}")
            self.logger.info(f"Query Latency: {latency:.4f} seconds")
            
            # Detect abnormal response
            if self._is_abnormal_response(response_text):
                self.logger.error(f"❌ Abnormal LLM response detected: {response_text[:50]}...")
                return {
                    'extracted_condition': '',
                    'confidence': '0',
                    'error': 'Abnormal LLM response detected',
                    'raw_response': response_text,
                    'latency': latency
                }
            
            # Extract condition from response
            extracted_condition = self._extract_condition(response_text)
            
            # Log the extracted condition
            self.logger.info(f"Extracted Condition: {extracted_condition}")
            
            return {
                'extracted_condition': extracted_condition,
                'confidence': '0.8',
                'raw_response': response_text,
                'latency': latency  # Add latency to the return dictionary
            }
        
        except Exception as e:
            # Calculate latency even for failed requests
            end_time = time.time()
            latency = end_time - start_time
            
            self.logger.error(f"Medical LLM query error: {str(e)}")
            self.logger.error(f"Error Type: {type(e).__name__}")
            self.logger.error(f"Detailed Error: {repr(e)}")
            self.logger.error(f"Query Latency (on error): {latency:.4f} seconds")
            
            # Additional context logging
            self.logger.error(f"Query that caused error: {query}")
            
            return {
                'extracted_condition': '',
                'confidence': '0',
                'error': str(e),
                'latency': latency  # Include latency even for error cases
            }

    def extract_medical_keywords_for_customization(
        self, 
        query: str, 
        max_tokens: int = 50, 
        timeout: Optional[float] = None
    ) -> List[str]:
        """
        Extract key medical concepts for hospital customization matching.
        
        Args:
            query: Medical query text
            max_tokens: Maximum tokens to generate
            timeout: Specific API call timeout
        
        Returns:
            List of key medical keywords/concepts
        """
        import time
        
        # Start timing
        start_time = time.time()
        
        try:
            self.logger.info(f"Extracting medical keywords for: {query}")
            
            # Prepare chat completion request for keyword extraction
            response = self.client.chat.completions.create(
                model="m42-health/Llama3-Med42-70B",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a medical keyword extractor. Extract 2-4 key medical concepts from queries for hospital document matching.

Return ONLY the key medical terms/concepts, separated by commas.

Examples:
- "Patient with severe chest pain and shortness of breath" → "chest pain, dyspnea, cardiac"
- "How to manage atrial fibrillation in emergency?" → "atrial fibrillation, arrhythmia, emergency"
- "Stroke protocol for elderly patient" → "stroke, cerebrovascular, elderly"

Focus on: conditions, symptoms, procedures, body systems."""
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                max_tokens=max_tokens
            )
            
            # Calculate latency
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract keywords from response
            keywords_text = response.choices[0].message.content or ""
            
            # Log response and latency
            self.logger.info(f"Keywords extracted: {keywords_text}")
            self.logger.info(f"Keyword extraction latency: {latency:.4f} seconds")
            
            # Parse keywords
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Filter out empty or very short keywords
            keywords = [k for k in keywords if len(k) > 2]
            
            return keywords
            
        except Exception as e:
            # Calculate latency even for failed requests
            end_time = time.time()
            latency = end_time - start_time
            
            self.logger.error(f"Medical keyword extraction error: {str(e)}")
            self.logger.error(f"Query that caused error: {query}")
            
            # Return empty list on error
            return []

    def _extract_condition(self, response: str) -> str:
        """
        Extract medical condition from model response.
        
        Args:
            response: Full model-generated text
        
        Returns:
            Extracted medical condition or empty string if non-medical
        """
        # Check if this is a rejection response first
        if self._is_rejection_response(response):
            return ""
        
        from medical_conditions import CONDITION_KEYWORD_MAPPING
        
        # Search in known medical conditions
        for condition in CONDITION_KEYWORD_MAPPING.keys():
            if condition.lower() in response.lower():
                return condition
        
        return response.split('\n')[0].strip() or ""
    
    def _is_abnormal_response(self, response: str) -> bool:
        """
        Detect abnormal LLM responses (e.g., repetitive characters, short/long responses)
        
        Args:
            response: LLM response text
            
        Returns:
            bool: True if response is abnormal, False otherwise
        """
        if not response or not response.strip():
            return True
            
        response_stripped = response.strip()
        
        # Detect repetitive characters (e.g., !!!!!!!)
        if len(response_stripped) > 20:
            unique_chars = len(set(response_stripped))
            if unique_chars <= 3:  # Only a few characters
                self.logger.warning(f"Detected repetitive character pattern: {response_stripped[:30]}...")
                return True
        
        # Detect special character patterns
        abnormal_patterns = ['!!!!', '????', '****', '####', '----']
        for pattern in abnormal_patterns:
            if pattern in response_stripped:
                self.logger.warning(f"Detected abnormal pattern '{pattern}' in response")
                return True
        
        # Detect short response (less than 2 characters)
        if len(response_stripped) < 2:
            return True            
            
        return False

    def _is_rejection_response(self, response: str) -> bool:
        """
        Dual-layer detection: prompt compliance + natural language patterns
        
        Args:
            response: LLM response text
            
        Returns:
            True if response indicates non-medical query rejection
        """
        response_upper = response.upper()
        response_lower = response.lower()
        
        # Layer 1: Check for standardized format (if LLM follows prompt)
        if "NON_MEDICAL_QUERY" in response_upper:
            return True
        
        # Layer 2: Check natural language rejection patterns (fallback)
        rejection_patterns = [
            "i do not address",
            "do not address", 
            "outside my biomedical scope",
            "outside my medical scope", 
            "unrelated to medical conditions",
            "not about a medical condition",
            "not a medical condition",
            "this query is outside",
            "culinary practice",  # cooking-related
            "technology trends",  # programming-related
            "meteorology",        # weather-related
            "non-medical context"
        ]
        
        return any(pattern in response_lower for pattern in rejection_patterns)

def main():
    """
    Test Medical LLM client functionality
    """
    import time
    from datetime import datetime

    # Record total execution start time
    total_start_time = time.time()
    execution_start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        print(f"Execution Started at: {execution_start_timestamp}")
        
        # Test client initialization
        client = llm_Med42_70BClient()
        
        test_queries = [
            "patient experiencing chest pain",
            "sudden weakness on one side",
            "severe headache with neurological symptoms"
        ]
        
        # Store individual query results
        query_results = []
        
        for query in test_queries:
            print(f"\nTesting query: {query}")
            result = client.analyze_medical_query(query)
            
            # Store query result
            query_result = {
                'query': query,
                'extracted_condition': result.get('extracted_condition', 'N/A'),
                'confidence': result.get('confidence', 'N/A'),
                'latency': result.get('latency', 'N/A')
            }
            query_results.append(query_result)
            
            # Print individual query results
            print("Extracted Condition:", query_result['extracted_condition'])
            print("Confidence:", query_result['confidence'])
            print(f"Latency: {query_result['latency']:.4f} seconds")
            
            if 'error' in result:
                print("Error:", result['error'])
            print("---")
        
        # Calculate total execution time
        total_end_time = time.time()
        total_execution_time = total_end_time - total_start_time
        execution_end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Print summary
        print("\n--- Execution Summary ---")
        print(f"Execution Started at: {execution_start_timestamp}")
        print(f"Execution Ended at: {execution_end_timestamp}")
        print(f"Total Execution Time: {total_execution_time:.4f} seconds")
        
        # Optional: Return results for potential further processing
        return {
            'start_time': execution_start_timestamp,
            'end_time': execution_end_timestamp,
            'total_execution_time': total_execution_time,
            'query_results': query_results
        }
            
    except Exception as e:
        print(f"Client initialization error: {str(e)}")
        print("Possible issues:")
        print("1. Invalid or missing Hugging Face token")
        print("2. Network connectivity problems")
        print("3. Model access restrictions")
        print("\nPlease check your .env file and Hugging Face token.")
        
        # Calculate total execution time even in case of error
        total_end_time = time.time()
        total_execution_time = total_end_time - total_start_time
        
        return {
            'error': str(e),
            'total_execution_time': total_execution_time
        }

if __name__ == "__main__":
    main()