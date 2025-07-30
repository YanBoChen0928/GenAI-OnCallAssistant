"""
OnCall.ai LLM Clients Module

Provides specialized LLM clients for medical query processing.

Author: OnCall.ai Team
Date: 2025-07-29
"""

import logging
import os
from typing import Dict, Optional
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MeditronClient:
    def __init__(
        self, 
        model: str = "TheBloke/meditron-7B-GPTQ",
        timeout: float = 30.0
    ):
        """
        Initialize Meditron API client for medical query processing.
        
        Args:
            model: Hugging Face model name
            timeout: API call timeout duration (not used in InferenceClient)
        
        Warning: This model should not be used for professional medical advice.
        """
        # Get HF token from environment variable
        hf_token = os.getenv('HF_TOKEN')
        if not hf_token:
            raise ValueError(
                "HF_TOKEN not found in environment variables. "
                "Please set HF_TOKEN in your .env file or environment."
            )
        
        self.client = InferenceClient(model=model, token=hf_token)
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.logger.warning(
            "Meditron Model: Research tool only. "
            "Not for professional medical diagnosis."
        )
        self.logger.info("Meditron client initialized with HF token")

    def analyze_medical_query(
        self, 
        query: str, 
        max_tokens: int = 100, 
        timeout: Optional[float] = None
    ) -> Dict[str, str]:
        """
        Analyze medical query and extract condition.
        
        Args:
            query: Medical query text
            max_tokens: Maximum tokens to generate
            timeout: Specific API call timeout (not used in InferenceClient)
        
        Returns:
            Extracted medical condition information
        """
        try:
            # ChatML style prompt for Meditron
            prompt = f"""<|im_start|>system
You are a professional medical assistant trained to extract medical conditions. 
Provide only the most representative condition name.
DO NOT provide medical advice.
<|im_end|>
<|im_start|>user
{query}
<|im_end|>
<|im_start|>assistant
"""
            
            self.logger.info(f"Calling Meditron API with query: {query}")
            
            # Remove timeout parameter as InferenceClient doesn't support it
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.7,
                top_k=50
            )
            
            self.logger.info(f"Received response: {response}")
            
            # Extract condition from response
            extracted_condition = self._extract_condition(response)
            
            return {
                'extracted_condition': extracted_condition,
                'confidence': 0.8,
                'raw_response': response
            }
        
        except Exception as e:
            self.logger.error(f"Meditron API query error: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            return {
                'extracted_condition': '',
                'confidence': 0,
                'error': str(e)
            }

    def _extract_condition(self, response: str) -> str:
        """
        Extract medical condition from model response.
        
        Args:
            response: Full model-generated text
        
        Returns:
            Extracted medical condition
        """
        from medical_conditions import CONDITION_KEYWORD_MAPPING
        
        # Remove prompt parts, keep only generated content
        generated_text = response.split('<|im_start|>assistant\n')[-1].strip()
        
        # Search in known medical conditions
        for condition in CONDITION_KEYWORD_MAPPING.keys():
            if condition.lower() in generated_text.lower():
                return condition
        
        return generated_text.split('\n')[0].strip()

def main():
    """
    Test Meditron client functionality
    """
    try:
        client = MeditronClient()
        test_queries = [
            "patient experiencing chest pain",
            "sudden weakness on one side",
            "severe headache with neurological symptoms"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: {query}")
            result = client.analyze_medical_query(query)
            print("Extracted Condition:", result['extracted_condition'])
            print("Confidence:", result['confidence'])
            if 'error' in result:
                print("Error:", result['error'])
            print("---")
            
    except Exception as e:
        print(f"Client initialization error: {str(e)}")
        print("This might be due to:")
        print("1. Missing Hugging Face API token")
        print("2. Network connectivity issues")
        print("3. Model access permissions")
        print("\nTo fix:")
        print("1. Set HF_TOKEN environment variable")
        print("2. Or login with: huggingface-cli login")

if __name__ == "__main__":
    main()