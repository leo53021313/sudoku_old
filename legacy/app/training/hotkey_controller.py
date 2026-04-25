# app/training/hotkey_controller.py
# -*- coding: utf-8 -*-

import time
import threading


class HotkeyController:
    def __init__(self):
        self.stop_requested  = False
        self.pause_requested = False
        self.save_requested  = False
        self.enabled         = False
        self.backend         = None

    def toggle_pause(self):
        self.pause_requested = not self.pause_requested
        print("\n[熱鍵] 暫停" if self.pause_requested else "\n[熱鍵] 繼續")

    def request_stop(self):
        self.stop_requested = True
        print("\n[熱鍵] 安全停止")

    def request_save(self):
        self.save_requested = True
        print("\n[熱鍵] 請求儲存")

    def install(self):
        try:
            import keyboard
            keyboard.add_hotkey("f8",  self.toggle_pause)
            keyboard.add_hotkey("f9",  self.request_stop)
            keyboard.add_hotkey("f10", self.request_save)
            self.enabled, self.backend = True, "keyboard"
            print("[熱鍵] F8=暫停, F9=停止, F10=儲存")
            return
        except Exception as e:
            print(f"[熱鍵] keyboard 失敗：{e}")
        try:
            import msvcrt

            def _poll():
                print("[熱鍵] msvcrt | P=暫停, Q=停止, S=儲存")
                while not self.stop_requested:
                    try:
                        if msvcrt.kbhit():
                            ch = msvcrt.getch()
                            if ch in (b"p", b"P"):
                                self.toggle_pause()
                            elif ch in (b"q", b"Q"):
                                self.request_stop()
                            elif ch in (b"s", b"S"):
                                self.request_save()
                        else:
                            time.sleep(0.05)
                    except Exception:
                        time.sleep(0.1)

            threading.Thread(target=_poll, daemon=True).start()
            self.enabled, self.backend = True, "msvcrt"
            return
        except Exception as e:
            print(f"[熱鍵] msvcrt 失敗：{e}")
        print("[熱鍵] 未啟用")

    def wait_if_paused(self, agent=None) -> None:
        from app.config import config
        while self.pause_requested and not self.stop_requested:
            if self.save_requested and _is_torch_agent(agent):
                try:
                    agent.save_model(config.get("model.path"))
                    print("[熱鍵] 暫停中已儲存")
                except Exception as e:
                    print(f"[熱鍵] 儲存失敗：{e}")
                finally:
                    self.save_requested = False
            time.sleep(0.2)

    def consume_save_request(self) -> bool:
        if self.save_requested:
            self.save_requested = False
            return True
        return False


def _is_torch_agent(agent) -> bool:
    try:
        from app.sudoku.torch_agent import TorchAgent
        return isinstance(agent, TorchAgent)
    except Exception:
        return False


# Module-level singleton shared by all training modules
HOTKEY = HotkeyController()
