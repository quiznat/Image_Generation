@echo off
echo.
echo ========================================
echo  OpenAI Image Generator - DOUBLE TROUBLE
echo ========================================
echo.
echo 🔥 Running parallel V1 workflow with TWO workers:
echo    Worker-1: Complete workflow (Images 1,3,5,7...)
echo    Worker-2: Complete workflow (Images 2,4,6,8...)
echo.
echo ⚡ All workers do: GPT-4V Analysis → DALL-E Generation
echo 🔄 Staggered startup: 0s, 3s intervals
echo 🏁 NO ARTIFICIAL RATE LIMITING - STEADY AND CONSISTENT!
echo ⚠️  DOUBLE TROUBLE - Reliable performance over long batches
echo 💥 2x parallelism = Optimal consistency balance
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run the DOUBLE TROUBLE parallel image generator
python src\openai_image_generator_pipelined.py

echo.
echo ✅ DOUBLE TROUBLE processing complete!
echo 📁 Check test_output\ for generated images
echo 📋 Check test_logs\ for detailed logs
echo 📊 Consistent performance - steady throughput without issues!
echo.
pause 