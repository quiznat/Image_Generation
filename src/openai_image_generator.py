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

class OpenAIImageGenerator:
    """Generate new images based on input images using OpenAI's DALL-E."""
    
    def __init__(self, config_path: str = "config/image_processing_config.json"):
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
                # Add DALL-E specific settings if not present
                if "dalle" not in config:
                    config["dalle"] = {
                        "model": "dall-e-3",
                        "size": "1024x1024",
                        "quality": "standard",
                        "n": 1
                    }
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "directories": {"input_dir": "./test", "output_dir": "./test_output"},
            "openai": {"model": "gpt-4o", "max_tokens": 4096, "temperature": 0.7},
            "dalle": {
                "model": "dall-e-3",
                "size": "1024x1024",
                "quality": "standard",
                "n": 1
            },
            "prompts": {
                "vision_analysis_prompt": "Analyze this image and describe what you see. Focus on the main object and provide a clear, detailed description that would help create an improved version for educational content for toddlers. Be specific about colors, shapes, and characteristics.",
                
                "dalle_wrapper_prompt": [
                    "Create a colorful crayon drawing based on this description: [CHATGPT_DESCRIPTION]",
                    "Style: Simple, friendly cartoon drawing for toddlers, as if drawn with crayons or colored pencils",
                    "Format: Single object centered on plain white background, filling about 80% of the image space",
                    "Quality: Bold, clean lines with bright, vibrant colors",
                    "Aesthetic: Child-friendly, warm, playful, and educational",
                    "Size: 1024x1024 pixels, no framing or borders"
                ],
                
                "follow_up_1": "Please create the image now.",
                "follow_up_2": "Okay thanks, I need to go soon please make the image file."
            },
            "processing": {
                "supported_formats": [".png", ".jpg", ".jpeg"],
                "max_retries": 2,
                "wait_between_retries": 2
            }
        }
    
    def initialize_openai_client(self) -> OpenAI:
        """Initialize OpenAI client."""
        # Load from .env file
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("OPENAI_API_KEY not found in .env file or not set properly. Please add your API key to the .env file.")
        
        # Handle potential proxy issues by explicitly configuring httpx
        try:
            # Try direct initialization first
            return OpenAI(api_key=api_key)
        except TypeError as e:
            if "proxies" in str(e):
                # If there's a proxy issue, try with custom httpx client
                import httpx
                # Create httpx client without proxy
                http_client = httpx.Client(trust_env=False)
                return OpenAI(api_key=api_key, http_client=http_client)
            else:
                raise
    
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
            
            # Create handlers with UTF-8 encoding
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            stream_handler = logging.StreamHandler()
            # Set encoding for console output if possible
            try:
                stream_handler.stream.reconfigure(encoding='utf-8')
            except AttributeError:
                pass  # Older Python versions
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[file_handler, stream_handler]
            )
        else:
            # Set up basic logging with UTF-8 support
            handler = logging.StreamHandler()
            try:
                handler.stream.reconfigure(encoding='utf-8')
            except AttributeError:
                pass  # Older Python versions
            logging.basicConfig(
                level=logging.INFO,
                handlers=[handler]
            )
        
        self.logger = logging.getLogger(__name__)
    
    def encode_image_to_base64(self, image_path: Path) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def save_image_from_url(self, image_url: str, output_path: Path) -> bool:
        """Download and save image from URL."""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Saved generated image to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving image from URL: {e}")
            return False
    
    def analyze_image(self, image_path: Path) -> Optional[str]:
        """Analyze the image and get a description for DALL-E generation."""
        self.logger.info(f"Analyzing image with GPT-4 Vision: {image_path}")
        
        base64_image = self.encode_image_to_base64(image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.config["prompts"]["vision_analysis_prompt"]
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_path.suffix[1:]};base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["openai"]["model"],
                messages=messages,
                max_tokens=self.config["openai"]["max_tokens"],
                temperature=self.config["openai"]["temperature"]
            )
            
            description = response.choices[0].message.content
            self.logger.info(f"GPT-4 Vision analysis: {description[:200]}...")
            return description
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            return None
    
    def wrap_description_for_dalle(self, chatgpt_description: str) -> str:
        """Wrap the ChatGPT description in a DALL-E prompt template."""
        prompt_template = self.config["prompts"]["dalle_wrapper_prompt"]
        
        # Handle prompt as array or string
        if isinstance(prompt_template, list):
            prompt_template = "\n".join(prompt_template)
        
        # Replace the placeholder with the actual description
        dalle_prompt = prompt_template.replace("[CHATGPT_DESCRIPTION]", chatgpt_description)
        
        self.logger.info(f"Wrapped DALL-E prompt ({len(dalle_prompt)} chars):")
        self.logger.info("=" * 60)
        self.logger.info(dalle_prompt)
        self.logger.info("=" * 60)
        
        return dalle_prompt
    
    def get_output_path(self, image_path: Path, relative_path: Path = None) -> Path:
        """Generate the output path for the generated image."""
        output_dir = Path(self.config["directories"]["output_dir"])
        
        if relative_path and relative_path.parent != Path("."):
            # Create subfolder structure in output directory
            output_subfolder = output_dir / relative_path.parent
            output_subfolder.mkdir(parents=True, exist_ok=True)
        else:
            output_subfolder = output_dir
        
        # Generate output filename
        output_filename = f"{image_path.stem}_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        return output_subfolder / output_filename

    def process_single_image(self, image_path: Path, relative_path: Path = None) -> bool:
        """Process a single image: analyze with GPT-4V, wrap response, generate with DALL-E."""
        self.logger.info(f"Processing image: {image_path}")
        
        # Step 1: Analyze the image with GPT-4 Vision
        self.logger.info("Step 1: Analyzing image with GPT-4 Vision...")
        chatgpt_description = self.analyze_image(image_path)
        
        if not chatgpt_description:
            self.logger.error("Failed to analyze image with GPT-4 Vision")
            return False
        
        # Step 2: Wrap the ChatGPT response in a DALL-E prompt template
        self.logger.info("Step 2: Wrapping description for DALL-E...")
        dalle_prompt = self.wrap_description_for_dalle(chatgpt_description)
        
        # Step 3: Generate output path
        output_path = self.get_output_path(image_path, relative_path)
        
        # Step 4: Generate image with DALL-E
        self.logger.info("Step 3: Generating image with DALL-E...")
        return self.generate_image_with_dalle(dalle_prompt, output_path)
    
    def generate_image_with_dalle(self, dalle_prompt: str, output_path: Path) -> bool:
        """Generate a new image using DALL-E based on the prompt."""
        attempts = 0
        
        while attempts <= self.config["processing"]["max_retries"]:
            try:
                if attempts > 0:
                    # Use follow-up messages for retries
                    follow_up_key = f"follow_up_{attempts}"
                    dalle_prompt = self.config["prompts"].get(follow_up_key, "Please create the image now.")
                
                self.logger.info(f"Attempt {attempts + 1}: Generating image with DALL-E")
                self.logger.info(f"Prompt preview: {dalle_prompt[:200]}...")
                
                # Generate image using DALL-E
                response = self.client.images.generate(
                    model=self.config["dalle"]["model"],
                    prompt=dalle_prompt[:4000],  # DALL-E has a prompt limit
                    size=self.config["dalle"]["size"],
                    quality=self.config["dalle"]["quality"],
                    n=self.config["dalle"]["n"]
                )
                
                # Get the image URL
                if response.data and len(response.data) > 0:
                    image_url = response.data[0].url
                    
                    if self.save_image_from_url(image_url, output_path):
                        self.logger.info(f"Successfully generated and saved: {output_path}")
                        return True
                
                # If we didn't get an image, increment attempts
                attempts += 1
                if attempts <= self.config["processing"]["max_retries"]:
                    self.logger.info(f"No image generated, trying follow-up...")
                    time.sleep(self.config["processing"]["wait_between_retries"])
                
            except Exception as e:
                self.logger.error(f"Error generating image: {e}")
                attempts += 1
                
                if attempts <= self.config["processing"]["max_retries"]:
                    time.sleep(self.config["processing"]["wait_between_retries"])
        
        self.logger.warning(f"Failed to generate image after {attempts} attempts")
        return False
    
    def process_directory(self):
        """Process all images in the input directory and subdirectories."""
        input_dir = Path(self.config["directories"]["input_dir"])
        supported_formats = self.config["processing"]["supported_formats"]
        
        # Find all image files recursively
        image_files = []
        for format in supported_formats:
            # Use rglob for recursive search
            image_files.extend(input_dir.rglob(f"*{format}"))
            image_files.extend(input_dir.rglob(f"*{format.upper()}"))
        
        # Remove duplicates
        image_files = list(set(image_files))
        
        if not image_files:
            self.logger.warning(f"No image files found in {input_dir}")
            print(f"\nNo images found in '{input_dir}' or its subdirectories")
            print(f"Supported formats: {', '.join(supported_formats)}")
            print("\nNote: This tool uses GPT-4 Vision to analyze images before generation!")
            print("Workflow: Image → GPT-4V Analysis → Wrap Description → DALL-E Generation")
            return
        
        # Group files by directory for better progress display
        files_by_dir = {}
        for image_file in image_files:
            relative_path = image_file.relative_to(input_dir)
            dir_path = relative_path.parent
            if dir_path not in files_by_dir:
                files_by_dir[dir_path] = []
            files_by_dir[dir_path].append((image_file, relative_path))
        
        self.logger.info(f"Found {len(image_files)} image(s) in {len(files_by_dir)} directories")
        print(f"\n🔍 [Vision-Enhanced] Found {len(image_files)} image(s) in {len(files_by_dir)} directories")
        print("📋 [Workflow] GPT-4V Analysis → Wrap Description → DALL-E Generation")
        print("⚠️  [Note] This is slower but more intelligent than v2_simple\n")
        
        # Process each image
        success_count = 0
        total_processed = 0
        
        for dir_path, files in sorted(files_by_dir.items()):
            if str(dir_path) != ".":
                print(f"\n📁 Processing directory: {dir_path}")
            
            for image_file, relative_path in sorted(files):
                total_processed += 1
                print(f"\n[{total_processed}/{len(image_files)}] {relative_path}")
                
                if self.process_single_image(image_file, relative_path):
                    success_count += 1
                    print(f"    ✅ Generated successfully")
                else:
                    print(f"    ❌ Generation failed")
                
                # Small delay between images to avoid rate limits
                if total_processed < len(image_files):
                    time.sleep(2)
        
        print(f"\n🎉 [COMPLETE] Generated: {success_count}/{len(image_files)} images")
        print(f"📁 [OUTPUT] Directory: {self.config['directories']['output_dir']}")
        print(f"💡 [TIP] Use Canva for background removal if needed")
        self.logger.info(f"Processing complete: {success_count}/{len(image_files)} images processed successfully")


def main():
    """Main function to run the image generator."""
    print("=== OpenAI Image Generator ===")
    print("Direct DALL-E generation using filename as object description")
    print("=" * 60)
    
    try:
        generator = OpenAIImageGenerator()
        generator.process_directory()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 