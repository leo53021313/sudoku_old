# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **重大變更紀錄**：查看 [HISTORY.md](HISTORY.md) 了解各版本的設計決策與 Bug Fix 背景。
> 若不確定某段邏輯為何這樣寫，HISTORY.md 是第一個查詢點。

## Overview

A reinforcement learning (PPO) agent that learns to solve Sudoku puzzles. Puzzles are fetched from websudoku.com via `requests` (no browser), stored in SQLite, and the agent trains using a curriculum that mixes MRV heuristic demonstrations with learned policy rollouts.

## Running

```bash
# Start training (fetches puzzles from websudoku.com + runs PPO loop)
python main_train.py

# Runtime hotkeys during training
# F8 = pause/resume, F9 = stop (also stops proxy validation thread), F10 = force model save
```

No package.json or requirements.txt. Dependencies: `torch` (CUDA), `requests`, `numpy`, `keyboard`.
Optional: `PySocks` for SOCKS proxy support. `playwright` retained for fallback only.

## Architecture

**Data flow:**
1. 20 producer threads fetch puzzles from `east.websudoku.com` via `requests` → `app/data/pool_db.py` (SQLite, WAL mode)
2. Main loop fetches puzzles from DB (all difficulties, natural curriculum) → creates `SudokuEnv` → runs episodes with agent
3. Agent collects 512-step rollouts → PPO update every rollout
4. Validated solutions written back to DB; model saved every N episodes

**Key files:**
- [main_train.py](main_train.py) — all hyperparameters (lines 27–130), training loop, hotkey controller, producer threads, `SUDOKU_LEVEL_DIST` for mixed-difficulty fetching
- [app/sudoku/env.py](app/sudoku/env.py) — `SudokuEnv`: 9×9 board, 8-channel observation, 729-action space (row×col×num), shaped reward system
- [app/sudoku/torch_agent.py](app/sudoku/torch_agent.py) — `SudokuPPONet` (cell embedding + ConstraintHead per row/col/box), `RolloutBuffer`, PPO+GAE update, behavior cloning loss, adaptive entropy
- [app/sudoku/agents.py](app/sudoku/agents.py) — `MRVAgent` (minimum remaining values heuristic, used as BC expert), `RandomAgent`
- [app/sudoku/validator.py](app/sudoku/validator.py) — validates completed boards against Sudoku rules
- [app/data/pool_db.py](app/data/pool_db.py) — thread-safe SQLite pool: puzzle locking, attempt tracking, solution storage
- [app/web/reader.py](app/web/reader.py) — `fetch_puzzle_via_requests()` (primary scraper), `WebSudokuReader` (Playwright fallback)
- [app/web/proxy_manager.py](app/web/proxy_manager.py) — downloads proxy lists, background validation with graceful stop via `stop_validation()`

**Observation space** (`env.py`): 8-channel 9×9 tensor — fixed cells, empty cells, row/col/box fill ratio, candidate counts, naked-single flags.

**Reward shaping** (tuned values in `env.py`): naked single +3.0, hidden single +1.5, unit complete +5.0, board done +15.0, dead-end −30.0, invalid −3.0.

**Curriculum**: MRV mixing ratio decays from 90% → 30% over 60,000 steps (`TORCH_MRV_MIX_PROB`, `TORCH_MRV_DECAY_STEPS`). Behavior cloning loss (`bc_coef`) trains the policy to imitate MRV decisions. Difficulty distribution: L1=60%, L2=30%, L3=10% during fetching; training pulls from all levels by DB sort order.

**Model**: `models/sudoku_policy_latest.pt` (PyTorch checkpoint). Puzzles: `data/puzzle_pool.db` (SQLite).

## Key Design Decisions

- **HTTP proxy priority**: Validated by actual page fetch (`puzzle_grid` check); SOCKS only TCP connect — HTTP proxies are more reliable and sorted first (`_PROTO_PRIORITY`).
- **Proxy stop on F9**: `run()` finally calls `proxy_manager.stop_validation()` before `_stop_event.set()`, ensuring the background validator exits within one iteration.
- **`PRINT_PRODUCER_SUCCESS_LOG = False`**: 20 producers inserting puzzles generates too much noise; set True only for debugging scraper issues.
- **`locked_by`/`locked_at`**: Informational only; `fetch_one_puzzle_for_training` selects by status, not lock state.
