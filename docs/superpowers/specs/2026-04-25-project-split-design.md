# Project Split Design: legacy/ + sb3/

**Date:** 2026-04-25
**Status:** Approved

## Goal

Split the current monolithic project into two clearly separated subfolders within the same git repository:
- `legacy/` — archived `main_train.py` version (frozen, reference only)
- `sb3/` — active development `train_sb3.py` version (SB3 MaskablePPO system)

## Folder Structure

```
sudoku_old/                     ← git repo root
├── data/
│   └── puzzle_pool.db          ← shared puzzle database (both versions read here)
│
├── legacy/                     ← archived main_train.py version (do not modify)
│   ├── main_train.py
│   ├── requirements.txt
│   ├── data/
│   │   └── user_config.json    ← legacy-specific settings
│   ├── models/
│   │   └── sudoku_policy_latest.pt
│   ├── tests/
│   └── app/
│       ├── config/
│       ├── data/               (pool_db.py)
│       ├── gui/
│       ├── sudoku/             (env, torch_agent, phase_manager, teacher_engine, validator, agents, policy_demo_store)
│       ├── training/
│       └── web/
│
├── sb3/                        ← active development version
│   ├── train_sb3.py
│   ├── requirements.txt
│   ├── models/
│   ├── runs/
│   └── app/
│       ├── data/               (pool_db.py — copied from shared)
│       ├── rl/                 (envs, models, curriculum)
│       └── sudoku/             (teacher_engine.py, validator.py — copied from shared)
│
├── CLAUDE.md
├── HISTORY.md
└── .git/
```

## File Mapping

### Files moved to `legacy/`

| Source | Destination |
|--------|-------------|
| `main_train.py` | `legacy/main_train.py` |
| `app/config/` | `legacy/app/config/` |
| `app/gui/` | `legacy/app/gui/` |
| `app/sudoku/` | `legacy/app/sudoku/` (all files) |
| `app/training/` | `legacy/app/training/` |
| `app/web/` | `legacy/app/web/` |
| `app/data/pool_db.py` | `legacy/app/data/pool_db.py` |
| `data/user_config.json` | `legacy/data/user_config.json` |
| `models/sudoku_policy_latest.pt` | `legacy/models/sudoku_policy_latest.pt` |
| `tests/` | `legacy/tests/` |

### Files moved to `sb3/`

| Source | Destination | Note |
|--------|-------------|------|
| `train_sb3.py` | `sb3/train_sb3.py` | |
| `app/rl/` | `sb3/app/rl/` | |
| `app/data/pool_db.py` | `sb3/app/data/pool_db.py` | copied (not moved) |
| `app/sudoku/teacher_engine.py` | `sb3/app/sudoku/teacher_engine.py` | copied |
| `app/sudoku/validator.py` | `sb3/app/sudoku/validator.py` | copied |
| `models/` | `sb3/models/` | |
| `runs/` | `sb3/runs/` | |

`pool_db.py`, `teacher_engine.py`, and `validator.py` are **copied** into both versions to ensure complete isolation. The legacy version is frozen so there is no maintenance burden from duplication.

## requirements.txt Split

The root `requirements.txt` is split into two version-specific files:

**`legacy/requirements.txt`** (original deps):
```
torch>=2.0.0, numpy, requests, PyQt6, keyboard, PySocks, playwright
```

**`sb3/requirements.txt`** (new deps):
```
torch>=2.0.0, numpy, stable-baselines3>=2.0.0, sb3-contrib>=2.0.0,
gymnasium>=1.0.0, tensorboard>=2.0.0, pytest>=7.4.0, pytest-cov>=4.1.0
```

## Code Changes

Only two lines change:

```python
# legacy/main_train.py
DB_PATH = "../data/puzzle_pool.db"   # was "data/puzzle_pool.db"

# sb3/train_sb3.py
DB_PATH = "../data/puzzle_pool.db"   # was "data/puzzle_pool.db"
```

All other import paths are unaffected because both versions are run by `cd`-ing into their subfolder first.

## Usage After Migration

```bash
# New (active development)
cd sb3
python train_sb3.py

# Legacy (reference only)
cd legacy
python main_train.py
```

## Root Cleanup

After migration the root will contain only:
- `data/` (shared DB)
- `legacy/` (archived)
- `sb3/` (active)
- `CLAUDE.md`, `HISTORY.md`, `.git/`, `.gitattributes`

All original `app/`, `main_train.py`, `train_sb3.py`, `requirements.txt`, `models/`, `runs/`, `tests/` at the root level are removed once their contents are relocated.
