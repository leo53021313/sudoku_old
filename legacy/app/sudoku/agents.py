# app/sudoku/agents.py
# -*- coding: utf-8 -*-

import random


class BaseAgent:
    def select_action(self, env, state):
        raise NotImplementedError("子類別必須實作 select_action()")


class RandomAgent(BaseAgent):
    def select_action(self, env, state):
        try:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                return None
            return random.choice(valid_actions)
        except Exception:
            return None


class MRVAgent(BaseAgent):
    """
    MRV（Minimum Remaining Values）Agent：
    優先選擇候選數最少的空格。
    choose_mode: "min" | "random"
    """

    def __init__(self, choose_mode="min"):
        self.choose_mode = choose_mode
        self.last_candidate_count = None

    def select_action(self, env, state):
        try:
            mask = env.get_action_mask()
        except Exception:
            self.last_candidate_count = None
            return None

        best_cells = []

        for row in range(9):
            for col in range(9):
                if state[row][col] != 0:
                    continue
                candidates = [
                    num_idx + 1
                    for num_idx in range(9)
                    if mask[row * 9 * 9 + col * 9 + num_idx]
                ]
                if candidates:
                    best_cells.append((row, col, candidates))

        if not best_cells:
            self.last_candidate_count = None
            return None

        best_cells.sort(key=lambda x: len(x[2]))
        min_count = len(best_cells[0][2])
        tied = [item for item in best_cells if len(item[2]) == min_count]

        row, col, candidates = random.choice(tied)
        num = random.choice(candidates) if self.choose_mode == "random" else min(candidates)
        self.last_candidate_count = len(candidates)
        return (row, col, num)
