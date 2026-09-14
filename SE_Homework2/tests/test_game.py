"""一箭又一箭 T01-T16 自动化测试。"""

import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from game import (  # noqa: E402
    BOARD_LEFT,
    BOARD_TOP,
    BUTTON_RECT,
    CELL_SIZE,
    FINAL_BUTTON_RECT,
    LEVELS,
    PAUSE_BUTTON_RECT,
    PAUSE_EXIT_BUTTON_RECT,
    PLAY_RESTART_BUTTON_RECT,
    START_BUTTON_RECT,
    START_EXIT_BUTTON_RECT,
    ArrowGame,
)


def arrow_position(arrow: dict) -> tuple[int, int]:
    """返回箭头所在格子的中心坐标。"""
    return (
        BOARD_LEFT + arrow["col"] * CELL_SIZE + CELL_SIZE // 2,
        BOARD_TOP + arrow["row"] * CELL_SIZE + CELL_SIZE // 2,
    )


def solve_current_level(game: ArrowGame) -> None:
    """不断点击当前可飞出的箭头，直到清空关卡。"""
    while game.arrows:
        arrow = next(arrow for arrow in game.arrows if not game.is_blocked(arrow))
        game.handle_click(arrow_position(arrow))
    for _ in range(17):
        game.update(0.016)


class ArrowGameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game = ArrowGame()
        self.game.handle_click(START_BUTTON_RECT.center)

    def test_t01_unblocked_arrow_flies_out(self) -> None:
        arrow = next(item for item in self.game.arrows if not self.game.is_blocked(item))
        before = len(self.game.arrows)
        self.game.handle_click(arrow_position(arrow))
        self.assertEqual(len(self.game.arrows), before - 1)
        self.assertEqual(self.game.feedback, "箭头飞出棋盘")
        self.assertIsNotNone(self.game.flying_arrow)

    def test_t02_blocked_arrow_costs_one_mistake(self) -> None:
        arrow = next(item for item in self.game.arrows if self.game.is_blocked(item))
        before = len(self.game.arrows)
        self.game.handle_click(arrow_position(arrow))
        self.assertEqual(len(self.game.arrows), before)
        self.assertEqual(self.game.mistakes_left, 2)
        self.assertEqual(self.game.shake_frame, 18)

    def test_t03_edge_outward_arrow_does_not_overflow(self) -> None:
        edge_arrow = {"row": 0, "col": 0, "direction": "up"}
        self.game.arrows = [edge_arrow]
        self.game.handle_click(arrow_position(edge_arrow))
        self.assertEqual(self.game.arrows, [])
        self.assertEqual(self.game.feedback, "箭头飞出棋盘")

    def test_t04_clear_level_shows_success(self) -> None:
        solve_current_level(self.game)
        self.assertEqual(self.game.game_state, "success")

    def test_t05_mistakes_exhausted_shows_failure(self) -> None:
        arrow = next(item for item in self.game.arrows if self.game.is_blocked(item))
        for _ in range(3):
            self.game.handle_click(arrow_position(arrow))
        self.assertEqual(self.game.mistakes_left, 0)
        self.assertEqual(self.game.game_state, "failed")

    def test_t06_restart_restores_current_level(self) -> None:
        arrow = next(item for item in self.game.arrows if not self.game.is_blocked(item))
        self.game.handle_click(arrow_position(arrow))
        self.game.elapsed_seconds = 12
        self.game.handle_click(PLAY_RESTART_BUTTON_RECT.center)
        self.assertEqual(self.game.arrows, LEVELS[0])
        self.assertEqual(self.game.mistakes_left, 3)
        self.assertEqual(self.game.elapsed_seconds, 0)

    def test_t07_start_button_initializes_first_level(self) -> None:
        game = ArrowGame()
        game.handle_click(START_BUTTON_RECT.center)
        self.assertEqual(game.game_state, "playing")
        self.assertEqual(game.current_level, 0)
        self.assertEqual(game.arrows, LEVELS[0])

    def test_t08_next_level_initializes_correctly(self) -> None:
        solve_current_level(self.game)
        self.game.handle_click(BUTTON_RECT.center)
        self.assertEqual(self.game.game_state, "playing")
        self.assertEqual(self.game.current_level, 1)
        self.assertEqual(self.game.arrows, LEVELS[1])

    def test_t09_pause_stops_timer_and_board_input(self) -> None:
        self.game.handle_click(PAUSE_BUTTON_RECT.center)
        elapsed = self.game.elapsed_seconds
        before = len(self.game.arrows)
        arrow = next(item for item in self.game.arrows if not self.game.is_blocked(item))
        self.game.update(3)
        self.game.handle_click(arrow_position(arrow))
        self.assertTrue(self.game.is_paused)
        self.assertEqual(self.game.elapsed_seconds, elapsed)
        self.assertEqual(len(self.game.arrows), before)

    def test_t10_continue_resumes_timer_and_input(self) -> None:
        self.game.handle_click(PAUSE_BUTTON_RECT.center)
        self.game.handle_click(PAUSE_BUTTON_RECT.center)
        self.game.update(1.5)
        self.assertFalse(self.game.is_paused)
        self.assertAlmostEqual(self.game.elapsed_seconds, 1.5)

    def test_t11_pause_exit_returns_to_menu(self) -> None:
        self.game.handle_click(PAUSE_BUTTON_RECT.center)
        self.game.handle_click(PAUSE_EXIT_BUTTON_RECT.center)
        self.assertEqual(self.game.game_state, "start")
        self.assertFalse(self.game.is_paused)
        self.assertFalse(self.game.should_exit)

    def test_t12_start_exit_closes_game(self) -> None:
        game = ArrowGame()
        game.handle_click(START_EXIT_BUTTON_RECT.center)
        self.assertTrue(game.should_exit)

    def test_t13_final_level_returns_to_menu(self) -> None:
        self.game.reset_level(len(LEVELS) - 1)
        self.game.game_state = "playing"
        solve_current_level(self.game)
        self.game.handle_click(FINAL_BUTTON_RECT.center)
        self.assertEqual(self.game.game_state, "start")
        self.assertEqual(self.game.current_level, 0)

    def test_t14_blank_cell_does_not_change_state(self) -> None:
        before_arrows = [arrow.copy() for arrow in self.game.arrows]
        before_mistakes = self.game.mistakes_left
        occupied = {(arrow["row"], arrow["col"]) for arrow in self.game.arrows}
        row, col = next(
            (row, col)
            for row in range(6)
            for col in range(6)
            if (row, col) not in occupied
        )
        blank_position = (
            BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2,
            BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2,
        )
        self.game.handle_click(blank_position)
        self.assertEqual(self.game.arrows, before_arrows)
        self.assertEqual(self.game.mistakes_left, before_mistakes)
        self.assertEqual(self.game.feedback, "这里没有箭头")

    def test_t15_animation_states_complete_normally(self) -> None:
        arrow = next(item for item in self.game.arrows if not self.game.is_blocked(item))
        self.game.handle_click(arrow_position(arrow))
        for _ in range(17):
            self.game.update(0.016)
        self.assertIsNone(self.game.flying_arrow)
        blocked = next(item for item in self.game.arrows if self.game.is_blocked(item))
        self.game.handle_click(arrow_position(blocked))
        for _ in range(18):
            self.game.update(0.016)
        self.assertEqual(self.game.shake_frame, 0)

    def test_t16_timer_resets_on_restart_and_next_level(self) -> None:
        self.game.elapsed_seconds = 8
        self.game.handle_click(PLAY_RESTART_BUTTON_RECT.center)
        self.assertEqual(self.game.elapsed_seconds, 0)
        solve_current_level(self.game)
        self.game.handle_click(BUTTON_RECT.center)
        self.assertEqual(self.game.elapsed_seconds, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
