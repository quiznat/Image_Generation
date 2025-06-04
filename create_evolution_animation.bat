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
echo.
pause

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run the evolution animation creator
python scripts\create_evolution_animation.py

echo.
echo ✅ Evolution animations complete!
echo 📁 Check .\evolution_animations\ for results
echo 🎬 Animated GIFs show the progression loop by loop
echo 🖼️  Grid images show all 10 iterations at once
echo.
pause 