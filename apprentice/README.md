# apprentice/ — Reasoner + Adaptive Curriculum

Sibling of `reasoner/` (frozen baseline). Applies 7 design changes:

| ID | Change |
|---|---|
| A3 | obs +2 channels (naked-single flag + hidden-single flag) — 26 ch total |
| B1 | Adaptive reverse curriculum (sweet-spot formula on `target_empty`) |
| A5 | Dynamic `max_steps = max(60, target_empty × 8)` |
| D1 | Policy hidden layer: `net_arch={"pi": [128], "vf": [128, 128]}` |
| E2 | Dynamic `max_wrong = max(20, target_empty × 1.2)` |
| C2 | `ent_coef = 0.05` (was 0.02) |
| E1 | Cold-start required (obs shape change vs reasoner) |

See [../docs/superpowers/specs/2026-05-13-apprentice-adaptive-curriculum-design.md](../docs/superpowers/specs/2026-05-13-apprentice-adaptive-curriculum-design.md).

## Run from repo root

```bash
# Fresh training
python -m apprentice.train.train

# Resume latest ckpt
python -m apprentice.train.train --load-model auto

# Custom curriculum config
python -m apprentice.train.train --curriculum-config apprentice/configs/curriculum_aggressive.json

# Disable curriculum (debug)
python -m apprentice.train.train --no-curriculum
```

## Tests

```bash
python -m pytest apprentice/tests/ -v
```

## Curriculum config

Edit [configs/curriculum.json](configs/curriculum.json) between training sessions. Hot-reload during a single run is not supported.

Three core hyperparameters:
- `target_rate`: desired success rate the curriculum aims for (default 0.70)
- `tolerance_band`: do-nothing zone around target rate (default [0.55, 0.85])
- `step_size`: difficulty adjustment per 10% deviation outside band (default 10.0)

## What's different vs reasoner/

- `env/sudoku_gym_env.py`: 26-channel obs; `target_empty` attribute drives fill_back, dynamic max_steps, dynamic max_wrong
- `env/obs_helpers.py`: new — compute naked/hidden single grids
- `train/curriculum_controller.py`: new — adaptive controller
- `train/curriculum_callback.py`: new — SB3 integration
- `train/train.py`: D1 policy hidden, C2 ent_coef, E1 cold-start assertion, curriculum wiring
- `configs/curriculum.json`: new — controller hyperparameters

`reasoner/` itself is untouched.

## TensorBoard metrics added

| Tag | Meaning |
|---|---|
| `curriculum/target_empty` | Current target_empty (continuous) |
| `curriculum/target_empty_rounded` | Rounded int value passed to envs |
| `curriculum/success_rate_window` | Rolling solve rate over last 200 ep |
| `curriculum/in_sweet_spot` | 1.0 if success_rate in [0.55, 0.85] |
| `curriculum/adjustment_per_update` | Magnitude/direction of last adjustment |
| `curriculum/steps_since_last_advance` | Steps since target_empty last changed |
| `curriculum/is_probing` | 1.0 if stagnation probe is in flight |

Metrics are written every `update_interval_steps` (default 50k). For short smoke tests (< 50k steps) you'll see SB3's standard `rollout/`, `train/`, `eval/` metrics but no `curriculum/` ones until the first update fires.

## Checkpoint sidecars

Each checkpoint zip is paired with two sidecars:
- `<ckpt>_vecnorm.pkl` — VecNormalize running stats
- `<ckpt>_curriculum.json` — CurriculumController state (target_empty, success window, probe state)

`--load-model auto` auto-detects and loads both sidecars if present alongside the chosen ckpt.
