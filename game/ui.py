import pygame
from config import *


class Button:
    def __init__(self, x, y, w, h, button_type: str):
        self.rect = pygame.Rect(x, y, w, h)
        self.button_type = button_type  # 'restart', 'undo', 'exit'
        self.state = "normal"  # 'normal' | 'pressed'
        self.visible = True

        self.image_keys = {
            "normal": f"button_{button_type}",
            "pressed": f"button_{button_type}_pressed",
        }

    def draw(self, screen: pygame.Surface, images: dict) -> None:
        if not self.visible:
            return

        key = self.image_keys.get(self.state, self.image_keys["normal"])
        image = images.get(key)

        if image is not None and image.get_width() > 0:
            img = pygame.transform.smoothscale(image, (self.rect.width, self.rect.height))
            screen.blit(img, self.rect)
        else:
            self._draw_fallback(screen)

    def _draw_fallback(self, screen: pygame.Surface) -> None:
        base_color = (220, 200, 170)
        pressed_color = (190, 170, 140)
        color = pressed_color if self.state == "pressed" else base_color

        pygame.draw.rect(screen, color, self.rect, border_radius=18)
        pygame.draw.rect(screen, (120, 100, 80), self.rect, 2, border_radius=18)

        font = pygame.font.Font(None, 26)
        text = self.button_type.capitalize()
        surf = font.render(text, True, (90, 70, 50))
        rect = surf.get_rect(center=self.rect.center)
        screen.blit(surf, rect)

    def handle_event(self, event):
        if not self.visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = "pressed"
                return None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == "pressed":
                pressed_inside = self.rect.collidepoint(event.pos)
                self.state = "normal"
                if pressed_inside:
                    return {"type": "button_click", "button": self.button_type}

        return None

    def set_visible(self, visible: bool) -> None:
        self.visible = visible

    def is_visible(self) -> bool:
        return self.visible


class UI:
    def __init__(self) -> None:
        self.buttons: dict[str, Button] = {}
        self._create_buttons()

    def _create_buttons(self) -> None:
        for key, pos in BUTTON_POSITIONS.items():
            x, y = pos
            self.buttons[key] = Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, key)

    def draw(self, screen: pygame.Surface, images: dict) -> None:
        for button in self.buttons.values():
            button.draw(screen, images)

    def handle_events(self, event):
        for button in self.buttons.values():
            result = button.handle_event(event)
            if isinstance(result, dict):
                return result
        return None

    def update_button_states(self, game_state: str, can_undo: bool = False) -> None:
        if "undo" in self.buttons:
            self.buttons["undo"].set_visible(can_undo)

    def get_button(self, button_type: str) -> Button | None:
        return self.buttons.get(button_type)
