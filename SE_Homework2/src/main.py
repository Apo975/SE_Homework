"""一箭又一箭：第一阶段的窗口和基础棋盘。"""

import sys
from pathlib import Path

import pygame


WINDOW_WIDTH = 720
WINDOW_HEIGHT = 820
BOARD_SIZE = 6
CELL_SIZE = 90
BOARD_LEFT = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_TOP = 150

BACKGROUND_COLOR = (245, 247, 250)
BOARD_COLOR = (255, 255, 255)
GRID_COLOR = (205, 211, 220)
TEXT_COLOR = (35, 40, 50)
FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")
ARROW_COLOR = (70, 125, 220)
ARROW_HEAD_COLOR = (45, 90, 180)

# 第一关的固定箭头数据。row 和 col 表示箭头所在的棋盘格。
ARROWS = [
    {"row": 0, "col": 0, "direction": "right"},
    {"row": 1, "col": 4, "direction": "down"},
    {"row": 3, "col": 2, "direction": "left"},
    {"row": 5, "col": 5, "direction": "up"},
]


def draw_board(screen: pygame.Surface) -> None:
    """绘制空的 6×6 游戏棋盘。"""
    board_width = BOARD_SIZE * CELL_SIZE
    board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, board_width, board_width)
    pygame.draw.rect(screen, BOARD_COLOR, board_rect, border_radius=8)

    for row in range(BOARD_SIZE + 1):
        y = BOARD_TOP + row * CELL_SIZE
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (BOARD_LEFT, y),
            (BOARD_LEFT + board_width, y),
            width=2,
        )

    for col in range(BOARD_SIZE + 1):
        x = BOARD_LEFT + col * CELL_SIZE
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, BOARD_TOP),
            (x, BOARD_TOP + board_width),
            width=2,
        )


def load_font(size: int) -> pygame.font.Font:
    """直接加载 Windows 中文字体，避免 Pygame 自动扫描字体异常。"""
    if FONT_PATH.exists():
        return pygame.font.Font(str(FONT_PATH), size)
    return pygame.font.Font(None, size)


def draw_arrow(screen: pygame.Surface, arrow: dict) -> None:
    """在指定的棋盘格中绘制一个箭头。"""
    row = arrow["row"]
    col = arrow["col"]
    direction = arrow["direction"]

    center_x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2
    center_y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2
    half_length = 28
    head_width = 22

    if direction == "up":
        shaft_start = (center_x, center_y + half_length)
        shaft_end = (center_x, center_y - half_length)
        head = [
            (center_x, center_y - half_length - 12),
            (center_x - head_width, center_y - half_length + 12),
            (center_x + head_width, center_y - half_length + 12),
        ]
    elif direction == "down":
        shaft_start = (center_x, center_y - half_length)
        shaft_end = (center_x, center_y + half_length)
        head = [
            (center_x, center_y + half_length + 12),
            (center_x - head_width, center_y + half_length - 12),
            (center_x + head_width, center_y + half_length - 12),
        ]
    elif direction == "left":
        shaft_start = (center_x + half_length, center_y)
        shaft_end = (center_x - half_length, center_y)
        head = [
            (center_x - half_length - 12, center_y),
            (center_x - half_length + 12, center_y - head_width),
            (center_x - half_length + 12, center_y + head_width),
        ]
    else:  # right
        shaft_start = (center_x - half_length, center_y)
        shaft_end = (center_x + half_length, center_y)
        head = [
            (center_x + half_length + 12, center_y),
            (center_x + half_length - 12, center_y - head_width),
            (center_x + half_length - 12, center_y + head_width),
        ]

    pygame.draw.line(screen, ARROW_COLOR, shaft_start, shaft_end, width=12)
    pygame.draw.polygon(screen, ARROW_HEAD_COLOR, head)


def draw_arrows(screen: pygame.Surface) -> None:
    """绘制当前关卡中的全部箭头。"""
    for arrow in ARROWS:
        draw_arrow(screen, arrow)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("一箭又一箭")
    clock = pygame.time.Clock()
    font = load_font(32)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        title = font.render("一箭又一箭", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 70))
        screen.blit(title, title_rect)
        draw_board(screen)
        draw_arrows(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
