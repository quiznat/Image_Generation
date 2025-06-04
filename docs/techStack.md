# Tech Stack

## Technologies and Dependencies

### Core Language
- **Tech**: Python 3.12
- **Role**: Primary development language

### Image Generation APIs
- **Tech**: OpenAI API v1.12.0
- **Role**: DALL-E 3 and GPT-4 Vision access
- **Deps**: openai, httpx, pydantic

### Image Processing
- **Tech**: Pillow 10.2.0
- **Role**: Image manipulation and format conversion
- **Deps**: PIL/Pillow

- **Tech**: NumPy 1.26+
- **Role**: Array operations for image processing and frame interpolation
- **Deps**: numpy

### Animation & Visualization
- **Tech**: Animated GIF Creation
- **Role**: Evolution timeline visualization with frame interpolation
- **Deps**: PIL.Image, numpy for blending

- **Tech**: Frame Interpolation
- **Role**: Smooth transitions between evolution frames
- **Patterns**: Crossfade blending, morphing with easing functions

- **Tech**: JSON Configuration
- **Role**: Animation settings management
- **Files**: config/animation_config.json

### Environment Management
- **Tech**: python-dotenv 1.0.0
- **Role**: Environment variable management
- **Deps**: python-dotenv

### Stable Diffusion Stack (Planned)
- **Tech**: PyTorch 2.1.2
- **Role**: Deep learning framework for SD
- **Deps**: torch, torchvision

- **Tech**: Diffusers 0.25.1
- **Role**: Stable Diffusion pipeline
- **Deps**: diffusers, transformers

- **Tech**: ControlNet
- **Role**: Composition control for SD
- **Deps**: controlnet-aux

### Utilities
- **Tech**: tqdm 4.66.1
- **Role**: Progress bars for batch processing
- **Deps**: tqdm

### Development Tools
- **Tech**: pytest 8.0.0
- **Role**: Testing framework
- **Deps**: pytest

- **Tech**: black 24.1.1
- **Role**: Code formatting
- **Deps**: black

### Patterns
- **Pattern**: Factory Pattern
- **Use Case**: Creating different image generators (OpenAI vs SD)

- **Pattern**: Pipeline Pattern
- **Use Case**: Image processing workflow stages

- **Pattern**: Configuration Management
- **Use Case**: JSON-based config for different generation modes

- **Pattern**: Batch Processing
- **Use Case**: Processing multiple images efficiently

### File Formats
- **Input**: .png, .jpg, .jpeg, .gif, .bmp, .webp
- **Output**: .png (primary), .jpg (optional)
- **Config**: .json for configuration files

### API Integrations
- **OpenAI**: DALL-E 3 for image generation
- **GPT-4 Vision**: Image analysis (v1 only)
- **remove.bg**: Potential background removal API

### Infrastructure
- **Version Control**: Git
- **Package Management**: pip, venv
- **OS Support**: Windows, Linux, macOS 