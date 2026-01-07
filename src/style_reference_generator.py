"""
Style Reference Generator
=========================

Generates new images using a reference image for style consistency.
Uses GPT-4o vision to analyze the reference and generate new content
in the exact same visual style.

Usage:
    python src/style_reference_generator.py --reference game_assets/ironwood_totems_card.png --catalog game_assets/nordic_toys_catalog.json
"""

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
import argparse

load_dotenv()


class StyleReferenceGenerator:
    """Generate images using a reference image for style consistency."""

    def __init__(self, reference_image: str, model: str = "gpt-4o"):
        """Initialize with a reference image for style matching."""
        self.reference_image = Path(reference_image)
        self.model = model
        self.client = self.initialize_openai_client()
        self.setup_logging()

        # Load and encode reference image
        self.reference_base64 = self.encode_image(self.reference_image)

        # Parallel processing
        self.work_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.shutdown_requested = threading.Event()

    def initialize_openai_client(self) -> OpenAI:
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        try:
            return OpenAI(api_key=api_key)
        except TypeError as e:
            if "proxies" in str(e):
                import httpx
                return OpenAI(api_key=api_key, http_client=httpx.Client(trust_env=False))
            raise

    def setup_logging(self):
        """Setup logging."""
        log_dir = Path("./generation_logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"style_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def encode_image(self, image_path: Path) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def generate_with_style_reference(self, asset: Dict, category_style: str, output_dir: Path) -> bool:
        """Generate a new image matching the reference style."""
        asset_id = asset.get("id", "unnamed")
        asset_name = asset.get("name", asset_id)
        description = asset.get("description", "")

        self.logger.info(f"Generating: {asset_name}")

        # Build the prompt with strong style matching instructions
        prompt = f"""Look at this reference image carefully. This is the EXACT visual style I need you to match.

REFERENCE STYLE ANALYSIS:
- This is a Scandinavian storybook card illustration
- Watercolor/gouache texture on paper
- Muted natural color palette
- Fine ink linework
- Rustic wooden title banner at top
- Misty Nordic pine forest background
- Soft ambient lighting

NOW CREATE A NEW IMAGE:
Subject: {asset_name}
Details: {description}

CRITICAL REQUIREMENTS:
1. Match the EXACT same illustration style as the reference
2. Same watercolor/gouache texture and paper feel
3. Same muted color palette (pine greens, birch whites, oak browns, wool greys)
4. Same wooden title banner style at top with the name "{asset_name}"
5. Same misty Nordic forest background
6. Same soft, ambient lighting
7. Same level of detail and artistic treatment

Category presentation: {category_style}

DO NOT deviate from the reference style. The new image must look like it belongs in the same card set."""

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = f"{asset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = output_dir / output_filename

        try:
            # Use GPT-4o with image generation tool
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{self.reference_base64}"
                            },
                            {
                                "type": "input_text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                tools=[{"type": "image_generation"}]
            )

            # Extract base64 image from response (same pattern as v2_simple)
            image_data = [
                output.result
                for output in response.output
                if output.type == "image_generation_call"
            ]

            if image_data:
                image_base64 = image_data[0]
                output_dir.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_base64))
                self.logger.info(f"Saved: {output_path}")

                # Save metadata
                metadata = {
                    "asset": asset,
                    "reference_image": str(self.reference_image),
                    "model": self.model,
                    "generated_at": datetime.now().isoformat()
                }
                with open(output_path.with_suffix('.json'), 'w') as f:
                    json.dump(metadata, f, indent=2)

                return True

            self.logger.warning(f"No image generated for {asset_id}")
            return False

        except Exception as e:
            self.logger.error(f"Error generating {asset_id}: {e}")
            return False

    def worker(self, worker_id: int):
        """Worker thread for parallel generation."""
        self.logger.info(f"Worker-{worker_id} started")

        while not self.shutdown_requested.is_set():
            try:
                item = self.work_queue.get(timeout=1.0)
                if item is None:
                    break

                asset, category, category_style, output_dir, index, total = item
                success = self.generate_with_style_reference(asset, category_style, output_dir / category)
                self.results_queue.put((asset.get("id", "unknown"), success, index, total))
                self.work_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker-{worker_id} error: {e}")
                self.work_queue.task_done()

    def process_catalog(self, catalog_path: str, output_dir: str, category_filter: str = None):
        """Process a catalog JSON file."""
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        project_name = catalog.get("project", "output").replace(" ", "_")
        categories = catalog.get("categories", {})

        output_base = Path(output_dir) / project_name

        print(f"\n{'='*60}")
        print(f"Style Reference Generator")
        print(f"{'='*60}")
        print(f"Reference: {self.reference_image}")
        print(f"Model: {self.model}")
        print(f"Project: {project_name}")

        # Count and queue assets
        total_assets = 0
        for cat_name, cat_data in categories.items():
            if category_filter and cat_name != category_filter:
                continue
            assets = cat_data.get("assets", [])
            total_assets += len(assets)
            category_style = cat_data.get("category_style", "")

            for asset in assets:
                self.work_queue.put((asset, cat_name, category_style, output_base,
                                    self.work_queue.qsize() + 1, total_assets))

        print(f"Total assets: {total_assets}")
        print(f"{'='*60}\n")

        # Start workers (using 1 worker for now to avoid rate limits)
        num_workers = 1
        workers = []
        for i in range(num_workers):
            t = threading.Thread(target=self.worker, args=(i + 1,))
            t.start()
            workers.append(t)

        # Monitor progress
        completed = 0
        successful = 0

        try:
            while completed < total_assets:
                try:
                    asset_id, success, index, total = self.results_queue.get(timeout=120.0)
                    completed += 1
                    if success:
                        successful += 1
                        print(f"[{completed}/{total}] ✅ {asset_id}")
                    else:
                        print(f"[{completed}/{total}] ❌ {asset_id}")
                except queue.Empty:
                    if all(not t.is_alive() for t in workers):
                        break
                    continue
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            self.shutdown_requested.set()

        # Cleanup
        for _ in workers:
            self.work_queue.put(None)
        for t in workers:
            t.join(timeout=5)

        print(f"\n{'='*60}")
        print(f"Complete: {successful}/{total_assets} generated")
        print(f"Output: {output_base}")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Generate images with style reference')
    parser.add_argument('--reference', type=str, required=True,
                        help='Reference image for style matching')
    parser.add_argument('--catalog', type=str, required=True,
                        help='Catalog JSON file with assets to generate')
    parser.add_argument('--output', type=str, default='./game_output',
                        help='Output directory')
    parser.add_argument('--model', type=str, default='gpt-4o',
                        help='Model to use (default: gpt-4o)')
    parser.add_argument('--category', type=str, default=None,
                        help='Only process specific category (toys or materials)')
    args = parser.parse_args()

    generator = StyleReferenceGenerator(
        reference_image=args.reference,
        model=args.model
    )

    generator.process_catalog(
        catalog_path=args.catalog,
        output_dir=args.output,
        category_filter=args.category
    )


if __name__ == "__main__":
    main()
