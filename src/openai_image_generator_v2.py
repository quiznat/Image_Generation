import os
import json
import base64
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from openai import OpenAI
import logging
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file
load_dotenv()

class OpenAIImageGeneratorV2:
    """Generate new images directly with DALL-E using filename as description."""
    
    def __init__(self, config_path: str = "config/image_processing_config-v2.json"):
        """Initialize the image generator with configuration."""
        self.config = self.load_config(config_path)
        self.client = self.initialize_openai_client()
        self.setup_directories()
        self.setup_logging()
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            # Return minimal default config
            return {
                "directories": {"input_dir": "./test", "output_dir": "./test_output"},
                "openai": {"model": "gpt-4o", "max_tokens": 4096, "temperature": 0},
                "dalle": {"model": "dall-e-3", "size": "1024x1024", "quality": "hd", "n": 1},
                "background_removal": {"enabled": True, "save_both_versions": True, "model": "u2net"},
                "prompts": {
                    "initial_prompt": "Create a crayon-style illustration... [OBJECT_DESCRIPTION]...",
                    "follow_up_1": "Please create the image now.",
                    "follow_up_2": "Okay thanks, I need to go soon please make the image file."
                },
                "processing": {"supported_formats": [".png", ".jpg", ".jpeg"], "max_retries": 2, "wait_between_retries": 2}
            }
    
    def initialize_openai_client(self) -> OpenAI:
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("OPENAI_API_KEY not found in .env file or not set properly.")
        return OpenAI(api_key=api_key)
    
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_key in ["input_dir", "output_dir"]:
            dir_path = Path(self.config["directories"][dir_key])
            dir_path.mkdir(parents=True, exist_ok=True)
        
        if self.config.get("logging", {}).get("log_responses", False):
            log_dir = Path(self.config["logging"]["log_dir"])
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging configuration."""
        if self.config.get("logging", {}).get("log_responses", False):
            log_dir = Path(self.config["logging"]["log_dir"])
            log_file = log_dir / f"image_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(level=logging.INFO)
        
        self.logger = logging.getLogger(__name__)
        
    def save_image_from_url(self, image_url: str, output_path: Path) -> bool:
        """Download and save image from URL with optional background removal."""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Saved generated image to: {output_path}")
            
            # Handle background removal if enabled
            if self.config.get("background_removal", {}).get("enabled", False):
                bg_removed_path = self.remove_background(output_path)
                
                if bg_removed_path:
                    # If not saving both versions, replace the original
                    if not self.config["background_removal"].get("save_both_versions", True):
                        output_path.unlink()  # Delete original
                        bg_removed_path.rename(output_path)  # Rename nobg version
                        self.logger.info(f"Replaced original with background-removed version")
                else:
                    self.logger.warning("Background removal failed, keeping original image")
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving image from URL: {e}")
            return False
    
    def process_single_image(self, image_path: Path, relative_path: Path = None) -> bool:
        """Process a single image: generate directly with DALL-E using filename."""
        self.logger.info(f"Processing: {relative_path if relative_path else image_path}")
        
        # Extract object description from filename (without extension)
        object_description = image_path.stem.replace("_", " ").replace("-", " ")
        self.logger.info(f"Object: {object_description}")
        
        # Get the prompt template and replace [OBJECT_DESCRIPTION]
        prompt_template = self.config["prompts"]["initial_prompt"]
        dalle_prompt = prompt_template.replace("[OBJECT_DESCRIPTION]", object_description)
        
        # Determine output path with subfolder structure
        output_dir = Path(self.config["directories"]["output_dir"])
        if relative_path and relative_path.parent != Path("."):
            output_subfolder = output_dir / relative_path.parent
            output_subfolder.mkdir(parents=True, exist_ok=True)
        else:
            output_subfolder = output_dir
        
        # Generate output filename
        output_filename = f"{image_path.stem}_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = output_subfolder / output_filename
        
        # Generate image with DALL-E
        attempts = 0
        while attempts <= self.config["processing"]["max_retries"]:
            try:
                # Use follow-up prompts for retries
                if attempts > 0:
                    follow_up_key = f"follow_up_{attempts}"
                    dalle_prompt = self.config["prompts"].get(follow_up_key, "Please create the image now.")
                    self.logger.info(f"Retry {attempts} with: {dalle_prompt}")
                
                self.logger.info(f"Generating with DALL-E (attempt {attempts + 1})")
                
                # Generate image
                response = self.client.images.generate(
                    model=self.config["dalle"]["model"],
                    prompt=dalle_prompt[:4000],  # DALL-E prompt limit
                    size=self.config["dalle"]["size"],
                    quality=self.config["dalle"]["quality"],
                    n=self.config["dalle"]["n"]
                )
                
                # Save if successful
                if response.data and len(response.data) > 0:
                    image_url = response.data[0].url
                    
                    if self.save_image_from_url(image_url, output_path):
                        self.logger.info(f"✅ Success: {output_path}")
                        return True
                
                # Retry if needed
                attempts += 1
                if attempts <= self.config["processing"]["max_retries"]:
                    self.logger.info(f"No image generated, retrying...")
                    time.sleep(self.config["processing"]["wait_between_retries"])
                
            except Exception as e:
                self.logger.error(f"Error: {e}")
                attempts += 1
                
                if attempts <= self.config["processing"]["max_retries"]:
                    time.sleep(self.config["processing"]["wait_between_retries"])
        
        self.logger.warning(f"Failed after {attempts} attempts")
        return False
    
    def process_directory(self):
        """Process all images in the input directory and subdirectories."""
        input_dir = Path(self.config["directories"]["input_dir"])
        supported_formats = self.config["processing"]["supported_formats"]
        
        # Find all image files recursively
        image_files = []
        for format in supported_formats:
            image_files.extend(input_dir.rglob(f"*{format}"))
            image_files.extend(input_dir.rglob(f"*{format.upper()}"))
        
        # Remove duplicates
        image_files = list(set(image_files))
        
        if not image_files:
            self.logger.warning(f"No image files found in {input_dir}")
            print(f"\nNo images found in '{input_dir}'")
            print(f"Supported formats: {', '.join(supported_formats)}")
            print("\nNote: This tool now uses filenames as object descriptions!")
            print("Example: 'courthouse.png' → 'courthouse' in the prompt")
            return
        
        print(f"\n📸 Found {len(image_files)} image(s)")
        print("📝 Using filenames as object descriptions")
        print("🎨 Generating directly with DALL-E (no analysis step)\n")
        
        # Process each image
        success_count = 0
        for i, image_file in enumerate(sorted(image_files), 1):
            relative_path = image_file.relative_to(input_dir)
            print(f"[{i}/{len(image_files)}] {relative_path}")
            
            if self.process_single_image(image_file, relative_path):
                success_count += 1
                print(f"    ✅ Generated successfully")
            else:
                print(f"    ❌ Generation failed")
            
            # Delay between images
            if i < len(image_files):
                time.sleep(2)
        
        print(f"\n🎉 Complete: {success_count}/{len(image_files)} images generated")
        print(f"📁 Output: {self.config['directories']['output_dir']}")
        
        if self.config.get("background_removal", {}).get("enabled", False):
            print(f"🎨 Background removal: Enabled")
            if self.config["background_removal"].get("save_both_versions", True):
                print(f"    - Original + transparent versions saved")
            else:
                print(f"    - Only transparent versions saved")


def main():
    """Main function to run the image generator."""
    print("=== OpenAI Image Generator V2 ===")
    print("Direct DALL-E generation using filenames")
    print("=" * 40)
    
    try:
        generator = OpenAIImageGeneratorV2()
        generator.process_directory()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 