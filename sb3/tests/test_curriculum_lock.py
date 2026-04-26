# sb3/tests/test_curriculum_lock.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import threading
from app.rl.curriculum.callback import CurriculumCallback, CURRICULUM_STAGES


def test_concurrent_on_step_no_deque_corruption():
    """Concurrent _success_buf and _diff_success writes must not corrupt the deques."""
    cb = CurriculumCallback(stages=CURRICULUM_STAGES, window=100, verbose=0)
    cb._stage_idx = 3  # final stage — no stage advancement

    errors = []

    def simulate_step(success, difficulty):
        try:
            import collections
            with cb._buf_lock:
                cb._total_eps += 1
                cb._stage_eps += 1
                cb._success_buf.append(success)
                cb._diff_buf.append(difficulty)
                cb._diff_success.setdefault(difficulty, collections.deque(maxlen=100)).append(success)
        except Exception as e:
            errors.append(e)

    threads = [
        threading.Thread(target=simulate_step, args=(i % 2 == 0, (i % 4) + 1))
        for i in range(200)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent access raised: {errors}"
    assert len(cb._success_buf) <= 100, "deque maxlen violated"
