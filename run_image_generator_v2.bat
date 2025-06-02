@echo off
echo.
echo === OpenAI Image Generator V2 ===
echo.
echo This version:
echo - Goes directly to DALL-E (no GPT-4 analysis)
echo - Uses filename as object description
echo - Prevents style drift for consistent results
echo - No background removal (use Canva later)
echo.
echo Example: "courthouse.png" becomes "courthouse" in the prompt
echo.
echo Make sure to:
echo 1. Name your files descriptively (e.g., "red_barn.png", "happy_sun.jpg")
echo 2. Place images in the 'test' directory
echo 3. Set your OPENAI_API_KEY in the .env file
echo.
pause

python src/openai_image_generator_v2_simple.py

echo.
echo Process complete. Check 'test_output' for results.
echo Use Canva or remove.bg for background removal.
pause 