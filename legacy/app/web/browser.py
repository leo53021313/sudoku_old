# app/web/browser.py
# -*- coding: utf-8 -*-

import random
from playwright.sync_api import sync_playwright

# 輪換使用者代理，降低被網站辨識為爬蟲的風險
_USER_AGENTS = [
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/122.0.0.0 Safari/537.36"),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/121.0.0.0 Safari/537.36"),
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/122.0.0.0 Safari/537.36"),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0)"
     " Gecko/20100101 Firefox/123.0"),
    ("Mozilla/5.0 (X11; Linux x86_64)"
     " AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/122.0.0.0 Safari/537.36"),
]


class BrowserManager:
    """
    Playwright 瀏覽器管理器，支援：
    - Proxy 注入（傳入 ProxyManager 實例）
    - 隨機 User-Agent 輪換
    - 執行中熱切換 Proxy（rotate_proxy），不需重啟整個瀏覽器
    """

    def __init__(self, headless=True, proxy_manager=None):
        """
        Parameters
        ----------
        headless      : 是否以無頭模式啟動
        proxy_manager : ProxyManager 實例；為 None 時直連
        """
        self.headless = headless
        self.proxy_manager = proxy_manager
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # ── 生命週期 ────────────────────────────────────────────────────────────

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )
        # 多個 worker 並行時，先輪換一次確保各自起步於不同 Proxy
        if self.proxy_manager:
            self.proxy_manager.rotate()
        self._new_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass

    # ── Context 管理 ────────────────────────────────────────────────────────

    def _new_context(self):
        """建立新的瀏覽器 context，套用目前的 Proxy 與隨機 User-Agent。"""
        if self.context:
            try:
                self.context.close()
            except Exception:
                pass

        proxy = (
            self.proxy_manager.get_playwright_proxy()
            if self.proxy_manager
            else None
        )
        ua = random.choice(_USER_AGENTS)
        self.context = self.browser.new_context(proxy=proxy, user_agent=ua)
        self.page = self.context.new_page()

    def rotate_proxy(self):
        """
        切換至下一個 Proxy 並重建 context/page。
        呼叫後需重新導航到目標頁面。
        """
        if self.proxy_manager:
            self.proxy_manager.rotate()
        self._new_context()

    # ── 導航 ────────────────────────────────────────────────────────────────

    def goto(self, url, wait_ms=0):
        """導航到指定 URL 並等待 DOM 載入完成。"""
        self.page.goto(url, wait_until="domcontentloaded")
        if wait_ms > 0:
            self.page.wait_for_timeout(wait_ms)
        return self.page
