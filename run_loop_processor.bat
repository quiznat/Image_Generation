@echo off
echo.
echo =========================================
echo    LOOP IMAGE PROCESSOR - 10 ITERATIONS
echo =========================================
echo.
echo 🔄 This script will:
echo    1. Process all files in .\test_loop\
echo    2. Run 10 iterations total
echo    3. Save each iteration to .\test_loop\X (where X = 1-10)
echo    4. Use the existing image generator pipeline
echo.
echo ⚠️  Make sure your OPENAI_API_KEY is set in the .env file!
echo 📁 Source files: .\test_loop\
echo 📂 Output pattern: .\test_loop\1\, .\test_loop\2\, etc.
echo.
pause

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Create the loop processor Python script and run it
python src\loop_processor.py

echo.
echo ✅ Loop processing complete!
echo 📁 Check .\test_loop\1\ through .\test_loop\10\ for results
echo 📋 Check test_logs\ for detailed logs
echo.
pause 