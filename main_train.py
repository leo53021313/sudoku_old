# main_train.py v6 — Proxy 支援、背景爬蟲執行緒、多難度擴充
# -*- coding: utf-8 -*-

import json
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
from app.config import config

# GUI EventBus（gui.enabled=False 時用空殼替代，零效能開銷）
class _NullBus:
    def put(self, *_, **__): pass
gui_bus = _NullBus()

# 爬蟲統計計數器（供 GUI 定時查詢）
_producer_stats_lock = threading.Lock()
_producer_stats = {"ok": 0, "fail": 0, "blocked": 0}

def _producer_stats_inc(key: str) -> None:
    with _producer_stats_lock:
        _producer_stats[key] += 1


# ── 所有設定統一由 app/config/schema.py 管理，透過 config.get() 存取 ──


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
                    agent.save_model(config.get("model.path"))
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
    mode = config.get("run.mode")
    if mode == "train":
        return None if config.get("run.infinite_training") else config.get("run.train_episodes")
    if mode == "eval":
        return config.get("run.eval_episodes")
    raise ValueError(f"不支援 run.mode：{mode}")


def should_print_episode_result(ep):
    n = config.get("logging.print_every_episodes")
    return n <= 1 or ep == 1 or ep % n == 0


def log_web(msg):
    if config.get("logging.print_web_retry"):
        print(msg)


def log_pool(msg):
    if config.get("logging.print_pool"):
        print(msg)


def log_producer_success(msg):
    if config.get("logging.print_producer_success"):
        print(msg)


def _pick_level():
    """依 training.level_dist 權重隨機選取抓題難度。"""
    raw = config.get("training.level_dist")
    if isinstance(raw, str):
        dist = {int(k): v for k, v in json.loads(raw).items()}
    else:
        dist = raw
    levels  = list(dist.keys())
    weights = [dist[lv] for lv in levels]
    return random.choices(levels, weights=weights, k=1)[0]


def create_agent():
    agent_type = config.get("training.agent_type")
    if agent_type == "mrv":
        return MRVAgent(choose_mode="min")

    if agent_type == "torch":
        mode = (
            config.get("training.train_policy_mode")
            if config.get("run.mode") == "train"
            else config.get("training.eval_policy_mode")
        )
        model_path = config.get("model.path") if config.get("model.auto_load") else None
        return TorchAgent(
            device=config.get("training.device"),
            policy_mode=mode,
            lr=config.get("training.lr"),
            gamma=config.get("training.gamma"),
            gae_lambda=config.get("training.gae_lambda"),
            entropy_coef=config.get("training.entropy_init"),
            target_entropy=config.get("training.target_entropy"),
            adaptive_entropy=config.get("training.adaptive_entropy"),
            entropy_lr=config.get("training.entropy_lr"),
            min_entropy_coef=config.get("training.min_entropy_coef"),
            max_entropy_coef=config.get("training.max_entropy_coef"),
            value_coef=config.get("training.value_coef"),
            grad_clip=config.get("training.grad_clip"),
            ppo_clip_eps=config.get("training.ppo_clip"),
            ppo_epochs=config.get("training.ppo_epochs"),
            ppo_minibatch=config.get("training.ppo_minibatch"),
            rollout_steps=config.get("training.rollout_steps"),
            normalize_returns=config.get("training.normalize_returns"),
            cell_dim=config.get("training.cell_dim"),
            head_dim=config.get("training.head_dim"),
            use_fixed_channel=True,
            use_empty_channel=True,
            use_row_fill_channel=True,
            use_col_fill_channel=True,
            use_box_fill_channel=True,
            use_candidate_count_channel=True,
            use_single_candidate_channel=True,
            mrv_mix_prob=config.get("training.mrv_mix_prob"),
            mrv_decay_steps=config.get("training.mrv_decay_steps"),
            mrv_min_prob=config.get("training.mrv_min_prob"),
            bc_coef=config.get("training.bc_coef"),
            use_fp16=config.get("training.use_fp16"),
            model_path=model_path,
            reset_optimizer_on_load=config.get("model.reset_optimizer_on_load"),
            reset_counters_on_load=config.get("model.reset_counters_on_load"),
            print_update_log=config.get("logging.print_agent_update_log"),
            phase1_steps=config.get("training.phase1_steps"),
            phase2_steps=config.get("training.phase2_steps"),
            phase1_tau=config.get("training.phase1_tau"),
            phase2_tau=config.get("training.phase2_tau"),
            teacher_max_cand=config.get("training.teacher_max_cand"),
            policy_demo_capacity=config.get("training.policy_demo_capacity"),
            policy_demo_weight=config.get("training.policy_demo_weight"),
        )

    raise ValueError(f"不支援 training.agent_type：{agent_type}")


def validate_loaded_puzzle(board, fixed):
    b = np.asarray(board, dtype=np.int8)
    f = np.asarray(fixed, dtype=bool)
    if b.shape != (9, 9):
        raise RuntimeError(f"board shape 錯誤：{b.shape}")
    if f.shape != (9, 9):
        raise RuntimeError(f"fixed shape 錯誤：{f.shape}")
    givens = int(np.count_nonzero(b != 0))
    fc     = int(np.count_nonzero(f))
    if givens < config.get("crawler.min_expected_givens"):
        raise RuntimeError(f"givens 過少：{givens}")
    if givens > config.get("crawler.max_expected_givens"):
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
            if db.count_unsolved() >= config.get("crawler.max_pool_size"):
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
                    timeout=config.get("crawler.page_timeout_ms") // 1000,
                    debug=config.get("logging.producer_debug"),
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
                    + (f"\n{traceback.format_exc().strip()}" if config.get("logging.producer_debug") else "")
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
                timeout=random.uniform(
                    config.get("crawler.min_delay"),
                    config.get("crawler.max_delay"),
                )
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
    if not config.get("logging.print_rolling_stats"):
        return
    window = config.get("logging.rolling_stats_window")
    if len(all_results) < min(window, 5):
        return
    recent = all_results[-window:]
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
    _board_push_interval = 1.0 / max(config.get("gui.board_fps"), 1)
    _max_steps = config.get("run.max_steps_per_episode")

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
            _bonus = config.get("training.success_bonus")
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
        "run_mode":       config.get("run.mode"),
        "buf_size":       buf_size,
    }

    if config.get("logging.print_episode_result") and should_print_episode_result(episode_idx):
        print_episode_result(summary)

    if hasattr(agent, "finish_episode"):
        do_update = (config.get("run.mode") == "train") and (stop_reason != "stop_requested")
        agent.finish_episode(
            success=success,
            summary=summary,
            do_update=do_update,
        )

    return summary


def print_run_config():
    if not config.get("logging.print_run_config"):
        return
    raw = config.get("training.level_dist")
    dist = {int(k): v for k, v in json.loads(raw).items()} if isinstance(raw, str) else raw
    dist_str = " / ".join(f"L{lv}={w:.0%}" for lv, w in sorted(dist.items()))
    total = get_effective_episode_count()
    print("=" * 60)
    print("執行設定 v6（Proxy + 背景爬蟲 + 混合難度）")
    print("=" * 60)
    print(f"難度分布           : {dist_str}")
    print(f"模式               : {config.get('run.mode')}")
    print(f"Agent              : {config.get('training.agent_type')}")
    print(f"裝置               : {config.get('training.device')}")
    print(f"回合數             : {'無限' if total is None else total}")
    print(f"最大步數           : {config.get('run.max_steps_per_episode')}")
    print(f"題庫上限           : {config.get('crawler.max_pool_size')} 題（全難度合計）")
    print(f"Proxy 啟用         : {config.get('proxy.enabled')}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════════
# 主執行流程
# ═══════════════════════════════════════════════════════════════════

def run():
    global gui_bus
    if config.get("gui.enabled"):
        from app.gui.event_bus import bus as _real_bus
        gui_bus = _real_bus

    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True

    HOTKEY.install()
    print_run_config()
    os.makedirs(config.get("model.dir"), exist_ok=True)
    db = PuzzlePoolDB(config.get("db.path"))

    # ── 初始化 Proxy 管理器 ──────────────────────────────────────
    proxy_manager = None
    if config.get("proxy.enabled"):
        proxy_manager = ProxyManager()
        n = proxy_manager.download_all()
        if n == 0:
            print("[Proxy] 無可用代理，改用真實 IP 直連")
            proxy_manager = None
        elif config.get("proxy.validate"):
            _vc = config.get("proxy.validate_count")
            proxy_manager.start_background_validation(
                max_validate=None if _vc == -1 else _vc,
                max_workers=config.get("proxy.validate_workers"),
                timeout=config.get("proxy.validate_timeout"),
            )

    # ── 啟動背景爬蟲執行緒 ────────────────────────────────────────
    _producer_workers = config.get("crawler.producer_workers")
    _stop_event = threading.Event()
    _producer_threads = []
    for _wi in range(_producer_workers):
        _t = threading.Thread(
            target=_run_producer,
            args=(db, proxy_manager, _stop_event),
            daemon=True,
            name=f"Producer-{_wi}",
        )
        _t.start()
        _producer_threads.append(_t)
    log_pool(f"[main] {_producer_workers} 個爬蟲執行緒已啟動")

    # 等待初始題庫填充（最多 120 秒）
    _wait_deadline = time.time() + 120.0
    while (
        db.count_unsolved() < min(config.get("crawler.min_pool_size"), 5)
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
    _n_results     = 0    # 累計已完成的 episode 數（all_results 被 trim 後仍有效）
    _run_steps     = 0
    _run_reward    = 0.0
    _run_empty     = 0
    _run_completed = 0
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
                _mpath = config.get("model.path")
                try:
                    agent.save_model(_mpath)
                    print(f"[main] 手動儲存：{_mpath}")
                    gui_bus.put("model_saved", path=_mpath, episode_idx=episode_idx)
                except Exception as e:
                    print(f"[main] 儲存失敗：{e}")

            if total_episodes is not None and episode_idx >= total_episodes:
                break

            episode_idx += 1

            _max_tries = config.get("crawler.max_tries_per_puzzle")
            row = db.fetch_one_puzzle_for_training(
                worker_name=config.get("db.worker_name"),
                max_tries=_max_tries,
            )

            if row is None:
                log_pool("[trainer] 無可用題目，等待爬蟲補充...")
                time.sleep(1.0)
                episode_idx -= 1  # 不計入有效回合
                continue

            if int(row.get("tries", 0)) >= _max_tries:
                db.mark_puzzle_skipped(row["id"])
                episode_idx -= 1  # 跳過題目不計入有效回合
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
                    "run_mode":       config.get("run.mode"),
                    "buf_size":       0,
                }
                if hasattr(agent, "finish_episode"):
                    agent.finish_episode(
                        success=False,
                        summary=result,
                        do_update=(config.get("run.mode") == "train"),
                    )

            all_results.append(result)
            _n_results     += 1
            _run_steps     += result["steps"]
            _run_reward    += result["total_reward"]
            _run_empty     += result["empty_cells"]
            _run_completed += int(result["completed"])
            # 只保留最近一個 rolling window，防止長時間訓練時 numpy array 累積耗盡記憶體
            _win = config.get("logging.rolling_stats_window")
            if len(all_results) > _win:
                del all_results[:-_win]

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
                level=int(row.get("level", 0)),
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
                    and new_tries >= _max_tries
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

            if episode_idx % config.get("logging.print_every_episodes") == 0:
                if config.get("logging.print_rolling_stats"):
                    print_rolling_stats(all_results, episode_idx, db)
                if isinstance(agent, TorchAgent):
                    _mrv = agent._effective_mrv_prob() if hasattr(agent, "_effective_mrv_prob") else 0.0
                    _phase = (agent.phase_manager.phase if hasattr(agent, "phase_manager") else
                              (1 if _mrv > 0.40 else (2 if _mrv > 0.10 else 3)))
                    gui_bus.put(
                        "stats_update",
                        episode_idx=episode_idx,
                        total_episodes=total_episodes or 0,
                        update_count=agent.update_counter,
                        mrv_prob=_mrv,
                        entropy=agent.last_entropy_value,
                        loss=agent.last_loss_value,
                        rollout_size=agent.rollout_buf.size() if hasattr(agent, "rollout_buf") else 0,
                        rollout_cap=config.get("training.rollout_steps"),
                        phase=_phase,
                    )

            _save_interval = config.get("training.save_every_episodes")
            if (
                isinstance(agent, TorchAgent)
                and config.get("run.mode") == "train"
                and episode_idx % _save_interval == 0
            ):
                _mpath = config.get("model.path")
                agent.save_model(_mpath)
                gui_bus.put("model_saved", path=_mpath, episode_idx=episode_idx)

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
        print(f"{config.get('run.mode').upper()} 結束")
        print("=" * 60)
        n = _n_results
        if n > 0:
            avg_steps  = _run_steps / n
            avg_reward = _run_reward / n
            avg_empty  = _run_empty / n
            comp_rate  = _run_completed / n
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
            if config.get("run.mode") == "train":
                _final_path = config.get("model.path")
                try:
                    agent.save_model(_final_path)
                    print(f"最終模型   : {_final_path}")
                except Exception as e:
                    print(f"儲存失敗   : {e}")


if __name__ == "__main__":
    if config.get("gui.enabled"):
        # 訓練跑在背景執行緒，Qt GUI 跑在主執行緒（Qt 規定）
        _train_thread = threading.Thread(
            target=run, name="TrainingThread", daemon=True
        )
        _train_thread.start()
        from app.gui.training_gui import launch_gui
        launch_gui(hotkey=HOTKEY, max_boards=config.get("gui.max_boards"))
        # GUI 視窗關閉後，等訓練執行緒自然退出（最多 10 秒）
        _train_thread.join(timeout=10.0)
    else:
        run()
