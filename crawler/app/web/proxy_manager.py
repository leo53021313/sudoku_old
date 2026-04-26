# app/web/proxy_manager.py
# -*- coding: utf-8 -*-

import random
import socket
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request

# ── Proxy 來源清單 ────────────────────────────────────────────────────────
_BASE_PROXIFLY = (
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main"
    "/proxies/protocols"
)
_BASE_SPEEDX = "https://raw.githubusercontent.com/TheSpeedX"

PROXY_SOURCES = [
    ("http",   f"{_BASE_PROXIFLY}/http/data.txt"),
    ("socks5", f"{_BASE_PROXIFLY}/socks5/data.txt"),
    ("socks4", f"{_BASE_PROXIFLY}/socks4/data.txt"),
    ("http",   f"{_BASE_SPEEDX}/PROXY-List/master/http.txt"),
    ("socks5", f"{_BASE_SPEEDX}/PROXY-List/master/socks5.txt"),
    ("socks4", f"{_BASE_SPEEDX}/SOCKS-List/master/socks4.txt"),
]

# HTTP 代理驗證最嚴格（實際確認能取到題目頁），優先放入輪換池
_PROTO_PRIORITY = {"http": 0, "socks5": 1, "socks4": 2}

# 驗證時實際測試的目標（與爬蟲目標一致，確保代理真的能連到該網站）
_VALIDATE_URL = "http://east.websudoku.com/?level=1"
# 回應中必須出現的特徵字串，確認拿到的是正確頁面而非錯誤頁
_VALIDATE_MARKER = "puzzle_grid"


def _test_one_proxy(p, timeout):
    """
    測試單一 Proxy 是否能成功抓取 websudoku.com 的題目頁面。
    - HTTP  proxy：透過代理發 HTTP 請求，並確認回應含 puzzle_grid
    - SOCKS proxy：TCP 連線確認端口開通（urllib 不原生支援 SOCKS）
    回傳 True 表示可用。
    """
    proto = p["protocol"]
    addr = p["address"]

    try:
        if proto == "http":
            proxy_url = f"http://{addr}"
            handler = urllib.request.ProxyHandler({
                "http":  proxy_url,
                "https": proxy_url,
            })
            opener = urllib.request.build_opener(handler)
            opener.addheaders = [("User-Agent", "Mozilla/5.0")]
            with opener.open(_VALIDATE_URL, timeout=timeout) as resp:
                if resp.status >= 400:
                    return False
                # 只讀前 8 KB，確認頁面內含 puzzle_grid
                chunk = resp.read(8192).decode("utf-8", errors="ignore")
                return _VALIDATE_MARKER in chunk
        else:
            # SOCKS4/5：urllib 不原生支援，改用 TCP socket 確認端口
            host, port_str = addr.rsplit(":", 1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port_str)))
            sock.close()
            return result == 0
    except Exception:
        return False


class ProxyManager:
    """
    從多個公開來源下載 Proxy 清單，提供執行緒安全的輪換介面。
    建議流程：download_all() → start_background_validation() → 開始使用
    """

    def __init__(self):
        # 每個元素：{"protocol": str, "address": "host:port"}
        self._proxies = []
        self._index = 0
        self._lock = threading.Lock()
        self._stop_validation = threading.Event()
        # GUI 統計用（執行緒安全）
        self._total_loaded: int = 0
        self._checked_count: int = 0

    # ── 下載 ─────────────────────────────────────────────────────────────────

    def download_all(self, timeout=15):
        """從所有來源下載 Proxy 清單，回傳載入的原始代理數量。"""
        collected = []
        for protocol, url in PROXY_SOURCES:
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    text = resp.read().decode("utf-8", errors="ignore")
                for line in text.splitlines():
                    line = line.strip()
                    if line and ":" in line and not line.startswith("#"):
                        collected.append({
                            "protocol": protocol,
                            "address": line,
                        })
                print(f"[Proxy] 來源 {url.split('/')[-1]} 載入完成")
            except Exception as e:
                print(f"[Proxy] 下載失敗 ({url.split('/')[-1]}): {e}")

        random.shuffle(collected)
        # HTTP 代理優先（驗證更嚴格、可靠性更高）
        collected.sort(key=lambda p: _PROTO_PRIORITY.get(p["protocol"], 9))

        with self._lock:
            self._proxies = collected
            self._index = 0
            self._total_loaded = len(collected)
            self._checked_count = 0

        print(f"[Proxy] 共下載 {len(collected)} 個代理（尚未驗證）")
        return len(collected)

    # ── 驗證 ─────────────────────────────────────────────────────────────────

    def validate_all(
        self,
        max_validate=None,
        max_workers=100,
        timeout=8,
        verbose=True,
    ):
        """
        多執行緒驗證 Proxy 是否能實際抓到 websudoku.com 的題目頁面。

        Parameters
        ----------
        max_validate : 最多驗證幾個；None 表示驗證全部
        max_workers  : 並行驗證的執行緒數
        timeout      : 每個 Proxy 的連線逾時（秒）
        verbose      : 是否印出進度
        """
        with self._lock:
            candidates = (
                self._proxies if max_validate is None
                else self._proxies[:max_validate]
            )

        if not candidates:
            print("[Proxy] 無代理可驗證")
            return 0

        n = len(candidates)
        if verbose:
            print(
                f"[Proxy] 開始驗證 {n} 個代理"
                f"（workers={max_workers}, timeout={timeout}s）..."
            )

        valid = []
        checked = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(_test_one_proxy, p, timeout): p
                for p in candidates
            }
            for future in as_completed(future_map):
                checked += 1
                with self._lock:
                    self._checked_count = checked
                try:
                    ok = future.result()
                except Exception:
                    ok = False
                if ok:
                    valid.append(future_map[future])
                if verbose and checked % 100 == 0:
                    print(
                        f"[Proxy] 驗證進度 {checked}/{n}"
                        f"  有效={len(valid)}"
                    )

        random.shuffle(valid)
        valid.sort(key=lambda p: _PROTO_PRIORITY.get(p["protocol"], 9))

        with self._lock:
            self._proxies = valid
            self._index = 0

        if verbose:
            print(f"[Proxy] 驗證完成：{len(valid)}/{n} 可用")

        return len(valid)

    # ── 背景驗證 ─────────────────────────────────────────────────────────────

    def start_background_validation(
        self,
        max_validate=None,
        max_workers=100,
        timeout=8,
    ):
        """
        在獨立執行緒中驗證 Proxy，邊驗證邊加入可用池，呼叫後立即返回。
        爬蟲執行緒可在驗證期間先以直連方式運作，代理逐漸上線後自動切換。
        呼叫 stop_validation() 可中止背景驗證。
        max_validate：最多驗證幾個；None 表示驗證全部下載的代理。
        """
        self._stop_validation.clear()

        with self._lock:
            candidates = (
                self._proxies if max_validate is None
                else self._proxies[:max_validate]
            )
            self._proxies = []
            self._index = 0

        if not candidates:
            print("[Proxy] 無代理可驗證")
            return None

        n = len(candidates)
        print(
            f"[Proxy] 背景驗證啟動：{n} 個代理"
            f"（workers={max_workers}, timeout={timeout}s）"
        )

        stop = self._stop_validation

        def _worker():
            checked = 0
            executor = ThreadPoolExecutor(max_workers=max_workers)
            future_map = {
                executor.submit(_test_one_proxy, p, timeout): p
                for p in candidates
            }
            try:
                for future in as_completed(future_map):
                    if stop.is_set():
                        break
                    checked += 1
                    with self._lock:
                        self._checked_count = checked
                    try:
                        ok = future.result()
                    except Exception:
                        ok = False
                    if ok:
                        with self._lock:
                            self._proxies.append(future_map[future])
                    if checked % 500 == 0:
                        print(
                            f"[Proxy] 背景驗證進度 {checked}/{n}"
                            f"  有效={self.size()}"
                        )
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

            if not stop.is_set():
                with self._lock:
                    self._proxies.sort(
                        key=lambda p: _PROTO_PRIORITY.get(p["protocol"], 9)
                    )
                print(f"[Proxy] 背景驗證完成：{self.size()}/{n} 可用")
            else:
                print(
                    f"[Proxy] 背景驗證已中止"
                    f"（已驗證 {checked}/{n}，有效 {self.size()}）"
                )

        t = threading.Thread(
            target=_worker, daemon=True, name="ProxyValidator"
        )
        t.start()
        return t

    # ── 中止背景驗證 ─────────────────────────────────────────────────────────

    def stop_validation(self):
        """中止背景驗證執行緒（下一個迭代時即停止）。"""
        self._stop_validation.set()

    # ── 取得目前 Proxy（原子性：取得同時自動輪換）────────────────────────────

    def get_playwright_proxy(self):
        """
        原子性取得並輪換至下一個 Proxy（執行緒安全）。
        每次呼叫回傳不同代理，確保並行 workers 不重複使用相同 IP。
        若清單為空則回傳 None（直連）。
        """
        with self._lock:
            if not self._proxies:
                return None
            p = self._proxies[self._index % len(self._proxies)]
            self._index = (self._index + 1) % len(self._proxies)

        proto = p["protocol"]
        addr = p["address"]
        server = (
            f"{proto}://{addr}" if proto in ("socks5", "socks4")
            else f"http://{addr}"
        )
        return {"server": server}

    def get_requests_proxy(self):
        """
        Returns a requests-compatible proxy dict {"http": ..., "https": ...},
        or None if no proxies are available (direct connection).
        """
        info = self.get_playwright_proxy()
        if info is None:
            return None
        server = info["server"]
        return {"http": server, "https": server}

    # ── 切換 Proxy（供 browser.py Playwright 模式使用）───────────────────────

    def rotate(self):
        """切換至下一個 Proxy（執行緒安全）。"""
        with self._lock:
            if not self._proxies:
                return
            self._index = (self._index + 1) % len(self._proxies)

    # ── 黑名單：移除永久失效的 Proxy ─────────────────────────────────────────

    def blacklist_server(self, server_url):
        """
        移除指定 server URL 的 Proxy（回傳 0 格、永久錯誤時呼叫）。
        格式：'proto://host:port'，如 'socks5://1.2.3.4:1080'。
        """
        if "://" not in server_url:
            return 0
        proto, addr = server_url.split("://", 1)
        with self._lock:
            before = len(self._proxies)
            self._proxies = [
                p for p in self._proxies
                if not (p["protocol"] == proto and p["address"] == addr)
            ]
            removed = before - len(self._proxies)
            if self._proxies:
                self._index = self._index % len(self._proxies)
            else:
                self._index = 0
        if removed:
            print(f"[Proxy] 黑名單移除 {server_url}（剩餘 {self.size()} 個）")
        return removed

    # ── 狀態查詢 ─────────────────────────────────────────────────────────────

    def size(self):
        with self._lock:
            return len(self._proxies)

    def is_empty(self):
        return self.size() == 0

    def get_stats(self) -> dict:
        """回傳 GUI 用的統計數據（執行緒安全）。"""
        with self._lock:
            return {
                "valid":   len(self._proxies),
                "checked": self._checked_count,
                "total":   self._total_loaded,
            }
