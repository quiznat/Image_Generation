@echo off
echo.
echo ========================================
echo    AI EVOLUTION ANIMATION CREATOR
echo ========================================
echo.
echo 🎬 This script will:
echo    1. Find all evolution chains in .\test_loop\
echo    2. Create animated GIFs showing AI evolution
echo    3. Create grid montages of all iterations
echo    4. Save results to .\evolution_animations\
echo    5. Create multiple versions (full-size + web-optimized)
echo.
pause

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo.
echo 🎬 Creating evolution animations (multiple versions from config)...
REM Run the evolution animation creator - it will create all configured versions
python scripts\create_evolution_animation.py

echo.
echo ✅ Evolution animations complete!
echo 📁 Check .\evolution_animations\ for results
echo 🎬 Full-size GIFs (512x512): Original quality
echo 📱 Web GIFs (400x400): Optimized for sharing/previews  
echo 🖼️  Grid images show all iterations at once
echo 📝 Edit config\animation_config.json to customize settings
echo.
pause 