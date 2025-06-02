#!/usr/bin/env python3
"""Test script to validate the DALL-E prompt from config."""
import json
from pathlib import Path

def test_prompt_config():
    """Load config and show what prompt would be generated."""
    
    # Load config
    config_path = Path("config/image_processing_config-v2.json")
    print(f"Loading config from: {config_path}")
    print("=" * 80)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Get prompt template
    prompt_template = config["prompts"]["initial_prompt"]
    
    # If it's a list, join it
    if isinstance(prompt_template, list):
        prompt_template = "\n".join(prompt_template)
    
    # Test with a few example objects
    test_objects = ["red barn", "courthouse", "happy sun", "green tractor"]
    
    print("PROMPT TEMPLATE:")
    print("-" * 80)
    print(prompt_template)
    print("-" * 80)
    
    print("\nEXAMPLE PROMPTS:")
    for obj in test_objects:
        print(f"\nObject: '{obj}'")
        print("-" * 40)
        test_prompt = prompt_template.replace("[OBJECT_NAME]", obj).replace("[OBJECT_DESCRIPTION]", obj)
        print(test_prompt)
        print(f"Length: {len(test_prompt)} characters")
    
    # Show other config settings
    print("\n" + "=" * 80)
    print("OTHER CONFIG SETTINGS:")
    print(f"DALL-E Model: {config['dalle']['model']}")
    print(f"Image Size: {config['dalle']['size']}")
    print(f"Quality: {config['dalle']['quality']}")
    print(f"Input Directory: {config['directories']['input_dir']}")
    print(f"Output Directory: {config['directories']['output_dir']}")

if __name__ == "__main__":
    test_prompt_config() 