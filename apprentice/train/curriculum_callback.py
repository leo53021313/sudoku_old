"""CurriculumCallback — SB3 callback wiring CurriculumController to training.

Responsibilities:
  1. After each env step, read `infos` for ended episodes and forward
     `is_success` to the controller.
  2. At every `update_interval_steps` steps, ask controller to update; if
     target_empty changed, push the new value to every vec_env worker.
  3. Write TB metrics (curriculum/target_empty, etc.) at update boundaries.
  4. Save / restore controller state via sidecar JSON.
"""

from __future__ import annotations

from stable_baselines3.common.callbacks import BaseCallback

from apprentice.train.curriculum_controller import CurriculumController


class CurriculumCallback(BaseCallback):
    """See module docstring."""

    def __init__(
        self,
        controller: CurriculumController,
        update_interval_steps: int = 50_000,
        save_path: str | None = None,
        save_freq_steps: int = 50_000,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self.controller = controller
        self.update_interval_steps = update_interval_steps
        self.save_path = save_path
        self.save_freq_steps = save_freq_steps
        self._last_update_step: int = 0
        self._last_save_step: int = 0
        self._last_pushed_target: int | None = None

    def _on_training_start(self) -> None:
        """Push initial target_empty to all envs."""
        self._push_target_to_envs()

    def _on_step(self) -> bool:
        # 1. Record episode outcomes from infos
        dones = self.locals.get("dones", [])
        infos = self.locals.get("infos", [])
        for done, info in zip(dones, infos):
            if not done:
                continue
            success = bool(info.get("is_success", False))
            self.controller.record_episode_outcome(success=success)

        step = int(self.model.num_timesteps)

        # 2. Maybe update controller
        if step - self._last_update_step >= self.update_interval_steps:
            self.controller.update(current_step=step)
            self._last_update_step = step
            new_target = self.controller.target_empty_rounded
            if new_target != self._last_pushed_target:
                self._push_target_to_envs()
            self._log_tb_metrics()

        # 3. Periodic save
        if self.save_path and step - self._last_save_step >= self.save_freq_steps:
            self.controller.save(self.save_path)
            self._last_save_step = step

        return True

    def _push_target_to_envs(self) -> None:
        target = self.controller.target_empty_rounded
        if self.training_env is None:
            return
        # SubprocVecEnv supports env_method; this calls set_target_empty(target) on every worker
        self.training_env.env_method("set_target_empty", target)
        self._last_pushed_target = target
        if self.verbose >= 1:
            print(f"[Curriculum] pushed target_empty={target} at step={self.model.num_timesteps if self.model else 0}")

    def _log_tb_metrics(self) -> None:
        if self.logger is None:
            return
        self.logger.record("curriculum/target_empty", float(self.controller.target_empty))
        self.logger.record("curriculum/target_empty_rounded", float(self.controller.target_empty_rounded))
        self.logger.record("curriculum/success_rate_window", float(self.controller.success_rate()))
        self.logger.record("curriculum/in_sweet_spot", 1.0 if self.controller.in_sweet_spot() else 0.0)
        self.logger.record("curriculum/adjustment_per_update", float(self.controller.last_adjustment))
        steps_since = int(self.model.num_timesteps) - int(self.controller.last_advance_step)
        self.logger.record("curriculum/steps_since_last_advance", float(steps_since))
        self.logger.record("curriculum/is_probing", 1.0 if self.controller._probe_target is not None else 0.0)

        # env-side limits aggregated from the first worker (all workers share target_empty,
        # so max_steps and max_wrong_fills are identical across workers)
        if self.training_env is not None:
            try:
                max_steps = int(self.training_env.get_attr("max_steps")[0])
                max_wrong = int(self.training_env.get_attr("max_wrong_fills")[0])
                self.logger.record("env/max_steps", float(max_steps))
                self.logger.record("env/max_wrong", float(max_wrong))
            except (AttributeError, IndexError):
                pass  # vec_env doesn't support get_attr (e.g., in some tests)
