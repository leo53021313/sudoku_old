# app/config/manager.py
# -*- coding: utf-8 -*-
"""
Thread-safe 設定管理器。
- 讀取 schema 預設值，允許使用者透過 JSON 檔案覆蓋
- reload_required=False 的設定變更後立即呼叫已註冊的 callback
- 所有 get/set 操作皆加鎖，可安全跨執行緒呼叫
"""

import json
import os
import threading


class ConfigManager:

    def __init__(self, schema: dict, user_config_path: str) -> None:
        self._schema = schema
        self._path = user_config_path
        self._user: dict = {}
        self._callbacks: dict[str, list] = {}
        self._lock = threading.RLock()
        self._load()

    # ── 公開 API ──────────────────────────────────────────────────────

    def get(self, key: str):
        """取得設定值（使用者覆蓋 > schema 預設值）。"""
        with self._lock:
            if key in self._user:
                return self._user[key]
            if key in self._schema:
                return self._schema[key]["default"]
            raise KeyError(f"未知設定鍵: {key}")

    def set(self, key: str, value) -> bool:
        """
        設定新值並儲存。
        回傳 True = 即時生效（已觸發 callback），False = 需重啟訓練。
        """
        if key not in self._schema:
            raise KeyError(f"未知設定鍵: {key}")
        value = self._coerce(key, value)
        with self._lock:
            self._user[key] = value
            self._save()
        hot_reload = not self._schema[key]["reload_required"]
        if hot_reload:
            for cb in self._callbacks.get(key, []):
                try:
                    cb(value)
                except Exception:
                    pass
        return hot_reload

    def register_callback(self, key: str, cb) -> None:
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
            self._save()

    # ── 私有 ──────────────────────────────────────────────────────────

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
            except (json.JSONDecodeError, OSError):
                self._user = {}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._user, f, indent=2, ensure_ascii=False)
