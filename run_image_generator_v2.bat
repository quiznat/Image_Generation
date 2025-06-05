@echo off
echo.
echo === OpenAI Image Generator V2 (GPT-4.1 Enhanced) ===
echo.
echo This tool will:
echo 1. Analyze your images with GPT-4.1 vision
echo 2. Generate improved versions using GPT-4.1's image generation tool
echo 3. Process images with 2-worker parallel pipeline for speed
echo 4. Save enhanced images with better colors, clarity, and composition
echo.
echo Make sure your OPENAI_API_KEY is set in the .env file!
echo And ensure you have the latest OpenAI library with responses API support.
echo.
pause

python src/openai_image_generator_v2_simple.py

echo.
echo Process complete! Check the 'test_output' folder for improved images.
pause 