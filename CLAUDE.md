# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered image generation system with multiple pipelines using OpenAI's DALL-E 3 and GPT-4o APIs. Supports batch processing with nested folder structures and configurable styling via JSON configuration files.

## Common Commands

### Running the Pipelines

```bash
# V1 Vision Pipeline - GPT-4o analysis → DALL-E 3 generation
python src/openai_image_generator.py
# Or with 2-worker parallel processing:
python src/openai_image_generator_pipelined.py

# V2 Enhanced Pipeline - GPT-4o analysis and generation (faster)
python src/openai_image_generator_v2_simple.py

# Loop Processor - Iterative AI evolution chains
python src/loop_processor.py
python src/loop_processor.py --config config/loop_processor_config.json

# Game Asset Generator - JSON-based batch game art generation
python src/game_asset_generator.py
python src/game_asset_generator.py --assets game_assets/my_game.json

# Animation Creator - Visualize evolution chains as GIFs
python scripts/create_evolution_animation.py
python scripts/create_evolution_animation.py --max-iterations 15
```

### Testing and Debugging

```bash
python scripts/verify_openai_setup.py      # Verify API connection
python scripts/debug_openai.py             # Debug connection issues
python scripts/test_vision_workflow.py     # Test V1 workflow
python scripts/test_prompt_config.py       # Test prompt configuration
python scripts/monitor_progress.py         # Monitor generation progress
python scripts/fix_loop_filenames.py       # Fix inconsistent loop filenames
```

### Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Requires `OPENAI_API_KEY` in `.env` file.

## Architecture

### Five Main Pipelines

1. **V1 Vision Pipeline** (`src/openai_image_generator.py`)
   - Flow: Input Image → GPT-4o Analysis → Wrap in Style Template → DALL-E 3 Generation
   - Uses `config/image_processing_config.json`
   - Two-stage prompting: vision analysis + DALL-E wrapper template
   - Pipelined version adds 2-worker parallel processing

2. **V2 Enhanced Pipeline** (`src/openai_image_generator_v2_simple.py`)
   - Flow: Image → GPT-4o Analysis & Generation (single API call)
   - Uses `config/image_processing_config-v2.json`
   - Uses `client.responses.create()` with `tools=[{"type": "image_generation"}]`
   - 2-worker parallel processing with offset pattern

3. **Loop Processor** (`src/loop_processor.py`)
   - Flow: Base folder → L1 → L2 → ... → LN (linear chain)
   - Uses `config/loop_processor_config.json`
   - Each iteration uses previous iteration's output as input
   - Creates numbered subdirectories for each iteration

4. **Game Asset Generator** (`src/game_asset_generator.py`)
   - Flow: JSON asset definitions → Art direction prompts → DALL-E 3 batch generation
   - Uses `config/game_assets_config.json`
   - Reads asset definitions from `game_assets/*.json`
   - Supports hierarchical art direction (global → project → category → asset)
   - Parallel processing with metadata output

5. **Animation Creator** (`scripts/create_evolution_animation.py`)
   - Creates animated GIFs from loop processor output
   - Supports crossfade and morph interpolation modes
   - Uses `config/animation_config.json`
   - Auto-detects iteration count and creates dynamic grid layouts

### Configuration Files

All pipelines are configured via JSON files in `config/`:
- `image_processing_config.json` - V1 Vision settings + prompts
- `image_processing_config-v2.json` - V2 Enhanced settings
- `loop_processor_config.json` - Loop iteration settings
- `game_assets_config.json` - Game asset generator settings + global art direction
- `animation_config.json` - Animation timing, interpolation, output versions

### Game Asset JSON Format

Define game assets in `game_assets/*.json`:
```json
{
    "project": "My Game",
    "art_direction": {
        "style": "2D cartoon, cel-shaded",
        "color_palette": "Warm and vibrant",
        "mood": "Friendly"
    },
    "categories": {
        "characters": {
            "category_style": "Expressive, simple designs",
            "assets": [
                {"id": "hero", "description": "...", "size": "1024x1024"}
            ]
        }
    }
}
```

### Directory Structure Conventions

- `test/` - Default input directory
- `test_output/` - Default output directory (preserves nested folder structure)
- `test_loop/` - Loop processor input/output (iterations in `1/`, `2/`, etc.)
- `game_assets/` - Game asset JSON definitions
- `game_output/` - Generated game assets (organized by project/category)
- `evolution_animations/` - Animation output
- `test_logs/` - Log files

### Key Patterns

- **Parallel Processing**: 2-worker pattern with odd/even distribution and 3-second startup offset
- **Proxy Handling**: Automatic fallback using `httpx.Client(trust_env=False)`
- **Image Encoding**: Base64 encoding for API calls
- **Output Naming**: `{original_name}_generated_{timestamp}.png` or `{original_name}_L{iteration}.png`
- **Art Direction Hierarchy**: Global config → Project JSON → Category → Individual asset
