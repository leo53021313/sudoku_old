"""Apprentice Sudoku — neo-brutalism live inference visualizer.

Loads the latest trained checkpoint and shows the AI solving a puzzle step
by step. One mouse-driven window — designed for a classroom demo where
the audience knows nothing about RL.

Aesthetic: neo-brutalism (cream canvas, pure-black ink borders, hot-red /
vivid-yellow / soft-violet accents, hard offset shadows, rotated sticker
layering, mechanical button physics). The Tailwind design tokens from the
spec are translated into Pygame primitives — see the token block below.

Usage (from repo root):
    python -m apprentice.demo.visualize

Controls (also clickable buttons on screen):
    Click [1]-[5]   switch difficulty preset
    Click [▶ RUN] / [‖ HALT]
    Click [→ STEP] / [↻ NEW]
    Click [« SLOW] / [FAST »]
    Keyboard:       SPACE = run/halt, → = step, ↑↓ = speed,
                    R = new puzzle, 1-5 = preset, ESC = quit
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
import pygame

from apprentice.env.sudoku_gym_env import SudokuGymEnv
from apprentice.solver.human_solver import HumanSolver
from apprentice.train.ppo import SudokuMaskablePPO

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


_REPO_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = str(_REPO_ROOT / "data" / "puzzle_pool.db")
_MODEL_DIR = str(_REPO_ROOT / "apprentice" / "models")
_CKPT_PATTERN = re.compile(r"apprentice_ckpt_(\d+)_steps\.zip$")


# ── Neo-brutalism design tokens ──────────────────────────────────────────────

# Colors (translated from Tailwind `neo-*` palette)
CREAM      = (255, 253, 245)   # #FFFDF5 — main canvas
INK        = (0, 0, 0)         # #000000 — all borders + text
WHITE      = (255, 255, 255)
RED        = (255, 107, 107)   # #FF6B6B — accent / wrong cell / primary action
YELLOW     = (255, 217, 61)    # #FFD93D — secondary / active cell / status
VIOLET     = (196, 181, 253)   # #C4B5FD — muted / AI-placed correct cell
RED_DARK   = (220, 80, 80)     # hover state
YELLOW_DK  = (235, 195, 35)
VIOLET_DK  = (175, 158, 240)

# Borders & shadows
BORDER_DEF   = 4
BORDER_THICK = 6
BORDER_HUGE  = 8

SHADOW_SM = 4
SHADOW_MD = 8
SHADOW_LG = 12
SHADOW_XL = 16


# ── Audience-facing technique names ──────────────────────────────────────────

TECH_NAMES_EN: dict[int, str] = {
    1:  "NAKED_SINGLE",
    2:  "HIDDEN_SINGLE",
    4:  "NAKED_PAIR",
    5:  "HIDDEN_PAIR",
    6:  "POINTING_PAIR",
    7:  "BOX_LINE_REDUCTION",
    8:  "NAKED_TRIPLE",
    9:  "NAKED_QUAD",
    10: "X_WING",
    11: "SWORDFISH",
    12: "XY_WING",
    13: "XYZ_WING",
    17: "TRIAL_AND_ERROR",
}
TECH_NAMES_ZH: dict[int, str] = {
    1:  "唯一候選",
    2:  "隱性唯一",
    4:  "顯性對子",
    5:  "隱性對子",
    6:  "指向對",
    7:  "宮列排除",
    8:  "顯性三元組",
    9:  "顯性四元組",
    10: "X-Wing 矩形排除",
    11: "Swordfish 劍魚",
    12: "XY-Wing",
    13: "XYZ-Wing",
    17: "嘗試錯誤法",
}


# ── Layout ───────────────────────────────────────────────────────────────────

CELL = 64
GRID = CELL * 9                       # 576
MARGIN_L = 122                        # = (W - GRID)/2 → board is page-centered
MARGIN_T = 196                        # title sticker + telemetry pills + preset bar
MARGIN_B = 260
W = GRID + MARGIN_L * 2               # 820 — board column has equal margins
H = GRID + MARGIN_T + MARGIN_B        # 1032


# ── Speed / preset tables ───────────────────────────────────────────────────

SPEEDS = [1.5, 1.0, 0.6, 0.35, 0.2, 0.1, 0.05, 0.02, 0.005]
SPEED_LABELS = ["VRY-SLW", "SLW", "SLW", "MED-SLW", "MED", "MED-FST", "FST", "VRY-FST", "MAX"]
DEFAULT_SPEED_IDX = 3

PRESETS: list[tuple[str, int | None, str, tuple[int,int,int]]] = [
    ("1",  3,    "3 EMPTY",   CREAM),
    ("2",  5,    "5 EMPTY",   YELLOW),
    ("3",  10,   "10 EMPTY",  VIOLET),
    ("4",  20,   "20 EMPTY",  RED),
    ("5",  None, "FULL",      INK),
]


# ── Helpers ─────────────────────────────────────────────────────────────────

def find_latest_checkpoint(model_dir: str) -> tuple[str, int] | None:
    if not os.path.isdir(model_dir):
        return None
    best: tuple[int, str] | None = None
    for fn in os.listdir(model_dir):
        m = _CKPT_PATTERN.match(fn)
        if m:
            n = int(m.group(1))
            if best is None or n > best[0]:
                best = (n, os.path.join(model_dir, fn))
    return (best[1], best[0]) if best else None


def load_brut_font(size: int, bold: bool = True) -> pygame.font.Font:
    """Display font. Priority: Trebuchet MS Bold (user-chosen — clearest
    in our font-clarity comparison) → Segoe UI Black → Arial Black → Verdana.
    """
    for name in ("Trebuchet MS", "Segoe UI Black", "Arial Black", "Verdana", "Bahnschrift"):
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f and f.size("A")[0] > 0:
                return f
        except Exception:
            continue
    return pygame.font.SysFont(None, size, bold=bold)


def load_cjk_font(size: int) -> pygame.font.Font:
    for name in ("Microsoft JhengHei", "MingLiU", "Microsoft YaHei", "SimHei"):
        try:
            f = pygame.font.SysFont(name, size, bold=True)
            if f and f.render("中", True, (0, 0, 0)).get_width() > 5:
                return f
        except Exception:
            continue
    return pygame.font.SysFont(None, size, bold=True)


def draw_halftone(
    screen: pygame.Surface,
    alpha: int = 30,
    spacing: int = 14,
    radius: int = 1,
) -> None:
    """Black halftone dot pattern overlay — neo-brutalism signature texture."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    color = (0, 0, 0, alpha)
    for y in range(spacing // 2, screen.get_height(), spacing):
        for x in range(spacing // 2, screen.get_width(), spacing):
            pygame.draw.circle(overlay, color, (x, y), radius)
    screen.blit(overlay, (0, 0))


def draw_brut_box(
    screen: pygame.Surface,
    rect: pygame.Rect,
    fill: tuple[int, int, int],
    border: int = BORDER_DEF,
    shadow: int = SHADOW_MD,
    hovered: bool = False,
    pressed: bool = False,
) -> pygame.Rect:
    """Draw a neo-brutalist box: shadow → fill → black border.
    - hovered → lifts up 2px and shadow grows.
    - pressed → moves to cover shadow (mechanical click).
    Returns the final rect (after lift / press offsets) for hit-test alignment.
    """
    if pressed:
        r = rect.move(2, 2)
        pygame.draw.rect(screen, fill, r)
        pygame.draw.rect(screen, INK, r, border)
        return r

    if hovered:
        r = rect.move(-2, -2)
        s = shadow + 4
    else:
        r = rect
        s = shadow

    if s > 0:
        pygame.draw.rect(screen, INK, r.move(s, s))
    pygame.draw.rect(screen, fill, r)
    pygame.draw.rect(screen, INK, r, border)
    return r


def render_sticker(
    text: str,
    font: pygame.font.Font,
    fill: tuple[int, int, int],
    fg: tuple[int, int, int] = INK,
    pad_x: int = 14,
    pad_y: int = 10,
    border: int = BORDER_DEF,
) -> pygame.Surface:
    """Render a bordered sticker surface (filled rect + border + centered text).
    Returned surface is opaque on the sticker area, transparent outside.
    """
    text_surf = font.render(text, True, fg)
    w = text_surf.get_width() + pad_x * 2
    h = text_surf.get_height() + pad_y * 2
    sticker = pygame.Surface((w, h), pygame.SRCALPHA)
    sticker.fill(fill)
    pygame.draw.rect(sticker, INK, sticker.get_rect(), border)
    sticker.blit(text_surf, (pad_x, pad_y))
    return sticker


def blit_rotated_with_shadow(
    screen: pygame.Surface,
    sticker: pygame.Surface,
    center: tuple[int, int],
    angle: float,
    shadow_offset: int = SHADOW_MD,
) -> None:
    """Blit a sticker rotated by `angle` with a hard black shadow underneath."""
    # Shadow = solid black silhouette of the sticker
    shadow_surf = pygame.Surface(sticker.get_size(), pygame.SRCALPHA)
    shadow_surf.fill(INK)
    # Mask shadow to sticker's opaque shape (the sticker has SRCALPHA;
    # the inner rect is opaque so this gives a clean rectangular shadow).
    shadow_rot = pygame.transform.rotate(shadow_surf, angle)
    sticker_rot = pygame.transform.rotate(sticker, angle)
    sr = shadow_rot.get_rect(center=(center[0] + shadow_offset,
                                     center[1] + shadow_offset))
    mr = sticker_rot.get_rect(center=center)
    screen.blit(shadow_rot, sr)
    screen.blit(sticker_rot, mr)


# ── Drawing: title + telemetry strip ─────────────────────────────────────────

def draw_title_sticker(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    tag_font: pygame.font.Font,
    ckpt_steps: int,
    paused: bool,
) -> None:
    title = "SUDOKU.AI * NEURAL DEMO"
    sticker = render_sticker(title, title_font, YELLOW, pad_x=18, pad_y=8,
                              border=BORDER_THICK)
    # Center horizontally on the page, slightly left of center to give room
    # for the right-side decorative stickers (CKPT / RUN).
    blit_rotated_with_shadow(screen, sticker, center=(W // 2 - 60, 40), angle=-2,
                              shadow_offset=SHADOW_MD)

    tag_text = f"CKPT  {ckpt_steps/1e6:.2f}M"
    tag = render_sticker(tag_text, tag_font, RED, pad_x=10, pad_y=4,
                          border=BORDER_DEF)
    blit_rotated_with_shadow(screen, tag, center=(W - 100, 28), angle=4,
                              shadow_offset=SHADOW_SM)

    status_text = "/ RUN /" if not paused else "/ HALT /"
    status_color = YELLOW if not paused else RED
    status = render_sticker(status_text, tag_font, status_color, pad_x=10, pad_y=4,
                             border=BORDER_DEF)
    blit_rotated_with_shadow(screen, status, center=(W - 100, 62), angle=-3,
                              shadow_offset=SHADOW_SM)


def draw_telemetry_pills(
    screen: pygame.Surface,
    hud_font: pygame.font.Font,
    step: int,
    elapsed: float,
    wrong: int,
    difficulty: int,
    target_empty: int | None,
    y: int,
) -> None:
    target_str = "FULL" if target_empty is None else f"{target_empty:02d}"
    pills = [
        (f"DIFF L{difficulty}",   WHITE),
        (f"TGT {target_str}",     WHITE),
        (f"STEP {step:03d}",      WHITE),
        (f"T+{elapsed:06.2f}s",   WHITE),
        (f"ERR {wrong:02d}",      RED if wrong > 0 else WHITE),
    ]
    # Pre-render to compute total width, then center the strip on the page.
    stickers = [
        render_sticker(text, hud_font, fill, pad_x=10, pad_y=6, border=BORDER_DEF)
        for text, fill in pills
    ]
    gap = 10
    total = sum(s.get_width() for s in stickers) + gap * (len(stickers) - 1)
    x = (W - total) // 2
    for sticker in stickers:
        rect = sticker.get_rect(topleft=(x, y))
        pygame.draw.rect(screen, INK, rect.move(SHADOW_SM, SHADOW_SM))
        screen.blit(sticker, rect.topleft)
        x += sticker.get_width() + gap


# ── Drawing: preset bar ──────────────────────────────────────────────────────

def draw_preset_bar(
    screen: pygame.Surface,
    current_target_empty: int | None,
    mono_font: pygame.font.Font,
    mouse_pos: tuple[int, int],
    mouse_down: bool,
    y: int,
) -> list[tuple[pygame.Rect, int | None]]:
    rects_out: list[tuple[pygame.Rect, int | None]] = []
    label_surf = mono_font.render("MODE", True, INK)
    h = 44
    # Pre-compute button widths so the whole bar can be page-centered.
    btn_widths = []
    for _key, _target, _label, _color in PRESETS:
        text = f"[{_key}]  {_label}"
        btn_widths.append(mono_font.size(text)[0] + 20)
    gap_btn = 12
    total = label_surf.get_width() + 16 + sum(btn_widths) + gap_btn * (len(btn_widths) - 1)
    x = (W - total) // 2
    screen.blit(label_surf, (x, y + 14))
    x += label_surf.get_width() + 16

    for (key, target, label, color), w in zip(PRESETS, btn_widths):
        active = (target == current_target_empty)
        # Compose label
        text = f"[{key}]  {label}"
        text_color = WHITE if color in (INK, RED) else INK
        active = (target == current_target_empty)
        rect = pygame.Rect(x, y, w, h)
        hovered = rect.collidepoint(mouse_pos) and not active
        pressed = hovered and mouse_down

        fill = color
        if active:
            fill = YELLOW
            text_color = INK

        text_surf = mono_font.render(text, True, text_color)
        final = draw_brut_box(
            screen, rect, fill,
            border=BORDER_DEF, shadow=SHADOW_MD,
            hovered=hovered, pressed=pressed,
        )
        screen.blit(text_surf,
                    (final.x + (final.w - text_surf.get_width()) // 2,
                     final.y + (final.h - text_surf.get_height()) // 2))
        rects_out.append((rect, target))
        x += w + gap_btn
    return rects_out


# ── Drawing: board ──────────────────────────────────────────────────────────

def draw_board(
    screen: pygame.Surface,
    board: np.ndarray,
    given_mask: np.ndarray,
    wrong_cells: set[tuple[int, int]],
    last_action: tuple[str, int, int, int] | None,
    digit_font: pygame.font.Font,
    t: float,
) -> None:
    """Board is the central sticker: thick black border + hard shadow.
    Cell BG carries the color semantics — given=cream, AI=violet,
    wrong=red, last-action=yellow. Digits stay pure black for max readability.
    """
    outer_pad = 6
    outer_rect = pygame.Rect(
        MARGIN_L - outer_pad, MARGIN_T - outer_pad,
        GRID + outer_pad * 2, GRID + outer_pad * 2,
    )
    # Hard shadow
    pygame.draw.rect(screen, INK, outer_rect.move(SHADOW_LG, SHADOW_LG))
    # Card body
    pygame.draw.rect(screen, CREAM, outer_rect)
    pygame.draw.rect(screen, INK, outer_rect, BORDER_HUGE)

    # Cell backgrounds — only color AI-touched / active / wrong cells.
    # Differentiate fill vs eliminate so the audience sees "AI is removing
    # candidates" as a distinct action from "AI filled a number".
    last_cell = None
    last_mode = None
    if last_action is not None:
        last_mode, lr, lc, _ = last_action
        last_cell = (lr, lc)

    for r in range(9):
        for c in range(9):
            v = int(board[r, c])
            cell_rect = pygame.Rect(MARGIN_L + c * CELL, MARGIN_T + r * CELL,
                                    CELL, CELL)
            if (r, c) == last_cell:
                # Fill action → bright yellow ("AI placed a digit").
                # Eliminate action → violet ("AI removed a candidate").
                bg = YELLOW if last_mode == "fill" else VIOLET
                pygame.draw.rect(screen, bg, cell_rect)
            elif (r, c) in wrong_cells:
                pygame.draw.rect(screen, RED, cell_rect)
            elif v != 0 and not given_mask[r, c]:
                pygame.draw.rect(screen, VIOLET, cell_rect)

    # Grid lines — thin (2px) for cell separators, thick (4px) on 3x3 box edges
    for i in range(10):
        thick = (i % 3 == 0)
        w = BORDER_DEF if thick else 2
        x = MARGIN_L + i * CELL
        y = MARGIN_T + i * CELL
        pygame.draw.line(screen, INK, (x, MARGIN_T), (x, MARGIN_T + GRID), w)
        pygame.draw.line(screen, INK, (MARGIN_L, y), (MARGIN_L + GRID, y), w)

    # Digits — pure black, bold, centered. NO color on digits (color is on cell).
    for r in range(9):
        for c in range(9):
            v = int(board[r, c])
            if v == 0:
                continue
            surf = digit_font.render(str(v), True, INK)
            cx = MARGIN_L + c * CELL + (CELL - surf.get_width()) // 2
            cy = MARGIN_T + r * CELL + (CELL - surf.get_height()) // 2
            screen.blit(surf, (cx, cy))

    # Last-action sticker badge — a tiny rotated "AI" label pinned to corner of active cell
    if last_action is not None:
        mode, r, c, _ = last_action
        pin_x = MARGIN_L + c * CELL + CELL - 4
        pin_y = MARGIN_T + r * CELL + 4
        text = "AI" if mode == "fill" else "AI-"
        tiny = load_brut_font(11, bold=True)
        badge = render_sticker(text, tiny, INK, fg=YELLOW, pad_x=4, pad_y=2,
                                border=2)
        blit_rotated_with_shadow(screen, badge, center=(pin_x, pin_y),
                                  angle=-12, shadow_offset=2)


# ── Drawing: action panel (FILL@... / RULE: ...) ─────────────────────────────

def draw_action_panel(
    screen: pygame.Surface,
    last_action: tuple[str, int, int, int] | None,
    last_tech: int | None,
    last_was_wrong: bool,
    body_font: pygame.font.Font,
    label_font: pygame.font.Font,
    cjk_font: pygame.font.Font,
    y: int,
) -> None:
    panel_rect = pygame.Rect(MARGIN_L, y, GRID, 100)
    # Shadow + card
    pygame.draw.rect(screen, INK, panel_rect.move(SHADOW_MD, SHADOW_MD))
    pygame.draw.rect(screen, WHITE, panel_rect)
    pygame.draw.rect(screen, INK, panel_rect, BORDER_DEF)

    # Top label strip
    strip = pygame.Rect(panel_rect.x, panel_rect.y,
                        panel_rect.w, 30)
    pygame.draw.rect(screen, INK, strip)
    label = label_font.render("AI  ACTION  /  REASONING", True, YELLOW)
    screen.blit(label, (strip.x + 14, strip.y + 6))

    if last_action is None:
        msg = body_font.render("AWAITING FIRST OPERATION...", True, INK)
        screen.blit(msg, (panel_rect.x + 14, panel_rect.y + 44))
        return

    mode, r, c, v = last_action
    op = "FILL" if mode == "fill" else "ELIM"
    line1 = f"{op}   R{r+1}C{c+1}   :=   {v}"
    line1_color = RED if last_was_wrong else INK
    s1 = body_font.render(line1, True, line1_color)
    screen.blit(s1, (panel_rect.x + 14, panel_rect.y + 40))

    if last_was_wrong:
        en = "RULE:  ERROR / SOLUTION MISMATCH"
        zh = "錯誤：這格的正確答案不是這個"
    elif last_tech is not None and last_tech in TECH_NAMES_EN:
        en = f"RULE:  {TECH_NAMES_EN[last_tech]}"
        zh = TECH_NAMES_ZH[last_tech]
    elif mode == "fill":
        en = "RULE:  HEURISTIC (lucky correct)"
        zh = "沒有明顯規則，碰運氣對了"
    else:
        en = "RULE:  HEURISTIC (candidate elim)"
        zh = "無明顯規則的候選消去"

    s_en = body_font.render(en, True, INK)
    screen.blit(s_en, (panel_rect.x + 14, panel_rect.y + 68))

    # Chinese on the right side, in a small yellow sticker
    if zh:
        zh_sticker = render_sticker(zh, cjk_font, YELLOW, pad_x=10, pad_y=4,
                                     border=BORDER_DEF)
        pygame.draw.rect(screen, INK,
                         pygame.Rect(panel_rect.right - zh_sticker.get_width() - 18 + SHADOW_SM,
                                     panel_rect.y + 56 + SHADOW_SM,
                                     zh_sticker.get_width(), zh_sticker.get_height()))
        screen.blit(zh_sticker,
                    (panel_rect.right - zh_sticker.get_width() - 18,
                     panel_rect.y + 56))


# ── Drawing: control bar (buttons + speed gauge) ─────────────────────────────

def draw_control_bar(
    screen: pygame.Surface,
    paused: bool,
    speed_label: str,
    speed_idx: int,
    mono_font: pygame.font.Font,
    mouse_pos: tuple[int, int],
    mouse_down: bool,
    y: int,
) -> dict[str, pygame.Rect]:
    rects: dict[str, pygame.Rect] = {}
    h = 50
    gap = 10
    gauge_w = 140
    # (name, text, fill_color, fg) — width auto-sizes to text below.
    play_text = ">> RUN" if paused else "|| HALT"
    items = [
        ("play",   play_text,    RED if paused else YELLOW,  WHITE if paused else INK),
        ("prev",   "< PREV",     WHITE,                       INK),
        ("step",   "STEP >",     WHITE,                       INK),
        ("reset",  "[R] NEW",    VIOLET,                      INK),
        ("slower", "<<",         WHITE,                       INK),
    ]
    # Pre-compute widths
    pad = 24
    widths = [(name, text, fill, fg, max(60, mono_font.size(text)[0] + pad))
              for name, text, fill, fg in items]
    # Total = button widths + gauge + faster button + gaps
    faster_w = max(60, mono_font.size(">>")[0] + pad)
    total = sum(w for _,_,_,_,w in widths) + gauge_w + faster_w + gap * 6
    x = (W - total) // 2

    def button_render(name: str, text: str, w: int, fill, fg):
        nonlocal x
        rect = pygame.Rect(x, y, w, h)
        hovered = rect.collidepoint(mouse_pos)
        pressed = hovered and mouse_down
        final = draw_brut_box(screen, rect, fill, border=BORDER_DEF,
                              shadow=SHADOW_MD, hovered=hovered, pressed=pressed)
        text_surf = mono_font.render(text, True, fg)
        screen.blit(text_surf,
                    (final.x + (final.w - text_surf.get_width()) // 2,
                     final.y + (final.h - text_surf.get_height()) // 2))
        rects[name] = rect
        x += w + gap

    for name, text, fill, fg, w in widths:
        button_render(name, text, w, fill, fg)

    # Speed gauge — chunky bordered tape with filled segments
    gauge_rect = pygame.Rect(x, y, gauge_w, h)
    pygame.draw.rect(screen, INK, gauge_rect.move(SHADOW_SM, SHADOW_SM))
    pygame.draw.rect(screen, WHITE, gauge_rect)
    pygame.draw.rect(screen, INK, gauge_rect, BORDER_DEF)
    inner = gauge_rect.inflate(-16, -16)
    seg_w = inner.w // len(SPEEDS)
    for i in range(len(SPEEDS)):
        sx = inner.x + i * seg_w
        seg = pygame.Rect(sx + 1, inner.y, seg_w - 2, inner.h)
        if i <= speed_idx:
            col = YELLOW if i < 5 else RED if i < 8 else INK
            pygame.draw.rect(screen, col, seg)
            pygame.draw.rect(screen, INK, seg, 1)
        else:
            pygame.draw.rect(screen, INK, seg, 1)
    # Label below
    lbl = mono_font.render(speed_label, True, INK)
    screen.blit(lbl, (gauge_rect.x + (gauge_rect.w - lbl.get_width()) // 2,
                       gauge_rect.bottom + 6))
    x = gauge_rect.right + gap

    button_render("faster", ">>", faster_w, WHITE, INK)
    return rects


def draw_end_banner(
    screen: pygame.Surface,
    solved: bool,
    title_font: pygame.font.Font,
    cjk_font: pygame.font.Font,
) -> None:
    # Banner sticker: big rotated badge that slams onto the board
    if solved:
        en = "SOLVED!"
        zh = "AI 解開了"
        color = YELLOW
    else:
        en = "FAILED"
        zh = "錯誤次數爆表"
        color = RED

    sticker = render_sticker(en, title_font, color, pad_x=26, pad_y=14,
                              border=BORDER_HUGE)
    cx = MARGIN_L + GRID // 2
    cy = MARGIN_T + GRID // 2 - 26
    blit_rotated_with_shadow(screen, sticker, center=(cx, cy), angle=-5,
                              shadow_offset=SHADOW_LG)

    sub_font = load_brut_font(20, bold=True)
    sub_sticker = render_sticker(zh, cjk_font, INK, fg=color, pad_x=18, pad_y=8,
                                  border=BORDER_DEF)
    blit_rotated_with_shadow(screen, sub_sticker,
                              center=(cx, cy + 80), angle=3,
                              shadow_offset=SHADOW_MD)


# ── Decorative floaters (sticker corners) ────────────────────────────────────

def draw_floaters(screen: pygame.Surface, mono_font: pygame.font.Font, t: float) -> None:
    """Sticker-style decorations at the page corners — adds 'bulletin board' vibe."""
    # Bottom-right rotating asterisk-as-star (ASCII for Bahnschrift compat)
    star_font = load_brut_font(28, bold=True)
    star = render_sticker("*", star_font, RED, fg=INK, pad_x=10, pad_y=2,
                           border=BORDER_DEF)
    angle = 6 + 8 * math.sin(t * 0.6)
    blit_rotated_with_shadow(screen, star, center=(W - 36, H - 36),
                              angle=angle, shadow_offset=SHADOW_SM)


# ── Main ────────────────────────────────────────────────────────────────────

def run(args: argparse.Namespace) -> None:
    found = find_latest_checkpoint(_MODEL_DIR) if args.ckpt is None else (args.ckpt, 0)
    if found is None:
        sys.exit(f"[demo] No checkpoint found in: {_MODEL_DIR}")
    ckpt_path, ckpt_steps = found
    if args.ckpt is not None:
        m = _CKPT_PATTERN.search(args.ckpt)
        if m:
            ckpt_steps = int(m.group(1))
    if not os.path.exists(ckpt_path):
        sys.exit(f"[demo] Checkpoint not found: {ckpt_path}")
    print(f"[demo] Loading: {ckpt_path}")
    model = SudokuMaskablePPO.load(ckpt_path, device="cpu")

    env = SudokuGymEnv(
        db_path=_DB_PATH,
        difficulty=args.difficulty,
        max_wrong_fills=20,
        max_steps=300,
    )
    env.set_target_empty(args.target_empty)
    obs, _ = env.reset(seed=args.seed)
    solver = HumanSolver()

    pygame.init()
    pygame.display.set_caption("SUDOKU.AI — NEURAL DEMO")
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    # Sizes for max clarity. Now that the preset bar + control bar
    # auto-size to text width, we can use larger fonts without overflow.
    title_font  = load_brut_font(32, bold=True)
    hud_font    = load_brut_font(15, bold=True)
    body_font   = load_brut_font(22, bold=True)
    label_font  = load_brut_font(14, bold=True)
    btn_font    = load_brut_font(17, bold=True)
    digit_font  = load_brut_font(42, bold=True)
    cjk_body    = load_cjk_font(18)
    end_font    = load_brut_font(54, bold=True)
    end_zh_font = load_cjk_font(24)

    t0 = time.monotonic()

    state = {
        "step": 0, "elapsed": 0.0, "start_time": time.monotonic(),
        "wrong_cells": set(),
        "last_action": None, "last_tech": None, "last_was_wrong": False,
        "speed_idx": DEFAULT_SPEED_IDX, "paused": False, "done": False,
        "next_step_at": time.monotonic() + SPEEDS[DEFAULT_SPEED_IDX],
        "preset_rects": [], "control_rects": {},
        "given_mask": (env.board != 0).copy(),
        # Snapshot history for PREV button (bounded so memory stays small)
        "history": deque(maxlen=200),
        # When AI finishes a puzzle in run-mode, auto-load next after this time
        "auto_next_at": None,
    }

    def snapshot_state():
        return {
            "board": env.board.copy(),
            "candidates": [[set(s) for s in row] for row in env.candidates_cache],
            "cand_count": env.candidate_count_grid.copy(),
            "wrong_count": env.wrong_count,
            "_step_count": env._step_count,
            "obs": obs.copy(),
            "step": state["step"],
            "elapsed": state["elapsed"],
            "last_action": state["last_action"],
            "last_tech": state["last_tech"],
            "last_was_wrong": state["last_was_wrong"],
            "wrong_cells": set(state["wrong_cells"]),
            "done": state["done"],
        }

    def restore_state(snap):
        nonlocal obs
        env.board = snap["board"].copy()
        env.candidates_cache = [[set(s) for s in row] for row in snap["candidates"]]
        env.candidate_count_grid = snap["cand_count"].copy()
        env.wrong_count = snap["wrong_count"]
        env._step_count = snap["_step_count"]
        obs = snap["obs"].copy()
        state["step"] = snap["step"]
        state["elapsed"] = snap["elapsed"]
        state["last_action"] = snap["last_action"]
        state["last_tech"] = snap["last_tech"]
        state["last_was_wrong"] = snap["last_was_wrong"]
        state["wrong_cells"] = set(snap["wrong_cells"])
        state["done"] = snap["done"]

    def new_puzzle():
        nonlocal obs
        obs, _ = env.reset()
        state.update(
            step=0, elapsed=0.0, start_time=time.monotonic(),
            wrong_cells=set(), last_action=None, last_tech=None,
            last_was_wrong=False, done=False,
            next_step_at=time.monotonic() + SPEEDS[state["speed_idx"]],
            given_mask=(env.board != 0).copy(),
            auto_next_at=None,
        )
        state["history"].clear()

    def do_one_step():
        nonlocal obs
        if state["done"]:
            return
        # Snapshot BEFORE stepping so PREV can rewind to this exact state.
        state["history"].append(snapshot_state())
        masks = env.action_masks()
        action, _ = model.predict(
            obs[None], deterministic=True, action_masks=masks[None],
        )
        a = int(action[0]) if hasattr(action, "__len__") else int(action)
        mode, r, c, v = SudokuGymEnv._decode(a)

        board_before = env.board.copy()
        is_correct_fill = (mode == "fill" and int(v) == int(env.solution[r, c]))
        is_bad_elim     = (mode == "eliminate" and int(v) == int(env.solution[r, c]))
        was_wrong = (mode == "fill" and not is_correct_fill) or is_bad_elim
        tech = None
        if not was_wrong:
            tech = solver.find_simplest_justifier(board_before, (mode, r, c, v))

        new_obs, _reward, terminated, truncated, _info = env.step(a)
        obs = new_obs

        state["step"] += 1
        state["elapsed"] = time.monotonic() - state["start_time"]
        state["last_action"] = (mode, r, c, v)
        state["last_tech"] = tech
        state["last_was_wrong"] = was_wrong
        if was_wrong and mode == "fill":
            state["wrong_cells"].add((r, c))
        state["done"] = bool(terminated or truncated)
        state["next_step_at"] = time.monotonic() + SPEEDS[state["speed_idx"]]

    def toggle_pause():
        state["paused"] = not state["paused"]
        if state["paused"]:
            # User wants to talk — cancel any pending auto-advance
            state["auto_next_at"] = None
        else:
            state["next_step_at"] = time.monotonic() + SPEEDS[state["speed_idx"]]
            if state["done"]:
                # Resuming run mode while already done — flash banner briefly
                state["auto_next_at"] = time.monotonic() + 0.8

    def single_step():
        if not state["done"]:
            do_one_step()
            state["paused"] = True

    def prev_step():
        if state["history"]:
            snap = state["history"].pop()
            restore_state(snap)
            state["paused"] = True
            state["auto_next_at"] = None

    def speed_up():
        state["speed_idx"] = min(len(SPEEDS) - 1, state["speed_idx"] + 1)

    def speed_down():
        state["speed_idx"] = max(0, state["speed_idx"] - 1)

    def apply_preset(target):
        env.set_target_empty(target)
        new_puzzle()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:    running = False
                elif ev.key == pygame.K_SPACE:   toggle_pause()
                elif ev.key == pygame.K_RIGHT:   single_step()
                elif ev.key == pygame.K_LEFT:    prev_step()
                elif ev.key == pygame.K_UP:      speed_up()
                elif ev.key == pygame.K_DOWN:    speed_down()
                elif ev.key == pygame.K_r:       new_puzzle()
                elif ev.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                pygame.K_4, pygame.K_5):
                    preset = {pygame.K_1: 3, pygame.K_2: 5, pygame.K_3: 10,
                              pygame.K_4: 20, pygame.K_5: None}[ev.key]
                    apply_preset(preset)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                pos = ev.pos
                hit = False
                for rect, target in state["preset_rects"]:
                    if rect.collidepoint(pos):
                        apply_preset(target)
                        hit = True
                        break
                if not hit:
                    rects = state["control_rects"]
                    if   "play"   in rects and rects["play"].collidepoint(pos):   toggle_pause()
                    elif "prev"   in rects and rects["prev"].collidepoint(pos):   prev_step()
                    elif "step"   in rects and rects["step"].collidepoint(pos):   single_step()
                    elif "reset"  in rects and rects["reset"].collidepoint(pos):  new_puzzle()
                    elif "slower" in rects and rects["slower"].collidepoint(pos): speed_down()
                    elif "faster" in rects and rects["faster"].collidepoint(pos): speed_up()

        now = time.monotonic()
        if (not state["paused"]) and (not state["done"]) and now >= state["next_step_at"]:
            do_one_step()
            # If this step finished the puzzle, auto-advance after a short
            # flash so audience sees the SOLVED / FAILED banner.
            if state["done"] and not state["paused"] and state["auto_next_at"] is None:
                state["auto_next_at"] = now + 0.8

        # Auto-advance to next puzzle when run-mode finishes one
        if state["auto_next_at"] is not None and now >= state["auto_next_at"]:
            new_puzzle()

        t = now - t0

        # ── Render ──
        screen.fill(CREAM)
        draw_halftone(screen, alpha=24, spacing=16, radius=1)

        draw_title_sticker(screen, title_font, hud_font,
                            ckpt_steps=ckpt_steps, paused=state["paused"])
        draw_telemetry_pills(
            screen, hud_font,
            step=state["step"], elapsed=state["elapsed"],
            wrong=env.wrong_count, difficulty=env._current_difficulty,
            target_empty=env.target_empty, y=88,
        )
        state["preset_rects"] = draw_preset_bar(
            screen, env.target_empty, btn_font,
            mouse_pos, mouse_down, y=MARGIN_T - 64,
        )
        draw_board(
            screen, env.board, state["given_mask"],
            state["wrong_cells"], state["last_action"],
            digit_font, t=t,
        )
        draw_action_panel(
            screen, state["last_action"], state["last_tech"],
            state["last_was_wrong"], body_font, label_font, cjk_body,
            y=MARGIN_T + GRID + 24,
        )
        state["control_rects"] = draw_control_bar(
            screen,
            paused=state["paused"],
            speed_label=SPEED_LABELS[state["speed_idx"]],
            speed_idx=state["speed_idx"],
            mono_font=btn_font, mouse_pos=mouse_pos, mouse_down=mouse_down,
            y=MARGIN_T + GRID + 24 + 100 + 24,
        )
        draw_floaters(screen, hud_font, t=t)

        if state["done"]:
            solved = bool(np.all(env.board != 0)) and env.wrong_count < 20
            draw_end_banner(screen, solved, end_font, end_zh_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", type=str, default=None)
    p.add_argument("--difficulty", type=int, default=1, choices=[1, 2, 3, 4])
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--target-empty", type=int, default=5,
                   help="Initial cells-empty target. Switchable in-app via [1]-[5].")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
