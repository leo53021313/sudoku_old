import pytest


def test_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    from config import CrawlerConfig
    cfg = CrawlerConfig()
    assert cfg.num_workers == 10
    assert cfg.max_pool_size == 50_000
    assert cfg.resume_threshold == 30_000
    assert cfg.level_weights == [25, 25, 25, 25]
    assert cfg.min_delay == 0.0
    assert cfg.max_delay == 0.3
    assert cfg.request_timeout == 8
    assert cfg.proxy_validate_workers == 50
    assert cfg.proxy_validate_timeout == 3


def test_save_and_load(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    from config import CrawlerConfig
    cfg = CrawlerConfig(num_workers=5, max_pool_size=1000)
    cfg.save()
    assert (tmp_path / "data" / "config.json").exists()
    cfg2 = CrawlerConfig.load()
    assert cfg2.num_workers == 5
    assert cfg2.max_pool_size == 1000


def test_load_falls_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    from config import CrawlerConfig
    cfg = CrawlerConfig.load()
    assert cfg.num_workers == 10
