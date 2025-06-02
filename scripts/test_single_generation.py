#!/usr/bin/env python3
"""Test single image generation with full prompt logging."""
import sys
sys.path.append('.')
from src.openai_image_generator_v2_simple import OpenAIImageGeneratorV2Simple
from pathlib import Path
import shutil

def test_single_generation():
    """Test generating a single image to validate prompt."""
    
    print("=== Single Image Generation Test ===")
    print("Testing prompt configuration with one image\n")
    
    # Create a test directory with one image
    test_dir = Path("test_single")
    test_dir.mkdir(exist_ok=True)
    
    # Create a dummy test file
    test_file = test_dir / "red_barn.png"
    test_file.write_text("")  # Create empty file
    
    try:
        # Initialize generator
        generator = OpenAIImageGeneratorV2Simple()
        
        # Update config to use our test directory
        generator.config["directories"]["input_dir"] = str(test_dir)
        generator.config["directories"]["output_dir"] = "test_output_single"
        
        # Process the single image
        print(f"Processing: {test_file.name}")
        print("\nCheck the console output below for the full DALL-E prompt:")
        print("=" * 60)
        
        generator.process_single_image(test_file)
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
    
    print("\nTest complete! Check above for the full prompt that was sent to DALL-E.")

if __name__ == "__main__":
    test_single_generation() 