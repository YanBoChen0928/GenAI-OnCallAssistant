#!/usr/bin/env python3
"""
OnCall.ai - Interactive Medical Emergency Assistant

A Gradio-based web interface for the OnCall.ai medical query processing system.
Provides real-time medical guidance based on evidence from medical guidelines.

Features:
- Complete pipeline: Query → Condition Extraction → Retrieval → Generation
- Multi-level fallback validation system
- Evidence-based medical advice with source attribution
- Environment-controlled debug mode
- Audio input ready (future enhancement)

Author: OnCall.ai Team
Date: 2025-07-31
Version: 0.9.0
"""

import os
import sys
import gradio as gr
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Also add project root to ensure customization module can be imported
sys.path.insert(0, str(current_dir))

# Import OnCall.ai modules
try:
    from user_prompt import UserPromptProcessor
    from retrieval import BasicRetrievalSystem
    from llm_clients import llm_Med42_70BClient
    from generation import MedicalAdviceGenerator
    from medical_conditions import CONDITION_KEYWORD_MAPPING
except ImportError as e:
    print(f"❌ Failed to import OnCall.ai modules: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

# Configuration
DEBUG_MODE = os.getenv('ONCALL_DEBUG', 'false').lower() == 'true'
print(f"🔧 Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")

class OnCallAIInterface:
    """
    Main interface class for OnCall.ai Gradio application
    """
    
    def __init__(self):
        """Initialize the complete OnCall.ai pipeline"""
        self.initialized = False
        self.initialization_error = None
        
        # Pipeline components
        self.llm_client = None
        self.retrieval_system = None
        self.user_prompt_processor = None
        self.medical_generator = None
        
        # Initialize pipeline
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize all pipeline components with error handling"""
        try:
            print("🔧 Initializing OnCall.ai Pipeline...")
            
            # Initialize LLM client
            print("  1. Loading Med42-70B client...")
            self.llm_client = llm_Med42_70BClient()
            
            # Initialize retrieval system
            print("  2. Loading medical guidelines indices...")
            self.retrieval_system = BasicRetrievalSystem()
            
            # Initialize user prompt processor
            print("  3. Setting up multi-level query processor...")
            self.user_prompt_processor = UserPromptProcessor(
                llm_client=self.llm_client,
                retrieval_system=self.retrieval_system
            )
            
            # Initialize medical advice generator
            print("  4. Preparing medical advice generator...")
            self.medical_generator = MedicalAdviceGenerator(
                llm_client=self.llm_client
            )
            
            self.initialized = True
            print("✅ OnCall.ai pipeline initialized successfully!")
            
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ Pipeline initialization failed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def process_medical_query(self, user_query: str, intention_override: Optional[str] = None) -> Tuple[str, str, str, str]:
        """
        Complete medical query processing pipeline
        
        Args:
            user_query: User's medical query
            intention_override: Optional intention override for testing
            
        Returns:
            Tuple of (medical_advice, processing_steps, retrieved_guidelines, technical_details)
        """
        if not self.initialized:
            error_msg = f"❌ System not initialized: {self.initialization_error}"
            return error_msg, error_msg, "{}", "{}"
        
        if not user_query or not user_query.strip():
            return "Please enter a medical query to get started.", "", "{}", "{}"
        
        processing_start = datetime.now()
        processing_steps = []
        technical_details = {}
        
        try:
            # STEP 1: Query Processing and Condition Extraction
            processing_steps.append("🎯 Step 1: Processing medical query and extracting conditions...")
            step1_start = datetime.now()
            
            condition_result = self.user_prompt_processor.extract_condition_keywords(user_query)
            step1_time = (datetime.now() - step1_start).total_seconds()
            
            processing_steps.append(f"   ✅ Condition: {condition_result.get('condition', 'None')}")
            processing_steps.append(f"   📋 Emergency Keywords: {condition_result.get('emergency_keywords', 'None')}")
            processing_steps.append(f"   💊 Treatment Keywords: {condition_result.get('treatment_keywords', 'None')}")
            processing_steps.append(f"   ⏱️ Processing Time: {step1_time:.3f}s")
            
            # Handle non-medical queries
            if condition_result.get('type') == 'invalid_query':
                non_medical_msg = condition_result.get('message', 'This appears to be a non-medical query.')
                processing_steps.append("   🚫 Query identified as non-medical")
                return non_medical_msg, '\n'.join(processing_steps), "{}", "{}"
            
            # STEP 1.5: Hospital-Specific Customization (Early retrieval)
            # Run this early since it has its own keyword extraction
            customization_results = []
            retrieval_results = {}  # Initialize early for hospital results
            try:
                from customization.customization_pipeline import retrieve_document_chunks
                
                processing_steps.append("\n🏥 Step 1.5: Checking hospital-specific guidelines...")
                custom_start = datetime.now()
                
                # Use original user query since hospital module has its own keyword extraction
                custom_results = retrieve_document_chunks(user_query, top_k=3, llm_client=self.llm_client)
                custom_time = (datetime.now() - custom_start).total_seconds()
                
                if custom_results:
                    processing_steps.append(f"   📋 Found {len(custom_results)} hospital-specific guidelines")
                    processing_steps.append(f"   ⏱️ Customization time: {custom_time:.3f}s")
                    
                    # Store customization results for later use
                    customization_results = custom_results
                    
                    # Add custom results to retrieval_results for the generator
                    retrieval_results['customization_results'] = custom_results
                else:
                    processing_steps.append("   ℹ️ No hospital-specific guidelines found")
            except ImportError as e:
                processing_steps.append(f"   ⚠️ Hospital customization module not available: {str(e)}")
                if DEBUG_MODE:
                    print(f"Import error: {traceback.format_exc()}")
            except Exception as e:
                processing_steps.append(f"   ⚠️ Customization search skipped: {str(e)}")
                if DEBUG_MODE:
                    print(f"Customization error: {traceback.format_exc()}")
            
            # STEP 2: User Confirmation (Auto-simulated)
            processing_steps.append("\n🤝 Step 2: User confirmation (auto-confirmed for demo)")
            confirmation = self.user_prompt_processor.handle_user_confirmation(condition_result)
            
            if not condition_result.get('condition'):
                processing_steps.append("   ⚠️ No medical condition identified")
                
                # If we have hospital customization results, we can still try to provide help
                if customization_results:
                    processing_steps.append("   ℹ️ Using hospital-specific guidelines to assist...")
                    
                    # Create a minimal retrieval_results structure for generation
                    retrieval_results['processed_results'] = []
                    
                    # Skip to generation with hospital results only
                    processing_steps.append("\n🧠 Step 4: Generating advice based on hospital guidelines...")
                    gen_start = datetime.now()
                    
                    medical_advice_result = self.medical_generator.generate_medical_advice(
                        condition_result.get('condition', user_query),
                        retrieval_results,
                        intention="general"
                    )
                    
                    gen_time = (datetime.now() - gen_start).total_seconds()
                    medical_advice = medical_advice_result.get('medical_advice', 'Unable to generate advice')
                    
                    processing_steps.append(f"   ⏱️ Generation time: {gen_time:.3f}s")
                    
                    # Format guidelines display
                    guidelines_display = f"Hospital Guidelines Found: {len(customization_results)}"
                    
                    # Conditional return based on DEBUG_MODE
                    if DEBUG_MODE:
                        return (medical_advice, '\n'.join(processing_steps), guidelines_display, "{}")
                    else:
                        return (medical_advice, '\n'.join(processing_steps), guidelines_display)
                else:
                    # No condition and no hospital results
                    no_condition_msg = "Unable to identify a specific medical condition. Please rephrase your query with more specific medical terms."
                    if DEBUG_MODE:
                        return no_condition_msg, '\n'.join(processing_steps), "{}", "{}"
                    else:
                        return no_condition_msg, '\n'.join(processing_steps), "{}"
            
            processing_steps.append(f"   ✅ Confirmed condition: {condition_result.get('condition')}")
            
            # STEP 3: Medical Guidelines Retrieval
            processing_steps.append("\n🔍 Step 3: Retrieving relevant medical guidelines...")
            step3_start = datetime.now()
            
            # Construct search query
            search_query = f"{condition_result.get('emergency_keywords', '')} {condition_result.get('treatment_keywords', '')}".strip()
            if not search_query:
                search_query = condition_result.get('condition', user_query)
            
            # Search for general medical guidelines
            general_results = self.retrieval_system.search(search_query, top_k=5)
            step3_time = (datetime.now() - step3_start).total_seconds()
            
            # Merge with existing retrieval_results (which contains hospital customization)
            retrieval_results.update(general_results)
            
            processed_results = retrieval_results.get('processed_results', [])
            emergency_count = len([r for r in processed_results if r.get('type') == 'emergency'])
            treatment_count = len([r for r in processed_results if r.get('type') == 'treatment'])
            
            processing_steps.append(f"   📊 Found {len(processed_results)} relevant guidelines")
            processing_steps.append(f"   🚨 Emergency guidelines: {emergency_count}")
            processing_steps.append(f"   💊 Treatment guidelines: {treatment_count}")
            processing_steps.append(f"   ⏱️ Retrieval time: {step3_time:.3f}s")
            
            # Format retrieved guidelines for display - conditional based on debug mode
            if DEBUG_MODE:
                guidelines_display = self._format_guidelines_display(processed_results)
            else:
                guidelines_display = self._format_user_friendly_sources(processed_results)
            
            # Hospital customization already done in Step 1.5
            
            # STEP 4: Medical Advice Generation
            processing_steps.append("\n🧠 Step 4: Generating evidence-based medical advice...")
            step4_start = datetime.now()
            
            # Determine intention (use override if provided, otherwise detect)
            intention = intention_override or self._detect_query_intention(user_query)
            
            medical_advice_result = self.medical_generator.generate_medical_advice(
                user_query=user_query,
                retrieval_results=retrieval_results,
                intention=intention
            )
            step4_time = (datetime.now() - step4_start).total_seconds()
            
            # Extract medical advice
            medical_advice = medical_advice_result.get('medical_advice', 'Unable to generate medical advice.')
            confidence_score = medical_advice_result.get('confidence_score', 0.0)
            
            processing_steps.append(f"   🎯 Intention: {intention}")
            processing_steps.append(f"   📈 Confidence: {confidence_score:.2f}")
            processing_steps.append(f"   ⏱️ Generation time: {step4_time:.3f}s")
            
            # STEP 5: Final Summary
            total_time = (datetime.now() - processing_start).total_seconds()
            processing_steps.append(f"\n✅ Complete pipeline finished in {total_time:.3f}s")
            
            # Prepare technical details
            technical_details = {
                "condition_extraction": {
                    "method": self._determine_extraction_source(condition_result),
                    "condition": condition_result.get('condition', ''),
                    "processing_time": step1_time
                },
                "retrieval": {
                    "search_query": search_query if DEBUG_MODE else "[Hidden in production]",
                    "total_results": len(processed_results),
                    "emergency_results": emergency_count,
                    "treatment_results": treatment_count,
                    "processing_time": step3_time
                },
                "generation": {
                    "intention": intention,
                    "confidence_score": confidence_score,
                    "chunks_used": medical_advice_result.get('query_metadata', {}).get('total_chunks_used', 0),
                    "processing_time": step4_time
                },
                "performance": {
                    "total_pipeline_time": total_time,
                    "debug_mode": DEBUG_MODE
                }
            }
            
            # Apply security filtering for production
            if not DEBUG_MODE:
                technical_details = self._sanitize_technical_details(technical_details)
            
            # Conditional return based on DEBUG_MODE
            if DEBUG_MODE:
                return (
                    medical_advice,
                    '\n'.join(processing_steps),
                    guidelines_display,
                    json.dumps(technical_details, indent=2)
                )
            else:
                return (
                    medical_advice,
                    '\n'.join(processing_steps),
                    guidelines_display
                )
            
        except Exception as e:
            error_msg = f"❌ System error: {str(e)}"
            processing_steps.append(f"\n❌ Error occurred: {str(e)}")
            
            error_details = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "query": user_query
            }
            
            # Conditional return based on DEBUG_MODE
            if DEBUG_MODE:
                return (
                    "I apologize, but I encountered an error while processing your medical query. Please try rephrasing your question or contact technical support.",
                    '\n'.join(processing_steps),
                    "{}",
                    json.dumps(error_details, indent=2)
                )
            else:
                return (
                    "I apologize, but I encountered an error while processing your medical query. Please try rephrasing your question or contact technical support.",
                    '\n'.join(processing_steps),
                    "{}"
                )
    
    def _format_guidelines_display(self, processed_results: List[Dict]) -> str:
        """Format retrieved guidelines for user-friendly display"""
        if not processed_results:
            return json.dumps({"message": "No guidelines retrieved"}, indent=2)
        
        guidelines = []
        for i, result in enumerate(processed_results[:6], 1):  # Show top 6
            guideline = {
                "guideline_id": i,
                "source_type": result.get('type', 'unknown').title(),
                "relevance_score": f"{1 - result.get('distance', 1):.3f}",
                "content_preview": result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', ''),
                "matched_keywords": result.get('matched', '') if DEBUG_MODE else "[Keywords used for matching]"
            }
            guidelines.append(guideline)
        
        return json.dumps({
            "total_guidelines": len(processed_results),
            "displayed_guidelines": guidelines
        }, indent=2)
    
    def _format_user_friendly_sources(self, processed_results: List[Dict]) -> str:
        """Format retrieved guidelines for production mode - user-friendly text format"""
        if not processed_results:
            return "No relevant medical guidelines found for this query."
        
        sources = []
        emergency_count = 0
        treatment_count = 0
        
        # Extract top 5 most relevant sources
        for i, result in enumerate(processed_results[:5], 1):
            source_type = result.get('type', 'medical').title()
            confidence = f"{(1 - result.get('distance', 1)) * 100:.0f}%"
            
            if source_type.lower() == 'emergency':
                emergency_count += 1
            elif source_type.lower() == 'treatment':
                treatment_count += 1
            
            sources.append(f"{i}. {source_type} Guideline (Relevance: {confidence})")
        
        # Build user-friendly text output
        result_text = "\n".join(sources)
        result_text += f"\n\n📊 Summary:"
        result_text += f"\n• Total guidelines consulted: {len(processed_results)}"
        if emergency_count > 0:
            result_text += f"\n• Emergency protocols: {emergency_count}"
        if treatment_count > 0:
            result_text += f"\n• Treatment guidelines: {treatment_count}"
        
        result_text += f"\n\n✅ Evidence-based recommendations provided above"
        
        return result_text

    def _detect_query_intention(self, user_query: str) -> str:
        """Simple intention detection based on query content"""
        query_lower = user_query.lower()
        
        treatment_indicators = ['treat', 'treatment', 'manage', 'therapy', 'protocol', 'how to']
        diagnosis_indicators = ['diagnos', 'differential', 'symptoms', 'signs', 'what is']
        
        treatment_score = sum(1 for indicator in treatment_indicators if indicator in query_lower)
        diagnosis_score = sum(1 for indicator in diagnosis_indicators if indicator in query_lower)
        
        if treatment_score > diagnosis_score:
            return "treatment"
        elif diagnosis_score > treatment_score:
            return "diagnosis"
        else:
            return "treatment"  # Default to treatment for emergency scenarios
    
    def _determine_extraction_source(self, condition_result: Dict) -> str:
        """Determine how the condition was extracted"""
        if condition_result.get('semantic_confidence') is not None:
            return "semantic_search"
        elif condition_result.get('generic_confidence') is not None:
            return "generic_search"
        elif condition_result.get('condition') in CONDITION_KEYWORD_MAPPING:
            return "predefined_mapping"
        else:
            return "llm_extraction"
    
    def _sanitize_technical_details(self, technical_details: Dict) -> Dict:
        """Remove sensitive technical information for production mode"""
        sanitized = {
            "processing_summary": {
                "total_time": technical_details["performance"]["total_pipeline_time"],
                "confidence": technical_details["generation"]["confidence_score"],
                "guidelines_found": technical_details["retrieval"]["total_results"]
            },
            "medical_context": {
                "condition_identified": bool(technical_details["condition_extraction"]["condition"]),
                "intention_detected": technical_details["generation"]["intention"],
                "evidence_sources": f"{technical_details['retrieval']['emergency_results']} emergency + {technical_details['retrieval']['treatment_results']} treatment"
            },
            "system_status": {
                "all_components_operational": True,
                "processing_mode": "production"
            }
        }
        return sanitized

def create_oncall_interface():
    """Create and configure the Gradio interface"""
    
    # Initialize OnCall.ai system
    oncall_system = OnCallAIInterface()
    
    # Define interface theme and styling
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="green",
        neutral_hue="slate"
    )
    
    # Create Gradio interface
    with gr.Blocks(
        theme=theme,
        title="OnCall.ai - Medical Emergency Assistant",
        css="""
        .main-container { max-width: 1200px; margin: 0 auto; }
        .medical-advice { font-size: 16px; line-height: 1.6; }
        .processing-steps { font-family: monospace; font-size: 14px; }
        .guidelines-display { max-height: 400px; overflow-y: auto; }
        """
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🏥 OnCall.ai - Medical Emergency Assistant
        
        **Evidence-based clinical guidance for healthcare professionals**
        
        ⚠️ **Medical Disclaimer**: This system is for research and educational purposes only. 
        Always consult qualified healthcare providers for medical decisions.
        """)
        
        # Main interface
        with gr.Row():
            with gr.Column(scale=1):
                # Input section
                gr.Markdown("## 📝 Medical Query Input")
                
                user_input = gr.Textbox(
                    label="Enter your medical query",
                    placeholder="Example: How to treat acute myocardial infarction in emergency department?",
                    lines=3,
                    max_lines=5
                )
                
                # Optional intention override for testing
                if DEBUG_MODE:
                    intention_override = gr.Dropdown(
                        choices=[None, "treatment", "diagnosis"],
                        label="🎯 Override Intention (Debug Mode)",
                        value=None
                    )
                else:
                    intention_override = gr.State(None)
                
                submit_btn = gr.Button("🔍 Get Medical Guidance", variant="primary", size="lg")
                
                # Example queries with categorization
                gr.Markdown("""
                ### 💡 Example Queries

                **🔬 Diagnosis-Focused (Recommended - Faster Response):**
                - "60-year-old patient with hypertension history, sudden chest pain. What are possible causes and how to assess?"
                - "30-year-old presents with sudden severe headache and neck stiffness. Differential diagnosis?"
                - "Patient with acute shortness of breath and leg swelling. What should I consider?"
                
                **⚕️ Treatment-Focused (Recommended - Faster Response):**
                - "Suspected acute hemorrhagic stroke. Tell me the next steps to take."
                - "Confirmed STEMI patient in ED. What is the immediate management protocol?"
                - "Patient with anaphylaxis reaction. What is the treatment approach?"
                
                **🔄 Combined Queries (Longer Response Time - Less Recommended):**
                - "20-year-old female, no medical history, sudden seizure. What are possible causes and complete management workflow?"
                
                *Note: For optimal query efficiency, it's recommended to separate diagnostic assessment and treatment management questions.*
                """)
        
        # Output sections
        gr.Markdown("## 📋 Medical Guidance Results")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Primary output - Medical Advice
                medical_advice_output = gr.Textbox(
                    label="🩺 Medical Advice",
                    lines=10,
                    max_lines=15,
                    elem_classes="medical-advice"
                )
                
                # Processing steps
                processing_steps_output = gr.Textbox(
                    label="📊 Processing Steps",
                    lines=8,
                    max_lines=12,
                    elem_classes="processing-steps"
                )
            
        with gr.Column(scale=1):
            # Debug Mode: Show full technical details
            if DEBUG_MODE:
                guidelines_output = gr.JSON(
                    label="📚 Retrieved Medical Guidelines (Debug)",
                    elem_classes="guidelines-display"
                )
                
                technical_output = gr.JSON(
                    label="⚙️ Technical Details (Debug Mode)",
                    elem_classes="technical-details"
                )
            
            # Production Mode: User-friendly simplified version
            else:
                guidelines_output = gr.Textbox(
                    label="📖 Evidence Sources",
                    lines=5,
                    max_lines=8,
                    interactive=False,
                    elem_classes="evidence-sources"
                )
                
                # Hide technical details - no system information shown
                technical_output = gr.State(None)
        
        # Audio input section (placeholder for future)
        with gr.Accordion("🎙️ Audio Input (Coming Soon)", open=False):
            gr.Markdown("""
            **Future Enhancement**: Voice input capability will be available soon.
            You'll be able to:
            - Record audio queries directly in the interface
            - Upload audio files for processing
            - Receive audio responses (Text-to-Speech)
            """)
            
            # Placeholder components for audio (inactive)
            audio_input = gr.Audio(
                label="Audio Query (Not yet functional)",
                type="filepath",
                interactive=False
            )
        
        # Conditional outputs based on debug mode
        if DEBUG_MODE:
            handler_outputs = [medical_advice_output, processing_steps_output, guidelines_output, technical_output]
        else:
            handler_outputs = [medical_advice_output, processing_steps_output, guidelines_output]

        # Event handlers
        submit_btn.click(
            fn=oncall_system.process_medical_query,
            inputs=[user_input, intention_override] if DEBUG_MODE else [user_input],
            outputs=handler_outputs
        )
        
        # Enter key support
        user_input.submit(
            fn=oncall_system.process_medical_query,
            inputs=[user_input, intention_override] if DEBUG_MODE else [user_input],
            outputs=handler_outputs
        )
        
        # Footer
        gr.Markdown("""
        ---
        **OnCall.ai v0.9.0** | Built with ❤️ for healthcare professionals | 
        [GitHub](https://github.com/your-username/oncall-ai) | 
        **⚠️ Research Use Only**
        """)
    
    return interface

def main():
    """Main application entry point"""
    print("🏥 Starting OnCall.ai Interactive Interface...")
    print(f"🔧 Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
    
    try:
        # Create interface
        interface = create_oncall_interface()
        
        # Launch configuration
        launch_config = {
            "server_name": "0.0.0.0",  # Allow external connections
            "server_port": 7860,       # Standard Gradio port
            "share": False,            # Set to True for public links
            "debug": DEBUG_MODE,
            "show_error": DEBUG_MODE
        }
        
        print("🚀 Launching OnCall.ai interface...")
        print(f"🌐 Interface will be available at: http://localhost:7860")
        
        if DEBUG_MODE:
            print("🔧 Debug mode active - Technical details will be visible")
        else:
            print("🛡️ Production mode - Limited technical information displayed")
        
        # Launch interface
        interface.launch(**launch_config)
        
    except Exception as e:
        print(f"❌ Failed to launch interface: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
