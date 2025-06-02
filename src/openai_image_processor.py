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

# Load environment variables from .env file
load_dotenv()

class OpenAIImageProcessor:
    """Process images using OpenAI API with follow-up logic."""
    
    def __init__(self, config_path: str = "config/image_processing_config.json"):
        """Initialize the image processor with configuration."""
        self.config = self.load_config(config_path)
        self.client = self.initialize_openai_client()
        self.setup_directories()
        self.setup_logging()
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Return default config
            return {
                "directories": {"input_dir": "./test", "output_dir": "./test_output"},
                "openai": {"model": "gpt-4o", "max_tokens": 4096, "temperature": 0.7},
                "prompts": {
                    "initial_prompt": "Please analyze and improve this image.",
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
            log_file = log_dir / f"image_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
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
            
            self.logger.info(f"Saved image to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving image from URL: {e}")
            return False
    
    def save_image_from_base64(self, base64_string: str, output_path: Path) -> bool:
        """Save image from base64 string."""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            with open(output_path, 'wb') as f:
                f.write(image_data)
            
            self.logger.info(f"Saved base64 image to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving base64 image: {e}")
            return False
    
    def extract_image_from_response(self, response) -> Optional[Tuple[str, str]]:
        """Extract image URL or base64 data from OpenAI response."""
        try:
            # Check if response contains image
            if hasattr(response, 'data') and response.data:
                # DALL-E style response
                image_data = response.data[0]
                if hasattr(image_data, 'url'):
                    return ('url', image_data.url)
                elif hasattr(image_data, 'b64_json'):
                    return ('base64', image_data.b64_json)
            
            # Check message content for images
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                
                # Check for image in content
                if hasattr(message, 'content') and isinstance(message.content, list):
                    for content_item in message.content:
                        if hasattr(content_item, 'type') and content_item.type == 'image':
                            if hasattr(content_item, 'image_url'):
                                return ('url', content_item.image_url.url)
                            elif hasattr(content_item, 'image'):
                                return ('base64', content_item.image)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting image from response: {e}")
            return None
    
    def process_single_image(self, image_path: Path) -> bool:
        """Process a single image with follow-up logic."""
        self.logger.info(f"Processing image: {image_path}")
        
        # Encode image
        base64_image = self.encode_image_to_base64(image_path)
        
        # Prepare messages
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.config["prompts"]["initial_prompt"]
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
        
        # Try to get image response
        for attempt in range(self.config["processing"]["max_retries"] + 1):
            try:
                # Make API call
                self.logger.info(f"Attempt {attempt + 1}: Sending request to OpenAI")
                
                response = self.client.chat.completions.create(
                    model=self.config["openai"]["model"],
                    messages=messages,
                    max_tokens=self.config["openai"]["max_tokens"],
                    temperature=self.config["openai"]["temperature"]
                )
                
                # Log response
                self.logger.info(f"Received response: {response.choices[0].message.content[:200]}...")
                
                # Check for image in response
                image_data = self.extract_image_from_response(response)
                
                if image_data:
                    # Save the image
                    output_filename = f"{image_path.stem}_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}{image_path.suffix}"
                    output_path = Path(self.config["directories"]["output_dir"]) / output_filename
                    
                    if image_data[0] == 'url':
                        success = self.save_image_from_url(image_data[1], output_path)
                    else:  # base64
                        success = self.save_image_from_base64(image_data[1], output_path)
                    
                    if success:
                        self.logger.info(f"Successfully processed and saved: {output_filename}")
                        return True
                else:
                    # No image found, add follow-up message
                    if attempt < self.config["processing"]["max_retries"]:
                        follow_up_key = f"follow_up_{attempt + 1}"
                        follow_up_text = self.config["prompts"].get(follow_up_key, "Please create the image.")
                        
                        self.logger.info(f"No image found, sending follow-up: {follow_up_text}")
                        
                        # Add assistant response and follow-up
                        messages.append({
                            "role": "assistant",
                            "content": response.choices[0].message.content
                        })
                        messages.append({
                            "role": "user",
                            "content": follow_up_text
                        })
                        
                        # Wait before retry
                        time.sleep(self.config["processing"]["wait_between_retries"])
                    
            except Exception as e:
                self.logger.error(f"Error processing image: {e}")
                
                if attempt < self.config["processing"]["max_retries"]:
                    time.sleep(self.config["processing"]["wait_between_retries"])
                    continue
                else:
                    return False
        
        self.logger.warning(f"Failed to get image response after {self.config['processing']['max_retries'] + 1} attempts")
        return False
    
    def process_directory(self):
        """Process all images in the input directory."""
        input_dir = Path(self.config["directories"]["input_dir"])
        supported_formats = self.config["processing"]["supported_formats"]
        
        # Find all image files
        image_files = []
        for format in supported_formats:
            image_files.extend(input_dir.glob(f"*{format}"))
            image_files.extend(input_dir.glob(f"*{format.upper()}"))
        
        if not image_files:
            self.logger.warning(f"No image files found in {input_dir}")
            return
        
        self.logger.info(f"Found {len(image_files)} image(s) to process")
        
        # Process each image
        success_count = 0
        for image_file in image_files:
            if self.process_single_image(image_file):
                success_count += 1
            
            # Small delay between images to avoid rate limits
            if len(image_files) > 1:
                time.sleep(1)
        
        self.logger.info(f"Processing complete: {success_count}/{len(image_files)} images processed successfully")


def main():
    """Main function to run the image processor."""
    print("=== OpenAI Image Processor ===")
    print("Starting image processing...")
    
    try:
        processor = OpenAIImageProcessor()
        processor.process_directory()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 