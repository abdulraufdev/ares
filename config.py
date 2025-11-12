"""Global configuration for Algorithm Arena."""

# Window settings
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
FPS = 60

# Graph settings
NUM_NODES = 28
GRAPH_SEED = 42

# Node rendering
NODE_RADIUS = 25
NODE_LABEL_FONT_SIZE = 14
EDGE_WIDTH = 2
ENEMY_PATH_WIDTH = 4

# Algorithm names
ALGORITHMS = [
    'BFS',
    'DFS',
    'UCS',
    'Greedy (Local Min)',
    'Greedy (Local Max)',
    'A* (Local Min)',
    'A* (Local Max)'
]

# Algorithm-specific themes
THEMES = {
    'BFS': {
        'name': 'Ocean Blue',
        'background': (15, 25, 45),
        'node_default': (60, 80, 120),
        'node_visited': (40, 60, 90),
        'player': (100, 200, 255),
        'enemy': (255, 100, 100),
        'enemy_path': (0, 255, 255),
        'edge': (80, 100, 140),
        'text': (200, 220, 255),
        'ui_accent': (100, 200, 255),
    },
    'DFS': {
        'name': 'Purple Mystery',
        'background': (25, 15, 35),
        'node_default': (80, 60, 120),
        'node_visited': (60, 40, 90),
        'player': (180, 100, 255),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 100, 255),
        'edge': (100, 80, 140),
        'text': (220, 200, 255),
        'ui_accent': (180, 100, 255),
    },
    'UCS': {
        'name': 'Green Mountain',
        'background': (15, 30, 20),
        'node_default': (60, 120, 80),
        'node_visited': (40, 90, 60),
        'player': (100, 255, 150),
        'enemy': (255, 100, 100),
        'enemy_path': (150, 255, 100),
        'edge': (80, 140, 100),
        'text': (200, 255, 220),
        'ui_accent': (100, 255, 150),
    },
    'Greedy (Local Min)': {
        'name': 'Lightning Yellow',
        'background': (35, 30, 15),
        'node_default': (120, 100, 60),
        'node_visited': (90, 75, 45),
        'player': (255, 230, 100),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 255, 100),
        'edge': (140, 120, 80),
        'text': (255, 240, 200),
        'ui_accent': (255, 230, 100),
    },
    'Greedy (Local Max)': {
        'name': 'Lightning Yellow',
        'background': (35, 30, 15),
        'node_default': (120, 100, 60),
        'node_visited': (90, 75, 45),
        'player': (255, 230, 100),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 255, 100),
        'edge': (140, 120, 80),
        'text': (255, 240, 200),
        'ui_accent': (255, 230, 100),
    },
    'A* (Local Min)': {
        'name': 'Desert Orange',
        'background': (35, 20, 15),
        'node_default': (120, 80, 60),
        'node_visited': (90, 60, 45),
        'player': (255, 150, 80),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 100, 50),
        'edge': (140, 100, 80),
        'text': (255, 220, 200),
        'ui_accent': (255, 150, 80),
    },
    'A* (Local Max)': {
        'name': 'Desert Orange',
        'background': (35, 20, 15),
        'node_default': (120, 80, 60),
        'node_visited': (90, 60, 45),
        'player': (255, 150, 80),
        'enemy': (255, 100, 100),
        'enemy_path': (255, 100, 50),
        'edge': (140, 100, 80),
        'text': (255, 220, 200),
        'ui_accent': (255, 150, 80),
    }
}

# Enemy AI settings
ENEMY_SPEEDS = {
    'BFS': 800,     # milliseconds between moves
    'DFS': 800,
    'UCS': 700,
    'Greedy (Local Min)': 600,  # Faster - rushes!
    'Greedy (Local Max)': 600,
    'A* (Local Min)': 700,
    'A* (Local Max)': 700
}

# Animation settings
ANIMATION_BASE_SPEED = 0.5  # seconds for BFS/DFS

# Combat settings
PLAYER_HP = 100
ENEMY_HP = 150
CONTACT_DAMAGE = 10
DAMAGE_COOLDOWN = 1000  # milliseconds

# Tooltip settings
TOOLTIP_BG = (255, 255, 225)
TOOLTIP_BORDER = (0, 0, 0)
TOOLTIP_TEXT = (0, 0, 0)
TOOLTIP_PADDING = 8

# UI Colors
UI_BUTTON_BG = (60, 60, 80)
UI_BUTTON_HOVER = (80, 80, 100)
UI_BUTTON_ACTIVE = (40, 40, 60)
UI_BUTTON_TEXT = (255, 255, 255)
UI_BUTTON_RADIUS = 10

# Game states
STATE_MENU = 'menu'
STATE_TUTORIAL = 'tutorial'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_VICTORY = 'victory'
STATE_DEFEAT = 'defeat'