"""
Game Asset Generator
====================

Generates game art assets from JSON definition files with art direction support.
Reads asset definitions from JSON files and systematically creates all game art
using OpenAI's DALL-E 3 with configurable style and art direction.

Usage:
    python src/game_asset_generator.py
    python src/game_asset_generator.py --assets game_assets/my_game.json
    python src/game_asset_generator.py --config config/game_assets_config.json
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


class GameAssetGenerator:
    """Generate game assets from JSON definitions with art direction support."""

    def __init__(self, config_path: str = "config/game_assets_config.json"):
        """Initialize the game asset generator."""
        self.config = self.load_config(config_path)
        self.client = self.initialize_openai_client()
        self.setup_directories()
        self.setup_logging()

        # Parallel processing queues
        self.work_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.shutdown_requested = threading.Event()

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "directories": {"assets_json_dir": "./game_assets", "output_dir": "./game_output"},
            "openai": {"vision_model": "gpt-4o", "generation_model": "gpt-4o-mini", "max_tokens": 4096, "temperature": 0.7},
            "dalle": {"model": "dall-e-3", "size": "1024x1024", "quality": "hd", "n": 1},
            "art_direction": {"global_style": "2D game art", "global_requirements": []},
            "processing": {"max_retries": 2, "wait_between_retries": 2, "parallel_workers": 2},
            "logging": {"log_responses": True, "log_dir": "./game_logs"}
        }

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

    def setup_directories(self):
        """Create necessary directories."""
        Path(self.config["directories"]["output_dir"]).mkdir(parents=True, exist_ok=True)
        Path(self.config["directories"]["assets_json_dir"]).mkdir(parents=True, exist_ok=True)
        if self.config.get("logging", {}).get("log_responses", False):
            Path(self.config["logging"]["log_dir"]).mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get("logging", {})
        if log_config.get("log_responses", False):
            log_dir = Path(log_config["log_dir"])
            log_file = log_dir / f"game_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
            )
        else:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_assets_json(self, json_path: Path) -> Optional[Dict]:
        """Load asset definitions from a JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading assets JSON {json_path}: {e}")
            return None

    def build_prompt(self, asset: Dict, category_style: str, project_art_direction: Dict) -> str:
        """Build a complete prompt with art direction for an asset.

        Supports Art.md template structure with fields:
        - style: Overall art style description
        - palette/color_palette: Color palette guidance
        - lighting: Lighting direction
        - mood: Emotional tone
        - avoid: Things to avoid (negative prompt elements)
        """
        # Global style from config
        global_style = self.config["art_direction"]["global_style"]
        global_requirements = self.config["art_direction"]["global_requirements"]

        # Project-level art direction (support both old and new field names)
        project_style = project_art_direction.get("style", "")
        project_palette = project_art_direction.get("palette", project_art_direction.get("color_palette", ""))
        project_lighting = project_art_direction.get("lighting", "")
        project_mood = project_art_direction.get("mood", "")
        project_avoid = project_art_direction.get("avoid", "")

        # Build the prompt
        prompt_parts = []

        # Style first (sets the overall tone)
        if project_style:
            prompt_parts.append(f"STYLE: {project_style}")

        # Category-specific presentation
        if category_style:
            prompt_parts.append(f"PRESENTATION: {category_style}")

        # Asset description (the subject - most important content)
        prompt_parts.append(f"SUBJECT: {asset['description']}")

        # Color/Palette direction
        if project_palette:
            prompt_parts.append(f"PALETTE: {project_palette}")

        # Lighting
        if project_lighting:
            prompt_parts.append(f"LIGHTING: {project_lighting}")

        # Mood
        if project_mood:
            prompt_parts.append(f"MOOD: {project_mood}")

        # Global requirements
        if global_requirements:
            prompt_parts.append("REQUIREMENTS: " + "; ".join(global_requirements))

        # Negative prompt / things to avoid
        if project_avoid:
            prompt_parts.append(f"AVOID: {project_avoid}")

        # Global style fallback
        if global_style and not project_style:
            prompt_parts.append(f"OVERALL STYLE: {global_style}")

        return "\n".join(prompt_parts)

    def generate_asset(self, asset: Dict, category: str, category_style: str,
                       project_art_direction: Dict, output_dir: Path) -> bool:
        """Generate a single asset using DALL-E."""
        asset_id = asset.get("id", asset.get("name", "unnamed"))
        self.logger.info(f"Generating asset: {asset_id}")

        # Build the complete prompt
        prompt = self.build_prompt(asset, category_style, project_art_direction)
        self.logger.info(f"Prompt for {asset_id}:\n{prompt}")

        # Create output subdirectory for category
        category_dir = output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        output_filename = f"{asset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = category_dir / output_filename

        # Determine size (use DALL-E supported sizes)
        dalle_size = self.config["dalle"]["size"]

        # Generate with DALL-E
        attempts = 0
        max_retries = self.config["processing"]["max_retries"]

        while attempts <= max_retries:
            try:
                self.logger.info(f"Attempt {attempts + 1} for {asset_id}")

                response = self.client.images.generate(
                    model=self.config["dalle"]["model"],
                    prompt=prompt[:4000],  # DALL-E prompt limit
                    size=dalle_size,
                    quality=self.config["dalle"]["quality"],
                    n=1
                )

                if response.data and len(response.data) > 0:
                    image_url = response.data[0].url
                    if self.save_image_from_url(image_url, output_path):
                        self.logger.info(f"Successfully generated: {output_path}")

                        # Save metadata
                        metadata = {
                            "asset": asset,
                            "prompt": prompt,
                            "generated_at": datetime.now().isoformat(),
                            "output_path": str(output_path)
                        }
                        metadata_path = output_path.with_suffix('.json')
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2)

                        return True

                attempts += 1
                if attempts <= max_retries:
                    time.sleep(self.config["processing"]["wait_between_retries"])

            except Exception as e:
                self.logger.error(f"Error generating {asset_id}: {e}")
                attempts += 1
                if attempts <= max_retries:
                    time.sleep(self.config["processing"]["wait_between_retries"])

        self.logger.warning(f"Failed to generate {asset_id} after {attempts} attempts")
        return False

    def save_image_from_url(self, image_url: str, output_path: Path) -> bool:
        """Download and save image from URL."""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            return False

    def worker_generate(self, worker_id: int):
        """Worker thread for parallel generation."""
        self.logger.info(f"Worker-{worker_id} started")

        while not self.shutdown_requested.is_set():
            try:
                item = self.work_queue.get(timeout=1.0)
                if item is None:  # Poison pill
                    break

                asset, category, category_style, project_art_direction, output_dir, index, total = item

                success = self.generate_asset(asset, category, category_style,
                                             project_art_direction, output_dir)

                self.results_queue.put((asset.get("id", "unknown"), success, index, total))
                self.work_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker-{worker_id} error: {e}")
                self.work_queue.task_done()

    def process_assets_file(self, assets_path: Path):
        """Process a single assets JSON file."""
        self.logger.info(f"Processing assets file: {assets_path}")

        assets_data = self.load_assets_json(assets_path)
        if not assets_data:
            return

        project_name = assets_data.get("project", assets_path.stem)
        project_art_direction = assets_data.get("art_direction", {})
        categories = assets_data.get("categories", {})

        print(f"\n🎮 Project: {project_name}")
        print(f"🎨 Art Direction: {project_art_direction.get('style', 'Default')}")

        # Create project output directory
        output_dir = Path(self.config["directories"]["output_dir"]) / project_name.replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Count total assets
        total_assets = sum(len(cat.get("assets", [])) for cat in categories.values())
        print(f"📦 Total assets to generate: {total_assets}")

        # Queue all assets
        asset_index = 0
        for category_name, category_data in categories.items():
            category_style = category_data.get("category_style", "")
            assets = category_data.get("assets", [])

            print(f"\n📁 Category: {category_name} ({len(assets)} assets)")

            for asset in assets:
                asset_index += 1
                self.work_queue.put((
                    asset, category_name, category_style,
                    project_art_direction, output_dir, asset_index, total_assets
                ))

        # Start worker threads
        num_workers = self.config["processing"].get("parallel_workers", 2)
        workers = []
        for i in range(num_workers):
            t = threading.Thread(target=self.worker_generate, args=(i + 1,), name=f"Worker-{i+1}")
            t.start()
            workers.append(t)
            if i < num_workers - 1:
                time.sleep(2)  # Stagger startup

        # Monitor progress
        completed = 0
        successful = 0

        try:
            while completed < total_assets:
                try:
                    asset_id, success, index, total = self.results_queue.get(timeout=1.0)
                    completed += 1
                    if success:
                        successful += 1
                        status = "✅"
                    else:
                        status = "❌"
                    print(f"[{completed}/{total}] {status} {asset_id}")
                    self.results_queue.task_done()
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

        print(f"\n🎉 Complete: {successful}/{total_assets} assets generated")
        print(f"📁 Output: {output_dir}")

    def process_all_assets(self):
        """Process all JSON files in the assets directory."""
        assets_dir = Path(self.config["directories"]["assets_json_dir"])
        json_files = list(assets_dir.glob("*.json"))

        if not json_files:
            print(f"\n❌ No JSON files found in {assets_dir}")
            print("Create asset definition files in this directory.")
            print("See game_assets/example_assets.json for the format.")
            return

        print(f"\n🎮 Game Asset Generator")
        print(f"📁 Found {len(json_files)} asset definition file(s)")

        for json_file in json_files:
            self.process_assets_file(json_file)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate game assets from JSON definitions')
    parser.add_argument('--config', type=str, default='config/game_assets_config.json',
                        help='Configuration file path')
    parser.add_argument('--assets', type=str, default=None,
                        help='Specific assets JSON file to process')
    args = parser.parse_args()

    print("=== Game Asset Generator ===")
    print("Generate game art from JSON definitions with art direction")
    print("=" * 50)

    try:
        generator = GameAssetGenerator(config_path=args.config)

        if args.assets:
            generator.process_assets_file(Path(args.assets))
        else:
            generator.process_all_assets()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
