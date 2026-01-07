#!/usr/bin/env python3
"""
Build Nordic Toys Catalog JSON for image generation.
Extracts toys and key materials from toys.json, applies Art.md style prompts.
"""

import json
import os
from collections import Counter
from pathlib import Path

# Toys that already have card images (skip these)
EXISTING_TOY_IMAGES = {
    'ironwood_totems', 'sun_wheel_chaser', 'yule_wreath',
    'north_wind_whirler', 'aurora_callers', 'frost_voice_chime',
    'light_bringer_candle', 'nisse_offering_basket',
    'grand_lineage_chess_set', 'great_bear_sentry', 'anglers_set'
}

# Raw materials to always include
RAW_MATERIALS = {
    # Woods
    'log_oak': {'name': 'Oak Log', 'description': 'A freshly hewn oak log with rich honey-gold heartwood showing through the bark. Heavy and dense, with visible grain patterns running lengthwise.'},
    'log_ash': {'name': 'Ash Log', 'description': 'A pale ash log with smooth grey bark. The wood is elastic and strong, prized for items that must bend without breaking.'},
    'log_birch': {'name': 'Birch Log', 'description': 'A white birch log with distinctive papery bark marked with dark lenticels. The pale wood beneath is close-grained and workable.'},
    'log_pine': {'name': 'Pine Log', 'description': 'A fragrant pine log with reddish bark and visible resin beads. Knotty and aromatic, the wood releases the scent of the northern forest.'},
    'log_maple': {'name': 'Maple Log', 'description': 'A dense maple log with tight, swirling grain. The hardwood is prized for items requiring weight and durability.'},
    # Fibers
    'wool_fiber': {'name': 'Raw Wool', 'description': 'A bundle of raw sheep wool, creamy white with natural lanolin sheen. Soft and springy, ready for carding and spinning.'},
    'flax': {'name': 'Flax Bundle', 'description': 'Dried flax stalks tied in a bundle. The golden stems contain strong fibers that will become linen thread.'},
    'hide': {'name': 'Raw Hide', 'description': 'A stretched animal hide, pale and stiff. The surface shows the texture of the original skin, ready for tanning.'},
    'sinew': {'name': 'Dried Sinew', 'description': 'Bundles of dried animal sinew, pale and stringy. When wetted it becomes pliable; when dried it shrinks tight as iron.'},
    # Organics
    'bone': {'name': 'Bone Pieces', 'description': 'Clean white bone pieces, smooth and chalky. The dense material takes carving well and polishes to a warm ivory sheen.'},
    'antler': {'name': 'Antler', 'description': 'A shed deer antler with multiple tines. The surface is rough and textured, the core dense and workable.'},
    'tallow': {'name': 'Rendered Tallow', 'description': 'A block of rendered animal fat, creamy white and waxy. It melts smoothly and carries scents well.'},
    'pine_resin': {'name': 'Pine Resin', 'description': 'Amber lumps of hardened pine sap. Translucent and sticky when warmed, it smells of deep forest and seals wood against moisture.'},
    'birch_bark': {'name': 'Birch Bark Sheets', 'description': 'Peeled birch bark in thin, flexible sheets. The papery material is white with dark markings and naturally waterproof.'},
    # Chemicals
    'lye': {'name': 'Lye Crystals', 'description': 'Coarse white crystals of wood ash lye in a ceramic pot. Caustic and powerful, used for bleaching and soap-making.'},
    'milk': {'name': 'Fresh Milk', 'description': 'A wooden pail of fresh milk, creamy white with a thin layer of cream rising to the top.'},
    'birch_tar': {'name': 'Birch Tar', 'description': 'A pot of thick, dark birch tar. The viscous liquid gleams like black honey and smells of smoke and forest.'},
    # Plants/Berries
    'rowan_berry': {'name': 'Rowan Berries', 'description': 'Clusters of bright red rowan berries on their stems. The vivid color stands out like drops of blood against the snow.'},
    'juniper_berry': {'name': 'Juniper Berries', 'description': 'Small blue-black juniper berries with a dusty bloom. They smell sharp and clean, like mountain air.'},
    'lingonberry': {'name': 'Lingonberries', 'description': 'Tiny red lingonberries in a wooden bowl. Tart and bright, they gleam like scattered rubies.'},
    'pine_needles': {'name': 'Pine Needles', 'description': 'Fresh green pine needles bundled together. They release a sharp, resinous scent when crushed.'},
}

# Minimum usage count for intermediate materials to be included
# Set to 1 to include ALL materials
MIN_USAGE_COUNT = 1


def load_toys_json(path: str) -> dict:
    """Load the toys.json file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_missing_toys(toys: dict) -> list:
    """Get toys that don't have existing images."""
    missing = []
    for toy_id, toy in toys.items():
        if toy_id == 'toy_id':  # Skip template
            continue
        if toy_id not in EXISTING_TOY_IMAGES:
            missing.append(toy)
    return missing


def split_compound_output(output: str) -> list:
    """Split compound outputs like 'quark_curd + liquid_whey' into separate materials."""
    if ' + ' in output:
        return [mat.strip() for mat in output.split(' + ')]
    return [output]


def get_key_materials(toys: dict) -> tuple:
    """Extract frequently used intermediate materials from processing steps."""
    output_counts = Counter()
    material_notes = {}  # Store notes for each material

    for toy_id, toy in toys.items():
        if toy_id == 'toy_id':
            continue
        for step in toy.get('processing', []):
            output = step.get('output')
            if output:
                # Split compound outputs (e.g., "quark_curd + liquid_whey")
                individual_outputs = split_compound_output(output)
                for mat in individual_outputs:
                    output_counts[mat] += 1
                    # Store the note for context
                    if mat not in material_notes and step.get('note'):
                        material_notes[mat] = {
                            'station': step.get('station', ''),
                            'mode': step.get('mode', ''),
                            'input': step.get('input', ''),
                            'note': step.get('note', ''),
                            'original_output': output  # Track if it was part of compound
                        }

    # Filter to frequently used materials
    frequent = {mat: count for mat, count in output_counts.items() if count >= MIN_USAGE_COUNT}
    return frequent, material_notes


def build_toy_description(toy: dict) -> str:
    """Build a rich description from the toy's final_visual section."""
    final_visual = toy.get('final_visual', {})
    if not final_visual:
        return toy.get('flavor_text', toy.get('name', ''))

    # Combine all visual aspects
    parts = []
    for aspect, description in final_visual.items():
        parts.append(f"{aspect}: {description}")

    return ' '.join(parts)


def build_material_description(mat_id: str, mat_info: dict) -> str:
    """Build description for an intermediate material."""
    # Clean up the material ID for display
    name = mat_id.replace('_', ' ').title()

    note = mat_info.get('note', '')
    station = mat_info.get('station', '')
    mode = mat_info.get('mode', '')
    input_mat = mat_info.get('input', '')

    # Build contextual description
    desc_parts = [f"A crafted component: {name}."]

    if input_mat:
        desc_parts.append(f"Made from {input_mat}.")
    if note:
        # Extract the descriptive part of the note
        desc_parts.append(note)

    return ' '.join(desc_parts)


def build_catalog(toys_path: str, output_path: str):
    """Build the nordic toys catalog JSON."""
    data = load_toys_json(toys_path)
    toys = data.get('toys', {})

    # Get missing toys
    missing_toys = get_missing_toys(toys)
    print(f"Found {len(missing_toys)} toys to generate")

    # Get key materials
    frequent_materials, material_notes = get_key_materials(toys)
    print(f"Found {len(frequent_materials)} frequently used materials")
    print(f"Adding {len(RAW_MATERIALS)} raw materials")

    # Build catalog structure
    catalog = {
        "project": "Santas Nordic Workshop",
        "art_direction": {
            "style": "Scandinavian storybook illustration; watercolor and gouache on textured paper; fine ink linework; soft ambient light; muted natural colors; medium detail",
            "palette": "Pine greens, birch whites, oak browns, soot blacks, wool greys, stone neutrals, ice blues",
            "lighting": "Ambient first; warm hearth light or diffuse arctic daylight",
            "avoid": "photorealism, 3D render, neon colors, hyper-detail, extreme contrast, glossy plastic, modern materials"
        },
        "categories": {
            "toys": {
                "category_style": "Card format with rustic wooden title banner at top displaying the toy name, misty Nordic pine forest background, storybook illustration feel, the toy centered and prominent",
                "assets": []
            },
            "materials": {
                "category_style": "Icon inventory style on clean parchment-colored background, item centered, no title banner, suitable for game crafting UI, clear silhouette",
                "assets": []
            }
        }
    }

    # Add toys
    for toy in missing_toys:
        toy_asset = {
            "id": toy['id'],
            "name": toy['name'],
            "description": build_toy_description(toy),
            "size": "1024x1024",
            "tier": toy.get('tier', 1)
        }
        catalog["categories"]["toys"]["assets"].append(toy_asset)

    # Add raw materials
    for mat_id, mat_info in RAW_MATERIALS.items():
        mat_asset = {
            "id": mat_id,
            "name": mat_info['name'],
            "description": mat_info['description'],
            "size": "512x512",
            "material_type": "raw"
        }
        catalog["categories"]["materials"]["assets"].append(mat_asset)

    # Add frequently used intermediate materials
    for mat_id, count in sorted(frequent_materials.items(), key=lambda x: -x[1]):
        # Skip if it's already in raw materials
        if mat_id.lower().replace(' ', '_') in RAW_MATERIALS:
            continue

        mat_info = material_notes.get(mat_id, {})
        mat_asset = {
            "id": mat_id,
            "name": mat_id.replace('_', ' ').title(),
            "description": build_material_description(mat_id, mat_info),
            "size": "512x512",
            "material_type": "intermediate",
            "usage_count": count
        }
        catalog["categories"]["materials"]["assets"].append(mat_asset)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\nCatalog written to: {output_path}")
    print(f"  Toys: {len(catalog['categories']['toys']['assets'])}")
    print(f"  Materials: {len(catalog['categories']['materials']['assets'])}")
    print(f"  Total assets: {len(catalog['categories']['toys']['assets']) + len(catalog['categories']['materials']['assets'])}")


if __name__ == '__main__':
    script_dir = Path(__file__).parent.parent
    toys_path = script_dir / 'game_assets' / 'toys.json'
    output_path = script_dir / 'game_assets' / 'nordic_toys_catalog.json'

    build_catalog(str(toys_path), str(output_path))
