# Codebase Summary

## File Map and Dependencies

### Core Image Generators
- **src/openai_image_generator.py**: Vision-enhanced DALL-E generator with GPT-4V analysis workflow (v1 PRODUCTION)
- **src/openai_image_generator_pipelined.py**: Parallel 3-worker vision-enhanced generator with optimal throughput (v1 PARALLEL PRODUCTION)
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
- **config/image_processing_config.json**: Configuration for v1 vision pipeline and pipelined version (currently set for crayon-style children's content)
- **config/image_processing_config-v2.json**: Configuration for v2 simple pipeline (currently set for crayon-style children's content)

### Batch Scripts
- **run_image_generator.bat**: Windows batch file for v1 vision pipeline (single-threaded)
- **run_image_generator_pipelined.bat**: Windows batch file for v1 parallel pipeline (TRIPLE THREAT - 3 workers)
- **run_image_generator_v2.bat**: Windows batch file for v2 simple pipeline

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
run_image_generator_pipelined.bat -> openai_image_generator_pipelined.py
run_image_generator_v2.bat -> openai_image_generator_v2_simple.py

config/image_processing_config.json -> openai_image_generator.py
config/image_processing_config.json -> openai_image_generator_pipelined.py
config/image_processing_config-v2.json -> openai_image_generator_v2_simple.py
```

### Input/Output Flow

```
test/assets/[category]/ -> openai_image_generator.py -> test_output/assets/[category]/
test/assets/[category]/ -> openai_image_generator_pipelined.py -> test_output/assets/[category]/
test/assets/[category]/ -> openai_image_generator_v2_simple.py -> test_output/assets/[category]/
```

### Production Pipelines

#### V1 Vision Workflow (Intelligent - Single-threaded)
```
Input Image → GPT-4V Analysis → Wrap in Style Template → DALL-E Generation → Output
Cost: Higher | Speed: Slower | Adaptability: Context-aware style application
```

#### V1 Parallel Workflow (Intelligent - TRIPLE THREAT)
```
3 Workers: Each handling complete workflow
Worker-1: Images 1,4,7... → GPT-4V Analysis → DALL-E Generation → Output
Worker-2: Images 2,5,8... → GPT-4V Analysis → DALL-E Generation → Output  
Worker-3: Images 3,6,9... → GPT-4V Analysis → DALL-E Generation → Output
Cost: Higher | Speed: Optimized for batches | Throughput: Maximum API utilization
```

#### V2 Simple Workflow (Fast)
```
Filename → Apply Style Template → DALL-E Generation → Output
Cost: Lower | Speed: Faster | Consistency: Direct style application
```

### Key Relationships
- Both production pipelines support nested folder structures
- All generators read from `.env` for API key
- Both pipelines handle proxy issues with httpx fallback
- V1 provides intelligent context analysis, V2 provides speed and consistency
- Style and format fully configurable via JSON configuration files
- Test scripts validate specific functionality
- Current configuration optimized for children's crayon-style educational content 