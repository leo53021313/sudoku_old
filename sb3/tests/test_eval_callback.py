# sb3/tests/test_eval_callback.py
"""Verify SudokuEvalCallback runs without error and logs to TensorBoard."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np


def test_eval_callback_logs(tmp_path):
    from app.rl.curriculum.eval_callback import SudokuEvalCallback
    from app.rl.models.sudoku_ppo import SudokuMaskablePPO
    from app.rl.models.features_extractor import SudokuFeaturesExtractor
    from stable_baselines3.common.vec_env import DummyVecEnv
    from app.rl.envs.sudoku_gym_env import SudokuGymEnv

    env = DummyVecEnv([lambda: SudokuGymEnv(db_path='../data/puzzle_pool.db')])
    model = SudokuMaskablePPO(
        "CnnPolicy", env, n_steps=64, verbose=0,
        tensorboard_log=str(tmp_path),
        policy_kwargs=dict(
            features_extractor_class=SudokuFeaturesExtractor,
            features_extractor_kwargs={"features_dim": 192},
            net_arch=[],
        ),
    )

    cb = SudokuEvalCallback(
        db_path='../data/puzzle_pool.db',
        eval_freq=64,
        n_episodes=3,
        difficulties=(1,),
        verbose=1,
    )

    model.learn(total_timesteps=64, callback=cb, reset_num_timesteps=True)
    # If we got here without exception, the callback ran
    print("PASS")
    env.close()


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_eval_callback_logs(d)
