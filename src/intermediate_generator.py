#!/usr/bin/env python3
"""
Intermediate Crafting Object Generator
=======================================

Generates images for intermediate crafting objects using the finished toy
as a style reference. Each intermediate matches its parent toy's visual style.

Usage:
    # Single toy
    python src/intermediate_generator.py --toy ironwood_totems --reference game_output/.../ironwood_totems.png

    # Batch mode with manifest
    python src/intermediate_generator.py --all --manifest game_assets/toy_references.json

    # List intermediates only (dry run)
    python src/intermediate_generator.py --toy ironwood_totems --list-only
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
import logging
from dotenv import load_dotenv
import argparse

load_dotenv()


class IntermediateGenerator:
    """Generate intermediate crafting object images using toy reference."""

    def __init__(self, model: str = "gpt-4o"):
        """Initialize generator."""
        self.model = model
        self.client = self.initialize_openai_client()
        self.setup_logging()
        self.catalog = self.load_catalog()

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
        log_file = log_dir / f"intermediate_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def load_catalog(self) -> dict:
        """Load the intermediate catalog."""
        catalog_path = Path("game_assets/intermediate_catalog.json")
        if not catalog_path.exists():
            raise FileNotFoundError(
                f"Intermediate catalog not found. Run: python scripts/build_intermediate_catalog.py"
            )
        with open(catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def encode_image(self, image_path: Path) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_toy_intermediates(self, toy_id: str) -> List[str]:
        """Get list of intermediates for a toy."""
        toy_data = self.catalog.get("toy_intermediates", {}).get(toy_id)
        if not toy_data:
            return []
        return toy_data.get("intermediates", [])

    def get_intermediate_details(self, int_id: str) -> dict:
        """Get details for an intermediate."""
        return self.catalog.get("intermediates", {}).get(int_id, {})

    def is_shared(self, int_id: str) -> bool:
        """Check if an intermediate is shared across multiple toys."""
        return int_id in self.catalog.get("shared_intermediates", [])

    def check_exists(self, int_id: str, toy_id: str, output_base: Path) -> bool:
        """Check if an intermediate already exists in the toy's folder."""
        toy_dir = output_base / toy_id
        return any(toy_dir.glob(f"{int_id}_*.png"))

    def generate_intermediate(
        self,
        int_id: str,
        toy_id: str,
        toy_name: str,
        reference_image: Path,
        output_base: Path
    ) -> bool:
        """Generate a single intermediate image."""
        details = self.get_intermediate_details(int_id)
        if not details:
            self.logger.warning(f"No details found for intermediate: {int_id}")
            return False

        int_name = details.get("name", int_id.replace("_", " ").title())
        description = details.get("description", "")
        input_materials = details.get("input", "")
        station = details.get("station", "")
        mode = details.get("mode", "")

        self.logger.info(f"Generating: {int_name}")

        # All intermediates go into the toy's folder for organization
        output_dir = output_base / toy_id

        output_dir.mkdir(parents=True, exist_ok=True)

        # Build the prompt
        prompt = f"""Look at this reference image carefully. This is the finished toy "{toy_name}".
Generate a crafting component in the EXACT same visual style.

COMPONENT: {int_name}
DESCRIPTION: {description}
MADE FROM: {input_materials}
CRAFTED AT: {station} ({mode} mode)

This component is used to make the toy shown in the reference image.

CRITICAL REQUIREMENTS:
1. Match the EXACT same illustration style as the reference toy
2. Same watercolor/gouache texture and paper feel
3. Same muted color palette (pine greens, birch whites, oak browns, wool greys)
4. Same artistic treatment and level of detail
5. The component should look like it belongs with the finished toy
6. Clean composition, 512x512, single component on simple background
7. Show the component as a crafted object, not the raw materials

DO NOT add title banners or text. Just the component itself in the matching style."""

        # Encode reference image
        reference_base64 = self.encode_image(reference_image)

        output_filename = f"{int_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = output_dir / output_filename

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{reference_base64}"
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

            # Extract image from response
            image_data = [
                output.result
                for output in response.output
                if output.type == "image_generation_call"
            ]

            if image_data:
                image_base64 = image_data[0]
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_base64))
                self.logger.info(f"Saved: {output_path}")

                # Save metadata
                metadata = {
                    "intermediate": {
                        "id": int_id,
                        "name": int_name,
                        "description": description,
                        "input": input_materials,
                        "station": station,
                        "mode": mode,
                        "shared": self.is_shared(int_id)
                    },
                    "parent_toy": {
                        "id": toy_id,
                        "name": toy_name
                    },
                    "reference_image": str(reference_image),
                    "model": self.model,
                    "generated_at": datetime.now().isoformat()
                }
                with open(output_path.with_suffix('.json'), 'w') as f:
                    json.dump(metadata, f, indent=2)

                return True

            self.logger.warning(f"No image generated for {int_id}")
            return False

        except Exception as e:
            self.logger.error(f"Error generating {int_id}: {e}")
            return False

    def process_toy(
        self,
        toy_id: str,
        reference_image: str,
        output_dir: str = "./game_output",
        force_regenerate: bool = False,
        skip_shared: bool = False
    ) -> dict:
        """Process all intermediates for a single toy."""
        reference_path = Path(reference_image)
        if not reference_path.exists():
            raise FileNotFoundError(f"Reference image not found: {reference_image}")

        toy_data = self.catalog.get("toy_intermediates", {}).get(toy_id)
        if not toy_data:
            raise ValueError(f"Toy not found in catalog: {toy_id}")

        toy_name = toy_data.get("name", toy_id)
        intermediates = toy_data.get("intermediates", [])

        output_base = Path(output_dir) / "Santas_Nordic_Workshop" / "intermediates"

        print(f"\n{'='*60}")
        print(f"Intermediate Generator")
        print(f"{'='*60}")
        print(f"Toy: {toy_name} ({toy_id})")
        print(f"Reference: {reference_image}")
        print(f"Intermediates: {len(intermediates)}")
        print(f"{'='*60}\n")

        results = {"generated": 0, "skipped": 0, "failed": 0, "details": []}

        for i, int_id in enumerate(intermediates, 1):
            is_shared = self.is_shared(int_id)
            exists = self.check_exists(int_id, toy_id, output_base)

            # Skip logic
            if skip_shared and is_shared:
                print(f"[{i}/{len(intermediates)}] ⏭️  {int_id} (shared, skipping)")
                results["skipped"] += 1
                results["details"].append({"id": int_id, "status": "skipped_shared"})
                continue

            if exists and not force_regenerate:
                print(f"[{i}/{len(intermediates)}] ⏭️  {int_id} (exists)")
                results["skipped"] += 1
                results["details"].append({"id": int_id, "status": "exists"})
                continue

            # Generate
            success = self.generate_intermediate(
                int_id=int_id,
                toy_id=toy_id,
                toy_name=toy_name,
                reference_image=reference_path,
                output_base=output_base
            )

            if success:
                print(f"[{i}/{len(intermediates)}] ✅ {int_id}")
                results["generated"] += 1
                results["details"].append({"id": int_id, "status": "generated"})
            else:
                print(f"[{i}/{len(intermediates)}] ❌ {int_id}")
                results["failed"] += 1
                results["details"].append({"id": int_id, "status": "failed"})

        print(f"\n{'='*60}")
        print(f"Complete: {results['generated']} generated, {results['skipped']} skipped, {results['failed']} failed")
        print(f"Output: {output_base}")
        print(f"{'='*60}")

        return results

    def process_all(
        self,
        manifest_path: str,
        output_dir: str = "./game_output",
        force_regenerate: bool = False,
        skip_shared: bool = False
    ) -> dict:
        """Process all toys from a manifest file."""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        references = manifest.get("references", {})
        if not references:
            raise ValueError("No references found in manifest")

        print(f"\n{'='*60}")
        print(f"Batch Intermediate Generator")
        print(f"{'='*60}")
        print(f"Toys in manifest: {len(references)}")
        print(f"{'='*60}\n")

        all_results = {}
        for toy_id, reference_image in references.items():
            try:
                results = self.process_toy(
                    toy_id=toy_id,
                    reference_image=reference_image,
                    output_dir=output_dir,
                    force_regenerate=force_regenerate,
                    skip_shared=skip_shared
                )
                all_results[toy_id] = results
            except Exception as e:
                self.logger.error(f"Error processing {toy_id}: {e}")
                all_results[toy_id] = {"error": str(e)}

        return all_results

    def list_intermediates(self, toy_id: str = None):
        """List intermediates (for a specific toy or all)."""
        if toy_id:
            toy_data = self.catalog.get("toy_intermediates", {}).get(toy_id)
            if not toy_data:
                print(f"Toy not found: {toy_id}")
                return

            print(f"\n{toy_data['name']} ({toy_id})")
            print(f"Tier: {toy_data.get('tier', '?')}, Era: {toy_data.get('era', '?')}")
            print(f"\nIntermediates ({len(toy_data['intermediates'])}):")
            for int_id in toy_data['intermediates']:
                details = self.get_intermediate_details(int_id)
                shared = "🔗" if self.is_shared(int_id) else "  "
                print(f"  {shared} {int_id}: {details.get('description', '')[:60]}...")
        else:
            print(f"\nAll Intermediates ({self.catalog['summary']['total_intermediates']})")
            print(f"  Shared: {self.catalog['summary']['shared_count']}")
            print(f"  Unique: {self.catalog['summary']['unique_count']}")

            print("\nShared intermediates (🔗):")
            for int_id in self.catalog.get("shared_intermediates", [])[:10]:
                details = self.get_intermediate_details(int_id)
                print(f"  {int_id}: used by {len(details.get('used_by', []))} toys")

            print("\nToys with most intermediates:")
            toy_ints = self.catalog.get("toy_intermediates", {})
            sorted_toys = sorted(toy_ints.items(),
                               key=lambda x: len(x[1].get('intermediates', [])),
                               reverse=True)
            for toy_id, data in sorted_toys[:10]:
                print(f"  {toy_id}: {len(data['intermediates'])} intermediates")


def main():
    parser = argparse.ArgumentParser(description='Generate intermediate crafting object images')
    parser.add_argument('--toy', type=str, help='Toy ID to process')
    parser.add_argument('--reference', type=str, help='Reference image (finished toy) path')
    parser.add_argument('--all', action='store_true', help='Process all toys from manifest')
    parser.add_argument('--manifest', type=str, help='Manifest JSON with toy->reference mappings')
    parser.add_argument('--output', type=str, default='./game_output', help='Output directory')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use')
    parser.add_argument('--force-regenerate', action='store_true', help='Regenerate even if exists')
    parser.add_argument('--skip-shared', action='store_true', help='Skip shared intermediates')
    parser.add_argument('--list-only', action='store_true', help='List intermediates without generating')

    args = parser.parse_args()

    generator = IntermediateGenerator(model=args.model)

    if args.list_only:
        generator.list_intermediates(args.toy)
        return

    if args.all:
        if not args.manifest:
            print("Error: --manifest required when using --all")
            return
        generator.process_all(
            manifest_path=args.manifest,
            output_dir=args.output,
            force_regenerate=args.force_regenerate,
            skip_shared=args.skip_shared
        )
    elif args.toy:
        if not args.reference:
            print("Error: --reference required when using --toy")
            return
        generator.process_toy(
            toy_id=args.toy,
            reference_image=args.reference,
            output_dir=args.output,
            force_regenerate=args.force_regenerate,
            skip_shared=args.skip_shared
        )
    else:
        print("Usage:")
        print("  Single toy:  python src/intermediate_generator.py --toy TOYID --reference PATH")
        print("  All toys:    python src/intermediate_generator.py --all --manifest PATH")
        print("  List only:   python src/intermediate_generator.py --list-only [--toy TOYID]")


if __name__ == "__main__":
    main()
