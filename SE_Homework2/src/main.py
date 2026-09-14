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
SELECTED_COLOR = (245, 180, 45)
FEEDBACK_COLOR = (210, 90, 70)
SUCCESS_COLOR = (45, 155, 90)
BUTTON_COLOR = (70, 125, 220)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RECT = pygame.Rect(270, 755, 180, 45)

# 每个关卡由若干箭头组成，row 和 col 表示箭头所在的棋盘格。
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
ARROWS = [arrow.copy() for arrow in LEVELS[0]]


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


def draw_arrows(screen: pygame.Surface, selected_index: int | None = None) -> None:
    """绘制当前关卡中的全部箭头。"""
    for index, arrow in enumerate(ARROWS):
        draw_arrow(screen, arrow)
        if index == selected_index:
            rect = pygame.Rect(
                BOARD_LEFT + arrow["col"] * CELL_SIZE + 6,
                BOARD_TOP + arrow["row"] * CELL_SIZE + 6,
                CELL_SIZE - 12,
                CELL_SIZE - 12,
            )
            pygame.draw.rect(screen, SELECTED_COLOR, rect, width=4, border_radius=8)


def get_arrow_at_position(position: tuple[int, int]) -> int | None:
    """根据鼠标位置返回被点击的箭头下标。"""
    mouse_x, mouse_y = position
    if not (
        BOARD_LEFT <= mouse_x < BOARD_LEFT + BOARD_SIZE * CELL_SIZE
        and BOARD_TOP <= mouse_y < BOARD_TOP + BOARD_SIZE * CELL_SIZE
    ):
        return None

    col = (mouse_x - BOARD_LEFT) // CELL_SIZE
    row = (mouse_y - BOARD_TOP) // CELL_SIZE
    for index, arrow in enumerate(ARROWS):
        if arrow["row"] == row and arrow["col"] == col:
            return index
    return None


def reset_game(level_index: int) -> None:
    """恢复指定关卡的初始箭头布局。"""
    ARROWS.clear()
    ARROWS.extend(arrow.copy() for arrow in LEVELS[level_index])


def draw_button(screen: pygame.Surface, font: pygame.font.Font, text: str) -> None:
    """绘制重新开始按钮。"""
    pygame.draw.rect(screen, BUTTON_COLOR, BUTTON_RECT, border_radius=8)
    button_text = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = button_text.get_rect(center=BUTTON_RECT.center)
    screen.blit(button_text, text_rect)


def is_blocked(arrow: dict, arrows: list[dict]) -> bool:
    """判断箭头前进方向至棋盘边界之间是否存在其他箭头。"""
    row = arrow["row"]
    col = arrow["col"]
    direction = arrow["direction"]

    for other in arrows:
        if other is arrow:
            continue

        other_row = other["row"]
        other_col = other["col"]
        if direction == "up" and other_col == col and other_row < row:
            return True
        if direction == "down" and other_col == col and other_row > row:
            return True
        if direction == "left" and other_row == row and other_col < col:
            return True
        if direction == "right" and other_row == row and other_col > col:
            return True

    return False


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("一箭又一箭")
    clock = pygame.time.Clock()
    font = load_font(32)
    selected_index = None
    feedback = "请点击一个箭头"
    mistakes_left = 3
    game_state = "playing"
    current_level = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state != "playing":
                    if BUTTON_RECT.collidepoint(event.pos):
                        if game_state == "success" and current_level < len(LEVELS) - 1:
                            current_level += 1
                        elif game_state == "success":
                            current_level = 0
                        reset_game(current_level)
                        selected_index = None
                        mistakes_left = 3
                        feedback = "请点击一个箭头"
                        game_state = "playing"
                    continue
                if mistakes_left == 0:
                    feedback = "失误次数已用完，请重新开始"
                    continue
                selected_index = get_arrow_at_position(event.pos)
                if selected_index is None:
                    feedback = "这里没有箭头"
                elif is_blocked(ARROWS[selected_index], ARROWS):
                    mistakes_left -= 1
                    selected_index = None
                    if mistakes_left == 0:
                        feedback = "失误次数已用完"
                        game_state = "failed"
                    else:
                        feedback = f"前方有阻挡，失误次数 -1"
                else:
                    ARROWS.pop(selected_index)
                    selected_index = None
                    feedback = "箭头飞出棋盘"
                    if not ARROWS:
                        game_state = "success"

        screen.fill(BACKGROUND_COLOR)
        title = font.render("一箭又一箭", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 70))
        screen.blit(title, title_rect)
        status = font.render(
            f"第 {current_level + 1} 关 / {len(LEVELS)}    剩余箭头：{len(ARROWS)}    剩余失误：{mistakes_left}",
            True,
            TEXT_COLOR,
        )
        status_rect = status.get_rect(center=(WINDOW_WIDTH // 2, 115))
        screen.blit(status, status_rect)
        draw_board(screen)
        draw_arrows(screen, selected_index)
        feedback_text = font.render(feedback, True, FEEDBACK_COLOR)
        feedback_rect = feedback_text.get_rect(center=(WINDOW_WIDTH // 2, 730))
        screen.blit(feedback_text, feedback_rect)

        if game_state == "success":
            result = font.render("恭喜通关！", True, SUCCESS_COLOR)
            result_rect = result.get_rect(center=(WINDOW_WIDTH // 2, 680))
            screen.blit(result, result_rect)
            button_text = "下一关" if current_level < len(LEVELS) - 1 else "重新开始"
            draw_button(screen, font, button_text)
        elif game_state == "failed":
            result = font.render("挑战失败", True, FEEDBACK_COLOR)
            result_rect = result.get_rect(center=(WINDOW_WIDTH // 2, 680))
            screen.blit(result, result_rect)
            draw_button(screen, font, "重新开始")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
