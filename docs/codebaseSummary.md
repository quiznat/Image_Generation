# Codebase Summary

## File Map and Dependencies

### Core Image Generators
- **src/openai_image_generator.py**: Vision-enhanced DALL-E generator with GPT-4V analysis workflow (v1 PRODUCTION)
- **src/openai_image_generator_pipelined.py**: Parallel 2-worker vision-enhanced generator with optimal throughput (v1 PARALLEL PRODUCTION)
- **src/openai_image_generator_v2_simple.py**: GPT-4.1 enhanced image processor with 2-worker parallel processing using responses API (v2 PRODUCTION)
- **src/openai_image_generator_v2.py**: Direct DALL-E generation with rembg support (legacy)
- **src/openai_image_processor.py**: Legacy GPT-4 Vision analysis (broken - replaced by v1)
- **src/loop_processor.py**: Configurable loop processor using GPT-4.1 responses API with 2-worker pipeline for iterative AI evolution chains (LOOP PRODUCTION)

### Scripts
- **scripts/test_vision_workflow.py**: Test the corrected v1 vision workflow
- **scripts/verify_openai_setup.py**: Test OpenAI API configuration
- **scripts/debug_openai.py**: Debug OpenAI client initialization and proxy issues
- **scripts/monitor_progress.py**: Monitor image generation progress in real-time
- **scripts/test_prompt_config.py**: Validate DALL-E prompts from configuration
- **scripts/test_single_generation.py**: Test single image generation with prompt logging
- **scripts/verify_rembg_setup.py**: Test rembg background removal setup (legacy)
- **scripts/create_evolution_animation.py**: Create animated GIFs and grid montages from loop processor output. Supports unlimited iterations and multiple output configurations (e.g., for web, high-quality) via its config file.
- **scripts/fix_loop_filenames.py**: Fix inconsistent filename patterns in loop iteration directories

### Configuration
- **config/image_processing_config.json**: Configuration for v1 vision pipeline and pipelined version (currently set for crayon-style children's content)
- **config/image_processing_config-v2.json**: Configuration for v2 GPT-4.1 enhanced pipeline with image analysis and generation settings
- **config/loop_processor_config.json**: Configuration for loop processor with GPT-4.1 responses API settings, start/end loop settings, and vision analysis prompts
- **config/animation_config.json**: Configuration for animation creator, including interpolation, timing, and multiple output version definitions (e.g., 'Full Quality', 'Web Optimized').

### Batch Scripts
- **run_image_generator.bat**: Windows batch file for v1 vision pipeline (single-threaded)
- **run_image_generator_pipelined.bat**: Windows batch file for v1 parallel pipeline (2-worker parallel processing)
- **run_image_generator_v2.bat**: Windows batch file for v2 GPT-4.1 enhanced pipeline (2 workers)
- **run_loop_processor.bat**: Windows batch file for loop processor (LINEAR CHAIN - 2 workers with GPT-4.1)
- **create_evolution_animation.bat**: Windows batch file for evolution animation creator

### Documentation
- **README.md**: Comprehensive documentation (general-purpose, configurable system)
- **docs/currentTask.md**: Active work tracking
- **docs/completedWork.md**: Archived completed tasks
- **docs/projectRoadmap.md**: Strategic roadmap and priorities
- **docs/techStack.md**: Technology stack documentation
- **docs/Pillars.md**: Core principles and guidelines

### Dependencies Graph

```
openai_image_generator.py -> openai, PIL, dotenv, httpx
openai_image_generator_pipelined.py -> openai, PIL, dotenv, httpx, threading, queue
openai_image_generator_v2_simple.py -> openai, PIL, dotenv, httpx, threading, queue, base64
openai_image_generator_v2.py -> openai, PIL, dotenv, rembg
openai_image_processor.py -> openai, PIL, dotenv (legacy/broken)
loop_processor.py -> openai, PIL, dotenv, threading, queue, base64

test_vision_workflow.py -> openai_image_generator.py
verify_openai_setup.py -> openai, dotenv
debug_openai.py -> openai, dotenv, httpx
monitor_progress.py -> pathlib, datetime
test_prompt_config.py -> json, pathlib
test_single_generation.py -> openai_image_generator_v2_simple.py
create_evolution_animation.py -> PIL, pathlib, datetime, numpy, json
fix_loop_filenames.py -> pathlib, re

run_image_generator.bat -> openai_image_generator.py
run_image_generator_pipelined.bat -> openai_image_generator_pipelined.py
run_image_generator_v2.bat -> openai_image_generator_v2_simple.py
run_loop_processor.bat -> loop_processor.py
create_evolution_animation.bat -> create_evolution_animation.py

config/image_processing_config.json -> openai_image_generator.py
config/image_processing_config.json -> openai_image_generator_pipelined.py
config/image_processing_config-v2.json -> openai_image_generator_v2_simple.py
config/loop_processor_config.json -> loop_processor.py
config/animation_config.json -> create_evolution_animation.py
```

### Input/Output Flow

```
test/assets/[category]/ -> openai_image_generator.py -> test_output/assets/[category]/
test/assets/[category]/ -> openai_image_generator_pipelined.py -> test_output/assets/[category]/
test/assets/[category]/ -> openai_image_generator_v2_simple.py -> test_output/assets/[category]/
test_loop/ -> loop_processor.py -> test_loop/1/, test_loop/2/, ..., test_loop/N/
test_loop/ + test_loop/1/../N/ -> create_evolution_animation.py -> evolution_animations/[name]_evolution.gif, [name]_grid.png
```

### Production Pipelines

#### V1 Vision Workflow (Intelligent - Single-threaded)
```
Input Image → GPT-4V Analysis → Wrap in Style Template → DALL-E Generation → Output
Cost: Higher | Speed: Slower | Adaptability: Context-aware style application
```

#### V1 Parallel Workflow (Intelligent - Dual Worker Processing)
```
2 Workers: Each handling complete workflow
Worker-1: Images 1,3,5... → GPT-4V Analysis → DALL-E Generation → Output
Worker-2: Images 2,4,6... → GPT-4V Analysis → DALL-E Generation → Output  
Cost: Higher | Speed: Optimized for batches | Throughput: Balanced API utilization
```

#### V2 Enhanced Workflow (GPT-4.1 with 2-Worker Parallel Processing)
```
2 Workers: Each handling complete GPT-4.1 responses API workflow
Worker-1: Images 1,3,5... → GPT-4.1 Analysis & Generation → Enhanced Output
Worker-2: Images 2,4,6... → GPT-4.1 Analysis & Generation → Enhanced Output
Cost: Moderate | Speed: Fast parallel processing | Enhancement: Improved colors, clarity, composition
Technology: Uses client.responses.create with image generation tools
```

#### Loop Processing Workflow (Evolution Chain with GPT-4.1)
```
2 Workers: Linear chain iterations with GPT-4.1 responses API
Loop 1: test_loop/ → GPT-4.1 Vision Analysis → GPT-4.1 Image Generation → test_loop/1/
Loop 2: test_loop/1/ → GPT-4.1 Vision Analysis → GPT-4.1 Image Generation → test_loop/2/
Loop N: test_loop/(N-1)/ → GPT-4.1 Vision Analysis → GPT-4.1 Image Generation → test_loop/N/
Cost: Controlled (GPT-4.1 pricing) | Speed: 2-worker parallel | Technology: responses API with image generation tools
Purpose: AI evolution experiments (unlimited iterations)
```

#### Animation Creation Workflow (Visualization with Interpolation)
```
test_loop/ + test_loop/1/../N/ → Auto-detect iterations → Frame Interpolation → Create Smooth GIFs + Grids
Input: Original + unlimited iterations | Output: Smooth animated evolution chains
Features: Crossfade/Morph transitions, configurable steps, dual timing (hold/transition), multiple output configurations (e.g., full-size, web-optimized).
Cost: Free (local processing) | Speed: Fast | Quality: Seamless morphing between frames
```

### Key Relationships
- All production pipelines support nested folder structures
- All generators read from `.env` for API key
- All pipelines handle proxy issues with httpx fallback
- V1 provides intelligent context analysis with DALL-E, V2 and Loop provide GPT-4.1 enhancement and evolution
- V2 and Loop processor use GPT-4.1 responses API with built-in image generation tools
- Loop processor enables iterative AI evolution with cost control (unlimited iterations)
- Animation creator visualizes unlimited evolution chains with auto-sizing
- Style and format fully configurable via JSON configuration files
- V2 and Loop processors support 2-worker parallel processing for improved throughput
- Current V1 configuration optimized for children's crayon-style educational content