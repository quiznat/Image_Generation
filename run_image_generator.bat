@echo off
echo.
echo === OpenAI Image Processor and Generator ===
echo.
echo This tool will:
echo 1. Analyze your images with GPT-4 Vision
echo 2. Generate new images based on the analysis
echo 3. Save both original and generated versions
echo.
echo Make sure your OPENAI_API_KEY is set in the .env file!
echo.
pause

python src/openai_image_processor.py

echo.
echo Process complete! Check the 'test_output' folder for results.
pause 