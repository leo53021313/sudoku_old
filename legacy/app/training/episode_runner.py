# app/training/episode_runner.py
# -*- coding: utf-8 -*-
# Runs a single training episode from a DB row.

import time
from typing import Any, Dict

import numpy as np

from app.config import config
from app.sudoku.env import SudokuEnv
from app.sudoku.validator import validate_completed_board
from app.data.pool_db import PuzzlePoolDB
from app.training.hotkey_controller import HOTKEY
import app.training.bus as _bus


# ── Board helpers ──────────────────────────────────────────────────────────

def count_empty_cells(board) -> int:
    return int(np.count_nonzero(np.asarray(board) == 0))


def is_board_complete(board) -> bool:
    return bool(np.all(np.asarray(board) != 0))


# ── Logging helpers ────────────────────────────────────────────────────────

def should_print_episode_result(ep: int) -> bool:
    n = config.get("logging.print_every_episodes")
    return n <= 1 or ep == 1 or ep % n == 0


def print_episode_result(s: dict) -> None:
    tag = (
        "success" if s["success"]
        else ("completed" if s["completed"] else s["stop_reason"])
    )
    print(
        f"[E{s['episode']:7d}] DB={s['puzzle_id']:5d} | try={s['tries']:3d} |"
        f" step={s['steps']:2d} | empty={s['empty_cells']:2d} |"
        f" reward={s['total_reward']:8.2f} | buf={s['buf_size']:4d} | {tag}"
    )


# ── Environment setup ──────────────────────────────────────────────────────

def create_env_from_db_row(row: dict):
    board = np.array(PuzzlePoolDB.string_to_board(row["puzzle"]), dtype=np.int8)
    fixed = board != 0
    env   = SudokuEnv(page=None, max_invalid=3)
    state = env.reset_from_board(board=board, fixed=fixed)
    return env, state, board.copy(), fixed.copy()


# ── Episode runner ─────────────────────────────────────────────────────────

def run_one_episode_from_db(
    db, row: dict, agent, episode_idx: int = 1
) -> Dict[str, Any]:
    env, state, base_board, base_fixed = create_env_from_db_row(row)

    if hasattr(agent, "start_episode"):
        agent.start_episode()

    total_reward  = 0.0
    step_count    = 0
    reward        = 0.0
    success       = False
    stop_reason   = None
    verify_status = None
    _committed    = False

    t0 = time.time()
    _last_board_push     = 0.0
    _board_push_interval = 1.0 / max(config.get("gui.board_fps"), 1)
    _max_steps           = config.get("run.max_steps_per_episode")

    while step_count < _max_steps:
        if HOTKEY.stop_requested:
            stop_reason = "stop_requested"
            break

        HOTKEY.wait_if_paused(agent=agent)
        if HOTKEY.stop_requested:
            stop_reason = "stop_requested"
            break

        action = agent.select_action(env, state)

        if action is None:
            stop_reason = "dead_end_no_legal_action"
            if hasattr(agent, "commit_step"):
                agent.commit_step(reward=config.get("training.dead_end_penalty"), done=True)
            _committed = True
            break

        next_state, reward, done, info = env.step(action)
        reward = float(reward)
        total_reward += reward

        if not info.get("valid", False):
            stop_reason = info.get("reason", "invalid_action")
            if hasattr(agent, "commit_step"):
                agent.commit_step(reward=reward, done=True)
            _committed = True
            break

        state      = next_state
        step_count += 1

        _now = time.monotonic()
        if _now - _last_board_push >= _board_push_interval:
            _last_board_push = _now
            r, c, _ = action
            _bus.gui_bus.put(
                "board_update",
                thread_id=0,
                board=state.tolist(),
                fixed=base_fixed.tolist(),
                highlight=(int(r), int(c)),
                episode_idx=episode_idx,
            )

        if done:
            stop_reason = info.get("reason", "env_done")
            if not is_board_complete(state):
                if hasattr(agent, "commit_step"):
                    agent.commit_step(reward=reward, done=True)
                _committed = True
            break

        if hasattr(agent, "commit_step"):
            agent.commit_step(reward=reward, done=False)

    elapsed   = time.time() - t0
    completed = is_board_complete(state)
    empty     = count_empty_cells(state)

    if completed and stop_reason != "stop_requested":
        vres = validate_completed_board(
            board=state, fixed=base_fixed, base_board=base_board
        )
        verify_status = vres["reason"]

        if vres["ok"]:
            success      = True
            _bonus       = config.get("training.success_bonus")
            final_reward = reward + _bonus
            total_reward += _bonus
            if hasattr(agent, "commit_step") and not _committed:
                agent.commit_step(reward=final_reward, done=True)
                _committed = True
        else:
            stop_reason = f"local_verify_fail:{vres['reason']}"
            if hasattr(agent, "commit_step") and not _committed:
                agent.commit_step(reward=reward, done=True)
                _committed = True

    if not _committed and stop_reason != "stop_requested":
        if hasattr(agent, "commit_step"):
            agent.commit_step(reward=reward, done=True)
        _committed = True

    if stop_reason is None or stop_reason == "env_done":
        stop_reason = (
            "success" if success
            else ("completed" if completed else "max_steps")
        )

    buf_size = agent.rollout_buf.size() if hasattr(agent, "rollout_buf") else 0

    summary = {
        "episode":        episode_idx,
        "puzzle_id":      int(row["id"]),
        "tries":          int(row["tries"]) + 1,
        "steps":          step_count,
        "total_reward":   total_reward,
        "completed":      completed,
        "success":        success,
        "stop_reason":    stop_reason,
        "verify_status":  verify_status,
        "empty_cells":    empty,
        "elapsed_sec":    round(elapsed, 3),
        "final_board":    state.copy(),
        "solution_steps": list(env.action_history),
        "base_board":     base_board.copy(),
        "base_fixed":     base_fixed.copy(),
        "run_mode":       config.get("run.mode"),
        "buf_size":       buf_size,
    }

    if config.get("logging.print_episode_result") and should_print_episode_result(episode_idx):
        print_episode_result(summary)

    if hasattr(agent, "finish_episode"):
        do_update = (config.get("run.mode") == "train") and (stop_reason != "stop_requested")
        agent.finish_episode(success=success, summary=summary, do_update=do_update)

    return summary
