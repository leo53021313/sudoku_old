# Phase 1 Results — Solver-as-Oracle Training

**Date:** 2026-04-27
**Spec:** [docs/superpowers/specs/2026-04-27-phase1-solver-oracle-design.md](../docs/superpowers/specs/2026-04-27-phase1-solver-oracle-design.md)
**Plan:** [docs/superpowers/plans/2026-04-27-phase1-solver-oracle.md](../docs/superpowers/plans/2026-04-27-phase1-solver-oracle.md)
**Checkpoint:** `sb3/models/sudoku_sb3_latest.zip` (2M steps, resumed from 100k after v1 milestone abort)

---

## TL;DR

🟢 **Pipeline success**: All milestones passed, training completed 2M steps cleanly without aborts.
🔴 **Generalization failure**: True held-out evaluation shows **0% on every difficulty**.
🔴 **In-training eval was misleading**: claimed 100% across all difficulties, but used a biased puzzle fetcher.
🔴 **Same problem in 400k baseline**: not new to Phase 1 — has been masked by the eval bug since the start.

**Phase 1 achieved technical milestones but did NOT achieve its generalization goal.**

---

## Training run summary

| Stage | Status |
|---|---|
| 100k milestone (v1) | 🔴 ABORT — `approx_kl=0.12` (>0.05), `entropy_loss=-2.635` (<-2.0) |
| Remediation (Option B) | n_epochs 4→3, clip_range 0.1→0.05, target_kl=0.02, bc_coef 1.0→0.5; resumed from 100k |
| 100k milestone (v2) | SKIP (already passed at resume) |
| 300k milestone | 🟢 PASS |
| 500k milestone | 🟢 PASS |
| 1M milestone (warn-only) | 🟢 PASS |
| 2M milestone | 🟢 PASS |
| Final stage | 4 (uniform L1:25 L2:25 L3:25 L4:25) |
| Total episodes | 57,388 |
| Final timesteps | 2,102,944 |

The HP remediation (Option B from the 100k post-mortem) successfully stabilised PPO and the model reached the end of training without further milestone failures.

---

## In-training eval (`SudokuEvalCallback`) — MISLEADING

| Step | L1 | L2 | L3 | L4 | Overall |
|---|---|---|---|---|---|
| 1,650,008 | 100% | 100% | 100% | 0% | 75% |
| 1,750,008 | 100% | 100% | 100% | 100% | 100% |
| 1,800,008 | 100% | 100% | 100% | 100% | 100% |
| 1,900,008 | 100% | 100% | 100% | 100% | 100% |
| 2,000,008 | 100% | 100% | 100% | 100% | 100% |
| 2,100,008 | 100% | 100% | 100% | 100% | 100% |

These numbers are **WRONG** — see "Eval bug discovered" below.

---

## True held-out eval (offline, post-training)

### Reserved set (40 puzzles, 10 per difficulty, set aside before training started)

```
                Phase 1 (2M)         400k baseline
L1              0/10 (0%)            0/10 (0%)
L2              0/10 (0%)            0/10 (0%)
L3              0/10 (0%)            0/10 (0%)
L4              0/10 (0%)            0/10 (0%)
Overall         0/40 (0%)            0/40 (0%)
```

### True random sample from DB pool (80 puzzles, 20 per difficulty, ORDER BY RANDOM())

```
                Phase 1 (2M)
L1              0/20 (0%)
L2              0/20 (0%)
L3              0/20 (0%)
L4              0/20 (0%)
Overall         0/80 (0%)
```

**Both models fail completely on truly held-out puzzles, regardless of difficulty.**

---

## Eval bug discovered (root cause of the misleading 100%)

`SudokuEvalCallback._on_step` calls `self._eval_env.reset()`, which routes through `SudokuGymEnv.reset()` → `db.fetch_one_puzzle_for_training(level=difficulty)`.

That fetcher's SQL is:

```sql
SELECT * FROM puzzles
WHERE status IN ('new','training')
ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END,
         tries ASC, best_empty ASC, id ASC
LIMIT 1
```

The `best_empty ASC` clause means **puzzles where the model has gotten CLOSEST to solving come first**. After 57k training episodes, those are the puzzles the model has memorised. The "eval" was sampling from "easy-for-this-model".

By contrast, `eval_sb3.py --eval-set random` uses `fetch_random_puzzles(level, n)`:

```sql
SELECT puzzle FROM puzzles WHERE level=? ORDER BY RANDOM() LIMIT ?
```

— a true random sample. This is what reveals 0% generalisation.

**This bug also affects training**: rollouts use the same biased fetcher, so the model trains on a self-curated curriculum of "puzzles I already know how to solve." This explains both the unstable PPO at 100k (model thrashing on easy memorised puzzles) and the eventual high in-training rollout success rates.

---

## Failure mode of the actual model

Sample debug output for L1 reserved puzzle #1 (initial → final):

```
. 3 . | . . 8 | 6 . .       5 3 1 | . 2 8 | 6 . .
2 . 8 | . . . | . 4 1       2 . 8 | . . 6 | . 4 1
. . 6 | . 3 . | 8 9 .       . . 6 | . 3 . | 8 9 .
------+-------+------       ------+-------+------
7 . 2 | . . 4 | . . .       7 9 2 | . . 4 | . . .
8 . 3 | 7 5 2 | 1 . 4       8 . 3 | 7 5 2 | 1 . 4
. . . | 3 . . | 2 . 7  -->  6 . 4 | 3 . . | 2 . 7
------+-------+------       ------+-------+------
. 6 5 | . 7 . | 9 . .       . 6 5 | . 7 . | 9 . .
9 2 . | . . . | 7 . 3       9 2 . | . . . | 7 . 3
. . 7 | 9 . . | . 2 .       1 . 7 | 9 . . | . 2 .
```

Wrong fills: 5  |  Correct: 3/8

The model:
- Picks **legal cells** (knows the structure)
- Gets **3 of 8 fills correct** (some understanding of constraints)
- Hits `max_wrong_fills=5` → episode terminates
- This pattern repeats across all 40 reserved puzzles

The model is not random; it has internalised approximate constraint propagation. It just **cannot transfer** that to unseen puzzles. Avg ~8 steps per episode = pattern-match-then-fail.

---

## PPO health (final 100k of training)

| Metric | Phase 1 (final ~100k) | Status |
|---|---|---|
| `approx_kl` | ~0.07-0.10 | 🟡 still above target 0.05 |
| `clip_fraction` | ~0.30 | 🟡 still above target 0.20 |
| `entropy_loss` | ~-1.0 to -1.3 | 🟢 not collapsed (≥ -2.0 target) |
| `explained_variance` | ~0.95-0.99 | 🟢 critic learning well |

The HP fix (Option B) stabilised entropy but `approx_kl` remained elevated throughout. Critic was always healthy.

---

## Verdict

### What worked
- The complete Phase 1 code pipeline (oracle teacher, decoupled BC, uniform stage 4, eval JSONL, MilestoneCallback, HP tuning, resume-aware milestones) executed end-to-end.
- The Option B remediation correctly identified and resolved the 100k PPO instability.
- 47/47 unit tests pass; no regression in any module.
- The training process is now reliable and resumable.

### What did NOT work
- **The model does not generalise**. Both Phase 1 (2M, oracle teacher) and pre-Phase-1 (400k, MRV teacher) achieve **0% on truly held-out puzzles**.
- The "100%" in-training eval was an artifact of biased puzzle sampling, not a real signal of capability.
- Spec §1.3 targets (L1≥80%, L2≥80%, L3≥60%, L4≥30% on held-out puzzles) — **none met**.

### Why the model didn't generalise (hypothesis)

1. **Biased training data**: `fetch_one_puzzle_for_training`'s `best_empty ASC` ordering created an auto-curriculum where the model only saw puzzles it was already close to solving. This collapses the effective training distribution to a small "comfort zone".
2. **Oracle teacher amplifies memorisation**: BC loss with always-correct labels lets the model learn (state → exact action) lookups. With 3M parameters and ~75k unique puzzles in the comfort zone, this is feasible.
3. **No regularisation**: no dropout, no weight decay, no data augmentation, no test-time evaluation feedback during training (because the eval was buggy).

---

## Recommendations

### Critical (must fix before any further training)

1. **Fix `SudokuEvalCallback` to use random sampling.** Replace its env-reset path with a direct call to `fetch_random_puzzles(level, 1)` so eval is honest. Without this fix, future runs cannot be diagnosed.

2. **Fix training-time fetcher bias too.** Either change `fetch_one_puzzle_for_training` to `ORDER BY RANDOM()` (keeping the lock semantics for thread safety) or accept the bias as a known artifact and re-evaluate whether the auto-curriculum is desirable.

### Important (before claiming Phase 1 success)

3. **Re-run Phase 1 evaluation with honest fetcher.** Once #1 is fixed, the in-training eval should match `eval_sb3.py --eval-set random` results.

4. **Add reserved-set eval into training callback.** Have `SudokuEvalCallback` ALSO evaluate against the reserved JSON every N steps so we get a continuous held-out signal.

### For Phase 2 readiness

5. **Phase 2 (inference-time search) cannot rescue this model.** A search wrapper needs the policy to provide useful priors over actions. With 0% on held-out, the model's priors are not better than random for unseen states. Phase 2 with this model will likely also score near-zero.

6. **Phase 1.5 needed before Phase 2.** Concretely:
   - Fix fetcher bias (above)
   - Add regularisation: `weight_decay=1e-4` in optimiser, possibly dropout in feature extractor
   - Train on a balanced sample of puzzles (random selection, not auto-curriculum)
   - Validate generalisation continuously via reserved-set eval
   - Only when held-out L1 ≥ 70% should we proceed to Phase 2

---

## Summary table

| Dimension | Goal | Achieved | Status |
|---|---|---|---|
| Code pipeline | All Phase 1 changes implemented + tested | 6/6 tasks, 47/47 tests | 🟢 |
| Training stability | Pass all 5 milestones | 5/5 (after Option B remediation) | 🟢 |
| L1 held-out success | ≥ 80% | 0% | 🔴 |
| L2 held-out success | ≥ 80% | 0% | 🔴 |
| L3 held-out success | ≥ 60% | 0% | 🔴 |
| L4 held-out success | ≥ 30% | 0% | 🔴 |
| PPO indicators | approx_kl < 0.03, clip_fraction < 0.20 | approx_kl ~0.07-0.10 | 🟡 |
| L2 rollout/eval gap < 15% | Diagnosed via JSONL | Diagnosed: training-time biased fetcher | 🟢 (different fix path than expected) |

---

## Next concrete action

Open a Phase 1.5 brainstorm focused on:
1. Fixing the puzzle fetcher bias (training + eval)
2. Adding regularisation
3. Defining "generalisation" via continuous reserved-set evaluation

Until the model demonstrates >50% on the reserved set on at least L1, Phase 2 (inference-time search) is premature.
