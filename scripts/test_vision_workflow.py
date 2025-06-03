#!/usr/bin/env python3
"""
Test the corrected vision analysis workflow:
1. GPT-4 Vision analyzes an image
2. Response gets wrapped in DALL-E prompt
3. DALL-E generates the new image
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from openai_image_generator import OpenAIImageGenerator
import logging

def test_vision_workflow():
    """Test the complete vision workflow with a single image."""
    
    print("=== Testing Vision Workflow ===")
    print("GPT-4V Analysis → ChatGPT Response → DALL-E Wrapper → Image Generation")
    print("=" * 60)
    
    try:
        # Initialize generator
        generator = OpenAIImageGenerator()
        
        # Find a test image
        test_dir = Path("./test/assets")
        
        # Look for any image file
        image_files = []
        for pattern in ["*.png", "*.jpg", "*.jpeg"]:
            image_files.extend(test_dir.rglob(pattern))
        
        if not image_files:
            print("❌ No test images found in ./test/assets")
            return False
        
        # Use the first image found
        test_image = image_files[0]
        print(f"📸 Testing with: {test_image.relative_to(Path('.'))}")
        
        # Test Step 1: Vision Analysis
        print("\n🔍 Step 1: Analyzing image with GPT-4 Vision...")
        description = generator.analyze_image(test_image)
        
        if not description:
            print("❌ Vision analysis failed")
            return False
        
        print("✅ Vision analysis successful")
        print(f"📝 Description preview: {description[:200]}...")
        
        # Test Step 2: Wrap description
        print("\n🎨 Step 2: Wrapping description for DALL-E...")
        dalle_prompt = generator.wrap_description_for_dalle(description)
        
        print("✅ Prompt wrapping successful")
        print(f"📏 Final prompt length: {len(dalle_prompt)} characters")
        
        # Test Step 3: Generate image
        print("\n🎯 Step 3: Testing full workflow...")
        success = generator.process_single_image(test_image)
        
        if success:
            print("✅ Complete workflow successful!")
            print(f"📁 Check output directory: {generator.config['directories']['output_dir']}")
            return True
        else:
            print("❌ Image generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.exception("Detailed error:")
        return False

if __name__ == "__main__":
    success = test_vision_workflow()
    sys.exit(0 if success else 1) 