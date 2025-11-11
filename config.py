"""Global configuration for Project ARES."""

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60

# Arena/Graph visualization settings
NODE_RADIUS = 18
NODE_COUNT = 25  # Number of nodes in the arena
EDGE_WIDTH = 3
SELECTED_NODE_RADIUS = 22

# Modern Color Scheme (Dark theme with vibrant accents)
COLOR_BACKGROUND = (15, 15, 25)
COLOR_GRID_LINE = (40, 45, 60)
COLOR_WALL = (45, 50, 65)
COLOR_FLOOR = (25, 28, 40)

# Node colors
COLOR_NODE = (50, 55, 75)
COLOR_NODE_BORDER = (80, 90, 120)
COLOR_NODE_VISITED = (100, 70, 150)
COLOR_NODE_FRONTIER = (70, 130, 180)

# Edge colors
COLOR_EDGE = (60, 65, 85)
COLOR_EDGE_ACTIVE = (100, 180, 255)

# Agent colors
COLOR_PLAYER = (100, 200, 255)
COLOR_PLAYER_GLOW = (60, 150, 255)
COLOR_ENEMY = (255, 80, 100)
COLOR_ENEMY_GLOW = (255, 40, 60)
COLOR_GOAL = (255, 215, 0)
COLOR_GOAL_GLOW = (255, 180, 0)

# Path colors
COLOR_PATH = (0, 255, 150)
COLOR_PATH_GLOW = (0, 200, 120)

# UI colors
COLOR_TEXT = (230, 230, 240)
COLOR_TEXT_DIM = (150, 155, 170)
COLOR_TEXT_HIGHLIGHT = (100, 200, 255)
COLOR_HUD_BG = (25, 28, 40, 200)
COLOR_BUTTON = (50, 60, 85)
COLOR_BUTTON_HOVER = (70, 85, 120)
COLOR_BUTTON_ACTIVE = (90, 110, 150)

# Gameplay settings
OBSTACLE_RATIO = 0.15  # For arena mode, obstacles are blocked nodes
DEFAULT_SEED = 42
MOVE_DELAY_MS = 200  # milliseconds between path steps (for enemy only)
MELEE_RANGE = 3  # cells

# Movement animation durations based on edge weight (in milliseconds)
ANIMATION_DURATION_FAST = 400    # For weights 1-2
ANIMATION_DURATION_MEDIUM = 700  # For weights 3-5
ANIMATION_DURATION_SLOW = 1400   # For weights 6-10

# Algorithm names (for initial selection only, no mid-game switching)
ALGORITHMS = {
    'BFS': 'BFS',
    'DFS': 'DFS',
    'UCS': 'UCS',
    'Greedy': 'Greedy',
    'A*': 'A*'
}

def get_animation_duration(weight: float) -> float:
    """Get animation duration in milliseconds based on edge weight."""
    if weight <= 2:
        return ANIMATION_DURATION_FAST
    elif weight <= 5:
        return ANIMATION_DURATION_MEDIUM
    else:
        return ANIMATION_DURATION_SLOW