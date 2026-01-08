---
name: list-toys
description: List available toys, show toy information, intermediate counts, or what toys need generation. Use when user asks what toys exist, which toys have intermediates, or toy details.
---

# List Toys and Intermediates

Show available toys and their intermediate crafting component counts.

## Commands

### List all intermediates summary
```bash
python3 src/intermediate_generator.py --list-only
```

### List intermediates for a specific toy
```bash
python3 src/intermediate_generator.py --list-only --toy {toy_id}
```

### List all toy IDs in manifest
```bash
python3 -c "import json; d=json.load(open('game_assets/toy_references.json')); print('\n'.join(sorted(d['references'].keys())))"
```

### Show toys with most intermediates
```bash
python3 src/intermediate_generator.py --list-only 2>&1 | grep -A20 "Toys with most"
```

## Toy Reference Locations

**28 toys in game_output:**
```bash
ls game_output/Santas_Nordic_Workshop/toys/*.png | sed 's/.*\///' | sed 's/_20.*//' | sort -u
```

**11 additional toys in game_assets (card images):**
- anglers_set
- aurora_callers
- frost_voice_chime
- grand_lineage_chess_set
- great_bear_sentry
- ironwood_totems
- light_bringer_candle
- nisse_offering_basket
- north_wind_whirler
- sun_wheel_chaser
- yule_wreath

## Top 10 Toys by Intermediate Count

1. polar_express - 20 intermediates
2. riding_horse - 15 intermediates
3. anglers_set - 14 intermediates
4. great_north_sleigh - 12 intermediates
5. jormungandr_drift - 12 intermediates
6. nisse_boundary_levitator - 11 intermediates
7. borealis_birds - 9 intermediates
8. frost_wyrm - 9 intermediates
9. treasure_chest - 9 intermediates
10. solstice_storm_drum - 8 intermediates

## Intermediate Types

- **144 total** unique intermediate types
- **29 shared** (used by 2+ toys, e.g., resin_seal, wool_spool)
- **115 unique** (toy-specific 1-of-1s)
