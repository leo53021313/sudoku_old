# app/config/manager.py
# -*- coding: utf-8 -*-
"""
Thread-safe 設定管理器。
- 讀取 schema 預設值，允許使用者透過 JSON 檔案覆蓋
- reload_required=False 的設定變更後立即呼叫已註冊的 callback
- 所有 get/set 操作皆加鎖，可安全跨執行緒呼叫
"""

from __future__ import annotations

import json
import logging
import os
import threading
from typing import Any, Callable


class ConfigManager:

    def __init__(self, schema: dict, user_config_path: str) -> None:
        self._schema = schema
        self._path = user_config_path
        self._user: dict = {}
        self._callbacks: dict[str, list] = {}
        self._lock = threading.RLock()
        self._load()

    # ── 公開 API ──────────────────────────────────────────────────────

    def get(self, key: str) -> Any:
        """取得設定值（使用者覆蓋 > schema 預設值）。"""
        with self._lock:
            if key in self._user:
                return self._user[key]
            if key in self._schema:
                return self._schema[key]["default"]
            raise KeyError(f"未知設定鍵: {key}")

    def set(self, key: str, value: Any) -> bool:
        """
        設定新值並儲存。
        回傳 True = 即時生效（已觸發 callback），False = 需重啟訓練。
        """
        if key not in self._schema:
            raise KeyError(f"未知設定鍵: {key}")
        value = self._coerce(key, value)
        self._validate(key, value)
        with self._lock:
            self._user[key] = value
            snapshot = dict(self._user)
        self._save(snapshot)  # I/O 在鎖外，避免 20 個 producer 執行緒造成串行等待
        hot_reload = not self._schema[key]["reload_required"]
        if hot_reload:
            for cb in self._callbacks.get(key, []):
                try:
                    cb(value)
                except Exception:
                    logging.warning("Hot-reload callback for %r raised:", key, exc_info=True)
        return hot_reload

    def register_callback(self, key: str, cb: Callable[[Any], None]) -> None:
        """為即時生效設定註冊 callback（reload_required=False 時才有意義）。"""
        self._callbacks.setdefault(key, []).append(cb)

    def schema(self) -> dict:
        return self._schema

    def get_schema_entry(self, key: str) -> dict:
        return self._schema[key]

    def all_keys(self) -> list[str]:
        return list(self._schema.keys())

    def reset_to_default(self, key: str) -> None:
        with self._lock:
            self._user.pop(key, None)
            snapshot = dict(self._user)
        self._save(snapshot)

    # ── 私有 ──────────────────────────────────────────────────────────

    def _validate(self, key: str, value: Any) -> None:
        """Raise ValueError if value violates schema constraints."""
        entry = self._schema.get(key, {})
        t = entry.get("type")
        if t in ("int", "float"):
            lo, hi = entry.get("min"), entry.get("max")
            if lo is not None and value < lo:
                raise ValueError(f"{key} 必須 >= {lo}，實際值 {value}")
            if hi is not None and value > hi:
                raise ValueError(f"{key} 必須 <= {hi}，實際值 {value}")
        if t == "str" and "options" in entry and value not in entry["options"]:
            raise ValueError(f"{key} 必須為 {entry['options']} 之一，實際值 {value!r}")
        if key.endswith("level_dist"):
            try:
                json.loads(value)
            except (json.JSONDecodeError, TypeError) as e:
                raise ValueError(f"{key} 必須為合法 JSON：{e}") from e

    def _coerce(self, key: str, value):
        """依照 schema type 做型別轉換。"""
        t = self._schema[key]["type"]
        if t == "int":
            return int(value)
        if t == "float":
            return float(value)
        if t == "bool":
            if isinstance(value, str):
                return value.lower() not in ("false", "0", "")
            return bool(value)
        return value  # str、dict 直接回傳

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._user = json.load(f)
            except json.JSONDecodeError as e:
                logging.warning("user_config.json 已損毀 (%s)；使用 schema 預設值。", e)
                self._user = {}
            except OSError:
                self._user = {}

    def _save(self, data: dict | None = None) -> None:
        if data is None:
            with self._lock:
                data = dict(self._user)
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self._path)
