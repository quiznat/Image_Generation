# Image Generation System

A comprehensive, configurable OpenAI image generation system featuring multiple AI-powered pipelines with customizable styles and workflows. Supports both **DALL-E 3** and **GPT-4.1 responses API** with built-in image generation tools.

## 🎨 Overview

This project offers **three production-ready, configurable pipelines** for AI-powered image generation:
- **Style**: Fully customizable via configuration files
- **Format**: Configurable output specifications  
- **Purpose**: Adaptable to any image generation use case
- **Output**: High-quality images in specified dimensions
- **Architecture**: Nested folder support for organized batch processing

**Current Configuration**: Set up for children's crayon-style educational content, but easily adaptable for sci-fi art, photorealistic images, abstract art, or any other style.

## 🚀 Four Main Capabilities

This system provides **four distinct capabilities** for AI-powered image generation and analysis:

1. **🔍 V1 Vision Pipeline** - Intelligent context-aware generation with DALL-E 3
2. **⚡ V2 Enhanced Pipeline** - Fast image enhancement with GPT-4.1  
3. **🔄 Loop Processor** - AI evolution experiments with GPT-4.1
4. **🎬 Animation Creator** - Visualize evolution chains

## 🚀 Three Production Pipelines

### 🔍 V1: Vision-Enhanced Pipeline (Intelligent)
**Best for**: Complex objects, style-aware generation, context-sensitive workflows
```bash
# Windows - Single-threaded
run_image_generator.bat

# Windows - 2-worker parallel processing
run_image_generator_pipelined.bat

# Direct Python
python src/openai_image_generator.py
python src/openai_image_generator_pipelined.py
```
**Workflow**: Input Image → GPT-4V Analysis → Wrap in Style Template → DALL-E 3 Generation
- **Cost**: Higher (~$0.06-0.10 per image)
- **Speed**: Slower (GPT-4V + DALL-E calls)
- **Adaptability**: Analyzes input context and adapts to configured style
- **Technology**: DALL-E 3 with GPT-4 Vision analysis
- **Parallel Options**: Single-threaded or 2-worker parallel processing

### ⚡ V2: Enhanced Pipeline (Fast) 
**Best for**: Batch processing, image enhancement, high-volume generation with parallel processing
```bash
# Windows  
run_image_generator_v2.bat

# Direct Python
python src/openai_image_generator_v2_simple.py
```
**Workflow**: Image Analysis & Enhancement with GPT-4.1
- **Input**: Images from target directories → GPT-4.1 Analysis & Generation → Enhanced Output
- **Cost**: Moderate (~$0.04-0.08 per image)
- **Speed**: Fast (2-worker parallel processing with optimized startup)
- **Enhancement**: GPT-4.1 analyzes and improves colors, clarity, and composition
- **Technology**: GPT-4.1 responses API with built-in image generation tools

### 🔄 Loop Processor: Evolution Chain (Experimental)
**Best for**: AI evolution experiments, iterative enhancement development, research analysis
```bash
# Windows
run_loop_processor.bat

# Direct Python
python src/loop_processor.py
```
**Workflow**: Linear Chain Processing with GPT-4.1
- Loop 1: `test_loop/` → GPT-4.1 Vision Analysis → GPT-4.1 Image Generation → `test_loop/1/`
- Loop 2: `test_loop/1/` → GPT-4.1 Vision Analysis → GPT-4.1 Image Generation → `test_loop/2/`
- Loop N: `test_loop/(N-1)/` → GPT-4.1 Vision Analysis → GPT-4.1 Image Generation → `test_loop/N/`

**Features**:
- **Cost**: Controlled (GPT-4.1 responses API pricing)
- **Workers**: 2-worker parallel processing
- **Resume**: Configurable start loop (`config/loop_processor_config.json`)
- **Purpose**: Study how AI interprets and evolves image styles over iterations
- **Technology**: GPT-4.1 responses API with built-in image generation tools

### 🎬 Animation Creator: Evolution Visualization with Smooth Transitions
**Best for**: Visualizing AI evolution chains, research presentation, analyzing iteration patterns
```bash
# Windows
create_evolution_animation.bat

# Direct Python
python scripts/create_evolution_animation.py
```
**Workflow**: Smooth Animation Generation with Frame Interpolation
- **Input**: Original images + Loop iterations (L1→L2→L3→...→LN)
- **Output**: Smooth animated GIFs with seamless transitions (unlimited iterations)
- **Bonus**: Grid montages with all frames side-by-side

**Features**:
- **🎬 Frame Interpolation**: Crossfade and morph transitions for smooth evolution visualization
- **⚙️ JSON Configuration**: Complete control via `config/animation_config.json`
- **✨ Multiple Output Versions**: Generate different sizes and qualities (e.g., 'Full Quality', 'Web Optimized') for animations and grids. These versions are defined in the `output_configurations` array within `config/animation_config.json`, allowing customization for various use cases like web sharing or high-resolution archiving.
- **⏱️ Dual Timing**: Separate hold duration (main frames) vs transition duration (morphing)
- **✨ Advanced Morphing**: Smooth easing functions with gaussian blur for natural transitions
- **📊 Auto-Discovery**: Finds evolution chains automatically, detects any number of iterations
- **🔢 Unlimited Frames**: Original + N iterations (supports 10, 20, 50+ iterations)
- **📐 Dynamic Layout**: Auto-calculates optimal grid size based on iteration count
- **🎛️ Configurable**: Adjustable interpolation steps (1-50+ between each frame)
- **📁 Multiple Formats**: Both smooth animated GIFs and static grid layouts
- **🔧 Filename Utilities**: Automatic cleanup of inconsistent naming

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Style Customization](#-style-customization)
- [Troubleshooting](#-troubleshooting)
- [Performance & Requirements](#-performance--requirements)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key with DALL-E 3 access
- 1GB free disk space

### Basic Setup

1. **Clone the repository**:
```bash
git clone [repository-url]
cd Image_Generation_
```

2. **Create and activate virtual environment**:
```bash
python -m venv .venv

# Activate the virtual environment:
.\activate        # Simple - works from project root!

# Or use the standard method:
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## 🌟 Usage

### Quick Generation

1. **Organize images in nested structure**:
```
test/assets/Category_1/object1.png
test/assets/Category_2/object2.png
test/assets/Category_3/object3.png
```

2. **Choose your pipeline**:

```bash
# V1: Intelligent Context Analysis
run_image_generator.bat

# V2: Fast Template Application  
run_image_generator_v2.bat
```

3. **Check output** (preserves folder structure):
```
test_output/assets/Category_1/object1_generated_*.png
test_output/assets/Category_2/object2_generated_*.png
```

### Pipeline Comparison

| Feature | V1 Vision | V2 Enhanced | Loop Processor | Animation Creator |
|---------|-----------|-------------|----------------|-------------------|
| **Analysis** | GPT-4 Vision | GPT-4.1 Vision | GPT-4.1 Vision | Pattern matching |
| **Context** | Full image understanding | Image enhancement | Full + evolution | Evolution chains |
| **Cost** | ~$0.06-0.10/image | ~$0.04-0.08/image | ~$0.04-0.08/image | Free (local processing) |
| **Speed** | Slower | Fast (2 workers) | Moderate (2 workers) | Fast (no API calls) |
| **Best For** | Complex/contextual styles | Image enhancement & batch processing | AI evolution research | Visualizing unlimited iterations |
| **Technology** | DALL-E 3 (Direct) | GPT-4.1 responses API | GPT-4.1 responses API | N/A |
| **Parallel Processing** | 2 workers (pipelined version) | 2 workers | 2 workers | N/A |

## 🎨 Style Customization

### Current Style Configuration
The system is currently configured for **children's crayon-style educational content**, but can be easily adapted for any style:

- **Sci-fi art**: Futuristic, metallic, neon aesthetics
- **Photorealistic**: High-detail, camera-like imagery  
- **Abstract art**: Non-representational, artistic expression
- **Technical illustrations**: Clean, precise, diagram-style
- **Fantasy art**: Mystical, otherworldly, imaginative styles

### Configuration Files

#### V1 Vision Pipeline (`config/image_processing_config.json`):
```json
{
    "prompts": {
        "vision_analysis_prompt": "Analyze this image and describe what you see...",
        "dalle_wrapper_prompt": [
            "Create a [STYLE] based on this description: [CHATGPT_DESCRIPTION]",
            "STYLE: [Your custom style instructions]",
            "FORMAT: [Your format preferences]",
            "TECHNIQUE: [Your technique specifications]"
        ]
    }
}
```

#### V2 Simple Pipeline (`config/image_processing_config-v2.json`):
```json
{
    "directories": {
        "input_dir": "./test",
        "output_dir": "./test_output"
    },
    "gpt_4_1_config": {
        "model": "gpt-4.1-mini",
        "analysis_and_generation_prompt": "Analyze this image carefully and then create an improved, high-quality version. Enhance the colors, clarity, and composition while maintaining the original subject matter."
    },
    "processing": {
        "supported_formats": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"],
        "max_retries": 2,
        "wait_between_retries": 2
    }
}
```

#### Loop Processor (`config/loop_processor_config.json`):
```json
{
    "loop_settings": {
        "start_loop": 1,
        "end_loop": 10,
        "pause_between_iterations": 5,
        "source_directory": "./test_loop"
    },
    "openai": {
        "model": "gpt-4.1",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "gpt_4_1_config": {
        "model": "gpt-4.1-mini",
        "user_prompt_template": "A vivid, high-resolution image of [DESCRIPTION]"
    },
    "prompts": {
        "vision_analysis_prompt": "Analyze this image and describe what you see. Provide a clear, verbose and detailed description so the generator can understand and improve the image."
    }
}
```

#### Animation Creator (`config/animation_config.json`):
```json
{
    "animation_settings": {
        "base_directory": "./test_loop",
        "output_directory": "./evolution_animations",
        "hold_duration": 2000,
        "transition_duration": 10,
        "size": [512, 512],
        "max_iterations": null,
        "interpolation": "morph",
        "interpolation_steps": 25,
        "grid_only": false,
        "animation_only": false
    }
}
```
**Key Settings**:
- **interpolation**: "none", "crossfade", or "morph" for transition style
- **interpolation_steps**: Number of frames between each evolution step (1-50+)
- **hold_duration**: Time main frames are displayed (milliseconds)
- **transition_duration**: Speed of morphing frames (milliseconds)

### Pipeline Features

- **Nested folder support**: Maintains directory structure in output
- **Configurable styling**: Complete control over artistic style via configuration
- **Batch processing**: Process entire directory trees at once
- **Progress logging**: Full prompt logging for validation
- **Error handling**: Automatic retries with fallback prompts
- **Proxy handling**: Automatic network configuration

### Tips for Best Results
- **V1 Vision**: Upload any image; the system analyzes content and applies your configured style
- **V2 Enhanced**: Optimized for image enhancement and quality improvement workflows
- Organize images by category in subfolders for better output management
- Process similar objects in batches for consistency
- Customize prompts in configuration files to match your desired aesthetic

## 🔧 Configuration Details

### V1 Vision Workflow Configuration

The V1 pipeline uses **two-stage prompting**:

1. **Vision Analysis**: GPT-4V analyzes the input image
2. **Style Wrapper**: Wraps the analysis in your custom style instructions

```json
"vision_analysis_prompt": "Analyze this image and describe what you see. Focus on [YOUR_FOCUS_AREA]...",
"dalle_wrapper_prompt": [
    "Create a [YOUR_STYLE] based on this description: [CHATGPT_DESCRIPTION]",
    "STYLE: [Your artistic style specifications]",
    "FORMAT: [Your composition and format rules]",
    "TECHNIQUE: [Your technique requirements]",
    "Key requirements: [Your specific requirements]"
]
```

### V2 Simple Workflow Configuration

Uses direct filename-to-style mapping:

```json
"initial_prompt": [
    "A [YOUR_STYLE] of a single object: [OBJECT_NAME]",
    "[Your style-specific instructions]",
    "[Your format and quality requirements]"
]
```

### Output Processing

**Configurable post-processing workflow**:

- **Format conversion**: Multiple output format support
- **Quality control**: Configurable validation criteria

Images are generated with backgrounds and formatting optimized for your specified style.

## 🧪 Testing & Validation

### Test Scripts

```bash
# Test V1 workflow with current configuration
python scripts/test_vision_workflow.py

# Test OpenAI API setup
python scripts/verify_openai_setup.py

# Debug connection issues  
python scripts/debug_openai.py

# Monitor generation progress
python scripts/monitor_progress.py

# Test prompt configuration
python scripts/test_prompt_config.py

# Create evolution animations (after loop processing)
python scripts/create_evolution_animation.py

# Create animations with specific iteration limit
python scripts/create_evolution_animation.py --max-iterations 15

# Fix inconsistent loop filenames (if needed)
python scripts/fix_loop_filenames.py
```

## 🐛 Troubleshooting

### Common Issues

#### "OPENAI_API_KEY not found"
- Create `.env` file in project root
- Add: `OPENAI_API_KEY=your-key-here`

#### Proxy/Connection Errors
- Both pipelines automatically handle proxy issues
- Uses `httpx.Client(trust_env=False)` to bypass system proxies
- Error typically shows: "unexpected keyword argument 'proxies'"

#### Style Inconsistency
- **V1**: Review vision analysis prompts in config for your use case
- **V2**: Ensure prompt templates match your desired style consistently
- Process similar items together for best results
- Adjust temperature settings for more/less variation

#### Vision Analysis Issues (V1 only)
- Verify GPT-4 Vision access in your OpenAI account
- Check image file formats (PNG, JPG, JPEG supported)
- Customize vision_analysis_prompt for your specific domain

## 📊 Performance & Requirements

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB |
| Storage | 1GB | 2GB |
| Python | 3.8+ | 3.12+ |
| Internet | Required | High-speed |

### Generation Speed & Cost

| Pipeline | Speed | Cost per Image | API Calls |
|----------|-------|---------------|-----------|
| **V1 Vision** | 20-30 seconds | $0.06-0.10 | GPT-4V + DALL-E |
| **V2 Simple** | 5-10 seconds | $0.04-0.08 | DALL-E only |
| **Loop Processor** | 15-25 seconds | $0.06-0.10 | GPT-4V + DALL-E |

### Batch Processing
- **V1**: ~2 seconds delay between images (rate limiting)
- **V2**: ~2 seconds delay between images (rate limiting)
- **Loop Processor**: 2-worker parallel processing with 3s offset
- **Nested folders**: Automatically maintains directory structure
- **API limits**: Check your OpenAI account limits

## 📁 Project Structure

```
Image_Generation_/
├── src/                              # Source code
│   ├── openai_image_generator.py     # V1: Vision-enhanced pipeline  
│   ├── openai_image_generator_v2_simple.py # V2: Fast pipeline
│   ├── loop_processor.py             # Loop: Evolution chain processor
│   └── openai_image_processor.py     # Legacy (replaced by V1)
├── scripts/                          # Utility scripts
│   ├── test_vision_workflow.py       # Test V1 workflow
│   ├── verify_openai_setup.py       # API verification
│   ├── debug_openai.py              # Connection debugging
│   ├── monitor_progress.py          # Progress monitoring
│   ├── create_evolution_animation.py # Evolution animation creator (unlimited iterations)
│   └── fix_loop_filenames.py        # Fix inconsistent loop filenames
├── config/                          # Configuration files
│   ├── image_processing_config.json # V1 configuration
│   ├── image_processing_config-v2.json # V2 configuration
│   └── loop_processor_config.json   # Loop processor configuration
├── test/assets/[categories]/         # Input images (nested structure)
├── test_output/assets/[categories]/  # Generated images (preserves structure)
├── test_loop/                       # Loop processor input/output
│   ├── 1/, 2/, 3/, ..., N/          # Evolution chain outputs (unlimited)
├── evolution_animations/            # Animation output directory
│   ├── [name]_evolution_*.gif       # Animated evolution chains (unlimited frames)
│   └── [name]_grid_*.png           # Auto-sized grid montages
├── docs/                            # Documentation & project tracking
├── run_image_generator.bat          # Windows batch (V1 vision)
├── run_image_generator_v2.bat       # Windows batch (V2 simple)
├── run_loop_processor.bat           # Windows batch (Loop processor)
├── create_evolution_animation.bat   # Windows batch (Animation creator)
└── .env                             # API keys (create this)
```