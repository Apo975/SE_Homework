"""一箭又一箭的游戏逻辑、界面绘制与运行循环。"""

import math
import sys
from pathlib import Path

import pygame


WINDOW_WIDTH = 720
WINDOW_HEIGHT = 760
BOARD_SIZE = 6
CELL_SIZE = 70
BOARD_LEFT = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_TOP = 110

TEXT_COLOR = (56, 48, 78)
SUBTLE_TEXT_COLOR = (111, 100, 137)
PANEL_COLOR = (249, 247, 255)
SHADOW_COLOR = (31, 24, 67)
HOVER_COLOR = (128, 103, 235)
FONT_PATH = Path(r"C:\Windows\Fonts\simhei.ttf")
TITLE_FONT_PATH = Path(r"C:\Windows\Fonts\Dengb.ttf")
SELECTED_COLOR = (255, 202, 92)
FEEDBACK_COLOR = (238, 103, 128)
SUCCESS_COLOR = (53, 184, 142)
BLOCKED_COLOR = (232, 79, 105)
BUTTON_COLOR = (105, 83, 217)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RECT = pygame.Rect(270, 650, 180, 46)
FINAL_BUTTON_RECT = pygame.Rect(270, 450, 180, 48)
PLAY_RESTART_BUTTON_RECT = pygame.Rect(585, 550, 115, 46)
PAUSE_BUTTON_RECT = pygame.Rect(585, 610, 115, 46)
START_BUTTON_RECT = pygame.Rect(270, 440, 180, 50)
START_EXIT_BUTTON_RECT = pygame.Rect(270, 505, 180, 44)
PAUSE_EXIT_BUTTON_RECT = pygame.Rect(285, 405, 150, 44)
DIRECTION_COLORS = {
    "up": (89, 126, 247),
    "down": (239, 113, 116),
    "left": (67, 187, 154),
    "right": (247, 166, 72),
}

LEVELS = [
    [
        {"row": 2, "col": 0, "direction": "right"},
        {"row": 2, "col": 3, "direction": "up"},
        {"row": 0, "col": 4, "direction": "down"},
        {"row": 4, "col": 4, "direction": "left"},
        {"row": 5, "col": 5, "direction": "up"},
        {"row": 0, "col": 0, "direction": "right"},
    ],
    [
        {"row": 1, "col": 1, "direction": "down"},
        {"row": 4, "col": 1, "direction": "down"},
        {"row": 4, "col": 5, "direction": "left"},
        {"row": 4, "col": 3, "direction": "up"},
        {"row": 0, "col": 5, "direction": "down"},
        {"row": 5, "col": 0, "direction": "right"},
        {"row": 3, "col": 0, "direction": "up"},
    ],
    [
        {"row": 0, "col": 2, "direction": "down"},
        {"row": 3, "col": 2, "direction": "right"},
        {"row": 3, "col": 5, "direction": "down"},
        {"row": 3, "col": 1, "direction": "right"},
        {"row": 5, "col": 4, "direction": "up"},
        {"row": 1, "col": 0, "direction": "down"},
        {"row": 5, "col": 0, "direction": "right"},
        {"row": 1, "col": 5, "direction": "left"},
    ],
]


class ArrowGame:
    """管理关卡数据、交互状态、动画与绘制。"""

    def __init__(self) -> None:
        self.arrows = []
        self.current_level = 0
        self.mistakes_left = 3
        self.game_state = "start"
        self.selected_index: int | None = None
        self.feedback = "请点击一个箭头"
        self.elapsed_seconds = 0.0
        self.is_paused = False
        self.flying_arrow: dict | None = None
        self.flying_progress = 0.0
        self.shake_index: int | None = None
        self.shake_frame = 0
        self.should_exit = False
        self.font: pygame.font.Font | None = None
        self.status_font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.reset_level(0)

    @staticmethod
    def load_font(size: int, font_path: Path = FONT_PATH) -> pygame.font.Font:
        if font_path.exists():
            return pygame.font.Font(str(font_path), size)
        return pygame.font.Font(None, size)

    def reset_level(self, level_index: int | None = None) -> None:
        if level_index is not None:
            self.current_level = level_index
        self.arrows = [arrow.copy() for arrow in LEVELS[self.current_level]]
        self.selected_index = None
        self.mistakes_left = 3
        self.feedback = "请点击一个箭头"
        self.elapsed_seconds = 0.0
        self.is_paused = False
        self.flying_arrow = None
        self.flying_progress = 0.0
        self.shake_index = None
        self.shake_frame = 0

    @staticmethod
    def format_time(elapsed_seconds: float) -> str:
        total_seconds = int(elapsed_seconds)
        return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"

    def is_blocked(self, arrow: dict) -> bool:
        row, col, direction = arrow["row"], arrow["col"], arrow["direction"]
        for other in self.arrows:
            if other is arrow:
                continue
            other_row, other_col = other["row"], other["col"]
            if direction == "up" and other_col == col and other_row < row:
                return True
            if direction == "down" and other_col == col and other_row > row:
                return True
            if direction == "left" and other_row == row and other_col < col:
                return True
            if direction == "right" and other_row == row and other_col > col:
                return True
        return False

    def get_arrow_at_position(self, position: tuple[int, int]) -> int | None:
        mouse_x, mouse_y = position
        if not (
            BOARD_LEFT <= mouse_x < BOARD_LEFT + BOARD_SIZE * CELL_SIZE
            and BOARD_TOP <= mouse_y < BOARD_TOP + BOARD_SIZE * CELL_SIZE
        ):
            return None
        col = (mouse_x - BOARD_LEFT) // CELL_SIZE
        row = (mouse_y - BOARD_TOP) // CELL_SIZE
        for index, arrow in enumerate(self.arrows):
            if arrow["row"] == row and arrow["col"] == col:
                return index
        return None

    def update(self, delta_time: float) -> None:
        if self.game_state == "playing" and not self.is_paused:
            self.elapsed_seconds += delta_time
            if self.flying_arrow is not None:
                self.flying_progress += 0.06
                if self.flying_progress >= 1:
                    self.flying_arrow = None
                    self.flying_progress = 0.0
                    if not self.arrows:
                        self.game_state = "success"
            if self.shake_frame > 0:
                self.shake_frame -= 1

    def handle_click(self, position: tuple[int, int]) -> None:
        if self.game_state == "start":
            if START_BUTTON_RECT.collidepoint(position):
                self.reset_level(0)
                self.game_state = "playing"
            elif START_EXIT_BUTTON_RECT.collidepoint(position):
                self.should_exit = True
            return

        if self.game_state != "playing":
            is_final_success = self.game_state == "success" and self.current_level == len(LEVELS) - 1
            action_rect = FINAL_BUTTON_RECT if is_final_success else BUTTON_RECT
            if action_rect.collidepoint(position):
                if self.game_state == "success" and self.current_level < len(LEVELS) - 1:
                    self.reset_level(self.current_level + 1)
                    self.game_state = "playing"
                elif self.game_state == "success":
                    self.current_level = 0
                    self.game_state = "start"
                else:
                    self.reset_level()
                    self.game_state = "playing"
            return

        if PAUSE_BUTTON_RECT.collidepoint(position):
            self.is_paused = not self.is_paused
            self.feedback = "游戏已暂停" if self.is_paused else "继续游戏"
            return
        if PLAY_RESTART_BUTTON_RECT.collidepoint(position):
            self.reset_level()
            self.feedback = "已重新开始当前关卡"
            return
        if self.is_paused:
            if PAUSE_EXIT_BUTTON_RECT.collidepoint(position):
                self.current_level = 0
                self.game_state = "start"
                self.is_paused = False
            return

        self.selected_index = self.get_arrow_at_position(position)
        if self.selected_index is None:
            self.feedback = "这里没有箭头"
            return
        if self.is_blocked(self.arrows[self.selected_index]):
            self.mistakes_left -= 1
            self.shake_index = self.selected_index
            self.shake_frame = 18
            self.selected_index = None
            if self.mistakes_left == 0:
                self.feedback = "失误次数已用完"
                self.game_state = "failed"
            else:
                self.feedback = "前方有阻挡，失误次数 -1"
            return

        self.flying_arrow = self.arrows.pop(self.selected_index)
        self.flying_progress = 0.0
        self.selected_index = None
        self.feedback = "箭头飞出棋盘"

    @staticmethod
    def draw_button(
        screen: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        rect: pygame.Rect,
        mouse_pos: tuple[int, int],
    ) -> None:
        color = HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, SHADOW_COLOR, rect.move(0, 4), border_radius=10)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        text_surface = font.render(text, True, BUTTON_TEXT_COLOR)
        screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    @staticmethod
    def draw_background(screen: pygame.Surface) -> None:
        top, bottom = (48, 39, 96), (105, 75, 157)
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color = tuple(int(a + (b - a) * ratio) for a, b in zip(top, bottom))
            pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
        glow = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for position, radius, color in (
            ((90, 110), 105, (108, 190, 255, 32)),
            ((655, 165), 125, (255, 135, 195, 28)),
            ((580, 720), 145, (126, 255, 211, 20)),
        ):
            pygame.draw.circle(glow, color, position, radius)
        screen.blit(glow, (0, 0))
        for x, y, radius in ((65, 220, 3), (665, 315, 4), (54, 650, 4), (650, 610, 3)):
            pygame.draw.circle(screen, (226, 218, 255), (x, y), radius)

    @staticmethod
    def draw_board(screen: pygame.Surface) -> None:
        board_width = BOARD_SIZE * CELL_SIZE
        board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, board_width, board_width)
        frame_rect = board_rect.inflate(22, 22)
        pygame.draw.rect(screen, (32, 25, 70), frame_rect.move(0, 8), border_radius=28)
        pygame.draw.rect(screen, (224, 218, 246), frame_rect, border_radius=28)
        pygame.draw.rect(screen, (184, 171, 226), frame_rect, width=2, border_radius=28)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell_rect = pygame.Rect(
                    BOARD_LEFT + col * CELL_SIZE + 4,
                    BOARD_TOP + row * CELL_SIZE + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8,
                )
                cell_color = (252, 250, 255) if (row + col) % 2 == 0 else (242, 238, 252)
                pygame.draw.rect(screen, (177, 166, 214), cell_rect.move(0, 3), border_radius=15)
                pygame.draw.rect(screen, cell_color, cell_rect, border_radius=15)
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, width=2, border_radius=15)

    @staticmethod
    def draw_arrow(
        screen: pygame.Surface,
        arrow: dict,
        offset: tuple[int, int] = (0, 0),
        color: tuple[int, int, int] | None = None,
    ) -> None:
        row, col, direction = arrow["row"], arrow["col"], arrow["direction"]
        center_x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2 + offset[0]
        center_y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2 + offset[1]
        base_points = [(-22, -9), (6, -9), (6, -20), (28, 0), (6, 20), (6, 9), (-22, 9)]

        def transform(point: tuple[int, int]) -> tuple[int, int]:
            x, y = point
            if direction == "down":
                x, y = -y, x
            elif direction == "left":
                x, y = -x, -y
            elif direction == "up":
                x, y = y, -x
            return center_x + x, center_y + y

        points = [transform(point) for point in base_points]
        arrow_color = color or DIRECTION_COLORS[direction]
        pygame.draw.circle(screen, (122, 110, 154), (center_x, center_y + 4), 28)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 28)
        pygame.draw.circle(screen, (232, 227, 247), (center_x, center_y), 28, width=2)
        pygame.draw.circle(screen, (255, 255, 255), (center_x - 8, center_y - 9), 8)
        pygame.draw.polygon(screen, (72, 61, 99), [(x + 2, y + 4) for x, y in points])
        pygame.draw.polygon(screen, arrow_color, points)
        pygame.draw.lines(screen, (255, 255, 255), False, points[:3], width=3)

    def draw_arrows(self, screen: pygame.Surface) -> None:
        for index, arrow in enumerate(self.arrows):
            offset, color = (0, 0), None
            if index == self.shake_index and self.shake_frame > 0:
                progress = (18 - self.shake_frame) / 18
                forward_distance = int(math.sin(math.pi * progress) * 15)
                jitter = int(math.sin(self.shake_frame * 2.2) * 4)
                direction = arrow["direction"]
                if direction == "up":
                    offset = (jitter, -forward_distance)
                elif direction == "down":
                    offset = (jitter, forward_distance)
                elif direction == "left":
                    offset = (-forward_distance, jitter)
                else:
                    offset = (forward_distance, jitter)
                color = BLOCKED_COLOR
            self.draw_arrow(screen, arrow, offset, color)
            if index == self.selected_index:
                rect = pygame.Rect(
                    BOARD_LEFT + arrow["col"] * CELL_SIZE + 9,
                    BOARD_TOP + arrow["row"] * CELL_SIZE + 9,
                CELL_SIZE - 18,
                CELL_SIZE - 18,
                )
                pygame.draw.rect(screen, SELECTED_COLOR, rect, width=4, border_radius=18)

    def draw_start_screen(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        assert self.font is not None and self.title_font is not None and self.small_font is not None
        card = pygame.Rect(100, 40, 520, 550)
        pygame.draw.rect(screen, SHADOW_COLOR, card.move(0, 8), border_radius=20)
        pygame.draw.rect(screen, PANEL_COLOR, card, border_radius=20)

        eyebrow = self.small_font.render("ARROW PUZZLE", True, (105, 83, 217))
        screen.blit(eyebrow, eyebrow.get_rect(center=(WINDOW_WIDTH // 2, 92)))
        title_card = pygame.Rect(145, 112, 430, 78)
        pygame.draw.rect(screen, (202, 192, 232), title_card.move(0, 5), border_radius=18)
        pygame.draw.rect(screen, (255, 255, 255), title_card, border_radius=18)
        pygame.draw.rect(screen, (183, 168, 226), title_card, width=2, border_radius=18)
        pygame.draw.rect(screen, (105, 83, 217), (185, 112, 350, 5), border_radius=3)
        title = self.title_font.render("一箭又一箭", True, TEXT_COLOR)
        screen.blit(title, title.get_rect(center=title_card.center))
        subtitle = self.small_font.render("观察方向，规划顺序，解开棋盘谜题", True, SUBTLE_TEXT_COLOR)
        screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 210)))

        pygame.draw.line(screen, (222, 214, 242), (165, 240), (555, 240), width=2)
        rules = (
            ("01", "前方无阻挡，箭头即可飞出棋盘"),
            ("02", "错误点击会消耗一次失误机会"),
            ("03", "清空全部箭头即可通过当前关卡"),
        )
        for index, (number, text) in enumerate(rules):
            y = 285 + index * 48
            pygame.draw.circle(screen, (232, 227, 247), (185, y), 16)
            number_surface = self.small_font.render(number, True, (105, 83, 217))
            screen.blit(number_surface, number_surface.get_rect(center=(185, y)))
            rule_surface = self.small_font.render(text, True, TEXT_COLOR)
            screen.blit(rule_surface, rule_surface.get_rect(midleft=(215, y)))
        self.draw_button(screen, self.font, "开始游戏", START_BUTTON_RECT, mouse_pos)
        self.draw_button(screen, self.status_font or self.font, "退出游戏", START_EXIT_BUTTON_RECT, mouse_pos)

    def draw_status_panel(self, screen: pygame.Surface) -> None:
        assert self.status_font is not None
        panel = pygame.Rect(15, 20, 690, 64)
        pygame.draw.rect(screen, SHADOW_COLOR, panel.move(0, 5), border_radius=16)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=16)
        items = [
            ("关卡", f"{self.current_level + 1}/{len(LEVELS)}", TEXT_COLOR),
            ("箭头", str(len(self.arrows)), TEXT_COLOR),
            ("失误", str(self.mistakes_left), FEEDBACK_COLOR if self.mistakes_left <= 1 else TEXT_COLOR),
            ("计时", self.format_time(self.elapsed_seconds), TEXT_COLOR),
        ]
        for (label_text, value_text, value_color), center_x in zip(items, (100, 275, 450, 620)):
            label = self.status_font.render(label_text, True, SUBTLE_TEXT_COLOR)
            value = self.status_font.render(value_text, True, value_color)
            start_x = center_x - (label.get_width() + 8 + value.get_width()) // 2
            screen.blit(label, label.get_rect(midleft=(start_x, 52)))
            screen.blit(value, value.get_rect(midleft=(start_x + label.get_width() + 8, 52)))

    def draw_feedback_panel(self, screen: pygame.Surface) -> None:
        assert self.font is not None
        panel = pygame.Rect(150, 550, 420, 46)
        pygame.draw.rect(screen, (31, 24, 67), panel.move(0, 5), border_radius=18)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=18)
        pygame.draw.rect(screen, (218, 208, 242), panel, width=2, border_radius=18)
        feedback = self.font.render(self.feedback, True, FEEDBACK_COLOR)
        screen.blit(feedback, feedback.get_rect(center=panel.center))

    def draw_pause_overlay(self, screen: pygame.Surface) -> None:
        assert self.font is not None
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((25, 19, 55, 135))
        screen.blit(overlay, (0, 0))
        card = pygame.Rect(195, 240, 330, 220)
        pygame.draw.rect(screen, (31, 24, 67), card.move(0, 7), border_radius=22)
        pygame.draw.rect(screen, PANEL_COLOR, card, border_radius=22)
        title = self.font.render("游戏已暂停", True, TEXT_COLOR)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 290)))
        hint = self.font.render("点击继续按钮恢复游戏", True, SUBTLE_TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 335)))

    def draw_result_panel(
        self,
        screen: pygame.Surface,
        title: str,
        title_color: tuple[int, int, int],
        button_text: str,
        mouse_pos: tuple[int, int],
        is_final: bool = False,
        dim_background: bool = False,
    ) -> None:
        assert self.font is not None
        if is_final or dim_background:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((25, 19, 55, 150))
            screen.blit(overlay, (0, 0))
        if is_final:
            panel = pygame.Rect(110, 190, 500, 330)
            badge = pygame.Rect(245, 245, 230, 58)
            action_rect = FINAL_BUTTON_RECT
        else:
            panel = pygame.Rect(145, 535, 430, 175)
            badge = pygame.Rect(245, 553, 230, 52)
            action_rect = BUTTON_RECT
        pygame.draw.rect(screen, (31, 24, 67), panel.move(0, 7), border_radius=22)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=22)
        pygame.draw.rect(screen, (218, 208, 242), panel, width=2, border_radius=22)
        badge_surface = pygame.Surface(badge.size, pygame.SRCALPHA)
        pygame.draw.rect(badge_surface, (*title_color, 35), badge_surface.get_rect(), border_radius=27)
        screen.blit(badge_surface, badge.topleft)
        result = self.font.render(title, True, title_color)
        screen.blit(result, result.get_rect(center=badge.center))
        self.draw_button(screen, self.font, button_text, action_rect, mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        self.draw_background(screen)
        mouse_pos = pygame.mouse.get_pos()
        if self.game_state == "start":
            self.draw_start_screen(screen, mouse_pos)
            return
        self.draw_status_panel(screen)
        self.draw_board(screen)
        self.draw_arrows(screen)
        if self.flying_arrow is not None:
            distance = int(520 * self.flying_progress)
            offset = {
                "up": (0, -distance), "down": (0, distance),
                "left": (-distance, 0), "right": (distance, 0),
            }[self.flying_arrow["direction"]]
            self.draw_arrow(screen, self.flying_arrow, offset)
        if self.game_state == "playing":
            if self.is_paused:
                self.draw_pause_overlay(screen)
            self.draw_feedback_panel(screen)
            assert self.status_font is not None
            self.draw_button(screen, self.status_font, "重开", PLAY_RESTART_BUTTON_RECT, mouse_pos)
            self.draw_button(screen, self.status_font, "继续" if self.is_paused else "暂停", PAUSE_BUTTON_RECT, mouse_pos)
            if self.is_paused:
                self.draw_button(screen, self.status_font, "退出至菜单", PAUSE_EXIT_BUTTON_RECT, mouse_pos)
        elif self.game_state == "success":
            button_text = "下一关" if self.current_level < len(LEVELS) - 1 else "返回开始"
            self.draw_result_panel(
                screen,
                "恭喜通关！",
                SUCCESS_COLOR,
                button_text,
                mouse_pos,
                is_final=self.current_level == len(LEVELS) - 1,
            )
        else:
            self.draw_result_panel(
                screen,
                "挑战失败",
                FEEDBACK_COLOR,
                "重新开始",
                mouse_pos,
                dim_background=True,
            )

    def run(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        clock = pygame.time.Clock()
        self.font = self.load_font(32)
        self.status_font = self.load_font(24)
        self.title_font = self.load_font(46, TITLE_FONT_PATH)
        self.small_font = self.load_font(20)
        running = True
        while running:
            delta_time = clock.tick(60) / 1000
            self.update(delta_time)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                    if self.should_exit:
                        running = False
            self.draw(screen)
            pygame.display.flip()
        pygame.quit()
        sys.exit()
