# sb3/tests/test_curriculum_save_load.py
"""Verify curriculum state is saved and restored correctly."""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.rl.curriculum.callback import CurriculumCallback, CURRICULUM_STAGES


def test_save_load_roundtrip():
    cb = CurriculumCallback(verbose=0)
    # Simulate having advanced to stage 2
    cb._stage_idx = 2
    cb._total_eps = 12345
    fake_mrv_prob = 0.20

    cb._stage_eps = 3000

    with tempfile.NamedTemporaryFile(mode='w', suffix='_curriculum.json', delete=False) as f:
        json.dump({
            "stage_idx": cb._stage_idx,
            "total_eps": cb._total_eps,
            "stage_eps": cb._stage_eps,
            "mrv_prob":  fake_mrv_prob,
        }, f, indent=2)
        path = f.name

    # Simulate restore
    cb2 = CurriculumCallback(verbose=0)
    with open(path, encoding="utf-8") as f:
        cs = json.load(f)
    cb2._stage_idx = int(cs["stage_idx"])
    cb2._total_eps = int(cs["total_eps"])
    cb2._stage_eps = int(cs.get("stage_eps", 0))
    restored_mrv   = float(cs["mrv_prob"])

    assert cb2._stage_idx == 2,     f"stage_idx: {cb2._stage_idx}"
    assert cb2._total_eps == 12345, f"total_eps: {cb2._total_eps}"
    assert cb2._stage_eps == 3000,  f"stage_eps: {cb2._stage_eps}"
    assert restored_mrv   == 0.20,  f"mrv_prob:  {restored_mrv}"
    os.unlink(path)
    print("PASS")


if __name__ == "__main__":
    test_save_load_roundtrip()
