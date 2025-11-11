"""Global configuration for Project ARES."""

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60

# Grid settings
CELL_SIZE = 32
GRID_WIDTH = 30
GRID_HEIGHT = 20

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
ENEMY_PATHFIND_INTERVAL = 500  # milliseconds between enemy path recalculations

# Combat settings
PLAYER_MAX_HP = 100
ENEMY_MAX_HP = 150
CONTACT_DAMAGE = 10
MELEE_DAMAGE = 25
DAMAGE_COOLDOWN_MS = 1000  # milliseconds between damage ticks

# Abilities configuration
ABILITIES = {
    'shield': {
        'key': 'Q',
        'name': 'Shield',
        'duration_ms': 3000,
        'cooldown_ms': 10000,
        'uses': float('inf')  # unlimited uses
    },
    'teleport': {
        'key': 'W',
        'name': 'Teleport',
        'distance': 5,
        'cooldown_ms': 8000,
        'uses': float('inf')
    },
    'block': {
        'key': 'E',
        'name': 'Block Node',
        'cooldown_ms': 0,
        'uses': 5
    },
    'weight': {
        'key': 'R',
        'name': 'Increase Weight',
        'multiplier': 5,
        'cooldown_ms': 0,
        'uses': 3
    }
}

# Algorithm themes (primary, secondary, background, path, visited)
ALGORITHM_THEMES = {
    'BFS': {
        'name': 'Ocean Blue',
        'primary': (50, 150, 255),
        'secondary': (30, 100, 200),
        'background': (15, 25, 40),
        'path': (0, 200, 255),
        'visited': (40, 80, 120),
        'open': (80, 150, 220),
        'closed': (60, 60, 80)
    },
    'DFS': {
        'name': 'Purple Mystery',
        'primary': (180, 50, 255),
        'secondary': (130, 30, 200),
        'background': (25, 15, 35),
        'path': (200, 100, 255),
        'visited': (100, 40, 130),
        'open': (150, 80, 200),
        'closed': (60, 60, 80)
    },
    'UCS': {
        'name': 'Green Mountain',
        'primary': (50, 200, 100),
        'secondary': (30, 150, 70),
        'background': (15, 30, 20),
        'path': (100, 255, 150),
        'visited': (40, 100, 60),
        'open': (80, 180, 120),
        'closed': (60, 80, 60)
    },
    'Greedy': {
        'name': 'Yellow Lightning',
        'primary': (255, 200, 50),
        'secondary': (200, 150, 30),
        'background': (35, 30, 15),
        'path': (255, 220, 100),
        'visited': (130, 100, 40),
        'open': (220, 180, 80),
        'closed': (80, 70, 60)
    },
    'A*': {
        'name': 'Orange Desert',
        'primary': (255, 120, 50),
        'secondary': (200, 90, 30),
        'background': (35, 25, 15),
        'path': (255, 150, 80),
        'visited': (130, 70, 40),
        'open': (220, 130, 70),
        'closed': (80, 65, 60)
    }
}

# Map types for different algorithms
MAP_TYPES = {
    'maze': ['BFS', 'DFS'],
    'weighted': ['UCS', 'A*'],
    'open': ['Greedy']
}

# Algorithm names
ALGORITHMS = {
    '1': 'BFS',
    '2': 'DFS',
    '3': 'UCS',
    '4': 'Greedy',
    '5': 'A*'
}