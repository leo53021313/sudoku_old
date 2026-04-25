# main_train.py — entry point (thin wrapper)
# -*- coding: utf-8 -*-
# Training logic lives in app/training/:
#   trainer.py          — main loop
#   episode_runner.py   — single-episode execution
#   producer.py         — background puzzle-fetching threads
#   hotkey_controller.py — F8/F9/F10 hotkey handling

import threading

from app.config import config
from app.training.trainer import run
from app.training.hotkey_controller import HOTKEY


if __name__ == "__main__":
    if config.get("gui.enabled"):
        _train_thread = threading.Thread(
            target=run, name="TrainingThread", daemon=True
        )
        _train_thread.start()
        from app.gui.training_gui import launch_gui
        launch_gui(hotkey=HOTKEY, max_boards=config.get("gui.max_boards"))
        _train_thread.join(timeout=10.0)
    else:
        run()
