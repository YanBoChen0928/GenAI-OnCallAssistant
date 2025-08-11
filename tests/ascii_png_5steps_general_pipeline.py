#!/usr/bin/env python3
"""
Improved ASCII to High-Resolution Image Converter
Optimized for academic conferences (NeurIPS) with fallback font support
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_ascii_diagram(ascii_text: str, output_path: str = "oncall_ai_flowchart.png") -> bool:
    """
    Convert ASCII diagram to high-resolution image with academic quality
    
    Args:
        ascii_text: ASCII art text content
        output_path: Output PNG file path
        
    Returns:
        Boolean indicating success
    """
    
    # Font selection with fallback options
    font_paths = [
        "/System/Library/Fonts/SFNSMono.ttf",           # macOS Big Sur+
        "/System/Library/Fonts/Monaco.ttf",             # macOS fallback
        "/System/Library/Fonts/Menlo.ttf",              # macOS alternative  
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "C:/Windows/Fonts/consola.ttf",                 # Windows
        None  # PIL default font fallback
    ]
    
    font = None
    font_size = 14  # Slightly smaller for better readability
    
    # Try fonts in order of preference
    for font_path in font_paths:
        try:
            if font_path is None:
                font = ImageFont.load_default()
                print("🔤 Using PIL default font")
                break
            elif os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                print(f"✅ Using font: {font_path}")
                break
        except Exception as e:
            print(f"⚠️ Font loading failed: {font_path} - {e}")
            continue
    
    if font is None:
        print("❌ No suitable font found")
        return False
    
    # Process text lines
    lines = ascii_text.strip().split("\n")
    lines = [line.rstrip() for line in lines]  # Remove trailing whitespace
    
    # Calculate dimensions using modern PIL methods
    try:
        # Modern Pillow 10.0+ method
        line_metrics = [font.getbbox(line) for line in lines]
        max_width = max([metrics[2] - metrics[0] for metrics in line_metrics])
        line_height = max([metrics[3] - metrics[1] for metrics in line_metrics])
    except AttributeError:
        # Fallback for older Pillow versions
        try:
            line_sizes = [font.getsize(line) for line in lines]
            max_width = max([size[0] for size in line_sizes])
            line_height = max([size[1] for size in line_sizes])
        except AttributeError:
            # Ultimate fallback
            max_width = len(max(lines, key=len)) * font_size * 0.6
            line_height = font_size * 1.2
    
    # Image dimensions with padding
    padding = 40
    img_width = int(max_width + padding * 2)
    img_height = int(line_height * len(lines) + padding * 2)
    
    print(f"📐 Image dimensions: {img_width} x {img_height}")
    print(f"📏 Max line width: {max_width}, Line height: {line_height}")
    
    # Create high-resolution image
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)
    
    # Draw text lines
    for i, line in enumerate(lines):
        y_pos = padding + i * line_height
        draw.text((padding, y_pos), line, font=font, fill="black")
    
    # Save with high DPI for academic use
    try:
        img.save(output_path, dpi=(300, 300), optimize=True)
        print(f"✅ High-resolution diagram saved: {output_path}")
        print(f"📊 Image size: {img_width}x{img_height} at 300 DPI")
        return True
    except Exception as e:
        print(f"❌ Failed to save image: {e}")
        return False

# Example usage with your OnCall.ai flowchart
if __name__ == "__main__":
    
    # Your OnCall.ai ASCII flowchart
    oncall_ascii = """
+---------------------------------------------------+-------------------------------------------------------------+
| User Input                                        | 1. STEP 1: Condition Extraction                             |
|   ↓                                               |    - Processes user input through 5-level fallback          |
| STEP 1: Condition Extraction (5-level fallback)   |    - Extracts medical conditions and keywords               |
|   ↓                                               |    - Handles complex symptom descriptions & terminology     |
| STEP 2: System Understanding Display (Transparent)|-------------------------------------------------------------|
|   ↓                                               | 2. STEP 2: System Understanding Display                     |
| STEP 3: Medical Guidelines Retrieval              |    - Shows transparent interpretation of user query         |
|   ↓                                               |    - No user interaction required                           |
| STEP 4: Evidence-based Advice Generation          |    - Builds confidence in system understanding              |
|   ↓                                               |-------------------------------------------------------------|
| STEP 5: Performance Summary & Technical Details   | 3. STEP 3: Medical Guidelines Retrieval                     |
|   ↓                                               |    - Searches dual-index system (emergency + treatment)     |
| Multi-format Output                               |    - Returns 8-9 relevant guidelines per query              |
| (Advice + Guidelines + Metrics)                   |    - Maintains emergency/treatment balance                  |
|                                                   |-------------------------------------------------------------|
|                                                   | 4. STEP 4: Evidence-based Advice Generation                 |
|                                                   |    - Uses RAG-based prompt construction                     |
|                                                   |    - Integrates specialized medical LLM (Med42-70B)         |
|                                                   |    - Generates clinically appropriate guidance              |
|                                                   |-------------------------------------------------------------|
|                                                   | 5. STEP 5: Performance Summary                              |
|                                                   |    - Aggregates timing and confidence metrics               |
|                                                   |    - Provides technical metadata for transparency           |
|                                                   |    - Enables system performance monitoring                  |
+---------------------------------------------------+-------------------------------------------------------------+
|                                  General Pipeline 5 steps Mechanism Overview                                    |
    """
    
    # Execute conversion
    success = create_ascii_diagram(oncall_ascii, "5level_general_pipeline.png")
    
    if success:
        print("\n🎉 Ready for NeurIPS presentation!")
        print("💡 You can now insert this high-quality diagram into your paper or poster")
    else:
        print("\n❌ Conversion failed - check font availability")