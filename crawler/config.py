from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "data" / "config.json"


@dataclass
class CrawlerConfig:
    num_workers: int = 10
    max_pool_size: int = 50_000
    resume_threshold: int = 30_000
    level_weights: list = field(default_factory=lambda: [25, 25, 25, 25])
    min_delay: float = 0.0
    max_delay: float = 0.3
    request_timeout: int = 8
    proxy_validate_workers: int = 50
    proxy_validate_timeout: int = 3

    def save(self) -> None:
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> "CrawlerConfig":
        if not _CONFIG_PATH.exists():
            return cls()
        try:
            data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**valid)
        except Exception:
            return cls()
