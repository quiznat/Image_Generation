#!/usr/bin/env python3
"""Monitor image generation progress."""
import os
from pathlib import Path
import time
from datetime import datetime

def count_files_recursive(directory, extensions=['.png', '.jpg', '.jpeg']):
    """Count files with specific extensions in directory and subdirectories."""
    count = 0
    if directory.exists():
        for ext in extensions:
            count += len(list(directory.rglob(f"*{ext}")))
    return count

def main():
    test_dir = Path("./test")
    output_dir = Path("./test_output")
    
    # Count source images
    source_count = count_files_recursive(test_dir)
    
    print("=== Image Generation Progress Monitor ===")
    print(f"Source images: {source_count}")
    print(f"Output directory: {output_dir}")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            # Count generated images
            generated_count = count_files_recursive(output_dir, ['.png'])
            
            # Calculate percentage
            percentage = (generated_count / source_count * 100) if source_count > 0 else 0
            
            # Create progress bar
            bar_length = 50
            filled_length = int(bar_length * generated_count // source_count)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Print progress
            print(f"\r[{bar}] {generated_count}/{source_count} ({percentage:.1f}%) - {datetime.now().strftime('%H:%M:%S')}", end='', flush=True)
            
            # Check if complete
            if generated_count >= source_count:
                print("\n\n✅ Generation complete!")
                break
                
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print(f"Final count: {count_files_recursive(output_dir, ['.png'])} images generated")

if __name__ == "__main__":
    main() 