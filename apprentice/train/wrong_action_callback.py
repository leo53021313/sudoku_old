"""WrongActionLogCallback — log per-episode wrong_count to TensorBoard.

Reads SB3's own episode-info buffer (`model.ep_info_buffer`) — the same rolling
window used for `rollout/ep_rew_mean` / `rollout/ep_len_mean` — so the new
`rollout/ep_wrong_mean` metric lines up apples-to-apples with them.

Relies on each episode's info carrying "wrong_count". That is wired in
train.py via make_vec_env(..., monitor_kwargs={"info_keywords": ("wrong_count",)}),
which makes Monitor copy the terminal-step wrong_count into ep_info_buffer.
"""

from __future__ import annotations

from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.utils import safe_mean


class WrongActionLogCallback(BaseCallback):
    """Record rollout/ep_wrong_mean from ep_info_buffer at each rollout end."""

    def _on_step(self) -> bool:  # required abstract method; no per-step work
        return True

    def _on_rollout_end(self) -> None:
        buf = self.model.ep_info_buffer
        if not buf:
            return
        wrongs = [ep["wrong_count"] for ep in buf if "wrong_count" in ep]
        if not wrongs:
            return
        self.logger.record("rollout/ep_wrong_mean", safe_mean(wrongs))
