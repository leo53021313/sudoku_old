"""Technique 3: Basic Elimination.

This technique is implemented implicitly inside CandidateEngine — every fill
propagates removal of the placed digit from related cells' candidate sets.
There is no separate detector to run; the engine maintains the invariant.

This file exists only to document the technique numbering. It exposes a
no-op marker for the human_solver's priority loop.
"""
TECHNIQUE_ID = 3
