# app/gui/event_bus.py
# -*- coding: utf-8 -*-
"""
訓練執行緒 → GUI 執行緒的單向事件匯流排。
訓練端只呼叫 bus.put()（非阻塞，佇列滿則靜默丟棄），
GUI 端以 QTimer 定期 drain()，全程不阻塞訓練。

Typed event dataclasses allow IDE autocomplete and catch key-name typos at
write-time. bus.put_event(typed_event) is the new preferred API; the legacy
bus.put(etype, **data) is preserved for backward compatibility.
"""

from queue import Queue, Full, Empty
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import time


@dataclass
class GUIEvent:
    type: str
    data: dict
    ts: float = field(default_factory=time.time)


# ── Typed event dataclasses ────────────────────────────────────────────────

@dataclass
class EpisodeStartEvent:
    episode_idx: int
    puzzle_id: int
    level: int
    board: List[List[int]]
    fixed: List[List[bool]]
    thread_id: int = 0


@dataclass
class BoardUpdateEvent:
    episode_idx: int
    board: List[List[int]]
    fixed: List[List[bool]]
    highlight: Optional[Tuple[int, int]] = None
    thread_id: int = 0


@dataclass
class EpisodeEndEvent:
    episode_idx: int
    success: bool
    steps: int
    total_reward: float
    board: List[List[int]]
    fixed: List[List[bool]]
    level: int
    thread_id: int = 0


@dataclass
class StatsUpdateEvent:
    episode_idx: int
    total_episodes: int
    update_count: int
    mrv_prob: float
    entropy: float
    loss: float
    rollout_size: int
    rollout_cap: int
    phase: int


@dataclass
class PoolUpdateEvent:
    unsolved: int
    total: int = 0


@dataclass
class ProxyUpdateEvent:
    valid: int
    total: int


@dataclass
class ProducerUpdateEvent:
    success_delta: int
    fail_delta: int
    blocked_delta: int


@dataclass
class StateChangeEvent:
    state: str  # "running" | "paused" | "stopped"


@dataclass
class ModelSavedEvent:
    path: str
    episode_idx: int


class EventBus:
    def __init__(self, maxsize: int = 2000):
        self._q: Queue = Queue(maxsize=maxsize)
        self.enabled: bool = True

    def put(self, etype: str, **data) -> None:
        """Legacy API: put(etype, key=value, ...). Prefer put_event() for new code."""
        if not self.enabled:
            return
        try:
            self._q.put_nowait(GUIEvent(type=etype, data=data))
        except Full:
            pass

    def put_event(self, event) -> None:
        """Typed API: put_event(EpisodeEndEvent(...)). Falls through to _dispatch()
        via isinstance() checks in the GUI. Existing dict-based callers unaffected."""
        if not self.enabled:
            return
        try:
            self._q.put_nowait(event)
        except Full:
            pass

    def drain(self, max_n: int = 80) -> list:
        events = []
        for _ in range(max_n):
            try:
                events.append(self._q.get_nowait())
            except Empty:
                break
        return events

    def clear(self) -> None:
        while True:
            try:
                self._q.get_nowait()
            except Empty:
                break


# 全域單例：訓練模組 import 這個 bus 並呼叫 put()
bus = EventBus()
