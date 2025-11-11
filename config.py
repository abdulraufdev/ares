"""Global configuration for Project ARES."""

# Window settings
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
FPS = 60

# Grid settings
CELL_SIZE = 24
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Colors (R, G, B)
COLOR_BACKGROUND = (20, 20, 30)
COLOR_GRID_LINE = (50, 50, 60)
COLOR_WALL = (60, 60, 70)
COLOR_FLOOR = (30, 30, 40)
COLOR_PATH = (0, 255, 100)
COLOR_PLAYER = (100, 150, 255)
COLOR_ENEMY = (255, 100, 100)
COLOR_TEXT = (220, 220, 220)
COLOR_HUD_BG = (40, 40, 50)

# Gameplay settings
OBSTACLE_RATIO = 0.25
DEFAULT_SEED = 42
MOVE_DELAY_MS = 100  # milliseconds between path steps
MELEE_RANGE = 3  # cells

# Algorithm names
ALGORITHMS = {
    '1': 'BFS',
    '2': 'DFS',
    '3': 'UCS',
    '4': 'Greedy',
    '5': 'A*'
}