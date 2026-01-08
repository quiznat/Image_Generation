---
name: gen-status
description: Check status of image generation tasks, background jobs, progress, or how many images have been generated. Use when user asks about progress, status, or completion.
---

# Check Generation Status

Monitor progress of image generation tasks and count generated assets.

## Quick Status Commands

### Count all intermediates
```bash
find game_output/Santas_Nordic_Workshop/intermediates -name "*.png" | wc -l
```

### List intermediate folders
```bash
ls -1 game_output/Santas_Nordic_Workshop/intermediates/ | grep -v "_shared"
```

### Count per toy
```bash
for d in game_output/Santas_Nordic_Workshop/intermediates/*/; do
  echo "$(basename $d): $(ls $d/*.png 2>/dev/null | wc -l) images"
done
```

### Check background task output
```bash
# Get latest output from a background task
tail -20 /tmp/claude/-Users-quiznat-Desktop-Image-Generation-Pipeline/tasks/{task_id}.output
```

### Count all game assets
```bash
echo "Toys: $(ls game_output/Santas_Nordic_Workshop/toys/*.png 2>/dev/null | wc -l)"
echo "Materials: $(ls game_output/Santas_Nordic_Workshop/materials/*.png 2>/dev/null | wc -l)"
echo "Intermediates: $(find game_output/Santas_Nordic_Workshop/intermediates -name '*.png' | wc -l)"
echo "Stations: $(find game_output/Santas_Nordic_Workshop_Stations -name '*.png' 2>/dev/null | wc -l)"
```

## Current Asset Counts (as of Jan 8, 2026)

- **Toys**: 73 images (39 unique toys)
- **Materials**: 395 images
- **Stations**: 48 images
- **Intermediates**: 464+ images across 38 folders
