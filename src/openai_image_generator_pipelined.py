import os
import json
import base64
import time
import threading
import queue
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

class OpenAIImageGeneratorPipelined:
    """Pipelined image generator with parallel workers doing complete workflows."""
    
    def __init__(self, config_path: str = "config/image_processing_config.json"):
        """Initialize the pipelined image generator."""
        self.config = self.load_config(config_path)
        self.client = self.initialize_openai_client()
        self.setup_directories()
        self.setup_logging()
        
        # Parallel processing queues - each worker gets its own queue
        self.worker1_queue = queue.Queue()
        self.worker2_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Pipeline control
        self.workers_complete = threading.Event()
        self.shutdown_requested = threading.Event()
        
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
        """Initialize OpenAI client with proxy handling."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        try:
            # Try with default settings first
            client = OpenAI(api_key=api_key)
            return client
        except Exception as e:
            print(f"Initial client creation failed: {e}")
            try:
                # Fallback: disable proxy trust
                import httpx
                client = OpenAI(
                    api_key=api_key,
                    http_client=httpx.Client(trust_env=False)
                )
                print("✅ OpenAI client initialized with proxy bypass")
                return client
            except Exception as fallback_e:
                print(f"Fallback client creation failed: {fallback_e}")
                raise

    def setup_directories(self):
        """Create necessary directories."""
        output_dir = Path(self.config["directories"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        logs_dir = Path("./test_logs")
        logs_dir.mkdir(exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"./test_logs/parallel_generation_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Parallel image generator initialized - Log: {log_file}")

    def encode_image_to_base64(self, image_path: Path) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def worker_complete_workflow(self, worker_id: int, work_queue: queue.Queue):
        """Worker thread that handles complete workflow: GPT-4V analysis → DALL-E generation."""
        self.logger.info(f"🚀 Worker-{worker_id} started (NO RATE LIMITING)")
        
        while not self.shutdown_requested.is_set():
            try:
                # Get next image to process with timeout
                try:
                    image_item = work_queue.get(timeout=1.0)
                    if image_item is None:  # Poison pill
                        break
                except queue.Empty:
                    continue
                
                image_path, relative_path, image_index = image_item
                
                self.logger.info(f"🔍 [Worker-{worker_id}] Starting analysis for {relative_path} ({image_index})")
                
                # Step 1: GPT-4V Analysis (NO RATE LIMITING)
                description = self.analyze_image(image_path)
                
                if not description:
                    self.logger.error(f"❌ [Worker-{worker_id}] Analysis failed for {relative_path}")
                    self.results_queue.put((image_path, relative_path, image_index, False, "Analysis failed"))
                    work_queue.task_done()
                    continue
                
                self.logger.info(f"✅ [Worker-{worker_id}] Analysis complete for {relative_path}")
                
                # Step 2: Wrap description for DALL-E
                dalle_prompt = self.wrap_description_for_dalle(description)
                
                # Step 3: DALL-E Generation (NO RATE LIMITING)
                self.logger.info(f"🎨 [Worker-{worker_id}] Starting generation for {relative_path}")
                
                # Generate output path
                input_dir = Path(self.config["directories"]["input_dir"])
                output_dir = Path(self.config["directories"]["output_dir"])
                
                # Preserve the existing directory structure (including assets/)
                relative_dir = relative_path.parent
                output_subdir = output_dir / relative_dir
                output_subdir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{image_path.stem}_generated_{timestamp}.png"
                output_path = output_subdir / output_filename
                
                # Generate image
                success = self.generate_image_with_dalle(dalle_prompt, output_path)
                
                if success:
                    self.logger.info(f"✅ [Worker-{worker_id}] Complete workflow success: {output_path}")
                    self.results_queue.put((image_path, relative_path, image_index, True, str(output_path)))
                else:
                    self.logger.error(f"❌ [Worker-{worker_id}] Generation failed for {relative_path}")
                    self.results_queue.put((image_path, relative_path, image_index, False, "Generation failed"))
                
                work_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"❌ Worker-{worker_id} error: {e}")
                if 'image_item' in locals():
                    work_queue.task_done()
        
        self.logger.info(f"🏁 Worker-{worker_id} completed")

    def analyze_image(self, image_path: Path) -> Optional[str]:
        """Analyze the image and get a description for DALL-E generation."""
        try:
            # Encode image
            base64_image = self.encode_image_to_base64(image_path)
            
            # Prepare messages
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
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
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

    def save_image_from_url(self, image_url: str, output_path: Path) -> bool:
        """Download and save image from URL."""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify the image can be opened
            with Image.open(output_path) as img:
                img.verify()
            
            self.logger.info(f"Saved generated image to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            if output_path.exists():
                output_path.unlink()  # Clean up failed file
            return False

    def process_directory_pipelined(self):
        """Process all images using parallel workers with NO rate limiting."""
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
            print(f"\nNo images found in '{input_dir}' or its subdirectories")
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
        print(f"\n🚀 [PARALLEL WORKERS - NO LIMITS] Found {len(image_files)} image(s) in {len(files_by_dir)} directories")
        print("⚡ [WORKFLOW] Both workers: GPT-4V Analysis → DALL-E Generation")
        print("🔄 [PATTERN] Worker-1: Images 1,3,5... | Worker-2: Images 2,4,6...")
        print("🏁 [SPEED TEST] No artificial rate limiting - let's see how fast we can go!")
        print("⚠️  [WARNING] May hit OpenAI rate limits - that's what we want to measure\n")
        
        # Distribute images between workers (offset pattern)
        image_index = 0
        for dir_path, files in sorted(files_by_dir.items()):
            for image_file, relative_path in sorted(files):
                image_index += 1
                
                # Offset pattern: Worker-1 gets odd numbers, Worker-2 gets even numbers
                if image_index % 2 == 1:
                    self.worker1_queue.put((image_file, relative_path, image_index))
                else:
                    self.worker2_queue.put((image_file, relative_path, image_index))
        
        total_images = len(image_files)
        
        # Start parallel worker threads
        worker1_thread = threading.Thread(
            target=self.worker_complete_workflow, 
            args=(1, self.worker1_queue), 
            name="Worker1-Complete"
        )
        worker2_thread = threading.Thread(
            target=self.worker_complete_workflow, 
            args=(2, self.worker2_queue), 
            name="Worker2-Complete"
        )
        
        # Add small delay before starting Worker-2 to create offset
        worker1_thread.start()
        time.sleep(3)  # 3-second offset to stagger initial startup
        worker2_thread.start()
        
        # Monitor progress and track rate limiting hits
        start_time = time.time()
        completed_images = 0
        successful_generations = 0
        rate_limit_hits = 0
        
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
                        # Check if it was a rate limit issue
                        if "429" in str(message) or "rate limit" in str(message).lower():
                            rate_limit_hits += 1
                    
                    elapsed_time = time.time() - start_time
                    avg_time_per_image = elapsed_time / completed_images if completed_images > 0 else 0
                    estimated_remaining = (total_images - completed_images) * avg_time_per_image
                    
                    # Determine which worker handled this image
                    worker_id = "W1" if image_index % 2 == 1 else "W2"
                    
                    print(f"[{completed_images}/{total_images}] {status} {worker_id} {relative_path}")
                    print(f"    Success: {successful_generations}/{completed_images} | "
                          f"Rate limits: {rate_limit_hits} | "
                          f"Avg: {avg_time_per_image:.1f}s/img | "
                          f"Est. remaining: {estimated_remaining/60:.1f}min")
                    
                    self.results_queue.task_done()
                    
                except queue.Empty:
                    # Check if workers are still alive
                    if not worker1_thread.is_alive() and not worker2_thread.is_alive():
                        break
                    continue
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping parallel workers...")
            self.shutdown_requested.set()
        
        # Signal workers to stop
        self.worker1_queue.put(None)  # Poison pill for worker 1
        self.worker2_queue.put(None)  # Poison pill for worker 2
        
        # Wait for workers to complete
        worker1_thread.join(timeout=10)
        worker2_thread.join(timeout=10)
        
        elapsed_time = time.time() - start_time
        print(f"\n🎉 [PARALLEL PROCESSING COMPLETE]")
        print(f"📊 Generated: {successful_generations}/{total_images} images")
        print(f"⏱️  Total time: {elapsed_time/60:.1f} minutes")
        print(f"🚀 Average: {elapsed_time/total_images:.1f} seconds/image")
        print(f"🛑 Rate limit hits: {rate_limit_hits}")
        print(f"📈 Actual throughput: {successful_generations/(elapsed_time/60):.1f} images/minute")
        print(f"📁 Output: {self.config['directories']['output_dir']}")
        
        self.logger.info(f"Parallel processing complete: {successful_generations}/{total_images} images, {rate_limit_hits} rate limit hits")


def main():
    """Main function to run the pipelined image generator."""
    try:
        generator = OpenAIImageGeneratorPipelined()
        generator.process_directory_pipelined()
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 