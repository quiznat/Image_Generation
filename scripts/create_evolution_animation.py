#!/usr/bin/env python3
"""
Create Evolution Animation Script
=================================

Creates animated GIFs showing AI evolution across loop iterations.
Auto-detects available iterations and processes all found frames.
Supports any number of iterations (not limited to 10).

Features:
- Frame interpolation for smooth transitions (crossfade, morph)
- Dynamic grid layouts for any number of frames
- Configurable animation speed and quality
"""

import os
from pathlib import Path
from PIL import Image
import argparse
from datetime import datetime
import numpy as np
import json


def load_config(config_path: str = "config/animation_config.json") -> dict:
    """Load animation configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ Loaded config from: {config_path}")
        return config
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_path}")
        print("   Using default settings...")
        return {
            "animation_settings": {
                "base_directory": "./test_loop",
                "output_directory": "./evolution_animations", 
                "duration": 800,
                "size": [512, 512],
                "max_iterations": None,
                "interpolation": "none",
                "interpolation_steps": 3,
                "grid_only": False,
                "animation_only": False
            }
        }
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}")
        print("   Using default settings...")
        return load_config()  # Return defaults


def find_evolution_chains(base_dir: Path, max_iterations: int = None) -> dict:
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
    
    # Auto-detect maximum iteration if not specified
    if max_iterations is None:
        max_iterations = 0
        for i in range(1, 101):  # Check up to 100 iterations
            iter_dir = base_dir / str(i)
            if iter_dir.exists():
                max_iterations = i
            else:
                break
        print(f"🔍 Auto-detected max iterations: {max_iterations}")
    
    # Then look through all iteration directories
    for i in range(1, max_iterations + 1):
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


def create_animated_gif(image_paths: list, output_path: Path, hold_duration: int, transition_duration: int, size: tuple = (512, 512), 
                       interpolation_mode: str = "none", interpolation_steps: int = 3):
    """Create an animated GIF from a list of image paths with optional frame interpolation."""
    frames = []
    durations = []  # Track duration for each frame
    
    # Load and resize all images first
    loaded_images = []
    for path in image_paths:
        if path and path.exists():
            img = Image.open(path)
            # Resize to consistent size
            img = img.resize(size, Image.Resampling.LANCZOS)
            # Convert to RGB if needed (for GIF)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            loaded_images.append(img)
        else:
            print(f"⚠️  Missing: {path}")

    if not loaded_images:
        return False

    # Add first frame (main frame - use hold duration)
    frames.append(loaded_images[0])
    durations.append(hold_duration)

    # Add interpolated frames between consecutive images
    if interpolation_mode != "none" and len(loaded_images) > 1:
        print(f"🎬 Creating {interpolation_steps} interpolation frames between each transition...")
        
        for i in range(len(loaded_images) - 1):
            current_img = loaded_images[i]
            next_img = loaded_images[i + 1]
            
            # Create transition frames
            if interpolation_mode == "crossfade":
                transition_frames = create_crossfade_frames(current_img, next_img, interpolation_steps)
            elif interpolation_mode == "morph":
                transition_frames = create_morph_frames(current_img, next_img, interpolation_steps)
            else:
                transition_frames = []
            
            # Add transition frames (use transition duration)
            frames.extend(transition_frames)
            durations.extend([transition_duration] * len(transition_frames))
            
            # Add the next main frame (use hold duration)
            frames.append(next_img)
            durations.append(hold_duration)
    else:
        # No interpolation - just add remaining frames (all main frames use hold duration)
        frames.extend(loaded_images[1:])
        durations.extend([hold_duration] * len(loaded_images[1:]))

    if frames:
        print(f"📺 Total frames: {len(frames)}")
        print(f"   Main frames: {len([d for d in durations if d == hold_duration])} @ {hold_duration}ms each")
        print(f"   Transition frames: {len([d for d in durations if d == transition_duration])} @ {transition_duration}ms each")
        
        # Create animated GIF with per-frame durations
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,  # Use list of durations instead of single value
            loop=0  # Loop forever
        )
        return True
    return False


def create_grid_image(image_paths: list, output_path: Path, grid_size: tuple = None, image_size: tuple = (256, 256)):
    """Create a grid montage showing all iterations at once."""
    total_images = len(image_paths)
    
    # Auto-calculate grid size if not specified
    if grid_size is None:
        # Try to make a roughly square grid, but prefer wider than tall
        import math
        cols = math.ceil(math.sqrt(total_images * 1.5))  # Bias toward wider
        rows = math.ceil(total_images / cols)
        grid_size = (cols, rows)
        print(f"📐 Auto-calculated grid: {cols}x{rows} for {total_images} images")
    
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


def create_crossfade_frames(img1: Image.Image, img2: Image.Image, steps: int = 3) -> list:
    """Create crossfade transition frames between two images."""
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    # Convert to numpy arrays for blending
    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)
    
    transition_frames = []
    for i in range(1, steps + 1):
        # Calculate blend ratio (0.0 to 1.0)
        alpha = i / (steps + 1)
        
        # Blend the images
        blended = arr1 * (1 - alpha) + arr2 * alpha
        blended = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Convert back to PIL Image
        transition_frame = Image.fromarray(blended)
        transition_frames.append(transition_frame)
    
    return transition_frames


def create_morph_frames(img1: Image.Image, img2: Image.Image, steps: int = 3) -> list:
    """Create morphing transition frames with more sophisticated blending."""
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    # Convert to numpy arrays
    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)
    
    transition_frames = []
    for i in range(1, steps + 1):
        # Use smooth easing function for more natural transitions
        t = i / (steps + 1)
        # Smooth step function: 3t² - 2t³
        alpha = 3 * t * t - 2 * t * t * t
        
        # Advanced blending with some edge preservation
        blended = arr1 * (1 - alpha) + arr2 * alpha
        
        # Optional: Add slight gaussian blur for smoother morphing
        from PIL import ImageFilter
        blended_img = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))
        blended_img = blended_img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        transition_frames.append(blended_img)
    
    return transition_frames


def main():
    # Load configuration first
    config = load_config()
    settings = config["animation_settings"]
    
    parser = argparse.ArgumentParser(description='Create evolution animations from loop processor output')
    parser.add_argument('--config', type=str, default='config/animation_config.json', help='Configuration file path')
    parser.add_argument('--base-dir', type=str, default=settings["base_directory"], help='Base directory containing loop iterations')
    parser.add_argument('--output-dir', type=str, default=settings["output_directory"], help='Output directory for animations')
    parser.add_argument('--hold-duration', type=int, default=settings["hold_duration"], help='Hold time for main frames (ms)')
    parser.add_argument('--transition-duration', type=int, default=settings["transition_duration"], help='Duration for transition frames (ms)')
    parser.add_argument('--size', type=int, nargs=2, default=settings["size"], help='Animation size (width height)')
    parser.add_argument('--max-iterations', type=int, default=settings["max_iterations"], help='Maximum iteration to process (auto-detect if not specified)')
    parser.add_argument('--interpolation', type=str, choices=['none', 'crossfade', 'morph'], default=settings["interpolation"], 
                       help='Frame interpolation mode')
    parser.add_argument('--interpolation-steps', type=int, default=settings["interpolation_steps"], 
                       help='Number of interpolation frames between each transition')
    parser.add_argument('--grid-only', action='store_true', default=settings["grid_only"], help='Create only grid images, no animations')
    parser.add_argument('--animation-only', action='store_true', default=settings["animation_only"], help='Create only animations, no grids')
    
    args = parser.parse_args()
    
    # If a different config file is specified, reload it
    if args.config != 'config/animation_config.json':
        config = load_config(args.config)
        settings = config["animation_settings"]
    
    print(f"🎬 Animation Settings:")
    print(f"   📁 Input: {args.base_dir}")
    print(f"   📤 Output: {args.output_dir}")  
    print(f"   ⏱️  Hold duration: {args.hold_duration}ms")
    print(f"   ⏱️  Transition duration: {args.transition_duration}ms")
    print(f"   📐 Size: {args.size[0]}x{args.size[1]}")
    print(f"   ✨ Interpolation: {args.interpolation} ({args.interpolation_steps} steps)")
    
    base_dir = Path(args.base_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"🔍 Looking for evolution chains in: {base_dir}")
    
    # Find all evolution chains
    chains = find_evolution_chains(base_dir, args.max_iterations)
    
    if not chains:
        print(f"❌ No evolution chains found in {base_dir}")
        print(f"   Make sure you have numbered directories with images")
        return
    
    print(f"✅ Found {len(chains)} evolution chains")
    
    # Find the actual max iteration across all chains
    max_found = 0
    for chain_iterations in chains.values():
        if chain_iterations:
            max_found = max(max_found, max(chain_iterations.keys()))
    
    print(f"📊 Processing frames: 0 (original) → L1 → L2 → ... → L{max_found}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for base_name, iterations in chains.items():
        print(f"\n🎬 Processing: {base_name}")
        print(f"   Found iterations: {sorted(iterations.keys())}")
        
        # Create ordered list of image paths (dynamic range)
        image_paths = []
        for i in range(0, max_found + 1):  # 0 through max_found
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
                hold_duration=args.hold_duration,
                transition_duration=args.transition_duration,
                size=tuple(args.size),
                interpolation_mode=args.interpolation,
                interpolation_steps=args.interpolation_steps
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
                grid_size=None,  # Auto-calculate based on number of images
                image_size=(256, 256)
            )
            
            if success:
                print(f"✅ Grid created: {grid_path}")
            else:
                print(f"❌ Failed to create grid")
    
    print(f"\n🎉 Evolution visualization complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"🎬 Animated GIFs: Show Original → L1 → L2 → ... → L{max_found} ({max_found + 1} frames)")
    if args.interpolation != "none":
        total_interpolated = (max_found) * args.interpolation_steps
        print(f"✨ Interpolation: {args.interpolation} mode with {args.interpolation_steps} steps (+{total_interpolated} transition frames)")
    print(f"🖼️  Grid images: Auto-sized layout for all frames")


if __name__ == "__main__":
    main() 