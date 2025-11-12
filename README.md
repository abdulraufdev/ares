# Algorithm Arena
**Educational Graph-Based Pathfinding Game**

A Python-based interactive game that teaches pathfinding algorithms through engaging gameplay. Players navigate a graph network while an AI enemy uses different algorithms to chase them.

## Features

### 🎮 Interactive Gameplay
- Beautiful interconnected graph with 28 nodes
- Click-to-move navigation system
- Real-time enemy pathfinding visualization
- Combat system with health tracking
- Algorithm-specific movement speeds

### 🧠 Educational Algorithms
Choose from 5 classic pathfinding algorithms:
- **BFS** (Breadth-First Search) - Ocean Blue theme
- **DFS** (Depth-First Search) - Purple Mystery theme
- **UCS** (Uniform Cost Search) - Green Mountain theme
- **Greedy** (Greedy Best-First) - Lightning Yellow theme
- **A*** (A* Search) - Desert Orange theme

### 🎨 Beautiful Visuals
- Unique color themes for each algorithm
- Glowing effects for player and enemy
- Real-time path highlighting
- Algorithm-specific metrics display
- Hover tooltips with node information

### 📊 Detailed Statistics
- Victory/Defeat screens with comprehensive stats
- Nodes explored tracking
- Path cost calculations
- Time tracking
- Movement history

## Team
- **Abdul Rauf** (@abdulraufdev) - Algorithms (Search + Local Planners)
- **Asaad Bin Amir** - Visuals & Sound (HUD, Theme, SFX)
- **Basim Khurram Gul** (@Basim-Gul) - Gameplay, UI, Repo/CI, Logging

## Screenshots

### Main Menu
![Main Menu](screenshots/menu_screenshot.png)

### Tutorial
![Tutorial](screenshots/tutorial_screenshot.png)

### Gameplay - BFS (Ocean Blue Theme)
![BFS Gameplay](screenshots/gameplay_bfs_screenshot.png)

### Gameplay - A* (Desert Orange Theme)
![A* Gameplay](screenshots/gameplay_astar_screenshot.png)

### Victory Screen
![Victory](screenshots/victory_screenshot.png)

## Quick Start

### Installation
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Run
```bash
python main.py
```

## Controls
- **Mouse Click**: Move to adjacent nodes
- **Mouse Hover**: View node information (works during pause!)
- **SPACE**: Pause/Unpause game
- **ESC**: Return to main menu

## Project Structure
```
algorithm_arena/
├── main.py              # Main game loop and state management
├── config.py            # Game settings and theme configurations
├── core/                # Core game systems
│   ├── node.py          # Node class for graph
│   ├── graph.py         # Graph generation and management
│   ├── gameplay.py      # Game session and entity logic
│   ├── graphics.py      # Rendering system
│   ├── menu.py          # Menu and UI components
│   ├── combat.py        # Combat system
│   └── models.py        # Data models
├── algorithms/          # Pathfinding algorithms
│   ├── graph_algorithms.py  # Graph-based implementations
│   ├── bfs.py           # Breadth-First Search (grid)
│   ├── dfs.py           # Depth-First Search (grid)
│   ├── ucs.py           # Uniform Cost Search (grid)
│   ├── greedy.py        # Greedy Best-First (grid)
│   └── astar.py         # A* Search (grid)
├── screenshots/         # Game screenshots
└── tests/               # Unit tests
```

## How It Works

### Graph Generation
- Creates 28 interconnected nodes with organic layout
- Each node connects to 3-6 neighbors
- Edge weights range from 1-10
- Ensures full graph connectivity

### Pathfinding Visualization
- Enemy recalculates path when player moves
- Path is highlighted in real-time with bright colors
- Movement speed varies by algorithm type
- Algorithm-specific metrics displayed in UI

### Combat System
- Player: 100 HP | Enemy: 150 HP
- Contact damage: 10 HP per collision
- Damage cooldown: 1 second
- Victory: Defeat enemy or trap them (no path)
- Defeat: Player HP reaches 0

## Algorithms Explained

### BFS (Breadth-First Search)
- Explores nodes level by level
- Guarantees shortest path (by number of nodes)
- Good for unweighted graphs
- **Enemy Speed**: Slower (600ms between moves)

### DFS (Depth-First Search)
- Explores as deep as possible first
- May not find shortest path
- Memory efficient
- **Enemy Speed**: Slower (600ms between moves)

### UCS (Uniform Cost Search)
- Considers edge weights
- Finds lowest-cost path
- Optimal for weighted graphs
- **Enemy Speed**: Medium (500ms between moves)

### Greedy Best-First
- Uses heuristic to goal
- Fast but not optimal
- Can get stuck in local minima
- **Enemy Speed**: Faster (400ms between moves)

### A* (A* Search)
- Combines UCS and Greedy
- Uses f(n) = g(n) + h(n)
- Optimal and efficient
- **Enemy Speed**: Medium (500ms between moves)

## Educational Value

This game teaches:
- Graph theory concepts
- Pathfinding algorithm behavior
- Heuristic functions
- Trade-offs between optimality and speed
- Real-time algorithm visualization

## Development

### Running Tests
```bash
pytest tests/
```

## License
Educational project for AI coursework.
