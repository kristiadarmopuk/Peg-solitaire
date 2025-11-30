import time
import random
import pygame

from config import *
from game.peg import Peg


class Board:
    """
    Логіка дошки:
    - 7x7, але дозволені клітинки задає BOARD_MASK
    - старт: усі дозволені заповнені фішками, центр порожній
    - хід: фішка стрибає через сусідню в порожній отвір
    """

    def __init__(self) -> None:
        self.cells: list[list[Peg | None]] = [
            [None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)
        ]
        self.selected_peg: Peg | None = None
        self.valid_moves: list[dict] = []
        self.move_history: list[dict] = []

        # автопідказка
        self.last_action_time = time.time()
        self.hint_source: Peg | None = None
        self.hint_move: dict | None = None

        self.initialize_board()

    # --- ініціалізація --- #

    def initialize_board(self) -> None:
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if BOARD_MASK[r][c] == 1:
                    if r == 3 and c == 3:
                        self.cells[r][c] = None
                    else:
                        self.cells[r][c] = Peg(r, c, "base")
                else:
                    self.cells[r][c] = None

    # --- утиліти --- #

    def board_pos_from_pixel(self, pos):
        x, y = pos
        if not (
            BOARD_OFFSET_X <= x < BOARD_OFFSET_X + BOARD_COLS * CELL_SIZE
            and BOARD_OFFSET_Y <= y < BOARD_OFFSET_Y + BOARD_ROWS * CELL_SIZE
        ):
            return None

        col = (x - BOARD_OFFSET_X) // CELL_SIZE
        row = (y - BOARD_OFFSET_Y) // CELL_SIZE
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and BOARD_MASK[row][col] == 1:
            return row, col
        return None

    def get_peg_at(self, row, col) -> Peg | None:
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return self.cells[row][col]
        return None

    def is_valid_cell(self, row, col) -> bool:
        return (
            0 <= row < BOARD_ROWS
            and 0 <= col < BOARD_COLS
            and BOARD_MASK[row][col] == 1
        )

    # --- рендеринг --- #

    def draw(self, screen: pygame.Surface, images: dict) -> None:
        self._draw_board_background(screen, images)
        self._draw_holes(screen, images)
        self._draw_hint_holes(screen, images)

        # звичайні фішки
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                peg = self.cells[r][c]
                if peg and peg.is_visible():
                    peg.draw(screen, images)

        # підсвітити фішку, якою ходити при підказці (якщо нема обраної)
        if (
            self.selected_peg is None
            and self.hint_source is not None
            and self.hint_source.is_visible()
        ):
            self._draw_hint_source_peg(screen, images)

    def _draw_board_background(self, screen: pygame.Surface, images: dict) -> None:
        """Малюємо дерев'яну дошку (Pole.png) по центру сітки."""
        if "board" not in images:
            return

        img = images["board"]

        # розміри сітки з отворами
        grid_w = BOARD_COLS * CELL_SIZE
        grid_h = BOARD_ROWS * CELL_SIZE
        grid_cx = BOARD_OFFSET_X + grid_w // 2
        grid_cy = BOARD_OFFSET_Y + grid_h // 2

        # дошка трохи більша за сітку
        base_size = max(grid_w, grid_h)
        board_size = int(base_size * 1.25)

        scaled = pygame.transform.smoothscale(img, (board_size, board_size))
        rect = scaled.get_rect(center=(grid_cx, grid_cy))
        screen.blit(scaled, rect)

    def _draw_holes(self, screen: pygame.Surface, images: dict) -> None:
        """
        Малюємо усі виямки (вони завжди видимі).
        Робимо їх трохи більшими за кульки – розмір HOLE_DIAMETER.
        """
        hole_img_raw = images.get("hole")
        if hole_img_raw is None:
            return

        hole_empty_raw = images.get("hole_empty", hole_img_raw)

        hole_img = pygame.transform.smoothscale(
            hole_img_raw, (HOLE_DIAMETER, HOLE_DIAMETER)
        )
        hole_empty_img = pygame.transform.smoothscale(
            hole_empty_raw, (HOLE_DIAMETER, HOLE_DIAMETER)
        )

        offset_in_cell = (CELL_SIZE - HOLE_DIAMETER) // 2

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if BOARD_MASK[r][c] != 1:
                    continue

                peg = self.cells[r][c]
                img = hole_img if peg and peg.is_visible() else hole_empty_img

                x = BOARD_OFFSET_X + c * CELL_SIZE + offset_in_cell
                y = BOARD_OFFSET_Y + r * CELL_SIZE + offset_in_cell
                screen.blit(img, (x, y))

    def _draw_hint_holes(self, screen: pygame.Surface, images: dict) -> None:
        """Малюємо зелені виямки для можливих ходів, точно по центру."""
        hint_raw = images.get("hole_hint")
        if hint_raw is None:
            return

        # збільшений розмір хінту
        hint_size = int(HOLE_DIAMETER * 1.55)
        hint_img = pygame.transform.smoothscale(hint_raw, (hint_size, hint_size))

        # позиція центру виямки
        base_offset = (CELL_SIZE - HOLE_DIAMETER) // 2
        
        # різниця між збільшеним і справжнім отвором
        center_fix = (hint_size - HOLE_DIAMETER) // 2

        def draw_hint_at(r, c):
            x = BOARD_OFFSET_X + c * CELL_SIZE + base_offset - center_fix
            y = BOARD_OFFSET_Y + r * CELL_SIZE + base_offset - center_fix
            screen.blit(hint_img, (x, y))

        # можливі ходи для вибраної фішки
        for move in self.valid_moves:
            tr, tc = move["target"]
            draw_hint_at(tr, tc)

        # автопідказка
        if self.selected_peg is None and self.hint_move is not None:
            tr, tc = self.hint_move["target"]
            draw_hint_at(tr, tc)

    def _draw_hint_source_peg(self, screen: pygame.Surface, images: dict) -> None:
        """Підсвічуємо фішку, якою потрібно ходити (для підказки H)."""
        peg = self.hint_source
        if peg is None:
            return

        if "peg_hint" in images:
            size = peg.radius * 2
            img = pygame.transform.smoothscale(images["peg_hint"], (size, size))
            rect = img.get_rect(center=(peg.x, peg.y))
            screen.blit(img, rect)
        else:
            pygame.draw.circle(screen, GREEN, (peg.x, peg.y), peg.radius + 4, 3)

    # --- кліки --- #

    def handle_click(self, pos) -> bool:
        """Обробка кліку по дошці. True, якщо стався хід."""
        board_pos = self.board_pos_from_pixel(pos)
        if board_pos is None:
            return False

        row, col = board_pos
        clicked_peg = self.get_peg_at(row, col)

        # будь-який клік скидає таймер автопідказки
        self.last_action_time = time.time()
        self.hint_source = None
        self.hint_move = None

        if clicked_peg and clicked_peg.is_visible():
            return self._handle_peg_click(clicked_peg)
        else:
            return self._handle_empty_click(row, col)

    def _handle_peg_click(self, peg: Peg) -> bool:
        if self.selected_peg is peg:
            self.selected_peg.set_state("base")
            self.selected_peg = None
            self.valid_moves.clear()
            return False

        # зняти попередній вибір
        if self.selected_peg:
            self.selected_peg.set_state("base")

        self.selected_peg = peg
        self.selected_peg.set_state("selected")
        self.valid_moves = self._get_valid_moves(peg)
        return False

    def _handle_empty_click(self, row: int, col: int) -> bool:
        if not self.selected_peg:
            return False

        for move in self.valid_moves:
            if move["target"] == (row, col):
                self._make_move(move)
                return True

        # клік на порожній клітинці без ходу – скидаємо вибір
        self.selected_peg.set_state("base")
        self.selected_peg = None
        self.valid_moves.clear()
        return False

    # --- пошук ходів --- #

    def _get_valid_moves(self, peg: Peg) -> list[dict]:
        moves: list[dict] = []
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]

        for dr, dc in directions:
            mid_r = peg.row + dr // 2
            mid_c = peg.col + dc // 2
            tr = peg.row + dr
            tc = peg.col + dc

            if self._is_valid_move(peg.row, peg.col, mid_r, mid_c, tr, tc):
                moves.append(
                    {
                        "source": (peg.row, peg.col),
                        "middle": (mid_r, mid_c),
                        "target": (tr, tc),
                    }
                )

        return moves

    def _is_valid_move(
        self,
        sr: int,
        sc: int,
        mid_r: int,
        mid_c: int,
        tr: int,
        tc: int,
    ) -> bool:
        if not (
            self.is_valid_cell(sr, sc)
            and self.is_valid_cell(mid_r, mid_c)
            and self.is_valid_cell(tr, tc)
        ):
            return False

        source_peg = self.get_peg_at(sr, sc)
        middle_peg = self.get_peg_at(mid_r, mid_c)
        target_peg = self.get_peg_at(tr, tc)

        if source_peg is None or not source_peg.is_visible():
            return False

        if middle_peg is None or not middle_peg.is_visible():
            return False

        if target_peg is not None and target_peg.is_visible():
            return False

        return True

    # --- виконання ходу / undo --- #

    def _make_move(self, move: dict) -> None:
        sr, sc = move["source"]
        mr, mc = move["middle"]
        tr, tc = move["target"]

        moving_peg = self.cells[sr][sc]
        jumped_peg = self.cells[mr][mc]

        self.move_history.append(
            {
                "source": (sr, sc),
                "middle": (mr, mc),
                "target": (tr, tc),
            }
        )

        # рух
        self.cells[sr][sc] = None
        self.cells[tr][tc] = moving_peg
        if moving_peg:
            moving_peg.row = tr
            moving_peg.col = tc
            moving_peg.update_pixel_position()
            moving_peg.set_state("base")

        # з'їли середню
        if jumped_peg:
            jumped_peg.hide()

        self.selected_peg = None
        self.valid_moves.clear()

    def undo_move(self) -> bool:
        if not self.move_history:
            return False

        last = self.move_history.pop()
        sr, sc = last["source"]
        mr, mc = last["middle"]
        tr, tc = last["target"]

        moving_peg = self.cells[tr][tc]
        jumped_peg = self.cells[mr][mc]

        self.cells[tr][tc] = None
        self.cells[sr][sc] = moving_peg
        if moving_peg:
            moving_peg.row = sr
            moving_peg.col = sc
            moving_peg.update_pixel_position()
            moving_peg.set_state("base")

        if jumped_peg:
            jumped_peg.show()

        self.selected_peg = None
        self.valid_moves.clear()
        self.last_action_time = time.time()
        self.hint_source = None
        self.hint_move = None
        return True

    # --- підказки --- #

    def update_hints(self) -> None:
        if self.selected_peg is not None:
            return

        now = time.time()
        if now - self.last_action_time < HINT_DELAY / 1000:
            return

        self._show_best_hint()

    def _show_best_hint(self) -> None:
        self.hint_source = None
        self.hint_move = None

        all_moves: list[tuple[Peg, dict]] = []

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                peg = self.cells[r][c]
                if peg and peg.is_visible():
                    for move in self._get_valid_moves(peg):
                        all_moves.append((peg, move))

        if not all_moves:
            return

        center_r, center_c = 3, 3
        scored = []
        for peg, move in all_moves:
            tr, tc = move["target"]
            dist = abs(tr - center_r) + abs(tc - center_c)
            scored.append((dist, peg, move))

        scored.sort(key=lambda x: x[0])
        best_dist = scored[0][0]
        candidates = [item for item in scored if item[0] == best_dist]
        _, peg, move = random.choice(candidates)

        self.hint_source = peg
        self.hint_move = move

    # --- стани гри --- #

    def get_peg_count(self) -> int:
        cnt = 0
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                peg = self.cells[r][c]
                if peg and peg.is_visible():
                    cnt += 1
        return cnt

    def has_valid_moves(self) -> bool:
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                peg = self.cells[r][c]
                if peg and peg.is_visible():
                    if self._get_valid_moves(peg):
                        return True
        return False

    def reset(self) -> None:
        self.__init__()
