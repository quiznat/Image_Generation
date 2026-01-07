#!/usr/bin/env python3
"""
Build Station Catalog JSON for image generation.
Maps stations to lineages based on tech_pack and applies Art.md styling.
"""

import json
from pathlib import Path

# Lineage definitions from Art.md 2.4.6
LINEAGES = {
    'ljosalfar': {
        'name': 'Ljósálfar',
        'shape_law': 'Organic "whiplash" curves, no right angles, forms follow wood grain',
        'motifs': 'birch bark layering, resin-gold inlays, light/leaf filigree',
        'lighting': 'Cool daylight with warm sun accents; airy and overexposed',
        'palette': 'Birch whites, pine greens, honey golds',
        'materials': 'birch, pine, resin, berries, linen'
    },
    'nisse': {
        'name': 'Nisse',
        'shape_law': '"Fast-hald" square forms—stout proportions, straight boards, peg joinery, visible repairs',
        'motifs': 'knit patterns, patched leather, iron hooks, practical storage geometry',
        'lighting': 'Hearth-warm, cozy soot, soft bounce light',
        'palette': 'Oak browns, wool greys, cream whites, iron blacks',
        'materials': 'oak, wool, leather, iron, tallow'
    },
    'svartalfar': {
        'name': 'Svartálfar',
        'shape_law': '"Geometric Dark"—hard angles, riveted planes, block silhouettes, carved symbols',
        'motifs': 'soot bands, verdigris hints, tar-black leather, kiln-slit lighting',
        'lighting': 'Low-key warm ember sources with heavy shadow massing',
        'palette': 'Soot blacks, ember oranges, verdigris greens, iron greys',
        'materials': 'iron, steel, charcoal, tar, stone'
    },
    'marmennill': {
        'name': 'Marmennill',
        'shape_law': '"Pressure-Hardened"—smooth hydrodynamic forms, minimal protrusions, restrained spiral motifs',
        'motifs': 'translucent skins/isinglass, bone fasteners, wet stone, waterline reflections',
        'lighting': 'Cold diffuse light + faint underwater glow; always damp and quiet',
        'palette': 'Ice blues, bone whites, sea greys, deep greens',
        'materials': 'bone, isinglass, seal leather, whale ivory, driftwood'
    }
}

# Map tech_pack to lineage
TECH_PACK_LINEAGE = {
    'hearth': 'nisse',
    'wool': 'nisse',
    'flax': 'nisse',
    'framing': 'nisse',
    'subassembly': 'nisse',
    'pigment': 'nisse',  # Mixed, but default to Nisse
    'bog_iron': 'svartalfar',
    'glass': 'svartalfar',
    'clockwork': 'svartalfar',
    'distillation': 'svartalfar',
    'sea': 'marmennill'
}

# Store IDs map directly to their lineage
STORE_LINEAGE = {
    'ljosalfar': 'ljosalfar',
    'nisse': 'nisse',
    'svartalfar': 'svartalfar',
    'marmennill': 'marmennill'
}


def load_stations_json(path: str) -> dict:
    """Load the stations.json file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_lineage_for_station(station: dict) -> str:
    """Determine lineage for a station based on tech_pack or store ID."""
    station_id = station.get('id', '')

    # Check if it's a store
    if station.get('is_store', False):
        return STORE_LINEAGE.get(station_id, 'nisse')

    # Otherwise map by tech_pack
    tech_pack = station.get('tech_pack', 'hearth')
    return TECH_PACK_LINEAGE.get(tech_pack, 'nisse')


def build_station_description(station: dict, lineage_key: str) -> str:
    """Build a rich description for a station using Art.md template."""
    lineage = LINEAGES[lineage_key]

    name = station.get('name', station.get('id', 'Unknown'))
    norse_name = station.get('norse_name', '')
    function = station.get('function', '')
    norse_flavor = station.get('norse', '')
    summary = station.get('summary', '')

    # Build modes description
    modes = station.get('modes', [])
    modes_text = ', '.join(modes) if modes else ''

    # Compose the description
    parts = []

    # Subject line
    subject = f"A {lineage['name']} crafting station: {name}"
    if norse_name:
        subject += f" ({norse_name})"
    parts.append(subject)

    # Function
    if function:
        parts.append(f"Function: {function}")

    # Shape law
    parts.append(f"SHAPE LAW: {lineage['shape_law']}")

    # Materials and motifs
    parts.append(f"MATERIALS: {lineage['materials']}")
    parts.append(f"MOTIFS: {lineage['motifs']}")

    # Lighting
    parts.append(f"LIGHTING: {lineage['lighting']}")

    # Flavor text
    if norse_flavor:
        parts.append(f"Nordic flavor: {norse_flavor}")

    return ' | '.join(parts)


def build_catalog(stations_path: str, output_path: str):
    """Build the stations catalog JSON."""
    data = load_stations_json(stations_path)
    stations = data.get('stations', {})

    print(f"Found {len(stations)} stations")

    # Categorize stations by lineage
    categorized = {
        'nisse_stations': [],
        'svartalfar_stations': [],
        'ljosalfar_stations': [],
        'marmennill_stations': [],
        'stores': []
    }

    for station_id, station in stations.items():
        if station_id == '_meta':
            continue

        lineage_key = get_lineage_for_station(station)
        lineage = LINEAGES[lineage_key]

        asset = {
            'id': station_id,
            'name': station.get('name', station_id),
            'description': build_station_description(station, lineage_key),
            'size': '512x512',
            'lineage': lineage_key,
            'tech_pack': station.get('tech_pack', ''),
            'era': station.get('era', 1)
        }

        # Add norse_name if present
        if station.get('norse_name'):
            asset['norse_name'] = station['norse_name']

        # Categorize
        if station.get('is_store', False):
            categorized['stores'].append(asset)
        elif lineage_key == 'svartalfar':
            categorized['svartalfar_stations'].append(asset)
        elif lineage_key == 'ljosalfar':
            categorized['ljosalfar_stations'].append(asset)
        elif lineage_key == 'marmennill':
            categorized['marmennill_stations'].append(asset)
        else:
            categorized['nisse_stations'].append(asset)

    # Build catalog structure
    catalog = {
        "project": "Santas Nordic Workshop Stations",
        "art_direction": {
            "style": "Scandinavian storybook illustration; watercolor + gouache on textured paper; fine ink linework; soft ambient light; muted natural colors; medium detail",
            "palette": "Pine greens, birch whites, oak browns, soot blacks, wool greys, ice blues",
            "lighting": "Ambient first; lineage-specific lighting per category",
            "avoid": "photorealism, 3D render, neon colors, hyper-detail, extreme contrast, glossy plastic, modern materials"
        },
        "categories": {}
    }

    # Add Nisse stations
    if categorized['nisse_stations']:
        catalog["categories"]["nisse_stations"] = {
            "category_style": "Nisse lineage crafting station icon. Front-facing view, 512x512, clean silhouette. Fast-hald square forms, stout proportions, straight boards, peg joinery. Hearth-warm lighting with cozy soot tones. Knit patterns, patched leather, iron hooks.",
            "assets": categorized['nisse_stations']
        }

    # Add Svartálfar stations
    if categorized['svartalfar_stations']:
        catalog["categories"]["svartalfar_stations"] = {
            "category_style": "Svartálfar lineage crafting station icon. Front-facing view, 512x512, clean silhouette. Geometric Dark—hard angles, riveted planes, block silhouettes. Ember low-key lighting with heavy shadows. Soot bands, verdigris hints, tar-black leather.",
            "assets": categorized['svartalfar_stations']
        }

    # Add stores (each with individual lineage styling in description)
    if categorized['stores']:
        catalog["categories"]["stores"] = {
            "category_style": "Material store icon. Front-facing view, 512x512, clean silhouette. Each store uses its own lineage visual style (see individual descriptions). Magical/ethereal feel as stores are run by mythical creatures.",
            "assets": categorized['stores']
        }

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\nCatalog written to: {output_path}")
    for cat_name, assets in categorized.items():
        if assets:
            print(f"  {cat_name}: {len(assets)}")

    total = sum(len(assets) for assets in categorized.values())
    print(f"  Total: {total}")


if __name__ == '__main__':
    script_dir = Path(__file__).parent.parent
    stations_path = script_dir / 'game_assets' / 'stations.json'
    output_path = script_dir / 'game_assets' / 'nordic_stations_catalog.json'

    build_catalog(str(stations_path), str(output_path))
