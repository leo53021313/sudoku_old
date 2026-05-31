# Apprentice — Corrected Diagnosis & Path (real-puzzle solving)

**Date:** 2026-05-31
**Status:** Tier 1 SHIPPED (commit `6ff8429`). Tier 2 optional.
**Supersedes:** the gate-driven-curriculum redesign that previously occupied this file (its premise was empirically refuted — see §6).

---

## 1. What we believed vs what is true

**Believed (wrong):** eval/reserved reads ~0% because of a *train/eval distribution gap* — the policy trains on fill-back boards (~26 empty) and cannot generalize to real-puzzle density (45–57 empty). The fix was a gate-driven curriculum that climbs to real density + real-puzzle mixing.

**True (measured):** the policy **already solves 100% of real L1–L4 puzzles**. eval read ~0% because of **two measurement-blocking bugs**, not a capability gap.

This was found by adversarial empirical probing of the live checkpoint, then verified directly on the newest checkpoint with the *real* (non-monkeypatched) fixed code.

---

## 2. The real root cause (proven)

Two coupled bugs, both in the inference/eval path:

1. **Action-mask self-sabotage.** `action_masks()` allowed eliminating a cell's **last remaining candidate** — which empties the cell and is always illegal (solution-agnostic). The eliminate-heavy policy did this constantly: 90% of all wrong actions were "bad eliminates," 98% at a cell whose answer was a *forced fill* the policy could already see (obs ch24/25). It was destroying answers it could have filled.

2. **Hard-coded wrong-budget.** `reward_computer.py` terminated on the module constant `MAX_WRONG = 20`, **not** `env.max_wrong_fills`. The documented dynamic formula was dead code. Worse, the eval/reserved envs use `target_empty=None`, whose `_update_dynamic_limits` branch pinned the budget to a flat static 20. The eliminate-heavy policy needs **25–40 wrong actions** to grind a full board to completion (incidental bad eliminates en route); a 20-cap killed it mid-solve before it could convert candidate-pruning into fills.

**Decisive evidence (newest checkpoint, deterministic, full real puzzles, no retraining):**

| Condition | Solved | Fill |
|---|---|---|
| Shipped (mask bug + `MAX_WRONG=20`) | **0/40** | ~0% |
| + mask fix + budget scaled to density (~55–66) | **40/40 (100%)** | 100% |

The training was succeeding the whole time; the eval metric was systematically hiding it.

---

## 3. Tier 1 — the fix (SHIPPED, commit `6ff8429`)

1. **Mask fix** — `action_masks()` forbids eliminating a cell's sole candidate. ~5 lines; solution-agnostic; no cold-start; removes ~87% of bad-eliminate wrong actions.
2. **Budget fix** — `reward_computer` terminates on `getattr(env, "max_wrong_fills", MAX_WRONG)`; `_update_dynamic_limits` scales the budget by the board's **actual empty count** even when `target_empty=None`, so eval/reserved on full puzzles get a real budget (~55–66) instead of 20.

Tests (TDD): `test_mask_last_candidate.py` (new) + dynamic-budget tests in `test_reward_computer.py` + density-scaling tests in `test_env_basic.py`. Full suite: 188 passed, 1 skipped.

**No eval-callback change needed:** both eval callbacks construct `SudokuGymEnv(target_empty=None)` and reset via `options`, so the env fix applies automatically. The next training run's `eval/reserved_overall` should jump from ~0 to ~1.0 — that live jump is the final confirmation in the real pipeline.

---

## 4. What this means for the goals

- **真實 (solve real puzzles): achieved.** The agent solves 100% of the DB's L1–L4 puzzles deterministically. Nothing more is required for this goal beyond Tier 1.
- **技巧 (clean reasoning): NOT achieved, and optional.** The policy solves *messily* — it rides the naked/hidden-single cascade and makes ~30 incidental bad eliminates per puzzle (it guesses eliminates rather than justifying them). If you want genuine technique discipline, that's Tier 2 (§5) — but it is polish, not capability.

---

## 5. Tier 2 — optional technique-quality polish (UNPROVEN — do only if you want clean reasoning)

> **Decision (2026-05-31): declined.** The 真實 (solve real puzzles) goal is met at Tier 1; Tier 2 is recorded here only as a pointer if clean-reasoning quality is wanted later.

The eliminate-spam (~30 bad eliminates/puzzle) is the remaining ugliness. Candidate mechanism-level levers, in rough order of expected leverage — **none verified; each needs retraining + measurement:**

1. **Remove the perverse incentive.** `reward_computer` pays **+0.1 for a legal-but-unjustified eliminate** — i.e. it pays the policy to guess-eliminate candidates it cannot justify, which is exactly the bad-eliminate behavior. Zeroing this (reward eliminates only when a technique justifies them) is the most direct structural lever. Reward-*structure* change, not a magnitude tweak.
2. **Entropy.** Lower `ent_coef` (now actually controllable on resume only via a code path that takes effect — note the existing trap: `MaskablePPO.load` restores the saved value, so a code change alone is inert on `--load-model`). Stochastic play makes far more bad eliminates than deterministic (53% vs 80% solve historically). Marginal for the already-solved goal; mostly cleans training-time behavior.
3. **Hidden-single mask extension.** Also forbid eliminating a value that has no other home in some unit (the residual ~2 bad eliminates/puzzle after the naked-single mask). More complex; low priority since the goal is already met.

**Recommendation:** do NOT start Tier 2 unless clean technique demonstration is an explicit goal. For "solve real puzzles," stop after Tier 1.

---

## 6. Superseded / dropped

- **Gate-driven curriculum, deadlock fix, `real_puzzle_prob` distribution bridge, two-stage transfer** — all built to cross a distribution gap that does not bind. Dropped. (The curriculum is still deadlocked at `target_empty=26`, but that no longer matters: the agent already generalizes to full puzzles. Fixing the deadlock / climbing is only worth doing if Tier 2 / harder-puzzle training is pursued, and even then the climb ceiling must be re-measured under the fixed budget — the old E1 sweep that "proved" a capability ceiling at ~38 empty was confounded by the same `MAX_WRONG=20` cap.)
- The earlier broad plan `docs/superpowers/plans/2026-05-31-apprentice-unfreeze-and-bridge.md` is replaced by the slimmed plan of the same name.

---

## 7. Open questions (for later, not blocking)

- Are L1–L4 (websudoku, largely singles-cascade-solvable) the real target, or do you want puzzles requiring advanced techniques? The current 100% may overstate "technique skill."
- Should training even continue? The agent already solves the goal set; further training only matters for Tier 2 or harder puzzles.
