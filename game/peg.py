import pygame
from config import *


class Peg:
    """
    Одна фішка на дошці.
    row / col – позиція в сітці.
    x / y – піксельні координати (рахуються автоматично).
    """

    def __init__(self, row: int, col: int, state: str = "base"):
        self.row = row
        self.col = col
        # розмір беремо з конфігу, щоб узгодити з отворами
        self.radius = PEG_RADIUS
        self.state = state  # 'base', 'selected', 'hint'
        self.visible = True
        self.update_pixel_position()

    # --- позиціонування --- #

    def update_pixel_position(self) -> None:
        self.x = BOARD_OFFSET_X + self.col * CELL_SIZE + CELL_SIZE // 2
        self.y = BOARD_OFFSET_Y + self.row * CELL_SIZE + CELL_SIZE // 2

    # --- рендеринг --- #

    def draw(self, screen: pygame.Surface, images: dict) -> None:
        if not self.visible:
            return

        if self.state == "selected" and "peg_selected" in images:
            key = "peg_selected"
        elif self.state == "hint" and "peg_hint" in images:
            key = "peg_hint"
        elif "peg_base" in images:
            key = "peg_base"
        else:
            self._draw_fallback(screen)
            return

        size = self.radius * 2
        image = pygame.transform.smoothscale(images[key], (size, size))
        rect = image.get_rect(center=(self.x, self.y))
        screen.blit(image, rect)

    def _draw_fallback(self, screen: pygame.Surface) -> None:
        if self.state == "selected":
            color = BLUE
        elif self.state == "hint":
            color = GREEN
        else:
            color = DARK_GRAY
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)

    # --- стани --- #

    def contains_point(self, pos) -> bool:
        if not self.visible:
            return False
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return (dx * dx + dy * dy) ** 0.5 <= self.radius

    def set_state(self, state: str) -> None:
        if state in ("base", "selected", "hint"):
            self.state = state

    def hide(self) -> None:
        self.visible = False

    def show(self) -> None:
        self.visible = True

    def is_visible(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return f"Peg(row={self.row}, col={self.col}, state={self.state}, visible={self.visible})"
