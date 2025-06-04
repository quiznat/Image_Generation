#!/usr/bin/env python3
"""
Create Evolution Animation Script
=================================

Creates animated GIFs showing AI evolution across loop iterations.
Processes all images from test_loop/1/ through test_loop/10/
"""

import os
from pathlib import Path
from PIL import Image
import argparse
from datetime import datetime


def find_evolution_chains(base_dir: Path) -> dict:
    """Find all evolution chains based on base filenames, including original images."""
    chains = {}
    
    # First, look for original images in the base directory
    for image_path in base_dir.glob("*.png"):
        base_name = image_path.stem
        if base_name not in chains:
            chains[base_name] = {}
        chains[base_name][0] = image_path  # Original image as frame 0
    
    for image_path in base_dir.glob("*.jpg"):
        base_name = image_path.stem
        if base_name not in chains:
            chains[base_name] = {}
        chains[base_name][0] = image_path  # Original image as frame 0
    
    # Then look through all iteration directories
    for i in range(1, 11):
        iter_dir = base_dir / str(i)
        if not iter_dir.exists():
            continue
            
        # Find all images in this iteration
        for image_path in iter_dir.glob("*.png"):
            # Extract base name (everything before _L{number})
            stem = image_path.stem
            if "_L" in stem:
                base_name = "_L".join(stem.split("_L")[:-1])
            else:
                base_name = stem
                
            if base_name not in chains:
                chains[base_name] = {}
            
            chains[base_name][i] = image_path
    
    return chains


def create_animated_gif(image_paths: list, output_path: Path, duration: int = 800, size: tuple = (512, 512)):
    """Create an animated GIF from a list of image paths."""
    frames = []
    
    for path in image_paths:
        if path and path.exists():
            img = Image.open(path)
            # Resize to consistent size
            img = img.resize(size, Image.Resampling.LANCZOS)
            # Convert to RGB if needed (for GIF)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            frames.append(img)
        else:
            print(f"⚠️  Missing: {path}")
    
    if frames:
        # Create animated GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0  # Loop forever
        )
        return True
    return False


def create_grid_image(image_paths: list, output_path: Path, grid_size: tuple = (5, 2), image_size: tuple = (256, 256)):
    """Create a grid montage showing all iterations at once."""
    cols, rows = grid_size
    total_width = cols * image_size[0]
    total_height = rows * image_size[1]
    
    # Create blank canvas
    grid_img = Image.new('RGB', (total_width, total_height), 'white')
    
    for idx, path in enumerate(image_paths[:cols * rows]):
        if path and path.exists():
            img = Image.open(path)
            img = img.resize(image_size, Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate position
            col = idx % cols
            row = idx // cols
            x = col * image_size[0]
            y = row * image_size[1]
            
            grid_img.paste(img, (x, y))
    
    grid_img.save(output_path)
    return True


def main():
    parser = argparse.ArgumentParser(description='Create evolution animations from loop processor output')
    parser.add_argument('--base-dir', type=str, default='./test_loop', help='Base directory containing loop iterations')
    parser.add_argument('--output-dir', type=str, default='./evolution_animations', help='Output directory for animations')
    parser.add_argument('--duration', type=int, default=800, help='Frame duration in milliseconds (default: 800)')
    parser.add_argument('--size', type=int, nargs=2, default=[512, 512], help='Animation size (width height)')
    parser.add_argument('--grid-only', action='store_true', help='Create only grid images, no animations')
    parser.add_argument('--animation-only', action='store_true', help='Create only animations, no grids')
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"🔍 Looking for evolution chains in: {base_dir}")
    
    # Find all evolution chains
    chains = find_evolution_chains(base_dir)
    
    if not chains:
        print(f"❌ No evolution chains found in {base_dir}")
        print(f"   Make sure you have directories 1/, 2/, ..., 10/ with images")
        return
    
    print(f"✅ Found {len(chains)} evolution chains")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for base_name, iterations in chains.items():
        print(f"\n🎬 Processing: {base_name}")
        print(f"   Found iterations: {sorted(iterations.keys())}")
        
        # Create ordered list of image paths (now including frame 0)
        image_paths = []
        for i in range(0, 11):  # 0 through 10 (11 frames total)
            if i in iterations:
                image_paths.append(iterations[i])
                if i == 0:
                    print(f"   Original: ✅ {iterations[i].name}")
                else:
                    print(f"   L{i}: ✅ {iterations[i].name}")
            else:
                image_paths.append(None)
                if i == 0:
                    print(f"   Original: ❌ Missing")
                else:
                    print(f"   L{i}: ❌ Missing")
        
        # Create animated GIF
        if not args.grid_only:
            gif_path = output_dir / f"{base_name}_evolution_{timestamp}.gif"
            print(f"🎥 Creating animation: {gif_path}")
            
            success = create_animated_gif(
                [p for p in image_paths if p], 
                gif_path, 
                duration=args.duration,
                size=tuple(args.size)
            )
            
            if success:
                print(f"✅ Animation created: {gif_path}")
            else:
                print(f"❌ Failed to create animation")
        
        # Create grid image
        if not args.animation_only:
            grid_path = output_dir / f"{base_name}_grid_{timestamp}.png"
            print(f"🖼️  Creating grid: {grid_path}")
            
            success = create_grid_image(
                [p for p in image_paths if p],
                grid_path,
                grid_size=(6, 2),  # 6x2 grid for 11 images (original + L1-L10)
                image_size=(256, 256)
            )
            
            if success:
                print(f"✅ Grid created: {grid_path}")
            else:
                print(f"❌ Failed to create grid")
    
    print(f"\n🎉 Evolution visualization complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"🎬 Animated GIFs: Show Original → L1 → L2 → ... → L10 (11 frames)")
    print(f"🖼️  Grid images: Original + 10 iterations in 6x2 layout")


if __name__ == "__main__":
    main() 