"""一箭又一箭：第一阶段的窗口和基础棋盘。"""

import sys
import math
from pathlib import Path

import pygame


WINDOW_WIDTH = 720
WINDOW_HEIGHT = 920
BOARD_SIZE = 6
CELL_SIZE = 90
BOARD_LEFT = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_TOP = 150

BACKGROUND_COLOR = (55, 45, 105)
BOARD_COLOR = (245, 242, 255)
GRID_COLOR = (221, 215, 242)
TEXT_COLOR = (56, 48, 78)
SUBTLE_TEXT_COLOR = (111, 100, 137)
PANEL_COLOR = (249, 247, 255)
SHADOW_COLOR = (31, 24, 67)
HOVER_COLOR = (128, 103, 235)
# 使用独立的黑体文件，避免字体集合和强制加粗造成边缘发糊。
FONT_PATH = Path(r"C:\Windows\Fonts\simhei.ttf")
ARROW_COLOR = (105, 83, 217)
ARROW_HEAD_COLOR = (105, 83, 217)
SELECTED_COLOR = (255, 202, 92)
FEEDBACK_COLOR = (238, 103, 128)
SUCCESS_COLOR = (53, 184, 142)
BLOCKED_COLOR = (232, 79, 105)
BUTTON_COLOR = (105, 83, 217)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RECT = pygame.Rect(270, 815, 180, 48)
PLAY_RESTART_BUTTON_RECT = pygame.Rect(585, 725, 115, 52)
PAUSE_BUTTON_RECT = pygame.Rect(585, 785, 115, 52)
START_BUTTON_RECT = pygame.Rect(270, 505, 180, 55)
DIRECTION_COLORS = {
    "up": (89, 126, 247),
    "down": (239, 113, 116),
    "left": (67, 187, 154),
    "right": (247, 166, 72),
}

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
    """绘制带悬浮层次的 6×6 游戏棋盘。"""
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


def load_font(size: int) -> pygame.font.Font:
    """直接加载 Windows 中文字体，避免 Pygame 自动扫描字体异常。"""
    if FONT_PATH.exists():
        font = pygame.font.Font(str(FONT_PATH), size)
    else:
        font = pygame.font.Font(None, size)
    return font


def draw_cartoon_background(screen: pygame.Surface) -> None:
    """绘制深紫渐变与柔和光斑。"""
    top = (48, 39, 96)
    bottom = (105, 75, 157)
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
    arrow_color = color or DIRECTION_COLORS[direction]

    # 圆形徽章底座，让箭头像独立的游戏棋子。
    pygame.draw.circle(screen, (122, 110, 154), (center_x, center_y + 4), 35)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 35)
    pygame.draw.circle(screen, (232, 227, 247), (center_x, center_y), 35, width=2)
    pygame.draw.circle(screen, (255, 255, 255), (center_x - 10, center_y - 11), 11)

    # 箭头使用偏移阴影、主色和高光三层，增强立体感。
    shadow_points = [(x + 2, y + 4) for x, y in points]
    pygame.draw.polygon(screen, (72, 61, 99), shadow_points)
    pygame.draw.polygon(screen, arrow_color, points)
    pygame.draw.lines(screen, (255, 255, 255), False, points[:3], width=3)


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
            # 沿箭头方向先前移再返回，同时在垂直方向轻微晃动。
            progress = (18 - shake_frame) / 18
            forward_distance = int(math.sin(math.pi * progress) * 15)
            jitter = int(math.sin(shake_frame * 2.2) * 4)
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
        draw_arrow(screen, arrow, offset, color)
        if index == selected_index:
            rect = pygame.Rect(
                BOARD_LEFT + arrow["col"] * CELL_SIZE + 9,
                BOARD_TOP + arrow["row"] * CELL_SIZE + 9,
                CELL_SIZE - 18,
                CELL_SIZE - 18,
            )
            pygame.draw.rect(screen, SELECTED_COLOR, rect, width=4, border_radius=18)


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


def draw_result_panel(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title: str,
    title_color: tuple[int, int, int],
    button_text: str,
) -> None:
    """在棋盘下方绘制独立的通关或失败结果卡片。"""
    panel = pygame.Rect(145, 710, 430, 175)
    pygame.draw.rect(screen, (31, 24, 67), panel.move(0, 7), border_radius=22)
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=22)
    pygame.draw.rect(screen, (218, 208, 242), panel, width=2, border_radius=22)

    badge = pygame.Rect(245, 728, 230, 54)
    badge_color = (*title_color, 35)
    badge_surface = pygame.Surface(badge.size, pygame.SRCALPHA)
    pygame.draw.rect(badge_surface, badge_color, badge_surface.get_rect(), border_radius=27)
    screen.blit(badge_surface, badge.topleft)

    result = font.render(title, True, title_color)
    result_rect = result.get_rect(center=badge.center)
    screen.blit(result, result_rect)
    draw_button(screen, font, button_text, BUTTON_RECT, pygame.mouse.get_pos())


def draw_feedback_panel(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
) -> None:
    """绘制游戏进行中的反馈提示框。"""
    panel = pygame.Rect(150, 725, 420, 52)
    pygame.draw.rect(screen, (31, 24, 67), panel.move(0, 5), border_radius=18)
    pygame.draw.rect(screen, (249, 247, 255), panel, border_radius=18)
    pygame.draw.rect(screen, (218, 208, 242), panel, width=2, border_radius=18)

    feedback = font.render(text, True, FEEDBACK_COLOR)
    feedback_rect = feedback.get_rect(center=panel.center)
    screen.blit(feedback, feedback_rect)


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
    elapsed_seconds: float,
) -> None:
    """绘制游戏中的顶部状态信息。"""
    panel = pygame.Rect(15, 45, 690, 75)
    pygame.draw.rect(screen, SHADOW_COLOR, panel.move(0, 5), border_radius=16)
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=16)

    items = [
        ("关卡", f"{current_level + 1}/{level_count}", TEXT_COLOR),
        ("箭头", str(arrow_count), TEXT_COLOR),
        ("失误", str(mistakes_left), FEEDBACK_COLOR if mistakes_left <= 1 else TEXT_COLOR),
        ("计时", format_time(elapsed_seconds), TEXT_COLOR),
    ]
    centers = (100, 275, 450, 620)
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


def format_time(elapsed_seconds: float) -> str:
    """将秒数格式化为分:秒。"""
    total_seconds = int(elapsed_seconds)
    return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"


def draw_pause_overlay(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """绘制暂停遮罩。"""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((25, 19, 55, 135))
    screen.blit(overlay, (0, 0))

    card = pygame.Rect(195, 350, 330, 130)
    pygame.draw.rect(screen, (31, 24, 67), card.move(0, 7), border_radius=22)
    pygame.draw.rect(screen, PANEL_COLOR, card, border_radius=22)
    title = font.render("游戏已暂停", True, TEXT_COLOR)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 398))
    screen.blit(title, title_rect)
    hint = font.render("点击继续按钮恢复游戏", True, SUBTLE_TEXT_COLOR)
    hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, 442))
    screen.blit(hint, hint_rect)


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
    elapsed_seconds = 0.0
    is_paused = False
    flying_arrow = None
    flying_progress = 0.0
    shake_index = None
    shake_frame = 0

    running = True
    while running:
        delta_time = clock.tick(60) / 1000
        if game_state == "playing" and not is_paused:
            elapsed_seconds += delta_time

        if flying_arrow is not None and not is_paused:
            flying_progress += 0.06
            if flying_progress >= 1:
                flying_arrow = None
                flying_progress = 0.0
                if not ARROWS:
                    game_state = "success"

        if shake_frame > 0 and not is_paused:
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
                        elapsed_seconds = 0.0
                        is_paused = False
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
                            game_state = "start"
                            continue
                        reset_game(current_level)
                        selected_index = None
                        mistakes_left = 3
                        feedback = "请点击一个箭头"
                        game_state = "playing"
                        elapsed_seconds = 0.0
                        is_paused = False
                        flying_arrow = None
                        flying_progress = 0.0
                        shake_index = None
                        shake_frame = 0
                    continue
                if PAUSE_BUTTON_RECT.collidepoint(event.pos):
                    is_paused = not is_paused
                    feedback = "游戏已暂停" if is_paused else "继续游戏"
                    continue
                if is_paused:
                    continue
                if mistakes_left == 0:
                    feedback = "失误次数已用完，请重新开始"
                    continue
                if PLAY_RESTART_BUTTON_RECT.collidepoint(event.pos):
                    reset_game(current_level)
                    selected_index = None
                    mistakes_left = 3
                    feedback = "已重新开始当前关卡"
                    elapsed_seconds = 0.0
                    is_paused = False
                    flying_arrow = None
                    flying_progress = 0.0
                    shake_index = None
                    shake_frame = 0
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
            continue

        draw_status_panel(
            screen,
            status_font,
            current_level,
            len(LEVELS),
            len(ARROWS),
            mistakes_left,
            elapsed_seconds,
        )
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
            if is_paused:
                draw_pause_overlay(screen, font)
            draw_feedback_panel(screen, font, feedback)
            draw_button(
                screen,
                status_font,
                "重开",
                PLAY_RESTART_BUTTON_RECT,
                pygame.mouse.get_pos(),
            )
            draw_button(
                screen,
                status_font,
                "继续" if is_paused else "暂停",
                PAUSE_BUTTON_RECT,
                pygame.mouse.get_pos(),
            )

        if game_state == "success":
            button_text = "下一关" if current_level < len(LEVELS) - 1 else "返回开始"
            draw_result_panel(screen, font, "恭喜通关！", SUCCESS_COLOR, button_text)
        elif game_state == "failed":
            draw_result_panel(screen, font, "挑战失败", FEEDBACK_COLOR, "重新开始")

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
