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
import shutil

# Load environment variables from .env file
load_dotenv()

class LoopImageProcessor:
    """Loop processor that runs the 2-worker pipeline with configurable start/end loops."""
    
    def __init__(self, config_path: str = "config/loop_processor_config.json"):
        """Initialize the loop processor."""
        self.config = self.load_config(config_path)
        self.client = self.initialize_openai_client()
        self.setup_logging()
        
        # Source directory (configurable now)
        self.source_dir = Path(self.config["loop_settings"]["source_directory"])
        
        # Loop settings
        self.start_loop = self.config["loop_settings"]["start_loop"]
        self.end_loop = self.config["loop_settings"]["end_loop"]
        self.pause_between_iterations = self.config["loop_settings"]["pause_between_iterations"]
        
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
                # Validate required sections
                if "loop_settings" not in config:
                    config["loop_settings"] = {
                        "start_loop": 1,
                        "end_loop": 10,
                        "pause_between_iterations": 5,
                        "source_directory": "./test_loop"
                    }
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
            "loop_settings": {
                "start_loop": 1,
                "end_loop": 10,
                "pause_between_iterations": 5,
                "source_directory": "./test_loop"
            },
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

    def setup_logging(self):
        """Setup logging configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"./test_logs/loop_processor_{timestamp}.log"
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("./test_logs")
        logs_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Loop processor initialized - Log: {log_file}")

    def encode_image_to_base64(self, image_path: Path) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self, image_path: Path) -> Optional[str]:
        """Analyze image using GPT-4 Vision."""
        try:
            # Encode image to base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # Make API call to GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.config["openai"]["model"],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.config["prompts"]["vision_analysis_prompt"]},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config["openai"]["max_tokens"],
                temperature=self.config["openai"]["temperature"]
            )
            
            description = response.choices[0].message.content.strip()
            self.logger.info(f"GPT-4V analysis successful for {image_path}")
            return description
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {e}")
            return None

    def wrap_description_for_dalle(self, chatgpt_description: str) -> str:
        """Wrap ChatGPT description in DALL-E prompt format."""
        dalle_prompt_template = "\n".join(self.config["prompts"]["dalle_wrapper_prompt"])
        dalle_prompt = dalle_prompt_template.replace("[CHATGPT_DESCRIPTION]", chatgpt_description)
        
        self.logger.info(f"DALL-E prompt created")
        return dalle_prompt

    def generate_image_with_dalle(self, dalle_prompt: str, output_path: Path) -> bool:
        """Generate image using DALL-E and save to output path."""
        attempts = 1
        
        while attempts <= self.config["processing"]["max_retries"] + 1:
            try:
                self.logger.info(f"DALL-E generation attempt {attempts}")
                
                # Generate image with DALL-E
                response = self.client.images.generate(
                    model=self.config["dalle"]["model"],
                    prompt=dalle_prompt,
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
            
            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
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

    def worker_complete_workflow(self, worker_id: int, work_queue: queue.Queue):
        """Worker thread that handles complete workflow: GPT-4V analysis → DALL-E generation."""
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
                
                image_path, relative_path, image_index, output_dir = image_item
                
                self.logger.info(f"🔍 [Worker-{worker_id}] Starting analysis for {relative_path} ({image_index})")
                
                # Step 1: GPT-4V Analysis
                description = self.analyze_image(image_path)
                
                if not description:
                    self.logger.error(f"❌ [Worker-{worker_id}] Analysis failed for {relative_path}")
                    self.results_queue.put((image_path, relative_path, image_index, False, "Analysis failed"))
                    work_queue.task_done()
                    continue
                
                self.logger.info(f"✅ [Worker-{worker_id}] Analysis complete for {relative_path}")
                
                # Step 2: Wrap description for DALL-E
                dalle_prompt = self.wrap_description_for_dalle(description)
                
                # Step 3: DALL-E Generation
                self.logger.info(f"🎨 [Worker-{worker_id}] Starting generation for {relative_path}")
                
                # Generate output path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{image_path.stem}_generated_{timestamp}.png"
                output_path = output_dir / output_filename
                
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
                self.logger.error(f"Worker-{worker_id} error: {e}")
                self.results_queue.put((image_path, relative_path, image_index, False, str(e)))
                work_queue.task_done()

    def process_iteration(self, iteration_num: int):
        """Process one iteration using the 2-worker pipeline."""
        print(f"\n🔄 Starting iteration {iteration_num}/{self.end_loop}")
        self.logger.info(f"Starting iteration {iteration_num}")
        
        # Create output directory for this iteration
        output_dir = self.source_dir / str(iteration_num)
        output_dir.mkdir(exist_ok=True)
        
        # Determine input directory for this iteration
        if iteration_num == 1:
            # Loop 1: Process base folder
            input_dir = self.source_dir
            print(f"📁 [Loop {iteration_num}] Processing BASE folder: {input_dir}")
        else:
            # Loop 2+: Process previous iteration's output
            input_dir = self.source_dir / str(iteration_num - 1)
            print(f"🔗 [Loop {iteration_num}] Processing folder {iteration_num - 1}: {input_dir}")
        
        # Clear queues from previous iteration
        while not self.worker1_queue.empty():
            self.worker1_queue.get()
        while not self.worker2_queue.empty():
            self.worker2_queue.get()
        while not self.results_queue.empty():
            self.results_queue.get()
        
        # Reset shutdown flag
        self.shutdown_requested.clear()
        
        # Find all image files in the input directory (not recursive for linear chain)
        supported_formats = self.config["processing"]["supported_formats"]
        image_files = []
        for format in supported_formats:
            # Use glob (not rglob) to only process files directly in input_dir
            image_files.extend(input_dir.glob(f"*{format}"))
            image_files.extend(input_dir.glob(f"*{format.upper()}"))
        
        # Remove duplicates
        image_files = list(set(image_files))
        
        if not image_files:
            self.logger.warning(f"No image files found in {input_dir}")
            print(f"❌ No images found in '{input_dir}'")
            return 0, 0
        
        print(f"🎯 [Iteration {iteration_num}] Processing {len(image_files)} images")
        print(f"    📂 Input:  {input_dir}")
        print(f"    📂 Output: {output_dir}")
        
        # Distribute images between workers (offset pattern)
        image_index = 0
        for image_file in sorted(image_files):
            image_index += 1
            relative_path = image_file.relative_to(input_dir)
            
            # Offset pattern: Worker-1 gets odd numbers, Worker-2 gets even numbers
            if image_index % 2 == 1:
                self.worker1_queue.put((image_file, relative_path, image_index, output_dir))
            else:
                self.worker2_queue.put((image_file, relative_path, image_index, output_dir))
        
        total_images = len(image_files)
        
        # Start parallel worker threads
        worker1_thread = threading.Thread(
            target=self.worker_complete_workflow, 
            args=(1, self.worker1_queue), 
            name=f"Worker1-Iter{iteration_num}"
        )
        worker2_thread = threading.Thread(
            target=self.worker_complete_workflow, 
            args=(2, self.worker2_queue), 
            name=f"Worker2-Iter{iteration_num}"
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
        print(f"✅ [Iteration {iteration_num}] Complete: {successful_generations}/{total_images} images in {elapsed_time:.1f}s")
        self.logger.info(f"Iteration {iteration_num} complete: {successful_generations}/{total_images} images")
        
        return successful_generations, total_images

    def run_loop(self):
        """Run the loop from start_loop to end_loop."""
        print("🚀 Starting loop processor with 2-worker pipeline")
        print(f"📁 Source: {self.source_dir}")
        print(f"🔄 Loop range: {self.start_loop} → {self.end_loop}")
        print(f"📂 Output pattern: {self.source_dir}/{self.start_loop}/, {self.source_dir}/{self.start_loop + 1}/, etc.")
        
        overall_start = time.time()
        total_successful = 0
        total_processed = 0
        
        try:
            for iteration in range(self.start_loop, self.end_loop + 1):
                successful, total = self.process_iteration(iteration)
                total_successful += successful
                total_processed += total
                
                # Small pause between iterations
                if iteration < self.end_loop:
                    print(f"⏸️  Pausing {self.pause_between_iterations} seconds before iteration {iteration + 1}...")
                    time.sleep(self.pause_between_iterations)
            
            overall_elapsed = time.time() - overall_start
            
            print(f"\n🎉 [LOOP COMPLETE]")
            print(f"📊 Total: {total_successful}/{total_processed} images across {self.end_loop - self.start_loop + 1} iterations")
            print(f"⏱️  Total time: {overall_elapsed/60:.1f} minutes")
            if total_processed > 0:
                print(f"🚀 Average: {overall_elapsed/total_processed:.1f} seconds/image")
            print(f"📁 Results in: {self.source_dir}/{self.start_loop}/ through {self.source_dir}/{self.end_loop}/")
            
            self.logger.info(f"Loop complete: {total_successful}/{total_processed} images in {overall_elapsed:.1f}s")
            
        except KeyboardInterrupt:
            print("\n🛑 Loop interrupted by user")
            self.logger.info("Loop interrupted by user")


def main():
    """Main function to run the loop processor."""
    try:
        processor = LoopImageProcessor()
        processor.run_loop()
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 