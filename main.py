import sys
import pygame

from config import *
from game.board import Board
from game.ui import UI


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Peg Solitaire")
        self.clock = pygame.time.Clock()

        self.running = True
        self.state = STATE_PLAYING

        self.images: dict[str, pygame.Surface] = {}
        self._load_assets()

        self.board = Board()
        self.ui = UI()

        self.font_main = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    # --- ресурси --- #

    def _load_assets(self) -> None:
        for key, path in IMAGE_PATHS.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.images[key] = img
                print(f"✓ Завантажено: {key} -> {path}")
            except Exception as e:
                print(f"⚠ Не вдалось завантажити {path}: {e}")
                # прозора заглушка
                surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))
                self.images[key] = surf

    # --- цикл --- #

    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    # --- події --- #

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self._restart()
                elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self._undo()
                elif event.key == pygame.K_h:
                    # ручний виклик підказки
                    self.board._show_best_hint()

            # спершу UI (кнопки)
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                ui_result = self.ui.handle_events(event)
                if ui_result:
                    self._handle_ui_action(ui_result)
                    continue  # не передаємо цей клік дошці

            # клік по дошці
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.state == STATE_PLAYING
            ):
                move_made = self.board.handle_click(event.pos)
                if move_made:
                    self._check_game_over()

    def _handle_ui_action(self, action: dict) -> None:
        btn = action.get("button")
        if btn == "exit":
            self.running = False
        elif btn == "restart":
            self._restart()
        elif btn == "undo":
            self._undo()

    # --- ігрова логіка --- #

    def _restart(self) -> None:
        print("=== RESTART ===")
        self.board = Board()
        self.state = STATE_PLAYING

    def _undo(self) -> None:
        if self.board.undo_move():
            self.state = STATE_PLAYING

    def _check_game_over(self) -> None:
        if not self.board.has_valid_moves():
            self.state = STATE_GAME_OVER
            left = self.board.get_peg_count()
            print(f"Гра завершена. Залишилось фішок: {left}")

    def _update(self) -> None:
        can_undo = len(self.board.move_history) > 0
        self.ui.update_button_states(self.state, can_undo)

        if self.state == STATE_PLAYING:
            self.board.update_hints()

    # --- малювання --- #

    def _draw(self) -> None:
        # легкий теплий фон
        self.screen.fill((253, 241, 219))

        self.board.draw(self.screen, self.images)
        self.ui.draw(self.screen, self.images)

        self._draw_hud()

        if self.state == STATE_GAME_OVER:
            self._draw_game_over_overlay()

        pygame.display.flip()

    def _draw_hud(self) -> None:
        pegs = self.board.get_peg_count()
        moves = len(self.board.move_history)

        text1 = self.font_main.render(f"Фішки: {pegs}", True, BLACK)
        text2 = self.font_main.render(f"Ходи: {moves}", True, BLACK)
        hint_text = self.font_small.render("H – підказка", True, BLACK)

        # Лічильники зверху зліва
        self.screen.blit(text1, (20, 20))
        self.screen.blit(text2, (20, 60))
        # Підказка по клавіші H знизу зліва
        hint_rect = hint_text.get_rect()
        hint_rect.bottomleft = (20, SCREEN_HEIGHT - 15)
        self.screen.blit(hint_text, hint_rect)

    def _draw_game_over_overlay(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        pegs_left = self.board.get_peg_count()
        msg = f"Гра завершена. Залишилось фішок: {pegs_left}"

        if pegs_left == 1:
            score = "Ідеально! 🎉"
        elif pegs_left <= 3:
            score = "Дуже добре! 👍"
        else:
            score = "Спробуй ще раз 🙂"

        msg_surf = self.font_main.render(msg, True, WHITE)
        score_surf = self.font_main.render(score, True, WHITE)
        info_surf = self.font_small.render(
            "Натисни R або кнопку Restart, щоб почати ще раз",
            True,
            WHITE,
        )

        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        info_rect = info_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(msg_surf, msg_rect)
        self.screen.blit(score_surf, score_rect)
        self.screen.blit(info_surf, info_rect)


if __name__ == "__main__":
    Game().run()
