---
name: intermediates-batch
description: Run batch intermediate generation for all toys at once. Use when user wants to generate all intermediates, run full batch, or regenerate everything.
---

# Batch Generate All Intermediates

Generate intermediate crafting components for all 39 toys using the manifest file.

## Usage

```bash
# All toys, unique intermediates only (recommended)
python3 src/intermediate_generator.py \
  --all \
  --manifest game_assets/toy_references.json \
  --skip-shared \
  --force-regenerate

# All toys, including shared intermediates
python3 src/intermediate_generator.py \
  --all \
  --manifest game_assets/toy_references.json \
  --force-regenerate
```

## Steps

1. **Run in background** (this takes ~2 hours):
   ```bash
   python3 src/intermediate_generator.py --all --manifest game_assets/toy_references.json --skip-shared --force-regenerate
   ```
   Use `run_in_background: true` and `timeout: 600000`

2. **Monitor progress**:
   ```bash
   tail -20 /tmp/claude/-Users-quiznat-Desktop-Image-Generation-Pipeline/tasks/{task_id}.output
   ```

3. **Check completion**:
   ```bash
   find game_output/Santas_Nordic_Workshop/intermediates -name "*.png" | wc -l
   ```

## Manifest File

`game_assets/toy_references.json` contains all 39 toys mapped to their reference images:
- 28 toys from `game_output/Santas_Nordic_Workshop/toys/`
- 11 toys from `game_assets/*_card.png`

## Counts

- 144 total unique intermediate types
- 29 shared (used by multiple toys)
- 115 unique (1-of-1 toy-specific)

With `--skip-shared`: ~115 images per run
Without `--skip-shared`: ~200+ images per run (shared duplicated per toy)

## Output

All images saved to `game_output/Santas_Nordic_Workshop/intermediates/{toy_id}/`
