"""
OnCall.ai LLM Clients Module

Provides specialized LLM clients for medical query processing.

Author: OnCall.ai Team
Date: 2025-07-29
"""

import logging
import os
from typing import Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MeditronClient:
    def __init__(
        self, 
        model_name: str = "TheBloke/meditron-7B-GPTQ",
        local_model_path: Optional[str] = None,
        use_local: bool = False,
        timeout: float = 30.0
    ):
        """
        Initialize Meditron client for medical query processing.
        
        Args:
            model_name: Hugging Face model name
            local_model_path: Path to local model files
            use_local: Flag to use local model
            timeout: API call timeout duration
        
        Warning: This model should not be used for professional medical advice.
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.use_local = use_local
        
        if use_local:
            if not local_model_path:
                raise ValueError("local_model_path must be provided when use_local is True")
            
            try:
                # Load local model using Hugging Face transformers
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    local_files_only=True, 
                    cache_dir=local_model_path
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    local_files_only=True,
                    cache_dir=local_model_path,
                    device_map="auto",
                    torch_dtype=torch.float16
                )
                
                self.logger.info(f"Local Meditron model loaded from: {local_model_path}")
                self.logger.warning(
                    "Meditron Model: Research tool only. "
                    "Not for professional medical diagnosis."
                )
            except Exception as e:
                self.logger.error(f"Failed to load local model: {str(e)}")
                raise ValueError(f"Failed to initialize local Meditron client: {str(e)}")
        else:
            # Existing InferenceClient logic
            hf_token = os.getenv('HF_TOKEN')
            if not hf_token:
                raise ValueError(
                    "HF_TOKEN not found in environment variables. "
                    "Please set HF_TOKEN in your .env file or environment."
                )
            
            try:
                self.client = InferenceClient(model=model_name, token=hf_token)
                self.logger.info(f"Meditron client initialized with model: {model_name}")
                self.logger.warning(
                    "Meditron Model: Research tool only. "
                    "Not for professional medical diagnosis."
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize InferenceClient: {str(e)}")
                raise ValueError(f"Failed to initialize Meditron client: {str(e)}")

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
            timeout: Specific API call timeout
        
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
            
            self.logger.info(f"Calling Meditron with query: {query}")
            
            if self.use_local:
                # Local model inference
                input_ids = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.model.device)
                
                response = self.model.generate(
                    input_ids, 
                    max_new_tokens=max_tokens, 
                    temperature=0.7, 
                    do_sample=True, 
                    top_k=50
                )
                
                response_text = self.tokenizer.decode(response[0], skip_special_tokens=True)
                self.logger.info(f"Local model response: {response_text}")
            else:
                # InferenceClient inference
                self.logger.info(f"Using model: {self.client.model}")
                
                # Test API connection first
                try:
                    test_response = self.client.text_generation(
                        "Hello",
                        max_new_tokens=5,
                        temperature=0.7,
                        top_k=50
                    )
                    self.logger.info("API connection test successful")
                except Exception as test_error:
                    self.logger.error(f"API connection test failed: {str(test_error)}")
                    return {
                        'extracted_condition': '',
                        'confidence': 0,
                        'error': f"API connection failed: {str(test_error)}"
                    }
                
                response_text = self.client.text_generation(
                    prompt,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    top_k=50
                )
            
            # Extract condition from response
            extracted_condition = self._extract_condition(response_text)
            
            return {
                'extracted_condition': extracted_condition,
                'confidence': 0.8,
                'raw_response': response_text
            }
        
        except Exception as e:
            self.logger.error(f"Meditron query error: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            self.logger.error(f"Error details: {repr(e)}")
            return {
                'extracted_condition': '',
                'confidence': 0,
                'error': f"{type(e).__name__}: {str(e)}"
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
        # Test local model loading
        client = MeditronClient(
            local_model_path="/Users/yanbochen/Documents/Life in Canada/CS study related/*Student Course, Guide/CS7180 GenAI/FinalProject_git_copy/models/cache/meditron-7B-GPTQ", 
            use_local=True
        )
        
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
        print("1. Incorrect local model path")
        print("2. Missing dependencies")
        print("3. Hardware limitations")
        print("\nTo fix:")
        print("1. Verify local model path")
        print("2. Install required dependencies")

if __name__ == "__main__":
    main()