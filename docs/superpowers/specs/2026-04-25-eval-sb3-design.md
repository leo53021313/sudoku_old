# eval_sb3.py Design

**Date:** 2026-04-25
**Status:** Approved

## Goal

Add a standalone evaluation script `sb3/eval_sb3.py` that loads a trained `SudokuMaskablePPO` checkpoint and tests it against Sudoku puzzles, reporting per-difficulty statistics. Supports a fixed reserved puzzle set (JSON) for reproducible benchmarking, and ASCII board visualization for debugging failure cases.

## Architecture

```
sb3/
├── eval_sb3.py                        ← main entry point (CREATE)
├── data/
│   └── eval_puzzles.json              ← reserved puzzle set, auto-generated on first use (CREATE)
└── app/rl/
    ├── eval/
    │   ├── __init__.py                ← (CREATE)
    │   └── puzzle_set.py              ← EvalPuzzleSet (CREATE)
    └── envs/
        └── sudoku_gym_env.py          ← add options support to reset() (MODIFY)
```

## CLI Interface

```bash
# Basic eval (random puzzles from DB)
python eval_sb3.py --model models/sudoku_sb3_latest.zip

# With VecNormalize stats (recommended when trained with VecNormalize)
python eval_sb3.py --model models/foo.zip --vecnorm models/foo_vecnorm.pkl

# Reserved eval set (reproducible benchmarking)
python eval_sb3.py --model models/foo.zip --eval-set reserved --n-puzzles 50

# Show ASCII debug boards for first 3 failures
python eval_sb3.py --model models/foo.zip --debug-n 3

# Specific difficulties only
python eval_sb3.py --model models/foo.zip --difficulty 1,2
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--model` | required | Path to .zip checkpoint |
| `--vecnorm` | None | Path to _vecnorm.pkl (load reward normalization stats) |
| `--eval-set` | `random` | `random` = sample from DB each run; `reserved` = fixed JSON set |
| `--n-puzzles` | 20 | Puzzles per difficulty level |
| `--difficulty` | `1,2,3,4` | Comma-separated difficulty levels to test |
| `--debug-n` | 0 | Print ASCII board viz for first N failure cases |
| `--db-path` | `../data/puzzle_pool.db` | Puzzle database path |
| `--reserved-path` | `data/eval_puzzles.json` | Path to reserved puzzle set JSON |
| `--seed` | 42 | Random seed for reproducible random sampling |

## Components

### `sb3/app/rl/eval/puzzle_set.py` — EvalPuzzleSet

Manages the reserved puzzle set. On first call with `reserved` mode, samples puzzles from the DB and saves to JSON. Subsequent calls load from JSON directly.

```python
class EvalPuzzleSet:
    def __init__(self, json_path: str, db_path: str, n_per_difficulty: int = 50)
    def get_puzzles(self, difficulty: int) -> list[tuple[np.ndarray, np.ndarray]]
        # returns list of (board_9x9, solution_9x9) arrays
    def _populate(self) -> None
        # sample n_per_difficulty puzzles per level from DB, save to JSON
```

JSON format:
```json
{
  "created": "2026-04-25",
  "n_per_difficulty": 50,
  "puzzles": {
    "1": [{"puzzle": "530...", "solution": "534..."}, ...],
    "2": [...],
    "3": [...],
    "4": [...]
  }
}
```

### `sb3/app/rl/envs/sudoku_gym_env.py` — reset() modification

Add `options` parameter to `reset()` (standard Gymnasium API). Backwards-compatible: if `options` is None or missing keys, falls back to DB random fetch.

```python
def reset(self, seed=None, options=None):
    if options and "board" in options and "solution" in options:
        self.board    = options["board"].copy()
        self.solution = options["solution"].copy()
        self._difficulty = options.get("difficulty", 1)
        self._rebuild_candidates()
        # ... init other state
    else:
        # existing DB fetch logic (unchanged)
        ...
```

### `sb3/eval_sb3.py` — Entry Point

1. Parse args
2. Load model via `SudokuMaskablePPO.load()` (+ optional VecNormalize)
3. Create single `DummyVecEnv` with one `SudokuGymEnv`
4. For each difficulty:
   - Fetch N puzzles (from DB or reserved JSON)
   - Run each puzzle with `model.predict(obs, deterministic=True)`
   - Collect: success (bool), steps (int), total_reward (float)
5. Print summary table
6. If `--debug-n > 0`: re-run first N failure cases and print ASCII boards

## Output Format

**Standard statistics table:**
```
=== Sudoku Eval — models/sudoku_sb3_latest.zip ===
Eval set: random  |  20 puzzles/difficulty  |  Difficulties: L1 L2 L3 L4

Difficulty   Success      Avg Steps   Avg Reward
L1           18/20  90%   35.2        142.3
L2           12/20  60%   48.7         98.1
L3            4/20  20%   61.3         45.6
L4            1/20   5%   71.2         12.4
──────────────────────────────────────────────
Overall      35/80  44%   54.1         74.6
```

**Debug board output (--debug-n N):**
```
── Debug: L2 failure #1 (34 steps, terminated by wrong fills) ──
Initial board:               Final board:
 5  3  . │ .  7  . │ .  .  .   5  3  4 │ 6  7  8 │ 9  1  2
 6  .  . │ 1  9  5 │ .  .  .   6  7  2 │ 1  9  5 │ 3  4  8
 .  9  8 │ .  .  . │ .  6  .   1  9  8 │ 3  4  2 │ 5  6  7
─────────┼─────────┼─────────  ─────────┼─────────┼─────────
 ...
Wrong fills: 5  |  Correct: 29/34
```

Only initial and final states printed (not step-by-step). Wrong fill count and correct/total ratio identify failure mode at a glance.

## Key Design Decisions

- **DummyVecEnv (single env)**: eval doesn't need parallelism; single env is simpler and avoids subprocess overhead
- **deterministic=True**: eval uses greedy policy (`argmax` over action probs), not sampling — removes noise for fair comparison
- **JSON reserved set**: stored outside DB to avoid schema changes; auto-populated on first `--eval-set reserved` run
- **options in reset()**: standard Gymnasium API, backward-compatible, minimal diff to existing code
- **VecNormalize is optional for eval**: `train_sb3.py` sets `norm_obs=False` — only rewards are normalized, not observations. The policy therefore runs correctly without VecNormalize. `--vecnorm` is provided for completeness but skipped if not supplied; eval always reports **raw (unnormalized) rewards** for human readability regardless.

## Files Summary

| File | Action | Notes |
|------|--------|-------|
| `sb3/eval_sb3.py` | CREATE | ~150 lines |
| `sb3/app/rl/eval/__init__.py` | CREATE | empty |
| `sb3/app/rl/eval/puzzle_set.py` | CREATE | EvalPuzzleSet class |
| `sb3/app/rl/envs/sudoku_gym_env.py` | MODIFY | ~15 lines added to reset() |
| `sb3/data/` directory | CREATE | for eval_puzzles.json |
