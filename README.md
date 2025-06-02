# Image Generation System

A streamlined OpenAI DALL-E 3 based system for creating consistent children's storybook-style illustrations, optimized for educational matching games.

## 🎨 Overview

This project uses OpenAI's DALL-E 3 to generate consistent, child-friendly illustrations:
- **Style**: Crayon/colored pencil aesthetic
- **Format**: Single objects on white backgrounds
- **Purpose**: Educational content for toddlers
- **Output**: High-quality 1024x1024 PNG images

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
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

1. **Place images in the `test/` directory** (filenames become object descriptions)
2. **Run the generation script**:

```bash
# Windows
run_image_generator_v2.bat

# Or directly with Python
python src/openai_image_generator_v2_simple.py
```

### Configuration

Edit `config/image_processing_config-v2.json`:
```json
{
    "prompts": {
        "initial_prompt": [
            "A colorful crayon drawing of a single object: [OBJECT_NAME]...",
            "Only the [OBJECT_NAME] should be visible..."
        ]
    }
}
```

### Pipeline Features

- **Automatic object detection**: Uses filename as object description
- **Consistent styling**: Maintains crayon aesthetic across all images
- **Batch processing**: Process entire directories at once
- **Progress logging**: Full prompt logging for validation
- **Error handling**: Automatic retries on failures

### Tips for Best Results
- Use descriptive filenames (e.g., "red_barn.png", "happy_sun.jpg")
- Process similar objects in batches
- Keep prompts focused on single objects
- Avoid complex or compound object names

## 🔧 Configuration Details

### Prompt Customization

The system uses a template-based approach where `[OBJECT_NAME]` is replaced with your filename:

```json
"initial_prompt": [
    "A colorful crayon drawing of a single object: [OBJECT_NAME]",
    "The object should look like a simple, friendly cartoon drawing for toddlers",
    "Only the [OBJECT_NAME] should be visible..."
]
```

### Optional Background Removal

For transparent backgrounds:

1. **Use rembg** (Python library):
```bash
pip install rembg
```

2. **Use online services**: 
   - Canva (recommended - free and high quality)
   - remove.bg
   - Adobe Express

## 🐛 Troubleshooting

### Verification Scripts

```bash
# Test OpenAI API setup
python scripts/verify_openai_setup.py

# Debug connection issues
python scripts/debug_openai.py

# Monitor generation progress
python scripts/monitor_progress.py
```

### Common Issues

#### "OPENAI_API_KEY not found"
- Create `.env` file in project root
- Add: `OPENAI_API_KEY=your-key-here`

#### Proxy/Connection Errors
- The system automatically handles proxy issues
- Uses `httpx.Client(trust_env=False)` to bypass system proxies

#### Style Inconsistency
- Review and adjust prompt template
- Ensure consistent object naming
- Process similar items together

## 📊 Performance & Requirements

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB |
| Storage | 5GB | 10GB |
| Python | 3.8+ | 3.12+ |
| Internet | Required | High-speed |

### Generation Speed

- **DALL-E 3**: 5-10 seconds per image
- **Batch processing**: ~2 seconds delay between images
- **API limits**: Check your OpenAI account limits

### Cost Estimates

- **DALL-E 3**: ~$0.04-0.08 per image (1024x1024, HD quality)
- **Monthly estimate**: $40-80 for 1000 images

## 📁 Project Structure

```
Image_Generation_/
├── src/                              # Source code
│   └── openai_image_generator*.py    # DALL-E generation variants
├── scripts/                          # Utility scripts
│   ├── verify_openai_setup.py       # API verification
│   ├── debug_openai.py              # Connection debugging
│   ├── monitor_progress.py          # Progress monitoring
│   ├── test_prompt_config.py        # Prompt validation
│   └── test_single_generation.py    # Single image testing
├── config/                          # Configuration files
│   └── image_processing_config*.json # Generation settings
├── test/                            # Input images
├── test_output/                     # Generated images
├── docs/                            # Documentation
├── requirements.txt                 # Full dependencies
├── requirements-minimal.txt         # Minimal dependencies
├── run_image_generator.bat          # Windows batch (v1)
├── run_image_generator_v2.bat       # Windows batch (v2)
├── .env                             # API keys (create this)
└── README.md                        # This file
```

## 🤝 Contributing

1. Check `docs/currentTask.md` for active work
2. Review `docs/projectRoadmap.md` for planned features
3. Follow the principles in `docs/Pillars.md`
4. Update documentation when making changes

## 📄 License

[Specify your license here]

## 🙏 Acknowledgments

- Built for creating educational content for children
- Optimized for matching game asset generation
- Uses OpenAI's DALL-E 3 for consistent, high-quality results

## 📝 Quick Commands Reference

```bash
# Verify setup
python scripts/verify_openai_setup.py

# Test single generation
python scripts/test_single_generation.py

# Monitor batch progress
python scripts/monitor_progress.py

# Main generation (Windows)
run_image_generator_v2.bat

# Main generation (Python)
python src/openai_image_generator_v2_simple.py

# Test prompt configuration
python scripts/test_prompt_config.py
```

## 🔗 Project Origin

This project was extracted from the OpsAssistant repository to create a standalone image generation tool, originally built for creating matching game assets for children's educational games.

> **Update (2024-12-29)**: After extensive testing, this project now focuses exclusively on the OpenAI DALL-E pipeline, which provides superior results for children's illustration style compared to local Stable Diffusion alternatives.