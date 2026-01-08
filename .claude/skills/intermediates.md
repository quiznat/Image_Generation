---
name: intermediates
description: Generate intermediate crafting objects for a specific toy. Use when user wants to generate intermediates, crafting components, or sub-components for a toy like borealis_birds, polar_express, etc.
---

# Generate Intermediates for a Toy

Generate intermediate crafting components that match a finished toy's visual style exactly.

## Usage

User will specify:
- **toy name** (e.g., "borealis_birds", "polar_express", "sun_wheel_chaser")
- **how many runs** (default: 1, can request 2-3 for variants)
- **skip shared** (default: yes - only generate unique 1-of-1 intermediates)

## Steps

1. **Find the reference image** for the toy:
   - Check `game_output/Santas_Nordic_Workshop/toys/{toy_id}_*.png`
   - Or check `game_assets/{toy_id}_card.png` for the 11 additional toys
   - Use the most recent image if multiple exist

2. **List intermediates** (optional, for user info):
   ```bash
   python3 src/intermediate_generator.py --list-only --toy {toy_id}
   ```

3. **Run generation** (in background for multiple runs):
   ```bash
   # Single run, unique intermediates only
   python3 src/intermediate_generator.py \
     --toy {toy_id} \
     --reference {path_to_reference} \
     --skip-shared \
     --force-regenerate
   ```

4. **For multiple runs**, launch in parallel:
   - Run the same command multiple times with `run_in_background: true`
   - Report the background task IDs to the user

## Reference Image Locations

- 28 toys in `game_output/Santas_Nordic_Workshop/toys/`
- 11 card images in `game_assets/`:
  - anglers_set, aurora_callers, frost_voice_chime, grand_lineage_chess_set
  - great_bear_sentry, ironwood_totems, light_bringer_candle, nisse_offering_basket
  - north_wind_whirler, sun_wheel_chaser, yule_wreath

## Key Flags

- `--skip-shared` - Only unique 1-of-1 intermediates (recommended)
- `--force-regenerate` - Overwrite existing files
- `--list-only` - Dry run, show what would be generated

## Output

Images saved to: `game_output/Santas_Nordic_Workshop/intermediates/{toy_id}/`
