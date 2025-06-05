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
import argparse

# Load environment variables from .env file
load_dotenv()

class LoopImageProcessor:
    """Loop processor that runs the 2-worker pipeline with configurable start/end loops."""
    
    def __init__(self, config_path: str = "config/loop_processor_config.json"):
        """Initialize the loop processor."""
        try:
            self.config = self.load_config(config_path)
            self.setup_logging()
            self.client = self.initialize_openai_client()
            
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
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            # If config loading or key access fails, log the error and stop initialization.
            logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
            logging.critical(f"Failed to initialize LoopImageProcessor due to a configuration error: {e}")
            # Re-raise the exception to ensure the script terminates.
            raise
        
    def load_config(self, config_path: str) -> Dict:
        """
        Load configuration from JSON file.
        This method will raise an exception if the file is not found or is invalid.
        """
        logging.info(f"Attempting to load configuration from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info("✅ Configuration loaded successfully.")
        # Basic validation can be added here if needed, e.g., checking for essential keys
        return config
    
    def initialize_openai_client(self) -> OpenAI:
        """Initialize OpenAI client with proxy handling."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        try:
            # Try with default settings first
            client = OpenAI(api_key=api_key)
            self.logger.info("✅ OpenAI client initialized successfully.")
            return client
        except Exception as e:
            self.logger.warning(f"Initial client creation failed: {e}. Falling back to proxy bypass.")
            try:
                # Fallback: disable proxy trust
                import httpx
                client = OpenAI(
                    api_key=api_key,
                    http_client=httpx.Client(trust_env=False)
                )
                self.logger.info("✅ OpenAI client initialized with proxy bypass.")
                return client
            except Exception as fallback_e:
                self.logger.error(f"Fallback client creation failed: {fallback_e}")
                raise

    def setup_logging(self):
        """Setup logging configuration based on the config file."""
        log_dir = Path(self.config["logging"]["log_dir"])
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"loop_processor_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging configured. Log file at: {log_file}")

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

    def generate_image_with_gpt4_tool(self, description: str, output_path: Path) -> bool:
        """
        Generates an image using the GPT-4.1 Responses API.
        This follows the official documentation for direct image generation.
        """
        config = self.config.get("gpt_4_1_config")
        if not config:
            self.logger.error("Configuration for 'gpt_4_1_config' is missing.")
            return False

        # Use the template from the config to create the final prompt
        prompt = config["user_prompt_template"].replace("[DESCRIPTION]", description)
        self.logger.info(f"Generating image with prompt: '{prompt}'")

        try:
            response = self.client.responses.create(
                model=config["model"],
                input=prompt,
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
                    self.logger.info(f"Successfully generated and saved image: {output_path}")
                    return True
                else:
                    self.logger.error("Failed to save base64 image.")
            else:
                self.logger.warning("API response did not contain an image generation call result.")

        except AttributeError:
            self.logger.critical("FATAL: The 'client.responses.create' method does not exist. Your OpenAI library version may be out of date.")
            return False
        except Exception as e:
            self.logger.error(f"An exception occurred during image generation: {e}", exc_info=True)

        return False

    def save_image_from_base64(self, image_base64: str, output_path: Path) -> bool:
        """Decode and save a base64 string as an image file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            return True
        except Exception as e:
            self.logger.error(f"Error saving base64 encoded image to {output_path}: {e}")
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

    def worker_complete_workflow(self, worker_id: int, work_queue: queue.Queue, iteration_num: int):
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
                
                # Step 2: Generate image using the new GPT-4.1 tool method
                self.logger.info(f"🎨 [Worker-{worker_id}] Starting generation for {relative_path}")
                
                # Generate output path with SHORT filename
                # Extract original base name (remove all previous generation suffixes)
                base_name = image_path.stem
                # Remove any previous generation timestamps/suffixes
                if "_generated_" in base_name:
                    base_name = base_name.split("_generated_")[0]
                if "_L" in base_name and base_name.endswith(base_name.split("_L")[-1]):
                    # Remove previous loop indicators like "_L1", "_L2", etc.
                    base_name = "_L".join(base_name.split("_L")[:-1])
                
                # Create short, clean filename: original_name_L{loop_number}.png
                output_filename = f"{base_name}_L{iteration_num}.png"
                output_path = output_dir / output_filename
                
                # Generate image
                success = self.generate_image_with_gpt4_tool(description, output_path)
                
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
            args=(1, self.worker1_queue, iteration_num), 
            name=f"Worker1-Iter{iteration_num}"
        )
        worker2_thread = threading.Thread(
            target=self.worker_complete_workflow, 
            args=(2, self.worker2_queue, iteration_num), 
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
    parser = argparse.ArgumentParser(description="Run the Loop Image Processor.")
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/loop_processor_config.json',
        help='Path to the configuration file (e.g., config/loop_processor_config_gpt4.1.json)'
    )
    args = parser.parse_args()

    try:
        processor = LoopImageProcessor(config_path=args.config)
        processor.run_loop()
    except Exception as e:
        logging.error(f"❌ Script failed to complete due to an unhandled exception: {e}")


if __name__ == "__main__":
    main() 