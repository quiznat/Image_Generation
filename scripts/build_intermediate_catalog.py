#!/usr/bin/env python3
"""
Build Intermediate Catalog JSON for image generation.
Extracts intermediate crafting objects from toys.json and maps them to their parent toys.
"""

import json
from pathlib import Path
from collections import defaultdict


def load_toys_json(path: str) -> dict:
    """Load the toys.json file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_intermediates(toys_data: dict) -> dict:
    """Extract all intermediates from toy processing steps."""
    toys = toys_data.get('toys', {})

    # Track intermediates: id -> details
    intermediates = {}
    # Track which toys use each intermediate
    usage = defaultdict(list)

    for toy_id, toy in toys.items():
        if toy_id == 'toy_id':  # Skip template
            continue

        toy_name = toy.get('name', toy_id)

        for step in toy.get('processing', []):
            output = step.get('output', '')
            if not output:
                continue

            # Track usage
            usage[output].append(toy_id)

            # Store intermediate details (first occurrence wins for description)
            if output not in intermediates:
                intermediates[output] = {
                    'id': output,
                    'name': output.replace('_', ' ').title(),
                    'description': step.get('note', ''),
                    'input': step.get('input', ''),
                    'station': step.get('station', ''),
                    'mode': step.get('mode', ''),
                    'used_by': [],
                    'shared': False
                }

    # Update usage info and shared status
    for int_id, toys_list in usage.items():
        if int_id in intermediates:
            intermediates[int_id]['used_by'] = sorted(set(toys_list))
            intermediates[int_id]['shared'] = len(set(toys_list)) > 1
            intermediates[int_id]['usage_count'] = len(toys_list)

    return intermediates


def build_toy_intermediates_map(toys_data: dict) -> dict:
    """Build a map of toy_id -> list of intermediates for that toy."""
    toys = toys_data.get('toys', {})
    toy_map = {}

    for toy_id, toy in toys.items():
        if toy_id == 'toy_id':
            continue

        intermediates = []
        for step in toy.get('processing', []):
            output = step.get('output', '')
            if output:
                intermediates.append(output)

        if intermediates:
            toy_map[toy_id] = {
                'name': toy.get('name', toy_id),
                'tier': toy.get('tier', 1),
                'era': toy.get('era', 1),
                'intermediates': intermediates
            }

    return toy_map


def build_catalog(toys_path: str, output_path: str):
    """Build the intermediate catalog JSON."""
    toys_data = load_toys_json(toys_path)

    intermediates = extract_intermediates(toys_data)
    toy_map = build_toy_intermediates_map(toys_data)

    # Separate shared vs toy-specific
    shared = {k: v for k, v in intermediates.items() if v['shared']}
    unique = {k: v for k, v in intermediates.items() if not v['shared']}

    print(f"Total toys: {len(toy_map)}")
    print(f"Total unique intermediates: {len(intermediates)}")
    print(f"  Shared (used by 2+ toys): {len(shared)}")
    print(f"  Toy-specific: {len(unique)}")

    # Build catalog structure
    catalog = {
        "project": "Santas Nordic Workshop Intermediates",
        "art_direction": {
            "style": "Scandinavian storybook illustration; watercolor + gouache on textured paper; fine ink linework; soft ambient light; muted natural colors; medium detail",
            "palette": "Pine greens, birch whites, oak browns, soot blacks, wool greys, ice blues",
            "size": "512x512",
            "note": "Each intermediate should match the style of its parent toy"
        },
        "summary": {
            "total_intermediates": len(intermediates),
            "shared_count": len(shared),
            "unique_count": len(unique),
            "total_toys": len(toy_map)
        },
        "intermediates": intermediates,
        "toy_intermediates": toy_map,
        "shared_intermediates": list(shared.keys()),
        "unique_intermediates": list(unique.keys())
    }

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\nCatalog written to: {output_path}")

    # Show some examples
    print("\nShared intermediates (sample):")
    for i, (int_id, details) in enumerate(list(shared.items())[:5]):
        print(f"  {int_id}: used by {len(details['used_by'])} toys")

    print("\nToy-specific intermediates (sample):")
    for i, (int_id, details) in enumerate(list(unique.items())[:5]):
        print(f"  {int_id}: {details['used_by'][0]}")

    print("\nToys with most intermediates:")
    sorted_toys = sorted(toy_map.items(), key=lambda x: len(x[1]['intermediates']), reverse=True)
    for toy_id, info in sorted_toys[:5]:
        print(f"  {toy_id}: {len(info['intermediates'])} intermediates")


if __name__ == '__main__':
    script_dir = Path(__file__).parent.parent
    toys_path = script_dir / 'game_assets' / 'toys.json'
    output_path = script_dir / 'game_assets' / 'intermediate_catalog.json'

    build_catalog(str(toys_path), str(output_path))
