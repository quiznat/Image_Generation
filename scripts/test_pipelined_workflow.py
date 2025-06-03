#!/usr/bin/env python3
"""
Test script for the pipelined image generation workflow.
Tests with a small subset of images to validate the dual-worker approach.
"""

import os
import sys
import time
from pathlib import Path
import shutil

# Add src directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openai_image_generator_pipelined import OpenAIImageGeneratorPipelined

def create_test_images():
    """Create a small test set by copying a few images to a test directory."""
    test_input_dir = Path("./test_pipelined")
    test_output_dir = Path("./test_output_pipelined")
    
    # Clean up previous test
    if test_input_dir.exists():
        shutil.rmtree(test_input_dir)
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    
    # Create test directories
    test_input_dir.mkdir()
    (test_input_dir / "assets").mkdir()
    
    # Copy a few test images from the main test directory
    main_test_dir = Path("./test/assets")
    if not main_test_dir.exists():
        print("❌ Main test directory not found. Please ensure test/assets/ contains images.")
        return False
    
    # Find some test images
    test_images = []
    for category_dir in main_test_dir.iterdir():
        if category_dir.is_dir():
            for image_file in category_dir.glob("*.png"):
                test_images.append((image_file, category_dir.name))
                if len(test_images) >= 5:  # Limit to 5 test images
                    break
            if len(test_images) >= 5:
                break
    
    if not test_images:
        print("❌ No test images found in test/assets/")
        return False
    
    # Copy test images
    print(f"📋 Creating test set with {len(test_images)} images:")
    for image_file, category in test_images:
        test_category_dir = test_input_dir / "assets" / category
        test_category_dir.mkdir(exist_ok=True)
        
        dest_file = test_category_dir / image_file.name
        shutil.copy2(image_file, dest_file)
        print(f"   📁 {category}/{image_file.name}")
    
    return True, test_input_dir, test_output_dir

def test_pipelined_workflow():
    """Test the pipelined workflow with a small set of images."""
    print("🧪 Testing Pipelined Image Generation Workflow")
    print("=" * 50)
    
    # Create test images
    result = create_test_images()
    if not result:
        return False
    
    created_successfully, test_input_dir, test_output_dir = result
    
    # Create custom config for testing
    test_config = {
        "directories": {
            "input_dir": str(test_input_dir),
            "output_dir": str(test_output_dir)
        },
        "openai": {
            "model": "gpt-4o",
            "max_tokens": 4096,
            "temperature": 0.7
        },
        "dalle": {
            "model": "dall-e-3",
            "size": "1024x1024",
            "quality": "standard",
            "n": 1
        },
        "prompts": {
            "vision_analysis_prompt": "Analyze this image and describe what you see. Focus on the main object and provide a clear, detailed description.",
            "dalle_wrapper_prompt": [
                "Create a simple illustration based on this description: [CHATGPT_DESCRIPTION]",
                "Style: Clean, modern illustration",
                "Format: Single object on white background"
            ],
            "follow_up_1": "Please create the image now.",
            "follow_up_2": "Okay thanks, I need to go soon please make the image file."
        },
        "processing": {
            "supported_formats": [".png", ".jpg", ".jpeg"],
            "max_retries": 1,  # Reduce retries for testing
            "wait_between_retries": 1
        }
    }
    
    # Save test config
    test_config_path = "config/test_pipelined_config.json"
    import json
    with open(test_config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    try:
        print("🚀 Starting pipelined test...")
        print("⚡ Worker-1: GPT-4V Analysis | Worker-2: DALL-E Generation")
        print()
        
        start_time = time.time()
        
        # Initialize and run pipelined generator
        generator = OpenAIImageGeneratorPipelined(config_path=test_config_path)
        generator.process_directory_pipelined()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Check results
        output_files = list(test_output_dir.rglob("*.png"))
        
        print("\n" + "=" * 50)
        print("🎉 PIPELINED TEST RESULTS")
        print("=" * 50)
        print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"📊 Generated files: {len(output_files)}")
        print(f"📁 Output directory: {test_output_dir}")
        print()
        
        if output_files:
            print("✅ Generated images:")
            for output_file in output_files:
                relative_path = output_file.relative_to(test_output_dir)
                print(f"   📄 {relative_path}")
        else:
            print("❌ No images were generated")
        
        # Compare with sequential processing time estimate
        estimated_sequential_time = len(test_images) * 25  # Rough estimate: 25s per image
        speedup = estimated_sequential_time / elapsed_time if elapsed_time > 0 else 1
        
        print(f"\n📈 Performance Analysis:")
        print(f"   Sequential estimate: {estimated_sequential_time:.1f}s")
        print(f"   Pipelined actual: {elapsed_time:.1f}s")
        print(f"   Estimated speedup: {speedup:.1f}x")
        
        return len(output_files) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup test config
        if os.path.exists(test_config_path):
            os.remove(test_config_path)

def main():
    """Main test function."""
    print("🧪 PIPELINED WORKFLOW TEST")
    print("=" * 50)
    print("This test validates the dual-worker pipelined approach:")
    print("• Worker-1: GPT-4V analysis (30/min rate limit)")
    print("• Worker-2: DALL-E generation (5/min rate limit)")
    print("• Offset processing for maximum throughput")
    print()
    
    success = test_pipelined_workflow()
    
    if success:
        print("\n✅ Pipelined workflow test PASSED!")
        print("🚀 Ready for full-scale processing with:")
        print("   run_image_generator_pipelined.bat")
    else:
        print("\n❌ Pipelined workflow test FAILED!")
        print("🔧 Check the error messages above and verify:")
        print("   • OpenAI API key is set")
        print("   • Test images exist in test/assets/")
        print("   • Network connectivity")

if __name__ == "__main__":
    main() 