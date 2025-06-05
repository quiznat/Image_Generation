@echo off
echo.
echo ========================================
echo  OpenAI Image Generator - Parallel Processing
echo ========================================
echo.
echo 🔥 Running parallel V1 workflow with dual workers:
echo    Worker-1: Complete workflow (Images 1,3,5,7...)
echo    Worker-2: Complete workflow (Images 2,4,6,8...)
echo.
echo ⚡ All workers execute: GPT-4V Analysis → DALL-E Generation
echo 🔄 Staggered startup: 0s, 3s intervals for optimal performance
echo 🏁 Optimized parallel processing for consistent throughput
echo ⚠️  Dual worker architecture - Reliable performance over long batches
echo 💥 2x parallelism provides optimal consistency and performance balance
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run the parallel image generator
python src\openai_image_generator_pipelined.py

echo.
echo ✅ Parallel processing complete!
echo 📁 Check test_output\ for generated images
echo 📋 Check test_logs\ for detailed logs
echo 📊 Consistent performance achieved with dual worker architecture!
echo.
pause 