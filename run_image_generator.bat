@echo off
echo.
echo === OpenAI Image Generator (Vision-Enhanced) ===
echo.
echo This tool will:
echo 1. Analyze your images with GPT-4 Vision
echo 2. Wrap the analysis in detailed DALL-E prompts
echo 3. Generate new crayon-style images with DALL-E 3
echo 4. Save generated images (use Canva for background removal)
echo.
echo Make sure your OPENAI_API_KEY is set in the .env file!
echo.
pause

python src/openai_image_generator.py

echo.
echo Process complete! Check the 'test_output' folder for results.
echo Use Canva or other tools for background removal if needed.
pause 