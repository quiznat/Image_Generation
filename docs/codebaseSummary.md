# Codebase Summary

## File Map and Dependencies

### Core Image Generators
- **src/openai_image_generator.py**: Original DALL-E generator with full pipeline
- **src/openai_image_generator_v2.py**: Direct DALL-E generation with rembg support
- **src/openai_image_generator_v2_simple.py**: Simplified DALL-E without background removal (RECOMMENDED)
- **src/openai_image_processor.py**: GPT-4 Vision analysis + DALL-E generation (v1)

### Scripts
- **scripts/verify_openai_setup.py**: Test OpenAI API configuration
- **scripts/verify_rembg_setup.py**: Test rembg background removal setup
- **scripts/debug_openai.py**: Debug OpenAI client initialization and proxy issues
- **scripts/monitor_progress.py**: Monitor image generation progress in real-time
- **scripts/test_prompt_config.py**: Validate DALL-E prompts from configuration
- **scripts/test_single_generation.py**: Test single image generation with prompt logging

### Configuration
- **config/image_processing_config.json**: Configuration for v1 pipeline
- **config/image_processing_config-v2.json**: Configuration for v2 pipeline (current)

### Batch Scripts
- **run_image_generator.bat**: Windows batch file for v1 pipeline
- **run_image_generator_v2.bat**: Windows batch file for v2 simple pipeline

### Documentation
- **README.md**: Comprehensive documentation (OpenAI-focused)

### Dependencies Graph

```
openai_image_generator.py -> openai, PIL, dotenv
openai_image_generator_v2.py -> openai, PIL, dotenv, rembg
openai_image_generator_v2_simple.py -> openai, PIL, dotenv, httpx
openai_image_processor.py -> openai, PIL, dotenv

verify_openai_setup.py -> openai, dotenv
verify_rembg_setup.py -> rembg, PIL
debug_openai.py -> openai, dotenv, httpx
monitor_progress.py -> pathlib, datetime
test_prompt_config.py -> json, pathlib
test_single_generation.py -> openai_image_generator_v2_simple.py, pathlib, shutil

run_image_generator.bat -> openai_image_processor.py
run_image_generator_v2.bat -> openai_image_generator_v2_simple.py

config/image_processing_config.json -> openai_image_processor.py
config/image_processing_config-v2.json -> openai_image_generator_v2_simple.py
```

### Input/Output Flow

```
test/ -> openai_image_generator_v2_simple.py -> test_output/
```

### Test Infrastructure
- **scripts/verify_openai_setup.py**: Verification script for OpenAI API setup
- **scripts/verify_rembg_setup.py**: Verification script for background removal setup
- **scripts/debug_openai.py**: Debug script for connection issues
- **scripts/monitor_progress.py**: Real-time progress monitoring

### Key Relationships
- All OpenAI generators read from `.env` for API key
- V2 simple is the recommended pipeline (most stable)
- Batch scripts provide easy Windows execution
- Config files control generation parameters 