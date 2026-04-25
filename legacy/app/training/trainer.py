# app/training/trainer.py
# -*- coding: utf-8 -*-
# Main training loop: episode management, rolling stats, periodic saves.

import json
import os
import threading
import time

import numpy as np
import torch

from app.config import config
from app.sudoku.agents import MRVAgent
from app.sudoku.torch_agent import TorchAgent
from app.data.pool_db import PuzzlePoolDB
from app.web.proxy_manager import ProxyManager
from app.training.hotkey_controller import HOTKEY
import app.training.bus as _bus
from app.training.bus import init_bus
from app.training.producer import run_producer, stats_snapshot_and_reset, pick_level
from app.training.episode_runner import run_one_episode_from_db


# ── Agent factory ──────────────────────────────────────────────────────────

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


def get_effective_episode_count():
    mode = config.get("run.mode")
    if mode == "train":
        return None if config.get("run.infinite_training") else config.get("run.train_episodes")
    if mode == "eval":
        return config.get("run.eval_episodes")
    raise ValueError(f"不支援 run.mode：{mode}")


# ── Rolling stats ──────────────────────────────────────────────────────────

def print_rolling_stats(recent: list, episode_idx: int, db) -> None:
    if not config.get("logging.print_rolling_stats"):
        return
    n = len(recent)
    if n == 0:
        return
    sr    = sum(1 for r in recent if r["success"]) / n
    cr    = sum(1 for r in recent if r["completed"]) / n
    avg_r = sum(r["total_reward"] for r in recent) / n
    avg_e = sum(r["empty_cells"] for r in recent) / n
    stats = db.get_pool_stats()
    print(
        f"[統計 ep={episode_idx}] "
        f"success={sr:.2%} complete={cr:.2%} "
        f"avg_reward={avg_r:.2f} avg_empty={avg_e:.2f} | "
        f"pool(total={stats['total']} solved={stats['solved_local']})"
    )


def print_run_config() -> None:
    if not config.get("logging.print_run_config"):
        return
    raw = config.get("training.level_dist")
    dist = {int(k): v for k, v in json.loads(raw).items()} if isinstance(raw, str) else raw
    dist_str   = " / ".join(f"L{lv}={w:.0%}" for lv, w in sorted(dist.items()))
    total      = get_effective_episode_count()
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


# ── Main training loop ─────────────────────────────────────────────────────

def run() -> None:
    if config.get("gui.enabled"):
        from app.gui.event_bus import bus as _real_bus
        init_bus(_real_bus)

    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True

    HOTKEY.install()
    print_run_config()
    os.makedirs(config.get("model.dir"), exist_ok=True)
    db = PuzzlePoolDB(config.get("db.path"))

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

    _producer_workers = config.get("crawler.producer_workers")
    _stop_event       = threading.Event()
    _producer_threads = []
    for _wi in range(_producer_workers):
        _t = threading.Thread(
            target=run_producer,
            args=(db, proxy_manager, _stop_event),
            daemon=True,
            name=f"Producer-{_wi}",
        )
        _t.start()
        _producer_threads.append(_t)

    _wait_deadline = time.time() + config.get("crawler.puzzle_ready_timeout_ms") / 1000.0
    _poll_secs     = config.get("crawler.puzzle_ready_poll_ms") / 1000.0
    while (
        db.count_unsolved() < min(config.get("crawler.min_pool_size"), 5)
        and time.time() < _wait_deadline
        and not HOTKEY.stop_requested
    ):
        print(f"[main] 等待初始題庫... 目前 {db.count_unsolved()} 題")
        time.sleep(_poll_secs)

    # Rolling results — protected by lock so GUI thread reads are safe
    _results_lock = threading.Lock()
    _win          = config.get("logging.rolling_stats_window")
    all_results   = []

    success_count  = 0
    episode_idx    = 0
    _n_results     = 0
    _run_steps     = 0
    _run_reward    = 0.0
    _run_empty     = 0
    _run_completed = 0
    total_episodes = get_effective_episode_count()
    agent          = create_agent()

    _gui_state     = "running"
    _last_periodic = time.time()
    _PERIODIC_SECS = 30.0
    _bus.gui_bus.put("state_change", state="running")
    _init_stats = db.get_pool_stats()
    _bus.gui_bus.put("pool_update", total=_init_stats.get("total", 0), unsolved=db.count_unsolved())
    if proxy_manager:
        _pm0 = proxy_manager.get_stats()
        _bus.gui_bus.put("proxy_update", valid=_pm0["valid"], total=_pm0["total"])

    try:
        while True:
            if HOTKEY.stop_requested:
                break

            if HOTKEY.pause_requested and _gui_state != "paused":
                _gui_state = "paused"
                _bus.gui_bus.put("state_change", state="paused")
            HOTKEY.wait_if_paused(agent=agent)
            if HOTKEY.stop_requested:
                break
            if _gui_state == "paused":
                _gui_state = "running"
                _bus.gui_bus.put("state_change", state="running")

            if HOTKEY.consume_save_request() and isinstance(agent, TorchAgent):
                _mpath = config.get("model.path")
                try:
                    agent.save_model(_mpath)
                    print(f"[main] 手動儲存：{_mpath}")
                    _bus.gui_bus.put("model_saved", path=_mpath, episode_idx=episode_idx)
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
                print("[trainer] 無可用題目，等待爬蟲補充...")
                time.sleep(1.0)
                episode_idx -= 1
                continue

            if int(row.get("tries", 0)) >= _max_tries:
                db.mark_puzzle_skipped(row["id"])
                episode_idx -= 1
                continue

            _ep_board = PuzzlePoolDB.string_to_board(row["puzzle"])
            _ep_fixed = (np.array(_ep_board, dtype=np.int8) != 0).tolist()
            _bus.gui_bus.put(
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

            with _results_lock:
                all_results.append(result)
                if len(all_results) > _win:
                    del all_results[:-_win]
                recent_snapshot = list(all_results)

            _n_results     += 1
            _run_steps     += result["steps"]
            _run_reward    += result["total_reward"]
            _run_empty     += result["empty_cells"]
            _run_completed += int(result["completed"])

            _raw_board = result.get("final_board")
            _raw_fixed = result.get("base_fixed")
            _end_board = (_raw_board.tolist() if hasattr(_raw_board, "tolist")
                          else (_raw_board or [[0]*9 for _ in range(9)]))
            _end_fixed = (_raw_fixed.tolist() if hasattr(_raw_fixed, "tolist")
                          else (_raw_fixed or [[False]*9 for _ in range(9)]))
            _bus.gui_bus.put(
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
                _bus.gui_bus.put("pool_update", unsolved=db.count_unsolved())
                db.mark_puzzle_attempt(
                    puzzle_id=result["puzzle_id"],
                    total_reward=result["total_reward"],
                    empty_cells=result["empty_cells"],
                    success=result["success"],
                )
                new_tries = int(row["tries"]) + 1
                if not result["success"] and new_tries >= _max_tries:
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
                print_rolling_stats(recent_snapshot, episode_idx, db)
                if isinstance(agent, TorchAgent):
                    _mrv   = agent._effective_mrv_prob() if hasattr(agent, "_effective_mrv_prob") else 0.0
                    _phase = (agent.phase_manager.phase if hasattr(agent, "phase_manager") else
                              (1 if _mrv > 0.40 else (2 if _mrv > 0.10 else 3)))
                    _bus.gui_bus.put(
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
                _bus.gui_bus.put("model_saved", path=_mpath, episode_idx=episode_idx)

            _now_t = time.time()
            if _now_t - _last_periodic >= _PERIODIC_SECS:
                _last_periodic = _now_t
                _ps = db.get_pool_stats()
                _bus.gui_bus.put("pool_update", total=_ps.get("total", 0), unsolved=db.count_unsolved())
                if proxy_manager:
                    _pm = proxy_manager.get_stats()
                    _bus.gui_bus.put("proxy_update", valid=_pm["valid"], total=_pm["total"])
                snap = stats_snapshot_and_reset()
                _bus.gui_bus.put(
                    "producer_update",
                    success_delta=snap["ok"],
                    fail_delta=snap["fail"],
                    blocked_delta=snap["blocked"],
                )

    finally:
        _bus.gui_bus.put("state_change", state="stopped")
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
            avg_steps  = _run_steps  / n
            avg_reward = _run_reward / n
            avg_empty  = _run_empty  / n
            comp_rate  = _run_completed / n
            succ_rate  = success_count  / n
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
