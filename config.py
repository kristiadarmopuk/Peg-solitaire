import os

# Шляхи до папок
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Розміри вікна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Налаштування дошки
BOARD_ROWS = 7
BOARD_COLS = 7
CELL_SIZE = 50

# відступ, щоб сітка була по центру
BOARD_OFFSET_X = (SCREEN_WIDTH - BOARD_COLS * CELL_SIZE) // 2
BOARD_OFFSET_Y = 100

# --- Розмір кульки і отвору ---

# Кулька: трохи менша за клітинку
# (якщо хочеш змінити РОЗМІР фішки – міняй тільки цей рядок)
PEG_RADIUS = int(CELL_SIZE * 0.6)        # ≈ 22 px при CELL_SIZE=50
PEG_DIAMETER = PEG_RADIUS * 2

# Отвір: тепер НЕ залежить від PEG_RADIUS
# (можна налаштовувати окремо від фішки)
HOLE_DIAMETER = int(PEG_DIAMETER * 0.75)     # ≈ 46 px при CELL_SIZE=50
# Отвір трохи більший за кульку, але не занадто

# Ігрові стани
STATE_PLAYING = "playing"
STATE_MENU = "menu"
STATE_GAME_OVER = "game_over"

# Затримка для автопідказки (мс)
HINT_DELAY = 30000

# Шляхи до картинок
IMAGE_PATHS = {
    # дошка
    "board": os.path.join(IMAGES_DIR, "Pole.png"),

    # фішки
    "peg_base": os.path.join(IMAGES_DIR, "peg_base.png"),
    "peg_selected": os.path.join(IMAGES_DIR, "peg_selected.png"),
    "peg_hint": os.path.join(IMAGES_DIR, "peg_hint.png"),

    # отвори
    "hole": os.path.join(IMAGES_DIR, "hole.png"),
    "hole_empty": os.path.join(IMAGES_DIR, "hole_empty.png"),
    "hole_hint": os.path.join(IMAGES_DIR, "hole_hint.png"),

    # кнопки
    "button_restart": os.path.join(IMAGES_DIR, "Button(restart).png"),
    "button_undo": os.path.join(IMAGES_DIR, "Button(undo).png"),
    "button_exit": os.path.join(IMAGES_DIR, "Button(Exit).png"),
    "button_restart_pressed": os.path.join(IMAGES_DIR, "Button_pressed (Restart).png"),
    "button_undo_pressed": os.path.join(IMAGES_DIR, "Button_pressed (Undo).png"),
    "button_exit_pressed": os.path.join(IMAGES_DIR, "Button_pressed (Exit).png"),
}

# --- Налаштування кнопок ---

BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40

# відстань між кнопками
BUTTON_SPACING = 20
BUTTON_Y = SCREEN_HEIGHT - 80  # трохи вище краю вікна

center_x = SCREEN_WIDTH // 2

# загальна ширина блоку з трьох кнопок і двох проміжків
total_buttons_width = 3 * BUTTON_WIDTH + 2 * BUTTON_SPACING

# ліва кнопка починається так, щоб увесь блок був по центру
start_x = center_x - total_buttons_width // 2

BUTTON_POSITIONS = {
    "restart": (start_x, BUTTON_Y),
    "undo": (start_x + BUTTON_WIDTH + BUTTON_SPACING, BUTTON_Y),
    "exit": (start_x + 2 * (BUTTON_WIDTH + BUTTON_SPACING), BUTTON_Y),
}

# Маска дошки у формі хреста
BOARD_MASK = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
]
