# Codebase Summary

## File Map and Dependencies

### Core Image Generators
- **src/openai_image_generator.py**: Vision-enhanced DALL-E generator with GPT-4V analysis workflow (v1 PRODUCTION)
- **src/openai_image_generator_v2_simple.py**: Direct filename-to-DALL-E generation without background removal (v2 PRODUCTION)
- **src/openai_image_generator_v2.py**: Direct DALL-E generation with rembg support (legacy)
- **src/openai_image_processor.py**: Legacy GPT-4 Vision analysis (broken - replaced by v1)

### Scripts
- **scripts/test_vision_workflow.py**: Test the corrected v1 vision workflow
- **scripts/verify_openai_setup.py**: Test OpenAI API configuration
- **scripts/debug_openai.py**: Debug OpenAI client initialization and proxy issues
- **scripts/monitor_progress.py**: Monitor image generation progress in real-time
- **scripts/test_prompt_config.py**: Validate DALL-E prompts from configuration
- **scripts/test_single_generation.py**: Test single image generation with prompt logging
- **scripts/verify_rembg_setup.py**: Test rembg background removal setup (legacy)

### Configuration
- **config/image_processing_config.json**: Configuration for v1 vision pipeline
- **config/image_processing_config-v2.json**: Configuration for v2 simple pipeline

### Batch Scripts
- **run_image_generator.bat**: Windows batch file for v1 vision pipeline
- **run_image_generator_v2.bat**: Windows batch file for v2 simple pipeline

### Documentation
- **README.md**: Comprehensive documentation (OpenAI-focused)
- **docs/currentTask.md**: Active work tracking
- **docs/completedWork.md**: Archived completed tasks
- **docs/projectRoadmap.md**: Strategic roadmap and priorities
- **docs/techStack.md**: Technology stack documentation
- **docs/Pillars.md**: Core principles and guidelines

### Dependencies Graph

```
openai_image_generator.py -> openai, PIL, dotenv, httpx
openai_image_generator_v2_simple.py -> openai, PIL, dotenv, httpx
openai_image_generator_v2.py -> openai, PIL, dotenv, rembg
openai_image_processor.py -> openai, PIL, dotenv (legacy/broken)

test_vision_workflow.py -> openai_image_generator.py
verify_openai_setup.py -> openai, dotenv
debug_openai.py -> openai, dotenv, httpx
monitor_progress.py -> pathlib, datetime
test_prompt_config.py -> json, pathlib
test_single_generation.py -> openai_image_generator_v2_simple.py

run_image_generator.bat -> openai_image_generator.py
run_image_generator_v2.bat -> openai_image_generator_v2_simple.py

config/image_processing_config.json -> openai_image_generator.py
config/image_processing_config-v2.json -> openai_image_generator_v2_simple.py
```

### Input/Output Flow

```
test/assets/[category]/ -> openai_image_generator.py -> test_output/assets/[category]/
test/assets/[category]/ -> openai_image_generator_v2_simple.py -> test_output/assets/[category]/
```

### Production Pipelines

#### V1 Vision Workflow (Intelligent)
```
Input Image → GPT-4V Analysis → Wrap Description → DALL-E Generation → Output
Cost: Higher | Speed: Slower | Quality: Context-aware
```

#### V2 Simple Workflow (Fast)
```
Filename → DALL-E Generation → Output
Cost: Lower | Speed: Faster | Quality: Consistent
```

### Key Relationships
- Both production pipelines support nested folder structures
- All generators read from `.env` for API key
- Both pipelines handle proxy issues with httpx fallback
- V1 provides intelligent analysis, V2 provides speed and efficiency
- Background removal handled manually via Canva
- Test scripts validate specific functionality 