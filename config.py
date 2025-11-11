"""Global configuration for Project ARES."""

# Window settings
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
FPS = 60

# Grid settings (legacy - for backwards compatibility)
CELL_SIZE = 24
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Graph settings
GRAPH_NUM_NODES = 15
GRAPH_TOPOLOGY = 'mesh'  # 'mesh', 'grid', 'ring'
NODE_RADIUS = 12
EDGE_LINE_WIDTH = 2

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

# Node visualization colors
COLOR_NODE_DEFAULT = (60, 60, 80)
COLOR_NODE_PLAYER = (100, 150, 255)
COLOR_NODE_ENEMY = (255, 100, 100)
COLOR_NODE_VISITED = (100, 100, 120)
COLOR_NODE_OPEN = (150, 200, 255)
COLOR_NODE_TARGET = (100, 255, 100)
COLOR_NODE_BLOCKED = (80, 50, 50)
COLOR_EDGE = (80, 80, 100)
COLOR_EDGE_WEIGHT = (150, 150, 170)

# Gameplay settings
OBSTACLE_RATIO = 0.25
DEFAULT_SEED = 42
MOVE_DELAY_MS = 100  # milliseconds between path steps (legacy)
MELEE_RANGE = 3  # cells

# Movement speed settings (milliseconds)
SPEED_FAST = 300      # For edges with weight 1-2
SPEED_NORMAL = 600    # For edges with weight 3-5
SPEED_SLOW = 1200     # For edges with weight 6-10

# Player abilities
ABILITY_WEIGHT_MULTIPLIER = 5.0  # How much to increase edge weight
ABILITY_COOLDOWN_MS = 3000  # Cooldown between ability uses

# Victory/Defeat conditions
SURVIVAL_TIME_SECONDS = 120  # Time to survive for victory
PLAYER_MAX_HP = 100
ENEMY_MAX_HP = 100

# Algorithm names
ALGORITHMS = {
    '1': 'BFS',
    '2': 'DFS',
    '3': 'UCS',
    '4': 'Greedy',
    '5': 'A*'
}

# Algorithm-specific UI displays
UI_DISPLAYS = {
    'BFS': ['Nodes Explored', 'Path Length', 'Frontier Size'],
    'DFS': ['Nodes Explored', 'Path Length', 'Stack Depth'],
    'UCS': ['Path Cost', 'Nodes Explored', 'Path Length', 'Total Distance'],
    'Greedy': ['Heuristic Value', 'Nodes Explored', 'Path Length'],
    'A*': ['f(n) = g(n) + h(n)', 'Path Cost (g)', 'Heuristic (h)', 'Total Cost (f)', 'Nodes Explored', 'Path Length']
}