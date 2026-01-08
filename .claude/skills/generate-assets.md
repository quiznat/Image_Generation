---
name: generate-assets
description: Generate game assets like toys, materials, stations using the image generation pipelines. Use when user wants to create new toy images, material images, or run the main asset generators.
---

# Generate Game Assets

Run the main image generation pipelines for toys, materials, and stations.

## Pipelines

### Game Asset Generator (recommended for batch)
```bash
# Generate from a catalog
python3 src/game_asset_generator.py --assets game_assets/nordic_toys_catalog.json

# Default catalog
python3 src/game_asset_generator.py
```

### Style Reference Generator (match existing style)
```bash
python3 src/style_reference_generator.py \
  --reference game_assets/ironwood_totems_card.png \
  --catalog game_assets/nordic_toys_catalog.json
```

### V2 Enhanced Pipeline (single images)
```bash
python3 src/openai_image_generator_v2_simple.py
```

## Available Catalogs

- `game_assets/nordic_toys_catalog.json` - Toy designs
- `game_assets/nordic_stations_catalog.json` - Station designs
- `game_assets/nordic_full_materials.json` - Material designs
- `game_assets/intermediate_catalog.json` - Intermediate components

## Build Catalogs (if needed)

```bash
python3 scripts/build_nordic_catalog.py        # Toys
python3 scripts/build_station_catalog.py       # Stations
python3 scripts/build_intermediate_catalog.py  # Intermediates
```

## Output Locations

- Toys: `game_output/Santas_Nordic_Workshop/toys/`
- Materials: `game_output/Santas_Nordic_Workshop/materials/`
- Stations: `game_output/Santas_Nordic_Workshop_Stations/`
- Intermediates: `game_output/Santas_Nordic_Workshop/intermediates/{toy_id}/`

## Verify Setup

```bash
python3 scripts/verify_openai_setup.py
```
