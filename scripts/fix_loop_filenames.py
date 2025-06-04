#!/usr/bin/env python3
"""
Fix Loop Filenames Script
=========================

Renames files in test_loop iterations to consistent format: basename_L{number}.png
This ensures the animation script can properly find evolution chains.
"""

import os
import re
from pathlib import Path


def extract_base_name(filename: str) -> str:
    """Extract the original base name from various filename formats."""
    # Remove file extension
    name = Path(filename).stem
    
    # Handle different patterns
    if name.startswith("A"):
        return "A"
    elif "fish" in name.lower():
        return "Fish"
    elif name.startswith("rdt_"):
        # Extract meaningful part or use generic name
        return "Image3"  # or we could extract more info
    
    # For other files, try to extract the meaningful part
    # Remove common suffixes
    for pattern in ["_generated_", "_L"]:
        if pattern in name:
            name = name.split(pattern)[0]
    
    # Clean up common prefixes/suffixes
    name = re.sub(r'_\d{8}_\d{6}.*', '', name)  # Remove timestamps
    name = re.sub(r'g\d+$', '', name)  # Remove trailing g{number}
    
    return name


def fix_filenames_in_directory(directory: Path, iteration_num: int):
    """Fix filenames in a specific iteration directory."""
    if not directory.exists():
        print(f"⚠️  Directory {directory} doesn't exist")
        return
    
    print(f"\n📁 Processing {directory}:")
    
    # Get all image files
    image_files = list(directory.glob("*.png")) + list(directory.glob("*.jpg")) + list(directory.glob("*.jpeg"))
    
    if not image_files:
        print(f"   No image files found")
        return
    
    for file_path in image_files:
        # Extract base name
        base_name = extract_base_name(file_path.name)
        
        # Create new filename
        new_filename = f"{base_name}_L{iteration_num}.png"
        new_path = directory / new_filename
        
        if file_path.name == new_filename:
            print(f"   ✅ {file_path.name} (already correct)")
            continue
        
        # Check if target already exists
        if new_path.exists():
            print(f"   ⚠️  {file_path.name} -> {new_filename} (target exists, skipping)")
            continue
        
        try:
            # Rename the file
            file_path.rename(new_path)
            print(f"   🔄 {file_path.name} -> {new_filename}")
        except Exception as e:
            print(f"   ❌ Failed to rename {file_path.name}: {e}")


def main():
    base_dir = Path("./test_loop")
    
    if not base_dir.exists():
        print(f"❌ Directory {base_dir} not found")
        return
    
    print("🔧 Fixing loop filenames for consistent animation...")
    print(f"📁 Base directory: {base_dir}")
    
    # Process each iteration directory
    for i in range(1, 11):
        iter_dir = base_dir / str(i)
        fix_filenames_in_directory(iter_dir, i)
    
    print(f"\n✅ Filename fixing complete!")
    print(f"🎬 Now you can run: create_evolution_animation.bat")
    print(f"📊 Expected chains: A_L1.png -> A_L2.png -> ... -> A_L10.png")
    print(f"                   Fish_L1.png -> Fish_L2.png -> ... -> Fish_L10.png")


if __name__ == "__main__":
    main() 