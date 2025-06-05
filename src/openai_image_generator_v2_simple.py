import os
import json
import base64
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import requests
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OpenAIImageGeneratorV2Simple:
    """Generate new images using GPT-4.1 built-in image generation tool with 2-worker parallel processing."""
    
    def __init__(self, config_path: str = "config/image_processing_config-v2.json"):
        """Initialize the image generator with configuration."""
        self.config = self.load_config(config_path)
        self.client = self.initialize_openai_client()
        self.setup_directories()
        self.setup_logging()
        
        # Parallel processing queues - each worker gets its own queue
        self.worker1_queue = queue.Queue()
        self.worker2_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Pipeline control
        self.shutdown_requested = threading.Event()
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            # Return minimal default config for GPT-4.1 image generation
            return {
                "directories": {"input_dir": "./test", "output_dir": "./test_output"},
                "gpt_4_1_config": {
                    "model": "gpt-4.1-mini",
                    "analysis_and_generation_prompt": "Analyze this image and then create an improved, high-quality version with better colors, clarity, and composition."
                },
                "processing": {"supported_formats": [".png", ".jpg", ".jpeg"], "max_retries": 2, "wait_between_retries": 2},
                "logging": {"log_responses": False, "log_dir": "./test_logs"}
            }
    
    def initialize_openai_client(self) -> OpenAI:
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("OPENAI_API_KEY not found in .env file or not set properly.")
        
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
            # Set encoding for console output
            stream_handler.stream.reconfigure(encoding='utf-8')
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[file_handler, stream_handler]
            )
        else:
            # Set up basic logging with UTF-8 support
            handler = logging.StreamHandler()
            handler.stream.reconfigure(encoding='utf-8')
            logging.basicConfig(
                level=logging.INFO,
                handlers=[handler]
            )
        
        self.logger = logging.getLogger(__name__)

    def encode_image(self, image_path: Path) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def save_image_from_base64(self, image_base64: str, output_path: Path) -> bool:
        """Decode and save a base64 string as an image file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            self.logger.info(f"Saved generated image to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving base64 encoded image to {output_path}: {e}")
            return False
    
    def worker_process_image(self, worker_id: int, work_queue: queue.Queue):
        """Worker thread that processes images using GPT-4.1 image generation tool."""
        self.logger.info(f"🚀 Worker-{worker_id} started")
        
        while not self.shutdown_requested.is_set():
            try:
                # Get next image to process with timeout
                try:
                    image_item = work_queue.get(timeout=1.0)
                    if image_item is None:  # Poison pill
                        break
                except queue.Empty:
                    continue
                
                image_path, relative_path, image_index, output_subfolder = image_item
                
                self.logger.info(f"🔍 [Worker-{worker_id}] Processing {relative_path} ({image_index})")
                
                # Get configuration for GPT-4.1
                gpt_config = self.config.get("gpt_4_1_config")
                if not gpt_config:
                    self.logger.error("Configuration for 'gpt_4_1_config' is missing.")
                    self.results_queue.put((image_path, relative_path, image_index, False, "Config missing"))
                    work_queue.task_done()
                    continue
                
                # Encode the input image to base64
                try:
                    base64_image = self.encode_image(image_path)
                except Exception as e:
                    self.logger.error(f"Failed to encode image {image_path}: {e}")
                    self.results_queue.put((image_path, relative_path, image_index, False, "Encoding failed"))
                    work_queue.task_done()
                    continue
                
                # Determine the image format for the data URL
                image_format = image_path.suffix.lower().replace('.', '')
                if image_format == 'jpg':
                    image_format = 'jpeg'
                
                # Generate output filename
                output_filename = f"{image_path.stem}_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                output_path = output_subfolder / output_filename
                
                # Generate improved image using GPT-4.1 responses API with image generation tool
                attempts = 0
                max_retries = self.config["processing"]["max_retries"]
                success = False
                
                while attempts <= max_retries and not success:
                    try:
                        self.logger.info(f"✨ [Worker-{worker_id}] Generating improved image (attempt {attempts + 1})")
                        
                        # Call GPT-4.1 with the image and ask it to generate an improved version
                        response = self.client.responses.create(
                            model=gpt_config["model"],
                            input=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "input_text", 
                                            "text": gpt_config["analysis_and_generation_prompt"]
                                        },
                                        {
                                            "type": "input_image",
                                            "image_url": f"data:image/{image_format};base64,{base64_image}",
                                        },
                                    ],
                                }
                            ],
                            tools=[{"type": "image_generation"}]
                        )
                        
                        # Extract the base64 image data from the response output
                        image_data = [
                            output.result
                            for output in response.output
                            if output.type == "image_generation_call"
                        ]
                        
                        if image_data:
                            image_base64 = image_data[0]
                            if self.save_image_from_base64(image_base64, output_path):
                                self.logger.info(f"✅ [Worker-{worker_id}] Success: {output_path}")
                                self.results_queue.put((image_path, relative_path, image_index, True, str(output_path)))
                                success = True
                            else:
                                self.logger.error(f"❌ [Worker-{worker_id}] Failed to save base64 image.")
                        else:
                            self.logger.warning(f"⚠️ [Worker-{worker_id}] API response did not contain image generation result.")
                        
                    except AttributeError:
                        self.logger.critical("FATAL: The 'client.responses.create' method does not exist. Your OpenAI library version may be out of date.")
                        self.results_queue.put((image_path, relative_path, image_index, False, "API method missing"))
                        break
                    except Exception as e:
                        self.logger.error(f"❌ [Worker-{worker_id}] Error: {e}")
                    
                    attempts += 1
                    if attempts <= max_retries and not success:
                        self.logger.info(f"🔄 [Worker-{worker_id}] Retrying in {self.config['processing']['wait_between_retries']} seconds...")
                        time.sleep(self.config["processing"]["wait_between_retries"])
                
                if not success:
                    self.logger.warning(f"❌ [Worker-{worker_id}] Failed after {attempts} attempts")
                    self.results_queue.put((image_path, relative_path, image_index, False, "Generation failed"))
                
                work_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Worker-{worker_id} error: {e}")
                self.results_queue.put((image_path, relative_path, image_index, False, str(e)))
                work_queue.task_done()

    def process_directory(self):
        """Process all images in the input directory using 2-worker parallel processing."""
        input_dir = Path(self.config["directories"]["input_dir"])
        output_dir = Path(self.config["directories"]["output_dir"])
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
            print("\nThis tool analyzes your images and creates improved versions using GPT-4.1!")
            return
        
        print(f"\n📷 Found {len(image_files)} image(s)")
        print("🤖 Using GPT-4.1 with built-in image generation tool")
        print("⚡ Processing with 2-worker parallel pipeline")
        print("✨ Analyzing and improving each image...\n")
        
        # Clear queues
        while not self.worker1_queue.empty():
            self.worker1_queue.get()
        while not self.worker2_queue.empty():
            self.worker2_queue.get()
        while not self.results_queue.empty():
            self.results_queue.get()
        
        # Reset shutdown flag
        self.shutdown_requested.clear()
        
        # Distribute images between workers (offset pattern)
        image_index = 0
        for image_file in sorted(image_files):
            image_index += 1
            relative_path = image_file.relative_to(input_dir)
            
            # Determine output subfolder
            if relative_path.parent != Path("."):
                output_subfolder = output_dir / relative_path.parent
                output_subfolder.mkdir(parents=True, exist_ok=True)
            else:
                output_subfolder = output_dir
            
            # Offset pattern: Worker-1 gets odd numbers, Worker-2 gets even numbers
            if image_index % 2 == 1:
                self.worker1_queue.put((image_file, relative_path, image_index, output_subfolder))
            else:
                self.worker2_queue.put((image_file, relative_path, image_index, output_subfolder))
        
        total_images = len(image_files)
        
        # Start parallel worker threads
        worker1_thread = threading.Thread(
            target=self.worker_process_image, 
            args=(1, self.worker1_queue), 
            name="Worker1-V2"
        )
        worker2_thread = threading.Thread(
            target=self.worker_process_image, 
            args=(2, self.worker2_queue), 
            name="Worker2-V2"
        )
        
        # Start workers with offset
        worker1_thread.start()
        time.sleep(3)  # 3-second offset to stagger initial startup
        worker2_thread.start()
        
        # Monitor progress
        start_time = time.time()
        completed_images = 0
        successful_generations = 0
        
        try:
            while completed_images < total_images:
                try:
                    # Get result with timeout
                    result = self.results_queue.get(timeout=1.0)
                    image_path, relative_path, image_index, success, message = result
                    
                    completed_images += 1
                    if success:
                        successful_generations += 1
                        status = "✅"
                    else:
                        status = "❌"
                    
                    # Determine which worker handled this image
                    worker_id = "W1" if image_index % 2 == 1 else "W2"
                    
                    print(f"[{completed_images}/{total_images}] {status} {worker_id} {relative_path}")
                    
                    self.results_queue.task_done()
                    
                except queue.Empty:
                    # Check if workers are still alive
                    if not worker1_thread.is_alive() and not worker2_thread.is_alive():
                        break
                    continue
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping workers...")
            self.shutdown_requested.set()
        
        # Signal workers to stop
        self.worker1_queue.put(None)  # Poison pill for worker 1
        self.worker2_queue.put(None)  # Poison pill for worker 2
        
        # Wait for workers to complete
        worker1_thread.join(timeout=10)
        worker2_thread.join(timeout=10)
        
        elapsed_time = time.time() - start_time
        print(f"\n🎉 Complete: {successful_generations}/{total_images} images processed in {elapsed_time:.1f}s")
        if total_images > 0:
            print(f"⚡ Average: {elapsed_time/total_images:.1f} seconds/image")
        print(f"📁 Output: {self.config['directories']['output_dir']}")


def main():
    """Main function to run the image generator."""
    print("=== OpenAI Image Generator V2 (GPT-4.1 Enhanced) ===")
    print("Analyzes your images and creates improved versions")
    print("=" * 55)
    
    try:
        generator = OpenAIImageGeneratorV2Simple()
        generator.process_directory()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 