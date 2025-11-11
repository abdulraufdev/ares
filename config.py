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

# Algorithm-specific themes
THEMES = {
    'BFS': {
        'name': 'Ocean Blue',
        'background': (15, 25, 45),
        'player': (100, 200, 255),
        'enemy': (255, 100, 100),
        'enemy_path': (0, 255, 255),
        'node': (60, 80, 120),
        'node_visited': (30, 40, 60),
        'edge': (40, 60, 100),
        'edge_highlight': (0, 255, 255),
        'text': (220, 240, 255)
    },
    'DFS': {
        'name': 'Purple Mystery',
        'background': (25, 15, 35),
        'player': (180, 100, 255),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 100, 255),
        'node': (80, 60, 120),
        'node_visited': (40, 30, 60),
        'edge': (60, 40, 100),
        'edge_highlight': (255, 100, 255),
        'text': (240, 220, 255)
    },
    'UCS': {
        'name': 'Green Mountain',
        'background': (15, 30, 20),
        'player': (100, 255, 150),
        'enemy': (255, 100, 100),
        'enemy_path': (150, 255, 100),
        'node': (60, 120, 80),
        'node_visited': (30, 60, 40),
        'edge': (40, 100, 60),
        'edge_highlight': (150, 255, 100),
        'text': (220, 255, 240)
    },
    'Greedy': {
        'name': 'Lightning Yellow',
        'background': (35, 30, 15),
        'player': (255, 230, 100),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 255, 100),
        'node': (120, 110, 60),
        'node_visited': (60, 55, 30),
        'edge': (100, 90, 40),
        'edge_highlight': (255, 255, 100),
        'text': (255, 250, 220)
    },
    'A*': {
        'name': 'Desert Orange',
        'background': (35, 20, 15),
        'player': (255, 150, 80),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 100, 50),
        'node': (120, 80, 60),
        'node_visited': (60, 40, 30),
        'edge': (100, 60, 40),
        'edge_highlight': (255, 100, 50),
        'text': (255, 240, 220)
    }
}

# Gameplay settings
OBSTACLE_RATIO = 0.25
DEFAULT_SEED = 42
MOVE_DELAY_MS = 100  # milliseconds between path steps
MELEE_RANGE = 3  # cells

# Graph settings
NUM_NODES = 28
NODE_RADIUS = 25

# Animation speed settings (in seconds)
ANIMATION_SPEEDS = {
    'BFS': lambda weight, heuristic, f_cost: 0.5,  # Constant
    'DFS': lambda weight, heuristic, f_cost: 0.5,  # Constant
    'UCS': lambda weight, heuristic, f_cost: 0.2 + (weight / 10.0) * 1.0,  # 0.2 to 1.2s based on weight
    'Greedy': lambda weight, heuristic, f_cost: 0.3 + (heuristic / 20.0) * 1.2,  # 0.3 to 1.5s based on heuristic
    'A*': lambda weight, heuristic, f_cost: 0.2 + (f_cost / 30.0) * 1.3  # 0.2 to 1.5s based on f-cost
}

# Graph layout per algorithm
GRAPH_LAYOUTS = {
    'BFS': 'maze',
    'DFS': 'maze',
    'UCS': 'organic',
    'Greedy': 'open',
    'A*': 'open'
}

# Algorithm names
ALGORITHMS = {
    '1': 'BFS',
    '2': 'DFS',
    '3': 'UCS',
    '4': 'Greedy',
    '5': 'A*'
}