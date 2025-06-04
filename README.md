# Image Generation System

A comprehensive, configurable OpenAI DALL-E 3 based system for creating consistent, high-quality illustrations with customizable styles and workflows. Features both **intelligent vision analysis** and **fast filename-based** generation pipelines.

## 🎨 Overview

This project offers **two production-ready, configurable pipelines** using OpenAI's DALL-E 3:
- **Style**: Fully customizable via configuration files
- **Format**: Configurable output specifications  
- **Purpose**: Adaptable to any image generation use case
- **Output**: High-quality images in specified dimensions
- **Architecture**: Nested folder support for organized batch processing

**Current Configuration**: Set up for children's crayon-style educational content, but easily adaptable for sci-fi art, photorealistic images, abstract art, or any other style.

## 🚀 Two Production Pipelines

### 🔍 V1: Vision-Enhanced Pipeline (Intelligent)
**Best for**: Complex objects, style-aware generation, context-sensitive workflows
```bash
# Windows
run_image_generator.bat

# Direct Python
python src/openai_image_generator.py
```
**Workflow**: Input Image → GPT-4V Analysis → Wrap in Style Template → DALL-E Generation
- **Cost**: Higher (~$0.06-0.10 per image)
- **Speed**: Slower (GPT-4V + DALL-E calls)
- **Adaptability**: Analyzes input context and adapts to configured style

### ⚡ V2: Simple Pipeline (Fast) 
**Best for**: Batch processing, consistent style application, high-volume generation
```bash
# Windows  
run_image_generator_v2.bat

# Direct Python
python src/openai_image_generator_v2_simple.py
```
**Workflow**: Filename → Apply Style Template → DALL-E Generation
- **Cost**: Lower (~$0.04-0.08 per image)
- **Speed**: Faster (single DALL-E call)
- **Consistency**: Direct style application from configuration

### 🔄 Loop Processor: Evolution Chain (Experimental)
**Best for**: AI evolution experiments, iterative style development, research analysis
```bash
# Windows
run_loop_processor.bat

# Direct Python
python src/loop_processor.py
```
**Workflow**: Linear Chain Processing
- Loop 1: `test_loop/` → GPT-4V Analysis → DALL-E → `test_loop/1/`
- Loop 2: `test_loop/1/` → GPT-4V Analysis → DALL-E → `test_loop/2/`
- Loop N: `test_loop/(N-1)/` → GPT-4V Analysis → DALL-E → `test_loop/N/`

**Features**:
- **Cost**: Controlled (80 total images for 8 inputs)
- **Workers**: 2-worker parallel processing
- **Resume**: Configurable start loop (`config/loop_processor_config.json`)
- **Purpose**: Study how AI interprets and evolves image styles over iterations

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
- 5GB free disk space

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
pip install -r requirements-minimal.txt
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

| Feature | V1 Vision | V2 Simple | Loop Processor |
|---------|-----------|-----------|----------------|
| **Analysis** | GPT-4 Vision | Filename only | GPT-4 Vision |
| **Context** | Full image understanding | Object name | Full + evolution |
| **Cost** | ~$0.06-0.10/image | ~$0.04-0.08/image | ~$0.06-0.10/image |
| **Speed** | Slower | Faster | Moderate (2 workers) |
| **Best For** | Complex/contextual styles | Consistent style application | AI evolution research |

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
    "prompts": {
        "initial_prompt": [
            "A [STYLE] of a single object: [OBJECT_NAME]",
            "[Your style-specific instructions]",
            "[Your format and composition rules]"
        ]
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
    "prompts": {
        "vision_analysis_prompt": "Analyze this image and describe what you see...",
        "dalle_wrapper_prompt": ["[CHATGPT_DESCRIPTION]"]
    }
}
```

### Pipeline Features

- **Nested folder support**: Maintains directory structure in output
- **Configurable styling**: Complete control over artistic style via configuration
- **Batch processing**: Process entire directory trees at once
- **Progress logging**: Full prompt logging for validation
- **Error handling**: Automatic retries with fallback prompts
- **Proxy handling**: Automatic network configuration

### Tips for Best Results
- **V1 Vision**: Place any image, system analyzes content and applies your configured style
- **V2 Simple**: Use descriptive filenames for best object recognition
- Organize by category in subfolders for better output management
- Process similar objects in batches for consistency
- Customize prompts in config files to match your desired aesthetic

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

- **Background removal**: Manual or automated options
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
| Storage | 5GB | 10GB |
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
│   └── monitor_progress.py          # Progress monitoring
├── config/                          # Configuration files
│   ├── image_processing_config.json # V1 configuration
│   ├── image_processing_config-v2.json # V2 configuration
│   └── loop_processor_config.json   # Loop processor configuration
├── test/assets/[categories]/         # Input images (nested structure)
├── test_output/assets/[categories]/  # Generated images (preserves structure)
├── test_loop/                       # Loop processor input/output
│   ├── 1/, 2/, 3/, ..., 10/         # Evolution chain outputs
├── docs/                            # Documentation & project tracking
├── run_image_generator.bat          # Windows batch (V1 vision)
├── run_image_generator_v2.bat       # Windows batch (V2 simple)
├── run_loop_processor.bat           # Windows batch (Loop processor)
└── .env                             # API keys (create this)
```