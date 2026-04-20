# main_train.py v6 — Proxy 支援、背景爬蟲執行緒、多難度擴充
# -*- coding: utf-8 -*-

import os
import time
import random
import threading
import numpy as np
import torch

from app.web.proxy_manager import ProxyManager
from app.web.reader import (
    BlockedError, fetch_puzzle_via_requests, get_level_url,
)
from app.sudoku.env import SudokuEnv
from app.sudoku.agents import MRVAgent
from app.sudoku.torch_agent import TorchAgent
from app.sudoku.validator import validate_completed_board
from app.data.pool_db import PuzzlePoolDB

# GUI EventBus（GUI_ENABLED=False 時用空殼替代，零效能開銷）
if True:  # 延遲決定，等 GUI_ENABLED 在後面定義後再用
    class _NullBus:
        def put(self, *_, **__): pass
    gui_bus = _NullBus()

# 爬蟲統計計數器（供 GUI 定時查詢）
import threading as _threading
_producer_stats_lock = _threading.Lock()
_producer_stats = {"ok": 0, "fail": 0, "blocked": 0}

def _producer_stats_inc(key: str) -> None:
    with _producer_stats_lock:
        _producer_stats[key] += 1


# ═══════════════════════════════════════════════════════════════════
# 執行設定
# ═══════════════════════════════════════════════════════════════════

# ── 混合難度抓題比例（不含 4=evil，等模型穩定後再加入）──────────
# 爬蟲依此分布隨機選難度；訓練時從全難度池取題（自然課程）
SUDOKU_LEVEL_DIST = {1: 0.6, 2: 0.3, 3: 0.1}

HEADLESS = True

RUN_MODE          = "train"
INFINITE_TRAINING = True
TRAIN_EPISODES    = 300
EVAL_EPISODES     = 30

MAX_STEPS_PER_EPISODE = 100

DB_PATH     = "data/puzzle_pool.db"
WORKER_NAME = "trainer_main"

# ── 題庫容量控制 ─────────────────────────────────────────────────
# 背景爬蟲最多補到這個數量（僅計算目前難度的未解題目）
MAX_POOL_SIZE  = 50000
MIN_POOL_SIZE  = 30

MAX_TRIES_PER_PUZZLE_BEFORE_SKIP = 9_999_999_999

# ── Proxy 設定 ───────────────────────────────────────────────────
PROXY_ENABLED          = True  # 是否啟用 Proxy（False 則直連）
PROXY_MAX_ROTATIONS    = 10   # 單次抓題最多切換幾次 Proxy
PROXY_VALIDATE         = True  # 啟動時是否驗證並過濾死亡代理
PROXY_VALIDATE_COUNT   = None   # None = 驗證所有下載的代理
PROXY_VALIDATE_WORKERS = 100  # 並行驗證執行緒數
PROXY_VALIDATE_TIMEOUT = 3    # 每個 Proxy 驗證逾時（秒）

# ── 背景爬蟲設定 ─────────────────────────────────────────────────
# 平行爬蟲執行緒數（requests 版無瀏覽器開銷，可大幅增加）
PRODUCER_WORKERS = 20
# 每次成功抓題後的隨機等待秒數
PRODUCER_MIN_DELAY = 0.0
PRODUCER_MAX_DELAY = 0.3

# ── 頁面載入逾時設定（毫秒） ─────────────────────────────────────
PAGE_GOTO_TIMEOUT_MS    = 8000
PUZZLE_READY_TIMEOUT_MS = 6000
PUZZLE_READY_POLL_MS    = 150

MIN_EXPECTED_GIVENS = 10
MAX_EXPECTED_GIVENS = 60

# ── 日誌控制 ────────────────────────────────────────────────────
PRINT_RUN_CONFIG      = True
PRINT_EPISODE_RESULT  = True
PRINT_EVERY_EPISODES  = 10
PRINT_ROLLING_STATS   = True
ROLLING_STATS_WINDOW  = 100
PRINT_AGENT_UPDATE_LOG = True
PRINT_WEB_RETRY_LOG   = True
PRINT_POOL_LOG        = True

# True：爬蟲每步印出 HTTP 狀態碼、HTML 前300字、解析格子數，用於除錯
# 確認爬蟲正常後請改回 False 以減少日誌量
PRODUCER_DEBUG             = False
# True：每插入一道新題印一行（20個 worker 同時跑時很吵，預設關閉）
PRINT_PRODUCER_SUCCESS_LOG = False

# ── Agent 設定 ──────────────────────────────────────────────────
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

TORCH_ADAPTIVE_ENTROPY = True
TORCH_TARGET_ENTROPY   = 0.5
TORCH_ENTROPY_INIT     = 0.05
TORCH_ENTROPY_LR       = 3e-4
TORCH_MIN_ENTROPY_COEF = 0.001
TORCH_MAX_ENTROPY_COEF = 1.0

TORCH_CELL_DIM          = 128
TORCH_HEAD_DIM          = 64
TORCH_USE_FP16          = True
TORCH_NORMALIZE_RETURNS = True

TORCH_MRV_MIX_PROB    = 0.9
TORCH_MRV_DECAY_STEPS = 60000
TORCH_MRV_MIN_PROB    = 0.0

# ── 模型儲存 ─────────────────────────────────────────────────────
MODEL_DIR  = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "sudoku_policy_latest.pt")
AUTO_LOAD_MODEL         = True
RESET_OPTIMIZER_ON_LOAD = False
RESET_COUNTERS_ON_LOAD  = False
SAVE_EVERY_EPISODES     = 100

SUCCESS_BONUS    = 100.0
DEAD_END_PENALTY = 0.0

# ── GUI 設定 ─────────────────────────────────────────────────────────
GUI_ENABLED    = True   # False = 純 CLI，零開銷
GUI_MAX_BOARDS = 4      # 最多同時顯示幾個盤面（1→1x1, 4→2x2, 9→3x3）
GUI_BOARD_FPS  = 20     # 盤面即時更新最高 FPS（限流，避免 event bus 爆滿）


# ═══════════════════════════════════════════════════════════════════
# 熱鍵控制器
# ═══════════════════════════════════════════════════════════════════

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
                            if ch in (b"p", b"P"):
                                self.toggle_pause()
                            elif ch in (b"q", b"Q"):
                                self.request_stop()
                            elif ch in (b"s", b"S"):
                                self.request_save()
                        else:
                            time.sleep(0.05)
                    except Exception:
                        time.sleep(0.1)
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


# ═══════════════════════════════════════════════════════════════════
# 工具函式
# ═══════════════════════════════════════════════════════════════════

def count_empty_cells(board):
    return int(np.count_nonzero(np.asarray(board) == 0))


def is_board_complete(board):
    return bool(np.all(np.asarray(board) != 0))


def count_givens(board):
    return int(np.count_nonzero(np.asarray(board) != 0))


def get_effective_episode_count():
    if RUN_MODE == "train":
        return None if INFINITE_TRAINING else TRAIN_EPISODES
    if RUN_MODE == "eval":
        return EVAL_EPISODES
    raise ValueError(f"不支援 RUN_MODE：{RUN_MODE}")


def should_print_episode_result(ep):
    return PRINT_EVERY_EPISODES <= 1 or ep == 1 or ep % PRINT_EVERY_EPISODES == 0


def log_web(msg):
    if PRINT_WEB_RETRY_LOG:
        print(msg)


def log_pool(msg):
    if PRINT_POOL_LOG:
        print(msg)


def log_producer_success(msg):
    if PRINT_PRODUCER_SUCCESS_LOG:
        print(msg)


def _pick_level():
    """依 SUDOKU_LEVEL_DIST 權重隨機選取抓題難度。"""
    levels  = list(SUDOKU_LEVEL_DIST.keys())
    weights = [SUDOKU_LEVEL_DIST[lv] for lv in levels]
    return random.choices(levels, weights=weights, k=1)[0]


def create_agent():
    if AGENT_TYPE == "mrv":
        return MRVAgent(choose_mode="min")

    if AGENT_TYPE == "torch":
        mode = (
            TORCH_TRAIN_POLICY_MODE if RUN_MODE == "train"
            else TORCH_EVAL_POLICY_MODE
        )
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
            bc_coef=1.0,
            use_fp16=TORCH_USE_FP16,
            model_path=MODEL_PATH if AUTO_LOAD_MODEL else None,
            reset_optimizer_on_load=RESET_OPTIMIZER_ON_LOAD,
            reset_counters_on_load=RESET_COUNTERS_ON_LOAD,
            print_update_log=PRINT_AGENT_UPDATE_LOG,
        )

    raise ValueError(f"不支援 AGENT_TYPE：{AGENT_TYPE}")


def validate_loaded_puzzle(board, fixed):
    b = np.asarray(board, dtype=np.int8)
    f = np.asarray(fixed, dtype=bool)
    if b.shape != (9, 9):
        raise RuntimeError(f"board shape 錯誤：{b.shape}")
    if f.shape != (9, 9):
        raise RuntimeError(f"fixed shape 錯誤：{f.shape}")
    givens = int(np.count_nonzero(b != 0))
    fc     = int(np.count_nonzero(f))
    if givens < MIN_EXPECTED_GIVENS:
        raise RuntimeError(f"givens 過少：{givens}")
    if givens > MAX_EXPECTED_GIVENS:
        raise RuntimeError(f"givens 過多：{givens}")
    if fc <= 0:
        raise RuntimeError("fixed_count=0，讀盤失敗")
    if fc != givens:
        raise RuntimeError(f"givens={givens} vs fixed={fc} 不一致")
    return True


# ═══════════════════════════════════════════════════════════════════
# 背景爬蟲執行緒
# ═══════════════════════════════════════════════════════════════════

def _run_producer(db, proxy_manager, stop_event):
    """
    背景爬蟲：用 requests 直接抓取 east.websudoku.com HTML，不需瀏覽器。
    每次請求即得到一道隨機新題，比 Playwright 快 5-10 倍。
    """
    import traceback
    name = threading.current_thread().name
    log_pool(f"[{name}] 執行緒啟動（requests 模式）")

    while not stop_event.is_set() and not HOTKEY.stop_requested:
        try:
            if db.count_unsolved() >= MAX_POOL_SIZE:
                stop_event.wait(timeout=30.0)
                continue

            level     = _pick_level()
            fetch_url = get_level_url(level)

            # 原子性取得 proxy（每次呼叫自動輪換，確保各 worker 取得不同 IP）
            proxy_dict = None
            server_url = None
            if proxy_manager:
                pw = proxy_manager.get_playwright_proxy()
                if pw:
                    server_url = pw["server"]
                    proxy_dict = {"http": server_url, "https": server_url}

            try:
                board, fixed = fetch_puzzle_via_requests(
                    fetch_url,
                    proxy_dict=proxy_dict,
                    timeout=PAGE_GOTO_TIMEOUT_MS // 1000,
                    debug=PRODUCER_DEBUG,
                )
                validate_loaded_puzzle(board, fixed)

            except BlockedError:
                log_pool(f"[{name}] IP 封鎖，切換 Proxy")
                _producer_stats_inc("blocked")
                stop_event.wait(timeout=2.0)
                continue

            except ValueError as e:
                # 代理回傳非題目頁面（0 格）→ 永久移出池
                if proxy_manager and server_url:
                    proxy_manager.blacklist_server(server_url)
                log_web(f"[{name}] 解析失敗，已移除代理：{e}")
                _producer_stats_inc("fail")
                stop_event.wait(timeout=0.5)
                continue

            except Exception as e:
                log_web(
                    f"[{name}] 抓取失敗（{type(e).__name__}: {e}）"
                    + (f"\n{traceback.format_exc().strip()}" if PRODUCER_DEBUG else "")
                )
                _producer_stats_inc("fail")
                stop_event.wait(timeout=1.0)
                continue

            res = db.upsert_puzzle(board, source="websudoku", level=level)
            if res["inserted"]:
                _producer_stats_inc("ok")
                log_producer_success(
                    f"[{name}] 新題 id={res['puzzle_id']}"
                    f" L{level} givens={count_givens(board)}"
                )

            stop_event.wait(
                timeout=random.uniform(PRODUCER_MIN_DELAY, PRODUCER_MAX_DELAY)
            )

        except Exception as e:
            log_pool(f"[{name}] 未預期例外：{type(e).__name__}: {e}")
            stop_event.wait(timeout=5.0)

    log_pool(f"[{name}] 執行緒結束")


# ═══════════════════════════════════════════════════════════════════
# 訓練輔助函式
# ═══════════════════════════════════════════════════════════════════

def create_env_from_db_row(row):
    board = np.array(PuzzlePoolDB.string_to_board(row["puzzle"]), dtype=np.int8)
    fixed = board != 0
    env   = SudokuEnv(page=None, max_invalid=3)
    state = env.reset_from_board(board=board, fixed=fixed)
    return env, state, board.copy(), fixed.copy()


def print_episode_result(s):
    tag = (
        "success" if s["success"]
        else ("completed" if s["completed"] else s["stop_reason"])
    )
    print(
        f"[E{s['episode']:7d}] DB={s['puzzle_id']:5d} | try={s['tries']:3d} |"
        f" step={s['steps']:2d} | empty={s['empty_cells']:2d} |"
        f" reward={s['total_reward']:8.2f} | buf={s['buf_size']:4d} | {tag}"
    )


def print_rolling_stats(all_results, episode_idx, db):
    if not PRINT_ROLLING_STATS:
        return
    if len(all_results) < min(ROLLING_STATS_WINDOW, 5):
        return
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
    _last_board_push = 0.0
    _board_push_interval = 1.0 / max(GUI_BOARD_FPS, 1)

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

        # GUI 盤面即時更新（限流）
        _now = time.monotonic()
        if _now - _last_board_push >= _board_push_interval:
            _last_board_push = _now
            r, c, _ = action
            gui_bus.put(
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
            agent.commit_step(
                reward=reward if "reward" in locals() else 0.0, done=True
            )
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
        "run_mode":       RUN_MODE,
        "buf_size":       buf_size,
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
    if not PRINT_RUN_CONFIG:
        return
    dist_str = " / ".join(
        f"L{lv}={w:.0%}" for lv, w in sorted(SUDOKU_LEVEL_DIST.items())
    )
    total = get_effective_episode_count()
    print("=" * 60)
    print("執行設定 v6（Proxy + 背景爬蟲 + 混合難度）")
    print("=" * 60)
    print(f"難度分布           : {dist_str}")
    print(f"模式               : {RUN_MODE}")
    print(f"Agent              : {AGENT_TYPE}")
    print(f"裝置               : {TORCH_DEVICE}")
    print(f"回合數             : {'無限' if total is None else total}")
    print(f"最大步數           : {MAX_STEPS_PER_EPISODE}")
    print(f"題庫上限           : {MAX_POOL_SIZE} 題（全難度合計）")
    print(f"Proxy 啟用         : {PROXY_ENABLED}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════════
# 主執行流程
# ═══════════════════════════════════════════════════════════════════

def run():
    # 依 GUI_ENABLED 決定是否啟用真實 EventBus
    global gui_bus
    if GUI_ENABLED:
        from app.gui.event_bus import bus as _real_bus
        gui_bus = _real_bus

    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True

    HOTKEY.install()
    print_run_config()
    os.makedirs(MODEL_DIR, exist_ok=True)
    db = PuzzlePoolDB(DB_PATH)

    # ── 初始化 Proxy 管理器 ──────────────────────────────────────
    proxy_manager = None
    if PROXY_ENABLED:
        proxy_manager = ProxyManager()
        n = proxy_manager.download_all()
        if n == 0:
            print("[Proxy] 無可用代理，改用真實 IP 直連")
            proxy_manager = None
        elif PROXY_VALIDATE:
            # 背景驗證：立即返回，爬蟲先以直連啟動，代理逐漸上線後自動使用
            proxy_manager.start_background_validation(
                max_validate=PROXY_VALIDATE_COUNT,
                max_workers=PROXY_VALIDATE_WORKERS,
                timeout=PROXY_VALIDATE_TIMEOUT,
            )

    # ── 啟動背景爬蟲執行緒（多個並行，每個各有獨立 browser）──────
    # daemon=True：主程式結束時執行緒自動終止
    _stop_event = threading.Event()
    _producer_threads = []
    for _wi in range(PRODUCER_WORKERS):
        _t = threading.Thread(
            target=_run_producer,
            args=(db, proxy_manager, _stop_event),
            daemon=True,
            name=f"Producer-{_wi}",
        )
        _t.start()
        _producer_threads.append(_t)
    log_pool(f"[main] {PRODUCER_WORKERS} 個爬蟲執行緒已啟動")

    # 等待初始題庫填充（最多 120 秒）
    _wait_deadline = time.time() + 120.0
    while (
        db.count_unsolved() < min(MIN_POOL_SIZE, 5)
        and time.time() < _wait_deadline
        and not HOTKEY.stop_requested
    ):
        cnt = db.count_unsolved()
        log_pool(f"[main] 等待初始題庫... 目前 {cnt} 題")
        time.sleep(3.0)

    # ── 訓練主迴圈 ───────────────────────────────────────────────
    all_results    = []
    success_count  = 0
    episode_idx    = 0
    total_episodes = get_effective_episode_count()
    agent          = create_agent()

    _gui_state        = "running"
    _last_periodic    = time.time()
    _PERIODIC_SECS    = 30.0
    gui_bus.put("state_change", state="running")
    # 初始資料推送
    _init_stats = db.get_pool_stats()
    gui_bus.put("pool_update", total=_init_stats.get("total", 0), unsolved=db.count_unsolved())
    if proxy_manager:
        _pm0 = proxy_manager.get_stats()
        gui_bus.put("proxy_update", valid=_pm0["valid"], total=_pm0["total"])

    try:
        while True:
            if HOTKEY.stop_requested:
                print("[main] 收到停止要求...")
                break

            # GUI 暫停/繼續狀態同步
            if HOTKEY.pause_requested and _gui_state != "paused":
                _gui_state = "paused"
                gui_bus.put("state_change", state="paused")
            HOTKEY.wait_if_paused(agent=agent)
            if HOTKEY.stop_requested:
                break
            if _gui_state == "paused":
                _gui_state = "running"
                gui_bus.put("state_change", state="running")

            if HOTKEY.consume_save_request() and isinstance(agent, TorchAgent):
                try:
                    agent.save_model(MODEL_PATH)
                    print(f"[main] 手動儲存：{MODEL_PATH}")
                    gui_bus.put("model_saved", path=MODEL_PATH, episode_idx=episode_idx)
                except Exception as e:
                    print(f"[main] 儲存失敗：{e}")

            if total_episodes is not None and episode_idx >= total_episodes:
                break

            episode_idx += 1

            row = db.fetch_one_puzzle_for_training(
                worker_name=WORKER_NAME,
                max_tries=MAX_TRIES_PER_PUZZLE_BEFORE_SKIP,
            )

            if row is None:
                log_pool("[trainer] 無可用題目，等待爬蟲補充...")
                time.sleep(1.0)
                episode_idx -= 1  # 不計入有效回合
                continue

            if int(row.get("tries", 0)) >= MAX_TRIES_PER_PUZZLE_BEFORE_SKIP:
                db.mark_puzzle_skipped(row["id"])
                continue

            # GUI：新 episode 開始
            _ep_board = PuzzlePoolDB.string_to_board(row["puzzle"])
            _ep_fixed = (np.array(_ep_board, dtype=np.int8) != 0).tolist()
            gui_bus.put(
                "episode_start",
                thread_id=0,
                episode_idx=episode_idx,
                puzzle_id=int(row["id"]),
                level=int(row.get("level", 0)),
                board=_ep_board,
                fixed=_ep_fixed,
            )

            try:
                result = run_one_episode_from_db(
                    db=db, row=row, agent=agent, episode_idx=episode_idx
                )
            except Exception as e:
                print(f"[Episode {episode_idx}] 失敗：{e}")
                result = {
                    "episode":        episode_idx,
                    "puzzle_id":      int(row["id"]),
                    "tries":          int(row["tries"]) + 1,
                    "steps":          0,
                    "total_reward":   0.0,
                    "completed":      False,
                    "success":        False,
                    "stop_reason":    "exception",
                    "verify_status":  None,
                    "empty_cells":    81,
                    "elapsed_sec":    0.0,
                    "final_board":    None,
                    "solution_steps": [],
                    "base_board":     None,
                    "base_fixed":     None,
                    "run_mode":       RUN_MODE,
                    "buf_size":       0,
                }
                if hasattr(agent, "finish_episode"):
                    agent.finish_episode(
                        success=False,
                        summary=result,
                        do_update=(RUN_MODE == "train"),
                    )

            all_results.append(result)

            # GUI：episode 結束
            _raw_board = result.get("final_board")
            _raw_fixed = result.get("base_fixed")
            _end_board = _raw_board.tolist() if hasattr(_raw_board, "tolist") else (_raw_board or [[0]*9]*9)
            _end_fixed = _raw_fixed.tolist() if hasattr(_raw_fixed, "tolist") else (_raw_fixed or [[False]*9]*9)
            gui_bus.put(
                "episode_end",
                thread_id=0,
                episode_idx=episode_idx,
                success=result["success"],
                steps=result["steps"],
                total_reward=result["total_reward"],
                board=_end_board,
                fixed=_end_fixed,
            )

            if result["stop_reason"] != "stop_requested":
                # 每回合更新題庫數（輕量查詢，不走 get_pool_stats）
                gui_bus.put("pool_update", unsolved=db.count_unsolved())
                db.mark_puzzle_attempt(
                    puzzle_id=result["puzzle_id"],
                    total_reward=result["total_reward"],
                    empty_cells=result["empty_cells"],
                    success=result["success"],
                )
                new_tries = int(row["tries"]) + 1
                if (
                    not result["success"]
                    and new_tries >= MAX_TRIES_PER_PUZZLE_BEFORE_SKIP
                ):
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

            if (
                PRINT_ROLLING_STATS
                and episode_idx % PRINT_EVERY_EPISODES == 0
            ):
                print_rolling_stats(all_results, episode_idx, db)
                # GUI stats 更新
                if isinstance(agent, TorchAgent):
                    gui_bus.put(
                        "stats_update",
                        episode_idx=episode_idx,
                        total_episodes=total_episodes or 0,
                        update_count=agent.update_counter,
                        mrv_prob=agent._effective_mrv_prob() if hasattr(agent, "_effective_mrv_prob") else 0.0,
                        entropy=getattr(agent, "last_entropy_value", 0.0),
                        loss=getattr(agent, "last_loss_value", 0.0),
                        rollout_size=agent.rollout_buf.size() if hasattr(agent, "rollout_buf") else 0,
                        rollout_cap=TORCH_ROLLOUT_STEPS,
                    )

            if (
                isinstance(agent, TorchAgent)
                and RUN_MODE == "train"
                and episode_idx % SAVE_EVERY_EPISODES == 0
            ):
                agent.save_model(MODEL_PATH)
                gui_bus.put("model_saved", path=MODEL_PATH, episode_idx=episode_idx)

            # 定時推送爬蟲 / 題庫 / proxy 狀態（每 30 秒）
            _now_t = time.time()
            if _now_t - _last_periodic >= _PERIODIC_SECS:
                _last_periodic = _now_t
                _ps = db.get_pool_stats()
                gui_bus.put(
                    "pool_update",
                    total=_ps.get("total", 0),
                    unsolved=db.count_unsolved(),
                )
                if proxy_manager:
                    _pm = proxy_manager.get_stats()
                    gui_bus.put(
                        "proxy_update",
                        valid=_pm["valid"],
                        total=_pm["total"],
                    )
                with _producer_stats_lock:
                    gui_bus.put(
                        "producer_update",
                        success_delta=_producer_stats["ok"],
                        fail_delta=_producer_stats["fail"],
                        blocked_delta=_producer_stats["blocked"],
                    )
                    _producer_stats.update({"ok": 0, "fail": 0, "blocked": 0})

    finally:
        gui_bus.put("state_change", state="stopped")
        # 中止背景驗證、通知所有爬蟲執行緒結束並等待
        if proxy_manager:
            proxy_manager.stop_validation()
        _stop_event.set()
        for _t in _producer_threads:
            _t.join(timeout=5.0)

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
    if GUI_ENABLED:
        # 訓練跑在背景執行緒，Qt GUI 跑在主執行緒（Qt 規定）
        _train_thread = threading.Thread(
            target=run, name="TrainingThread", daemon=True
        )
        _train_thread.start()
        from app.gui.training_gui import launch_gui
        launch_gui(hotkey=HOTKEY, max_boards=GUI_MAX_BOARDS)
        # GUI 視窗關閉後，等訓練執行緒自然退出（最多 10 秒）
        _train_thread.join(timeout=10.0)
    else:
        run()
