# Project Split: legacy/ + sb3/ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the repo into two self-contained subfolders — `legacy/` (archived `main_train.py` version) and `sb3/` (active `train_sb3.py` version) — sharing only `data/puzzle_pool.db` at the root.

**Architecture:** Use `git mv` for moves to preserve history. Copy the three shared modules (`pool_db.py`, `teacher_engine.py`, `validator.py`) into both subfolders so they are fully independent. Both versions run by `cd`-ing into their subfolder; paths like `"data/..."` resolve correctly relative to the working directory, except `puzzle_pool.db` which moves to root and requires `"../data/puzzle_pool.db"`.

**Tech Stack:** Git (mv for history), Python (namespace packages — no `__init__.py` required for implicit namespace packages, but explicit ones added for clarity), Bash shell commands.

---

## Task 1: Create Directory Skeleton

**Files:**
- Create: `legacy/app/config/`, `legacy/app/gui/`, `legacy/app/sudoku/`, `legacy/app/training/`, `legacy/app/web/`, `legacy/app/data/`, `legacy/data/`, `legacy/models/`, `legacy/tests/`
- Create: `sb3/app/rl/`, `sb3/app/data/`, `sb3/app/sudoku/`, `sb3/models/`

- [ ] **Step 1: Create legacy/ directory tree**

```bash
mkdir -p legacy/app/config legacy/app/gui legacy/app/sudoku legacy/app/training legacy/app/web legacy/app/data legacy/data legacy/models legacy/tests
```

- [ ] **Step 2: Create sb3/ directory tree**

```bash
mkdir -p sb3/app/rl sb3/app/data sb3/app/sudoku sb3/models
```

- [ ] **Step 3: Verify directories exist**

```bash
ls legacy/app/ && ls sb3/app/
```

Expected output:
```
config  data  gui  sudoku  training  web
data  rl  sudoku
```

---

## Task 2: Copy Shared Modules to sb3/

Three files are used by both versions. Copy (do NOT git mv) them to `sb3/` — legacy will receive them via git mv in Task 4.

**Files:**
- Copy: `app/data/pool_db.py` → `sb3/app/data/pool_db.py`
- Copy: `app/sudoku/teacher_engine.py` → `sb3/app/sudoku/teacher_engine.py`
- Copy: `app/sudoku/validator.py` → `sb3/app/sudoku/validator.py`

- [ ] **Step 1: Copy shared modules**

```bash
cp app/data/pool_db.py sb3/app/data/pool_db.py
cp app/sudoku/teacher_engine.py sb3/app/sudoku/teacher_engine.py
cp app/sudoku/validator.py sb3/app/sudoku/validator.py
```

- [ ] **Step 2: Create __init__.py files for sb3/ packages**

```bash
touch sb3/app/__init__.py sb3/app/data/__init__.py sb3/app/sudoku/__init__.py
```

- [ ] **Step 3: Stage copied files**

```bash
git add sb3/
```

---

## Task 3: Move sb3-Specific Files

Move `train_sb3.py`, `app/rl/`, `runs/`, and the current `requirements.txt` into `sb3/`.

**Files:**
- git mv: `train_sb3.py` → `sb3/train_sb3.py`
- git mv: `app/rl/` → `sb3/app/rl/`
- git mv: `runs/` → `sb3/runs/`

- [ ] **Step 1: Move train_sb3.py**

```bash
git mv train_sb3.py sb3/train_sb3.py
```

- [ ] **Step 2: Move app/rl/**

```bash
git mv app/rl sb3/app/rl
```

- [ ] **Step 3: Move runs/**

```bash
git mv runs sb3/runs
```

- [ ] **Step 4: Move sb3 model files (any .zip checkpoints)**

```bash
# Move any SB3 checkpoint .zip files if they exist
ls models/*.zip 2>/dev/null && git mv models/*.zip sb3/models/ || echo "No .zip checkpoints yet — skipping"
```

- [ ] **Step 5: Verify sb3/ structure**

```bash
find sb3/ -not -path '*/__pycache__/*' | sort
```

Expected: `sb3/train_sb3.py`, `sb3/app/rl/...`, `sb3/runs/...`

---

## Task 4: Move Legacy Files

Move everything remaining from the old structure into `legacy/`.

**Files:**
- git mv: `main_train.py` → `legacy/main_train.py`
- git mv: `app/config/` → `legacy/app/config/`
- git mv: `app/gui/` → `legacy/app/gui/`
- git mv: `app/sudoku/` → `legacy/app/sudoku/`
- git mv: `app/training/` → `legacy/app/training/`
- git mv: `app/web/` → `legacy/app/web/`
- git mv: `app/data/` → `legacy/app/data/`
- git mv: `tests/` → `legacy/tests/`
- git mv: `models/*.pt` → `legacy/models/`
- Modify: `data/user_config.json` → `legacy/data/user_config.json`

- [ ] **Step 1: Move main entry point**

```bash
git mv main_train.py legacy/main_train.py
```

- [ ] **Step 2: Move app/ submodules**

```bash
git mv app/config legacy/app/config
git mv app/gui legacy/app/gui
git mv app/sudoku legacy/app/sudoku
git mv app/training legacy/app/training
git mv app/web legacy/app/web
git mv app/data legacy/app/data
```

- [ ] **Step 3: Move tests/**

```bash
git mv tests legacy/tests
```

- [ ] **Step 4: Move PyTorch model files to legacy/models/**

```bash
git mv models/sudoku_policy_latest.pt legacy/models/sudoku_policy_latest.pt
ls models/sudoku_policy_latest.pt.old 2>/dev/null && git mv models/sudoku_policy_latest.pt.old legacy/models/sudoku_policy_latest.pt.old || echo "No .pt.old — skipping"
```

- [ ] **Step 5: Move user_config.json**

```bash
git mv data/user_config.json legacy/data/user_config.json
```

- [ ] **Step 6: Verify legacy/ structure**

```bash
find legacy/ -not -path '*/__pycache__/*' | sort | head -40
```

Expected: `legacy/main_train.py`, `legacy/app/config/...`, `legacy/app/gui/...`, `legacy/app/sudoku/...` etc.

---

## Task 5: Fix Path Constants

Two path constants point to the wrong location after the restructure. Both become `"../data/puzzle_pool.db"` since we run from inside the subfolder.

**Files:**
- Modify: `sb3/train_sb3.py` line with `DB_PATH`
- Modify: `legacy/app/config/schema.py` — `db.path` default value

- [ ] **Step 1: Update DB_PATH in sb3/train_sb3.py**

Find and replace line 39 in `sb3/train_sb3.py`:
```python
# Before
DB_PATH    = "data/puzzle_pool.db"

# After
DB_PATH    = "../data/puzzle_pool.db"
```

- [ ] **Step 2: Update db.path default in legacy/app/config/schema.py**

Find the `"db.path"` entry (around line 499) and change its default:
```python
# Before
"default": "data/puzzle_pool.db",

# After
"default": "../data/puzzle_pool.db",
```

- [ ] **Step 3: Verify the change in sb3**

```bash
grep "DB_PATH" sb3/train_sb3.py
```

Expected: `DB_PATH    = "../data/puzzle_pool.db"`

- [ ] **Step 4: Verify the change in legacy**

```bash
grep "puzzle_pool" legacy/app/config/schema.py
```

Expected: `"default": "../data/puzzle_pool.db",`

---

## Task 6: Split requirements.txt

The root `requirements.txt` is split into two version-specific files; the root one is removed.

**Files:**
- Create: `legacy/requirements.txt`
- Create: `sb3/requirements.txt`
- Delete: `requirements.txt` (root)

- [ ] **Step 1: Create legacy/requirements.txt**

```bash
cat > legacy/requirements.txt << 'EOF'
torch>=2.0.0
numpy>=1.24.0
requests>=2.28.0
PyQt6>=6.4.0
keyboard>=0.13.5
PySocks>=1.7.1
playwright>=1.30.0
EOF
```

- [ ] **Step 2: Create sb3/requirements.txt**

```bash
cat > sb3/requirements.txt << 'EOF'
torch>=2.0.0
numpy>=1.24.0
stable-baselines3>=2.0.0
sb3-contrib>=2.0.0
gymnasium>=1.0.0
tensorboard>=2.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
EOF
```

- [ ] **Step 3: Remove root requirements.txt**

```bash
git rm requirements.txt
```

- [ ] **Step 4: Stage new requirements files**

```bash
git add legacy/requirements.txt sb3/requirements.txt
```

---

## Task 7: Smoke Test Both Versions

Verify imports work from each version's working directory before committing.

- [ ] **Step 1: Test sb3/ imports**

```bash
cd sb3 && python -c "
from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.rl.models.sudoku_ppo import SudokuMaskablePPO
from app.rl.curriculum.callback import CurriculumCallback
print('sb3 imports OK')
"
```

Expected: `sb3 imports OK`

- [ ] **Step 2: Test legacy/ imports**

```bash
cd ../legacy && python -c "
from app.config import config
from app.sudoku.env import SudokuEnv
from app.sudoku.teacher_engine import TeacherEngine
print('legacy imports OK')
"
```

Expected: `legacy imports OK`

- [ ] **Step 3: Verify sb3 DB path resolves**

```bash
cd ../sb3 && python -c "
import os; path = '../data/puzzle_pool.db'
print('DB exists:', os.path.exists(path))
"
```

Expected: `DB exists: True`

- [ ] **Step 4: Verify legacy DB path resolves**

```bash
cd ../legacy && python -c "
import os; path = '../data/puzzle_pool.db'
print('DB exists:', os.path.exists(path))
"
```

Expected: `DB exists: True`

---

## Task 8: Clean Up Root and Commit

Remove now-empty directories, clean up root, and commit.

- [ ] **Step 1: Remove empty app/ at root (if empty)**

```bash
cd ..
rmdir app/data app/gui app/config app/sudoku app/training app/web app 2>/dev/null && echo "app/ removed" || echo "app/ not empty — check contents"
```

- [ ] **Step 2: Remove empty models/ at root (if empty)**

```bash
rmdir models 2>/dev/null && echo "models/ removed" || echo "models/ has remaining files"
```

- [ ] **Step 3: Stage all changes and check status**

```bash
git add -A
git status
```

Verify: only changes inside `legacy/`, `sb3/`, `data/`, and removed root files.

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor: split project into legacy/ and sb3/ subfolders

- legacy/: archived main_train.py + PyQt6 GUI version (frozen)
- sb3/: active train_sb3.py + SB3 MaskablePPO version
- data/puzzle_pool.db shared at repo root; both versions use ../data/
- pool_db.py, teacher_engine.py, validator.py copied into both versions
- requirements.txt split per version"
```

---

## Verification Checklist

After the commit, confirm:

- [ ] `ls` at repo root shows only: `data/`, `legacy/`, `sb3/`, `CLAUDE.md`, `HISTORY.md`, `docs/`, `.git/`, `.gitattributes`
- [ ] `cd sb3 && python train_sb3.py --help` runs without ImportError
- [ ] `cd legacy && python -c "from app.config import config; print(config.get('db.path'))"` prints `../data/puzzle_pool.db`
- [ ] `git log --oneline -5` shows the split commit on top
