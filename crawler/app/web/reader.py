# app/web/reader.py  (requests-only; Playwright fallback removed)
# -*- coding: utf-8 -*-

import random
from html.parser import HTMLParser

# ── 封鎖偵測 ────────────────────────────────────────────────────────────────

# IP 封鎖特徵字串（出現即代表被封鎖）
_BLOCK_SIGNATURES = [
    "this ip address has been blocked",
    "too many requests from it",
    "automated querying",
]

# ── 難度對照表（擴充介面：新增難度只需加入此 dict） ────────────────────────
SUDOKU_LEVELS = {
    1: "easy",
    2: "medium",
    3: "hard",
    4: "evil",
}

# User-Agent 輪換（用於 requests 直接抓取）
_FETCH_USER_AGENTS = [
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/122.0.0.0 Safari/537.36"),
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/122.0.0.0 Safari/537.36"),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0)"
     " Gecko/20100101 Firefox/123.0"),
    ("Mozilla/5.0 (X11; Linux x86_64)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/122.0.0.0 Safari/537.36"),
]


def get_level_url(level):
    """
    依難度等級回傳對應的 websudoku.com 網址。
    level 須為 SUDOKU_LEVELS 中定義的整數（1~4）。
    """
    if level not in SUDOKU_LEVELS:
        raise ValueError(
            f"不支援的難度等級 {level}，"
            f"可用值：{list(SUDOKU_LEVELS.keys())}"
        )
    # east.websudoku.com 直接提供含題目的靜態 HTML；
    # www.websudoku.com 只是一個 frameset 殼，requests 看不到題目
    # 使用 http:// 避免 SOCKS 代理 + HTTPS 的 SSL 憑證驗證問題
    return f"http://east.websudoku.com/?level={level}"


class BlockedError(RuntimeError):
    """IP 被封鎖例外；呼叫端應切換 Proxy 並重試。"""
    pass


# ── HTML 解析器（用於 requests 直接抓取） ───────────────────────────────────

class _PuzzleHTMLParser(HTMLParser):
    """
    從 websudoku.com 的原始 HTML 中直接提取 81 個格子的資料。
    ID 格式：f{col}{row}，如 f00 / f10 / f23。
    """

    def __init__(self):
        super().__init__()
        self.board = [[0] * 9 for _ in range(9)]
        self.fixed = [[False] * 9 for _ in range(9)]
        self.cell_count = 0
        self.iframe_src = None  # 若題目在 iframe 內，記錄其 src

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # 若有 iframe，記錄 src 以便後續追蹤
        if tag == "iframe" and self.iframe_src is None:
            self.iframe_src = attrs.get("src")
            return

        if tag != "input":
            return

        el_id = attrs.get("id", "")
        # 只處理格式為 f{col}{row} 的 input
        if not (len(el_id) == 3 and el_id[0] == "f"):
            return
        try:
            col = int(el_id[1])
            row = int(el_id[2])
        except ValueError:
            return
        if not (0 <= col <= 8 and 0 <= row <= 8):
            return

        value = attrs.get("value", "").strip()
        readonly = "readonly" in attrs
        self.board[row][col] = int(value) if value.isdigit() else 0
        self.fixed[row][col] = readonly
        self.cell_count += 1


def fetch_puzzle_via_requests(url, proxy_dict=None, timeout=8, debug=False):
    """
    使用 requests 函式庫直接抓取 websudoku.com 頁面並解析棋盤。
    不需要 Playwright browser，速度比 Playwright 快 5-10 倍。
    支援 HTTP / SOCKS4 / SOCKS5 Proxy（SOCKS 需安裝 PySocks）。

    Parameters
    ----------
    url        : 目標 URL（如 https://www.websudoku.com/?level=1）
    proxy_dict : requests 格式的 proxy 字典，例如：
                   HTTP  → {"http": "http://host:port", ...}
                   SOCKS → {"http": "socks5://host:port", ...}
                 None 表示直連。
    timeout    : 請求逾時（秒）
    debug      : True 時印出每個步驟的詳細診斷資訊

    Returns: (board: list[9][9], fixed: list[9][9])
    Raises : BlockedError, ValueError, requests.exceptions.*
    """
    import requests  # noqa: PLC0415
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    proxy_label = (
        next(iter(proxy_dict.values())) if proxy_dict else "直連（無 Proxy）"
    )

    if debug:
        print(f"[DEBUG 步驟1] 發送請求 proxy={proxy_label}  url={url}")

    headers = {
        "User-Agent": random.choice(_FETCH_USER_AGENTS),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    resp = requests.get(
        url, headers=headers, proxies=proxy_dict, timeout=timeout, verify=False
    )

    html = resp.text
    if debug:
        snippet = html[:300].replace("\n", " ").replace("\r", "")
        print(
            f"[DEBUG 步驟2] 收到回應 HTTP={resp.status_code}"
            f"  長度={len(html)} bytes"
        )
        print(f"[DEBUG 步驟2] HTML 前300字: {snippet}")

    if any(sig in html.lower() for sig in _BLOCK_SIGNATURES):
        if debug:
            print("[DEBUG 步驟3] 偵測到封鎖特徵字串 -> BlockedError")
        raise BlockedError("IP 被封鎖，需要切換 Proxy")

    parser = _PuzzleHTMLParser()
    parser.feed(html)

    if debug:
        print(
            f"[DEBUG 步驟3] HTML 解析完畢"
            f"  格子數={parser.cell_count}/81"
            f"  iframe_src={parser.iframe_src!r}"
        )

    if parser.cell_count == 81:
        if debug:
            print("[DEBUG 步驟4] 成功解析 81 格，回傳棋盤")
        return parser.board, parser.fixed

    # 若題目在 iframe 裡，追蹤 iframe src 再抓一次
    if parser.iframe_src:
        src = parser.iframe_src
        if not src.startswith("http"):
            base = url.split("?")[0].rstrip("/")
            src = f"{base}/{src.lstrip('/')}"
        if debug:
            print(f"[DEBUG 步驟4] iframe 追蹤，重新抓取: {src}")
        resp2 = requests.get(
            src, headers=headers, proxies=proxy_dict, timeout=timeout, verify=False
        )
        if debug:
            print(
                f"[DEBUG 步驟5] iframe 回應 HTTP={resp2.status_code}"
                f"  長度={len(resp2.text)} bytes"
            )
        parser2 = _PuzzleHTMLParser()
        parser2.feed(resp2.text)
        if debug:
            print(
                f"[DEBUG 步驟5] iframe 解析完畢"
                f"  格子數={parser2.cell_count}/81"
            )
        if parser2.cell_count == 81:
            if debug:
                print("[DEBUG 步驟5] iframe 成功解析 81 格，回傳棋盤")
            return parser2.board, parser2.fixed

    raise ValueError(
        f"解析失敗：找到 {parser.cell_count} 格，預期 81 格"
        f"（proxy={proxy_label}）"
    )
