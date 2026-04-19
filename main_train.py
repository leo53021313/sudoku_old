# main_train.py v5 — Major RL Bug Fixes Applied
# -*- coding: utf-8 -*-
"""
main_train.py v5 — 修復大量強化學習底層嚴重 Bug
"""

import os
import time
import threading
import numpy as np
import torch

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.web.browser import BrowserManager
from app.sudoku.env import SudokuEnv
from app.sudoku.agents import MRVAgent
from app.sudoku.torch_agent import TorchAgent
from app.sudoku.validator import validate_completed_board
from app.data.pool_db import PuzzlePoolDB


# ═══════════════════════════════════════════════
# 執行設定
# ═══════════════════════════════════════════════

URL      = "https://www.websudoku.com/"
HEADLESS = True

RUN_MODE           = "train"
INFINITE_TRAINING  = True
TRAIN_EPISODES     = 300
EVAL_EPISODES      = 30

MAX_STEPS_PER_EPISODE = 100

DB_PATH                          = "data/puzzle_pool.db"
MIN_POOL_SIZE                    = 30
PRODUCER_FILL_PER_CALL           = 3
WORKER_NAME                      = "trainer_main"
MAX_TRIES_PER_PUZZLE_BEFORE_SKIP = 9_999_999_999

RELOAD_WAIT_MS          = 0
PAGE_GOTO_TIMEOUT_MS    = 8000
PAGE_RELOAD_TIMEOUT_MS  = 8000
RELOAD_RETRY_COUNT      = 3
RETRY_WAIT_MS           = 300
RESET_RETRY_COUNT       = 4
RESET_RETRY_WAIT_MS     = 300
PUZZLE_READY_TIMEOUT_MS = 6000
PUZZLE_READY_POLL_MS    = 150
MIN_EXPECTED_GIVENS     = 10
MAX_EXPECTED_GIVENS     = 60

PRINT_RUN_CONFIG      = True
PRINT_EPISODE_RESULT  = True
PRINT_EVERY_EPISODES  = 10
PRINT_ROLLING_STATS   = True
ROLLING_STATS_WINDOW  = 100
PRINT_AGENT_UPDATE_LOG= True
PRINT_WEB_RETRY_LOG   = True
PRINT_POOL_LOG        = True

AGENT_TYPE              = "torch"
TORCH_DEVICE            = "cuda"
TORCH_TRAIN_POLICY_MODE = "sample"
TORCH_EVAL_POLICY_MODE  = "greedy"

TORCH_LR            = 3e-4
TORCH_GAMMA         = 0.99
TORCH_GAE_LAMBDA    = 0.95
TORCH_VALUE_COEF    = 0.5
TORCH_GRAD_CLIP     = 0.5
TORCH_PPO_CLIP      = 0.2
TORCH_PPO_EPOCHS    = 10
TORCH_PPO_MINIBATCH = 64
TORCH_ROLLOUT_STEPS = 512

TORCH_ADAPTIVE_ENTROPY  = True
TORCH_TARGET_ENTROPY    = 0.5
TORCH_ENTROPY_INIT      = 0.05
TORCH_ENTROPY_LR        = 3e-4
TORCH_MIN_ENTROPY_COEF  = 0.001
TORCH_MAX_ENTROPY_COEF  = 1.0

TORCH_CELL_DIM = 128
TORCH_HEAD_DIM = 64
TORCH_USE_FP16 = True
TORCH_NORMALIZE_RETURNS = True

TORCH_MRV_MIX_PROB    = 0.9
TORCH_MRV_DECAY_STEPS = 60000  
TORCH_MRV_MIN_PROB    = 0.3     

MODEL_DIR  = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "sudoku_policy_latest.pt")
AUTO_LOAD_MODEL         = True
RESET_OPTIMIZER_ON_LOAD = False
RESET_COUNTERS_ON_LOAD  = False
SAVE_EVERY_EPISODES     = 100

SUCCESS_BONUS    = 100.0  
DEAD_END_PENALTY = 0.0    


class HotkeyController:
    def __init__(self):
        self.stop_requested  = False
        self.pause_requested = False
        self.save_requested  = False
        self.enabled = False
        self.backend = None

    def toggle_pause(self):
        self.pause_requested = not self.pause_requested
        print("\n[熱鍵] 暫停" if self.pause_requested else "\n[熱鍵] 繼續")

    def request_stop(self):
        self.stop_requested = True
        print("\n[熱鍵] 安全停止")

    def request_save(self):
        self.save_requested = True
        print("\n[熱鍵] 請求儲存")

    def install(self):
        try:
            import keyboard
            keyboard.add_hotkey("f8",  self.toggle_pause)
            keyboard.add_hotkey("f9",  self.request_stop)
            keyboard.add_hotkey("f10", self.request_save)
            self.enabled, self.backend = True, "keyboard"
            print("[熱鍵] F8=暫停, F9=停止, F10=儲存")
            return
        except Exception as e:
            print(f"[熱鍵] keyboard 失敗：{e}")
        try:
            import msvcrt
            def _poll():
                print("[熱鍵] msvcrt | P=暫停, Q=停止, S=儲存")
                while not self.stop_requested:
                    try:
                        if msvcrt.kbhit():
                            ch = msvcrt.getch()
                            if ch in (b"p",b"P"): self.toggle_pause()
                            elif ch in (b"q",b"Q"): self.request_stop()
                            elif ch in (b"s",b"S"): self.request_save()
                        else: time.sleep(0.05)
                    except: time.sleep(0.1)
            threading.Thread(target=_poll, daemon=True).start()
            self.enabled, self.backend = True, "msvcrt"
            return
        except Exception as e:
            print(f"[熱鍵] msvcrt 失敗：{e}")
        print("[熱鍵] 未啟用")

    def wait_if_paused(self, agent=None):
        while self.pause_requested and not self.stop_requested:
            if self.save_requested and isinstance(agent, TorchAgent):
                try:
                    agent.save_model(MODEL_PATH)
                    print("[熱鍵] 暫停中已儲存")
                except Exception as e:
                    print(f"[熱鍵] 儲存失敗：{e}")
                finally:
                    self.save_requested = False
            time.sleep(0.2)

    def consume_save_request(self):
        if self.save_requested:
            self.save_requested = False
            return True
        return False


HOTKEY = HotkeyController()

def count_empty_cells(board):  return int(np.count_nonzero(np.asarray(board) == 0))
def is_board_complete(board):  return bool(np.all(np.asarray(board) != 0))
def count_givens(board):       return int(np.count_nonzero(np.asarray(board) != 0))

def get_effective_episode_count():
    if RUN_MODE == "train": return None if INFINITE_TRAINING else TRAIN_EPISODES
    if RUN_MODE == "eval":  return EVAL_EPISODES
    raise ValueError(f"不支援 RUN_MODE：{RUN_MODE}")

def should_print_episode_result(ep):
    return PRINT_EVERY_EPISODES <= 1 or ep == 1 or ep % PRINT_EVERY_EPISODES == 0

def log_web(msg):
    if PRINT_WEB_RETRY_LOG: print(msg)

def log_pool(msg):
    if PRINT_POOL_LOG: print(msg)

def create_agent():
    if AGENT_TYPE == "mrv":
        return MRVAgent(choose_mode="min")

    if AGENT_TYPE == "torch":
        mode = TORCH_TRAIN_POLICY_MODE if RUN_MODE == "train" else TORCH_EVAL_POLICY_MODE
        return TorchAgent(
            device=TORCH_DEVICE,
            policy_mode=mode,
            lr=TORCH_LR,
            gamma=TORCH_GAMMA,
            gae_lambda=TORCH_GAE_LAMBDA,
            entropy_coef=TORCH_ENTROPY_INIT,
            target_entropy=TORCH_TARGET_ENTROPY,
            adaptive_entropy=TORCH_ADAPTIVE_ENTROPY,
            entropy_lr=TORCH_ENTROPY_LR,
            min_entropy_coef=TORCH_MIN_ENTROPY_COEF,
            max_entropy_coef=TORCH_MAX_ENTROPY_COEF,
            value_coef=TORCH_VALUE_COEF,
            grad_clip=TORCH_GRAD_CLIP,
            ppo_clip_eps=TORCH_PPO_CLIP,
            ppo_epochs=TORCH_PPO_EPOCHS,
            ppo_minibatch=TORCH_PPO_MINIBATCH,
            rollout_steps=TORCH_ROLLOUT_STEPS,
            normalize_returns=TORCH_NORMALIZE_RETURNS,
            cell_dim=TORCH_CELL_DIM,
            head_dim=TORCH_HEAD_DIM,
            use_fixed_channel=True,
            use_empty_channel=True,
            use_row_fill_channel=True,
            use_col_fill_channel=True,
            use_box_fill_channel=True,
            use_candidate_count_channel=True,
            use_single_candidate_channel=True,
            mrv_mix_prob=TORCH_MRV_MIX_PROB,
            mrv_decay_steps=TORCH_MRV_DECAY_STEPS,
            mrv_min_prob=TORCH_MRV_MIN_PROB,
            bc_coef=1.0,  # 開啟 Expert Behavior Cloning 權重
            use_fp16=TORCH_USE_FP16,
            model_path=MODEL_PATH if AUTO_LOAD_MODEL else None,
            reset_optimizer_on_load=RESET_OPTIMIZER_ON_LOAD,
            reset_counters_on_load=RESET_COUNTERS_ON_LOAD,
            print_update_log=PRINT_AGENT_UPDATE_LOG,
        )

    raise ValueError(f"不支援 AGENT_TYPE：{AGENT_TYPE}")


def _count_inputs(page):
    max_c = 0
    for sel in ["input[id^='f']","input[id*='f']","table input","form input"]:
        try: max_c = max(max_c, page.locator(sel).count())
        except: pass
    try:
        for frame in page.frames:
            for sel in ["input[id^='f']","table input"]:
                try: max_c = max(max_c, frame.locator(sel).count())
                except: pass
    except: pass
    return max_c

def wait_until_puzzle_ready(page, timeout_ms=PUZZLE_READY_TIMEOUT_MS):
    deadline = time.time() + timeout_ms / 1000.0
    last = 0
    while time.time() < deadline:
        try:
            n = _count_inputs(page)
            last = max(last, n)
            if n >= 20: return True
        except: pass
        try: page.wait_for_timeout(PUZZLE_READY_POLL_MS)
        except: time.sleep(PUZZLE_READY_POLL_MS / 1000.0)
    raise RuntimeError(f"puzzle grid 等待超時，最多 {last} input")

def safe_page_goto(page, url=URL):
    page.goto(url, wait_until="domcontentloaded", timeout=PAGE_GOTO_TIMEOUT_MS)
    if RELOAD_WAIT_MS > 0: page.wait_for_timeout(RELOAD_WAIT_MS)
    wait_until_puzzle_ready(page)
    return True

def safe_page_reload(page):
    page.reload(wait_until="domcontentloaded", timeout=PAGE_RELOAD_TIMEOUT_MS)
    if RELOAD_WAIT_MS > 0: page.wait_for_timeout(RELOAD_WAIT_MS)
    wait_until_puzzle_ready(page)
    return True

def reload_websudoku(page, url=URL):
    last_error = None
    for attempt in range(1, RELOAD_RETRY_COUNT + 1):
        try:
            safe_page_goto(page, url=url)
            return True
        except PlaywrightTimeoutError as e:
            last_error = e
            try:
                safe_page_reload(page)
                return True
            except Exception as e2: last_error = e2
        except Exception as e:
            last_error = e
            log_web(f"[web] 失敗 {attempt}/{RELOAD_RETRY_COUNT}：{e}")
            try:
                safe_page_reload(page)
                return True
            except Exception as e2: last_error = e2
        if RETRY_WAIT_MS > 0:
            try: page.wait_for_timeout(RETRY_WAIT_MS)
            except: time.sleep(RETRY_WAIT_MS / 1000.0)
    raise RuntimeError(f"websudoku 重載失敗：{last_error}")

def validate_loaded_puzzle(board, fixed):
    b = np.asarray(board, dtype=np.int8)
    f = np.asarray(fixed, dtype=bool)
    if b.shape != (9, 9): raise RuntimeError(f"board shape 錯誤：{b.shape}")
    if f.shape != (9, 9): raise RuntimeError(f"fixed shape 錯誤：{f.shape}")
    givens = int(np.count_nonzero(b != 0))
    fc     = int(np.count_nonzero(f))
    if givens < MIN_EXPECTED_GIVENS: raise RuntimeError(f"givens 過少：{givens}")
    if givens > MAX_EXPECTED_GIVENS: raise RuntimeError(f"givens 過多：{givens}")
    if fc <= 0:       raise RuntimeError("fixed_count=0，讀盤失敗")
    if fc != givens:  raise RuntimeError(f"givens={givens} vs fixed={fc} 不一致")
    return True

def reset_env_from_web_with_retry(page):
    last_error = None
    for attempt in range(1, RESET_RETRY_COUNT + 1):
        try:
            wait_until_puzzle_ready(page)
            env   = SudokuEnv(page=page, max_invalid=3)
            state = env.reset_from_web()
            fixed = env.fixed.copy()
            validate_loaded_puzzle(state, fixed)
            return env, state.copy(), fixed.copy()
        except Exception as e:
            last_error = e
            log_web(f"[reset] 失敗 {attempt}/{RESET_RETRY_COUNT}：{e}")
            try: safe_page_reload(page)
            except Exception as re: last_error = re
            if RESET_RETRY_WAIT_MS > 0:
                try: page.wait_for_timeout(RESET_RETRY_WAIT_MS)
                except: time.sleep(RESET_RETRY_WAIT_MS / 1000.0)
    raise RuntimeError(f"reset_from_web() 徹底失敗：{last_error}")

def producer_fill_pool(db, producer_page, fill_count=PRODUCER_FILL_PER_CALL):
    inserted = 0
    for _ in range(fill_count):
        if HOTKEY.stop_requested: break
        HOTKEY.wait_if_paused()
        try:
            reload_websudoku(producer_page, url=URL)
            _, board, fixed = reset_env_from_web_with_retry(producer_page)
            validate_loaded_puzzle(board, fixed)
            res = db.upsert_puzzle(board, source="websudoku")
            if res["inserted"]:
                inserted += 1
                log_pool(f"[producer] 新題 id={res['puzzle_id']} givens={count_givens(board)}")
        except Exception as e:
            pass
    return inserted

def create_env_from_db_row(row):
    board = np.array(PuzzlePoolDB.string_to_board(row["puzzle"]), dtype=np.int8)
    fixed = board != 0
    env   = SudokuEnv(page=None, max_invalid=3)
    state = env.reset_from_board(board=board, fixed=fixed)
    return env, state, board.copy(), fixed.copy()

def print_episode_result(s):
    tag = "success" if s["success"] else ("completed" if s["completed"] else s["stop_reason"])
    print(
        f"[E{s['episode']:7d}] DB={s['puzzle_id']:5d} | try={s['tries']:3d} | "
        f"step={s['steps']:2d} | empty={s['empty_cells']:2d} | "
        f"reward={s['total_reward']:8.2f} | buf={s['buf_size']:4d} | {tag}"
    )

def print_rolling_stats(all_results, episode_idx, db):
    if not PRINT_ROLLING_STATS: return
    if len(all_results) < min(ROLLING_STATS_WINDOW, 5): return
    recent = all_results[-ROLLING_STATS_WINDOW:]
    n  = len(recent)
    sr = sum(1 for r in recent if r["success"]) / n
    cr = sum(1 for r in recent if r["completed"]) / n
    avg_r = sum(r["total_reward"] for r in recent) / n
    avg_e = sum(r["empty_cells"] for r in recent) / n
    stats = db.get_pool_stats()
    print(
        f"[統計 ep={episode_idx}] "
        f"success={sr:.2%} complete={cr:.2%} "
        f"avg_reward={avg_r:.2f} avg_empty={avg_e:.2f} | "
        f"pool(total={stats['total']} solved={stats['solved_local']})"
    )

def run_one_episode_from_db(db, row, agent, episode_idx=1):
    env, state, base_board, base_fixed = create_env_from_db_row(row)

    if hasattr(agent, "start_episode"):
        agent.start_episode()

    total_reward  = 0.0
    step_count    = 0
    success       = False
    stop_reason   = None
    verify_status = None
    _committed    = False   

    t0 = time.time()

    while step_count < MAX_STEPS_PER_EPISODE:
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
                agent.commit_step(reward=DEAD_END_PENALTY, done=True)
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
        vres = validate_completed_board(board=state, fixed=base_fixed, base_board=base_board)
        verify_status = vres["reason"]

        if vres["ok"]:
            success = True
            final_reward = reward + SUCCESS_BONUS
            total_reward += SUCCESS_BONUS
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
            agent.commit_step(reward=reward if 'reward' in dir() else 0.0, done=True)
        _committed = True

    if stop_reason is None or stop_reason == "env_done":
        stop_reason = "success" if success else ("completed" if completed else "max_steps")

    buf_size = agent.rollout_buf.size() if hasattr(agent, "rollout_buf") else 0

    summary = {
        "episode":       episode_idx,
        "puzzle_id":     int(row["id"]),
        "tries":         int(row["tries"]) + 1,
        "steps":         step_count,
        "total_reward":  total_reward,
        "completed":     completed,
        "success":       success,
        "stop_reason":   stop_reason,
        "verify_status": verify_status,
        "empty_cells":   empty,
        "elapsed_sec":   round(elapsed, 3),
        "final_board":   state.copy(),
        "solution_steps": list(env.action_history),
        "base_board":    base_board.copy(),
        "base_fixed":    base_fixed.copy(),
        "run_mode":      RUN_MODE,
        "buf_size":      buf_size,
    }

    if PRINT_EPISODE_RESULT and should_print_episode_result(episode_idx):
        print_episode_result(summary)

    if hasattr(agent, "finish_episode"):
        do_update = (RUN_MODE == "train") and (stop_reason != "stop_requested")
        agent.finish_episode(
            success=success,
            summary=summary,
            do_update=do_update,
        )

    return summary

def print_run_config():
    if not PRINT_RUN_CONFIG: return
    total = get_effective_episode_count()
    print("=" * 60)
    print("執行設定 v5 (Massive RL Bug Fixes)")
    print("=" * 60)
    print(f"模式               : {RUN_MODE}")
    print(f"Agent              : {AGENT_TYPE}")
    print(f"裝置               : {TORCH_DEVICE}")
    print(f"回合數             : {'無限' if total is None else total}")
    print(f"最大步數           : {MAX_STEPS_PER_EPISODE}")
    print("=" * 60)
    print("★ 強力 Bug 修正已套用:")
    print("  [1] ★加入 Behavior Cloning (BC) Loss 解決 Agent 無法從 MRV 學習的問題")
    print("  [2] ★修正 Returns 歸一化與 Value 計算的嚴重維度/尺度不匹配")
    print("  [3] ★修正 Adaptive Entropy 梯度方向錯誤導致喪失探索能力的 Bug")
    print("=" * 60)

def run():
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True

    HOTKEY.install()
    print_run_config()

    os.makedirs(MODEL_DIR, exist_ok=True)
    db = PuzzlePoolDB(DB_PATH)

    all_results   =[]
    success_count = 0
    episode_idx   = 0
    total_episodes = get_effective_episode_count()

    with BrowserManager(headless=HEADLESS) as browser:
        producer_page = browser.goto(URL)
        agent = create_agent()

        current = db.count_unsolved(max_tries=MAX_TRIES_PER_PUZZLE_BEFORE_SKIP)
        if current < MIN_POOL_SIZE:
            loops = max(1, (MIN_POOL_SIZE - current + PRODUCER_FILL_PER_CALL - 1) // PRODUCER_FILL_PER_CALL)
            for _ in range(loops):
                if HOTKEY.stop_requested: break
                producer_fill_pool(db, producer_page)

        while True:
            if HOTKEY.stop_requested:
                print("[main] 收到停止要求...")
                break

            HOTKEY.wait_if_paused(agent=agent)
            if HOTKEY.stop_requested: break

            if HOTKEY.consume_save_request() and isinstance(agent, TorchAgent):
                try:
                    agent.save_model(MODEL_PATH)
                    print(f"[main] 手動儲存：{MODEL_PATH}")
                except Exception as e:
                    print(f"[main] 儲存失敗：{e}")

            if total_episodes is not None and episode_idx >= total_episodes:
                break

            episode_idx += 1

            if db.count_unsolved(max_tries=MAX_TRIES_PER_PUZZLE_BEFORE_SKIP) < MIN_POOL_SIZE:
                producer_fill_pool(db, producer_page)

            row = db.fetch_one_puzzle_for_training(
                worker_name=WORKER_NAME, max_tries=MAX_TRIES_PER_PUZZLE_BEFORE_SKIP)

            if row is None:
                log_pool("[trainer] 無可用題目，補題中...")
                producer_fill_pool(db, producer_page)
                row = db.fetch_one_puzzle_for_training(
                    worker_name=WORKER_NAME, max_tries=MAX_TRIES_PER_PUZZLE_BEFORE_SKIP)
                if row is None:
                    print("[trainer] 仍無題目，等待 1s...")
                    time.sleep(1.0)
                    continue

            if int(row.get("tries", 0)) >= MAX_TRIES_PER_PUZZLE_BEFORE_SKIP:
                db.mark_puzzle_skipped(row["id"])
                continue

            try:
                result = run_one_episode_from_db(
                    db=db, row=row, agent=agent, episode_idx=episode_idx)
            except Exception as e:
                print(f"[Episode {episode_idx}] 失敗：{e}")
                result = {
                    "episode": episode_idx, "puzzle_id": int(row["id"]),
                    "tries": int(row["tries"]) + 1, "steps": 0, "total_reward": 0.0,
                    "completed": False, "success": False, "stop_reason": "exception",
                    "verify_status": None, "empty_cells": 81, "elapsed_sec": 0.0,
                    "final_board": None, "solution_steps":[], "base_board": None,
                    "base_fixed": None, "run_mode": RUN_MODE, "buf_size": 0,
                }
                if hasattr(agent, "finish_episode"):
                    agent.finish_episode(success=False, summary=result, do_update=(RUN_MODE=="train"))

            all_results.append(result)

            if result["stop_reason"] != "stop_requested":
                db.mark_puzzle_attempt(
                    puzzle_id=result["puzzle_id"],
                    total_reward=result["total_reward"],
                    empty_cells=result["empty_cells"],
                    success=result["success"],
                )
                new_tries = int(row["tries"]) + 1
                if not result["success"] and new_tries >= MAX_TRIES_PER_PUZZLE_BEFORE_SKIP:
                    db.mark_puzzle_skipped(result["puzzle_id"])
                if result["success"] and result["final_board"] is not None:
                    success_count += 1
                    db.save_solution(
                        puzzle_id=result["puzzle_id"],
                        solved_board=result["final_board"],
                        solution_steps=result["solution_steps"],
                        verified_local=True,
                        verify_status=result["verify_status"],
                    )

            if PRINT_ROLLING_STATS and episode_idx % PRINT_EVERY_EPISODES == 0:
                print_rolling_stats(all_results, episode_idx, db)

            if isinstance(agent, TorchAgent) and RUN_MODE == "train":
                if episode_idx % SAVE_EVERY_EPISODES == 0:
                    agent.save_model(MODEL_PATH)

        print("\n" + "=" * 60)
        print(f"{RUN_MODE.upper()} 結束")
        print("=" * 60)
        n = len(all_results)
        if n > 0:
            avg_steps  = sum(r["steps"] for r in all_results) / n
            avg_reward = sum(r["total_reward"] for r in all_results) / n
            avg_empty  = sum(r["empty_cells"] for r in all_results) / n
            comp_rate  = sum(1 for r in all_results if r["completed"]) / n
            succ_rate  = success_count / n
        else:
            avg_steps = avg_reward = avg_empty = comp_rate = succ_rate = 0.0

        stats = db.get_pool_stats()
        print(f"總回合數   : {n}")
        print(f"成功率     : {succ_rate:.2%}")
        print(f"填滿率     : {comp_rate:.2%}")
        print(f"平均步數   : {avg_steps:.2f}")
        print(f"平均獎勵   : {avg_reward:.2f}")
        print(f"平均空格   : {avg_empty:.2f}")
        print(f"Pool stats : {stats}")

        if isinstance(agent, TorchAgent):
            print(f"更新次數   : {agent.update_counter}")
            print(f"最後 loss  : {agent.last_loss_value}")
            print(f"entropy_c  : {agent.entropy_coef:.5f}")
            if RUN_MODE == "train":
                try:
                    agent.save_model(MODEL_PATH)
                    print(f"最終模型   : {MODEL_PATH}")
                except Exception as e:
                    print(f"儲存失敗   : {e}")

if __name__ == "__main__":
    run()