# app/gui/event_bus.py
# -*- coding: utf-8 -*-
"""
訓練執行緒 → GUI 執行緒的單向事件匯流排。
訓練端只呼叫 bus.put()（非阻塞，佇列滿則靜默丟棄），
GUI 端以 QTimer 定期 drain()，全程不阻塞訓練。
"""

from queue import Queue, Full, Empty
from dataclasses import dataclass, field
import time


@dataclass
class GUIEvent:
    type: str
    data: dict
    ts: float = field(default_factory=time.time)


class EventBus:
    def __init__(self, maxsize: int = 2000):
        self._q: Queue = Queue(maxsize=maxsize)
        self.enabled: bool = True

    def put(self, etype: str, **data) -> None:
        if not self.enabled:
            return
        try:
            self._q.put_nowait(GUIEvent(type=etype, data=data))
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
