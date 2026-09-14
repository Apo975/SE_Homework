"""一箭又一箭：第一阶段的窗口和基础棋盘。"""

import sys
import math
from pathlib import Path

import pygame


WINDOW_WIDTH = 720
WINDOW_HEIGHT = 820
BOARD_SIZE = 6
CELL_SIZE = 90
BOARD_LEFT = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_TOP = 150

BACKGROUND_COLOR = (184, 232, 255)
BOARD_COLOR = (255, 253, 241)
GRID_COLOR = (224, 194, 139)
TEXT_COLOR = (75, 63, 82)
SUBTLE_TEXT_COLOR = (116, 103, 120)
PANEL_COLOR = (255, 249, 224)
SHADOW_COLOR = (118, 184, 205)
HOVER_COLOR = (255, 166, 86)
# 使用独立的黑体文件，避免字体集合和强制加粗造成边缘发糊。
FONT_PATH = Path(r"C:\Windows\Fonts\simhei.ttf")
ARROW_COLOR = (255, 157, 73)
ARROW_HEAD_COLOR = (239, 103, 74)
SELECTED_COLOR = (255, 209, 75)
FEEDBACK_COLOR = (225, 87, 92)
SUCCESS_COLOR = (68, 166, 116)
BLOCKED_COLOR = (224, 79, 94)
BUTTON_COLOR = (92, 174, 225)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RECT = pygame.Rect(270, 755, 180, 45)
START_BUTTON_RECT = pygame.Rect(270, 505, 180, 55)

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
    shadow_rect = board_rect.move(0, 7)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=14)
    pygame.draw.rect(screen, BOARD_COLOR, board_rect, border_radius=14)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                cell_rect = pygame.Rect(
                    BOARD_LEFT + col * CELL_SIZE + 2,
                    BOARD_TOP + row * CELL_SIZE + 2,
                    CELL_SIZE - 4,
                    CELL_SIZE - 4,
                )
                pygame.draw.rect(screen, (255, 248, 224), cell_rect, border_radius=5)

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
        font = pygame.font.Font(str(FONT_PATH), size)
    else:
        font = pygame.font.Font(None, size)
    return font


def draw_cartoon_background(screen: pygame.Surface) -> None:
    """绘制统一的卡通天空背景和装饰。"""
    screen.fill(BACKGROUND_COLOR)

    # 太阳
    pygame.draw.circle(screen, (255, 220, 94), (635, 70), 34)
    pygame.draw.circle(screen, (255, 235, 132), (635, 70), 25)

    # 云朵
    for x, y in ((78, 82), (535, 180), (120, 720)):
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 22)
        pygame.draw.circle(screen, (255, 255, 255), (x + 25, y - 10), 30)
        pygame.draw.circle(screen, (255, 255, 255), (x + 58, y), 22)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, 58, 22), border_radius=10)

    # 底部草地
    pygame.draw.rect(screen, (139, 211, 137), (0, 805, WINDOW_WIDTH, 15))


def draw_arrow(
    screen: pygame.Surface,
    arrow: dict,
    offset: tuple[int, int] = (0, 0),
    color: tuple[int, int, int] | None = None,
) -> None:
    """在指定的棋盘格中绘制一个箭头。"""
    row = arrow["row"]
    col = arrow["col"]
    direction = arrow["direction"]

    center_x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2 + offset[0]
    center_y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2 + offset[1]
    # 以向右为基准的圆润箭头轮廓，再根据方向旋转。
    base_points = [
        (-28, -12),
        (8, -12),
        (8, -25),
        (35, 0),
        (8, 25),
        (8, 12),
        (-28, 12),
    ]

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
    arrow_color = color or ARROW_COLOR
    pygame.draw.polygon(screen, (111, 75, 84), points)
    inner_points = [
        transform((int(x * 0.9), int(y * 0.9))) for x, y in base_points
    ]
    pygame.draw.polygon(screen, arrow_color, inner_points)
    pygame.draw.lines(screen, (255, 224, 158), False, inner_points[:3], width=3)


def draw_arrows(
    screen: pygame.Surface,
    selected_index: int | None = None,
    shake_index: int | None = None,
    shake_frame: int = 0,
) -> None:
    """绘制当前关卡中的全部箭头。"""
    for index, arrow in enumerate(ARROWS):
        offset = (0, 0)
        color = None
        if index == shake_index and shake_frame > 0:
            offset = (int(math.sin(shake_frame * 1.8) * 8), 0)
            color = BLOCKED_COLOR
        draw_arrow(screen, arrow, offset, color)
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


def draw_button(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    rect: pygame.Rect = BUTTON_RECT,
    mouse_pos: tuple[int, int] | None = None,
) -> None:
    """绘制重新开始按钮。"""
    color = HOVER_COLOR if mouse_pos and rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, SHADOW_COLOR, rect.move(0, 4), border_radius=10)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    button_text = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, text_rect)


def draw_start_screen(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """绘制游戏开始界面。"""
    card = pygame.Rect(100, 90, 520, 550)
    pygame.draw.rect(screen, SHADOW_COLOR, card.move(0, 8), border_radius=20)
    pygame.draw.rect(screen, PANEL_COLOR, card, border_radius=20)

    title = font.render("一箭又一箭", True, TEXT_COLOR)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 175))
    screen.blit(title, title_rect)

    instruction_lines = ("按照合适的顺序点击箭头", "清空棋盘即可通关")
    for index, line in enumerate(instruction_lines):
        instruction = font.render(line, True, SUBTLE_TEXT_COLOR)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 300 + index * 42))
        screen.blit(instruction, instruction_rect)

    draw_button(screen, font, "开始游戏", START_BUTTON_RECT, pygame.mouse.get_pos())


def draw_status_panel(
    screen: pygame.Surface,
    font: pygame.font.Font,
    current_level: int,
    level_count: int,
    arrow_count: int,
    mistakes_left: int,
) -> None:
    """绘制游戏中的顶部状态信息。"""
    panel = pygame.Rect(40, 45, 640, 75)
    pygame.draw.rect(screen, SHADOW_COLOR, panel.move(0, 5), border_radius=16)
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=16)

    items = [
        ("关卡", f"{current_level + 1}/{level_count}", TEXT_COLOR),
        ("箭头", str(arrow_count), TEXT_COLOR),
        ("失误", str(mistakes_left), FEEDBACK_COLOR if mistakes_left <= 1 else TEXT_COLOR),
    ]
    centers = (150, 360, 570)
    for (label_text, value_text, value_color), center_x in zip(items, centers):
        label = font.render(label_text, True, SUBTLE_TEXT_COLOR)
        value = font.render(value_text, True, value_color)
        gap = 8
        total_width = label.get_width() + gap + value.get_width()
        start_x = center_x - total_width // 2
        label_rect = label.get_rect(midleft=(start_x, 82))
        value_rect = value.get_rect(midleft=(label_rect.right + gap, 82))
        screen.blit(label, label_rect)
        screen.blit(value, value_rect)


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
    status_font = load_font(24)
    selected_index = None
    feedback = "请点击一个箭头"
    mistakes_left = 3
    game_state = "start"
    current_level = 0
    flying_arrow = None
    flying_progress = 0.0
    shake_index = None
    shake_frame = 0

    running = True
    while running:
        if flying_arrow is not None:
            flying_progress += 0.06
            if flying_progress >= 1:
                flying_arrow = None
                flying_progress = 0.0
                if not ARROWS:
                    game_state = "success"

        if shake_frame > 0:
            shake_frame -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "start":
                    if START_BUTTON_RECT.collidepoint(event.pos):
                        reset_game(0)
                        current_level = 0
                        mistakes_left = 3
                        selected_index = None
                        feedback = "请点击一个箭头"
                        game_state = "playing"
                        flying_arrow = None
                        flying_progress = 0.0
                        shake_index = None
                        shake_frame = 0
                    continue
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
                        flying_arrow = None
                        flying_progress = 0.0
                        shake_index = None
                        shake_frame = 0
                    continue
                if mistakes_left == 0:
                    feedback = "失误次数已用完，请重新开始"
                    continue
                selected_index = get_arrow_at_position(event.pos)
                if selected_index is None:
                    feedback = "这里没有箭头"
                elif is_blocked(ARROWS[selected_index], ARROWS):
                    mistakes_left -= 1
                    shake_index = selected_index
                    shake_frame = 18
                    selected_index = None
                    if mistakes_left == 0:
                        feedback = "失误次数已用完"
                        game_state = "failed"
                    else:
                        feedback = f"前方有阻挡，失误次数 -1"
                else:
                    flying_arrow = ARROWS.pop(selected_index)
                    flying_progress = 0.0
                    selected_index = None
                    feedback = "箭头飞出棋盘"

        draw_cartoon_background(screen)
        if game_state == "start":
            draw_start_screen(screen, font)
            pygame.display.flip()
            clock.tick(60)
            continue

        draw_status_panel(screen, status_font, current_level, len(LEVELS), len(ARROWS), mistakes_left)
        draw_board(screen)
        draw_arrows(screen, selected_index, shake_index, shake_frame)
        if flying_arrow is not None:
            distance = int(520 * flying_progress)
            direction = flying_arrow["direction"]
            offset = {
                "up": (0, -distance),
                "down": (0, distance),
                "left": (-distance, 0),
                "right": (distance, 0),
            }[direction]
            draw_arrow(screen, flying_arrow, offset)
        if game_state == "playing":
            feedback_text = font.render(feedback, True, FEEDBACK_COLOR)
            feedback_rect = feedback_text.get_rect(center=(WINDOW_WIDTH // 2, 730))
            screen.blit(feedback_text, feedback_rect)

        if game_state == "success":
            result = font.render("恭喜通关！", True, SUCCESS_COLOR)
            result_rect = result.get_rect(center=(WINDOW_WIDTH // 2, 715))
            screen.blit(result, result_rect)
            button_text = "下一关" if current_level < len(LEVELS) - 1 else "重新开始"
            draw_button(screen, font, button_text, BUTTON_RECT, pygame.mouse.get_pos())
        elif game_state == "failed":
            result = font.render("挑战失败", True, FEEDBACK_COLOR)
            result_rect = result.get_rect(center=(WINDOW_WIDTH // 2, 715))
            screen.blit(result, result_rect)
            draw_button(screen, font, "重新开始", BUTTON_RECT, pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
