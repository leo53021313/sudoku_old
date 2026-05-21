"""Build a self-contained sudoku_demo/ folder for Google Drive distribution.

Copies the minimal set of files needed to (a) display the HTML presentation
and (b) run the pygame AI visualizer on another Windows machine. The output
folder layout matches what launcher.bat / SETUP.bat / START.bat expect
(see demo/package-template/).

Usage (from repo root):
    python demo/build_package.py
    python demo/build_package.py --out C:\\tmp\\sudoku_demo
    python demo/build_package.py --ckpt apprentice/models/apprentice_ckpt_28350112_steps.zip
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Files in apprentice/ that visualize.py needs (transitively) — derived by
# AST-walking the imports plus the pickle-reachable model class.
APPRENTICE_FILES = [
    "__init__.py",
    "data_pkg/__init__.py",
    "data_pkg/pool_db.py",
    "demo/__init__.py",
    "demo/visualize.py",
    "env/__init__.py",
    "env/obs_helpers.py",
    "env/reward_computer.py",
    "env/sudoku_gym_env.py",
    "model/__init__.py",
    "model/features_extractor.py",
    "solver/__init__.py",
    "solver/candidate_engine.py",
    "solver/human_solver.py",
    "solver/techniques/__init__.py",
    "solver/techniques/box_line.py",
    "solver/techniques/hidden_pair.py",
    "solver/techniques/hidden_single.py",
    "solver/techniques/naked_pair.py",
    "solver/techniques/naked_quad.py",
    "solver/techniques/naked_single.py",
    "solver/techniques/naked_triple.py",
    "solver/techniques/pointing_pair.py",
    "solver/techniques/swordfish.py",
    "solver/techniques/trial_error.py",
    "solver/techniques/x_wing.py",
    "solver/techniques/xy_wing.py",
    "solver/techniques/xyz_wing.py",
    "solver_ext/__init__.py",
    "solver_ext/backtracking.py",
    "train/__init__.py",
    "train/ppo.py",
]

# Helpers (don't ship): tests, eval, configs, train.py, curriculum_*, all
# other checkpoints — kept here so the assertion below can spot drift.
_INTENTIONALLY_EXCLUDED = {
    "tests",
    "eval",
    "configs",
    "train/train.py",
    "train/curriculum_callback.py",
    "train/curriculum_controller.py",
}

CKPT_RE = re.compile(r"apprentice_ckpt_(\d+)_steps\.zip$")


def find_latest_checkpoint(models_dir: Path) -> Path:
    # 資料夾完全不存在時 iterdir() 會丟 FileNotFoundError，這裡先攔下來
    # 給清楚的提示（代表還沒訓練出任何 checkpoint），而不是噴 traceback。
    if not models_dir.is_dir():
        raise SystemExit(
            f"No checkpoint found: {models_dir} does not exist.\n"
            f"Train a model first:  python -m apprentice.train.train"
        )
    candidates = []
    for p in models_dir.iterdir():
        m = CKPT_RE.search(p.name)
        if m:
            candidates.append((int(m.group(1)), p))
    if not candidates:
        raise SystemExit(f"No checkpoint found in {models_dir}")
    candidates.sort()
    return candidates[-1][1]


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise SystemExit(f"Missing source file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise SystemExit(f"Missing source dir: {src}")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def dir_size(p: Path) -> int:
    total = 0
    for sub in p.rglob("*"):
        if sub.is_file():
            total += sub.stat().st_size
    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dist-package/sudoku_demo",
                        help="Output folder (relative to repo root)")
    parser.add_argument("--ckpt", default=None,
                        help="Path to checkpoint .zip (default: newest apprentice_ckpt_*_steps.zip)")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    out = (repo / args.out).resolve()
    if out.exists():
        print(f"  removing existing {out} ...")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    print(f"Output: {out}")
    print()

    # ── 1. Package-template files at the root ────────────────────────────────
    template = repo / "demo" / "package-template"
    print(f"[1/5] Copying top-level scripts from {template.relative_to(repo)} ...")
    for name in ("SETUP.bat", "START.bat", "UNINSTALL.bat", "README.txt"):
        copy_file(template / name, out / name)
        print(f"      + {name}")
    print()

    # ── 2. apprentice/ minimal subset ────────────────────────────────────────
    print(f"[2/5] Copying apprentice/ source ({len(APPRENTICE_FILES)} files)...")
    for rel in APPRENTICE_FILES:
        src = repo / "apprentice" / rel
        dst = out / "apprentice" / rel
        copy_file(src, dst)
    print(f"      OK ({len(APPRENTICE_FILES)} files)")
    print()

    # ── 3. apprentice/models/<latest>* (checkpoint + sidecars) ───────────────
    models_dir = repo / "apprentice" / "models"
    if args.ckpt:
        ckpt = Path(args.ckpt).resolve()
    else:
        ckpt = find_latest_checkpoint(models_dir)
    stem = ckpt.with_suffix("").name
    sidecars = [
        ckpt,
        ckpt.with_name(f"{stem}_vecnorm.pkl"),
        ckpt.with_name(f"{stem}_curriculum.json"),
    ]
    print(f"[3/5] Copying checkpoint {ckpt.name} + sidecars ...")
    out_models = out / "apprentice" / "models"
    out_models.mkdir(parents=True, exist_ok=True)
    for src in sidecars:
        if not src.exists():
            print(f"      WARNING: sidecar missing: {src.name}")
            continue
        shutil.copy2(src, out_models / src.name)
        print(f"      + {src.name}  ({human_size(src.stat().st_size)})")
    print()

    # ── 4. data/puzzle_pool.db ───────────────────────────────────────────────
    print("[4/5] Copying data/puzzle_pool.db ...")
    db_src = repo / "data" / "puzzle_pool.db"
    copy_file(db_src, out / "data" / "puzzle_pool.db")
    print(f"      OK ({human_size(db_src.stat().st_size)})")
    print()

    # ── 5. demo/presentation/dist + demo/visualizer-launch/{launcher.bat,reqs} ─
    print("[5/5] Copying presentation dist + visualizer-launch ...")
    dist_src = repo / "demo" / "presentation" / "dist"
    if not (dist_src / "index.html").exists():
        raise SystemExit("demo/presentation/dist/index.html not found. "
                         "Run `npm run build` inside demo/presentation first.")
    copy_tree(dist_src, out / "demo" / "presentation" / "dist")
    print(f"      + demo/presentation/dist  ({human_size(dir_size(dist_src))})")

    vl_src = repo / "demo" / "visualizer-launch"
    vl_dst = out / "demo" / "visualizer-launch"
    vl_dst.mkdir(parents=True, exist_ok=True)
    for name in ("launcher.bat", "requirements-demo.txt"):
        copy_file(vl_src / name, vl_dst / name)
        print(f"      + demo/visualizer-launch/{name}")
    print()

    # ── Summary ──────────────────────────────────────────────────────────────
    total = dir_size(out)
    file_count = sum(1 for _ in out.rglob("*") if _.is_file())
    print("============================================================")
    print(f"  Package built: {out}")
    print(f"  Files        : {file_count}")
    print(f"  Total size   : {human_size(total)}")
    print("============================================================")
    print()
    print("Next steps:")
    print(f"  - Zip {out.name}/ and upload to Google Drive")
    print(f"  - On the target machine: extract, double-click SETUP.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
