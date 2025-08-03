"""
Manual modification instructions for app.py

你需要在以下位置手動修改代碼：

## 修改 1: 添加新方法 (在第 280 行 \_detect_query_intention 之前)

"""

def \_format_user_friendly_sources(self, processed_results: List[Dict]) -> str:
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

"""

## 修改 2: 更改第 177 行

從：
guidelines_display = self.\_format_guidelines_display(processed_results)

改為： # Format retrieved guidelines for display - conditional based on debug mode
if DEBUG_MODE:
guidelines_display = self.\_format_guidelines_display(processed_results)
else:
guidelines_display = self.\_format_user_friendly_sources(processed_results)

## 修改 3: 更改第 418-434 行的界面定義

從：
with gr.Column(scale=1): # Retrieved guidelines
guidelines_output = gr.JSON(
label="📚 Retrieved Medical Guidelines",
elem_classes="guidelines-display"
)

                # Technical details (collapsible in production)
                if DEBUG_MODE:
                    technical_output = gr.JSON(
                        label="⚙️ Technical Details (Debug Mode)",
                        elem_classes="technical-details"
                    )
                else:
                    with gr.Accordion("🔧 System Information", open=False):
                        technical_output = gr.JSON(
                            label="Processing Information",
                            elem_classes="technical-details"
                        )

改為：
with gr.Column(scale=1): # Debug Mode: Show full technical details
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

## 修改 4: 更改事件處理器 (第 470 行左右)

在 submit_btn.click 和 user_input.submit 之前添加： # Conditional outputs based on debug mode
if DEBUG_MODE:
handler_outputs = [medical_advice_output, processing_steps_output, guidelines_output, technical_output]
else:
handler_outputs = [medical_advice_output, processing_steps_output, guidelines_output]

然後修改兩個事件處理器的 outputs：
submit_btn.click(
fn=oncall_system.process_medical_query,
inputs=[user_input, intention_override] if DEBUG_MODE else [user_input],
outputs=handler_outputs
)

    user_input.submit(
        fn=oncall_system.process_medical_query,
        inputs=[user_input, intention_override] if DEBUG_MODE else [user_input],
        outputs=handler_outputs
    )

"""
