# Project ARES
**AI Responsive Enemy System**

A Python-based pathfinding simulation with two game modes: an interactive Algorithm Arena where you evade AI enemies, and a classic visualization mode for algorithm comparison.

## Team
- **Abdul Rauf** (@abdulraufdev) - Algorithms (Search + Local Planners)
- **Asaad Bin Amir** - Visuals & Sound (HUD, Theme, SFX)
- **Basim Khurram Gul** (@Basim-Gul) - Gameplay, UI, Repo/CI, Logging

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

## Game Modes

### 🎮 Algorithm Arena (New!)
An interactive survival game where you evade an AI enemy using pathfinding algorithms.

**Objective**: Survive as long as possible while the enemy hunts you using various pathfinding algorithms!

**How to Play**:
- Click on adjacent nodes to move
- Use abilities to outsmart the enemy
- The enemy gets faster or slower depending on the algorithm
- Watch out - the enemy recalculates its path every move!

**Player Abilities**:
- **Q - Shield**: Become invincible for 3 seconds (10s cooldown)
- **W - Teleport**: Jump to a nearby node (8s cooldown)
- **E - Block Node**: Place an obstacle to trap the enemy (12s cooldown)
- **R - Increase Weight**: Make nearby paths costly for the enemy (6s cooldown, 5s duration)

**Enemy AI Speeds** (time between moves):
- BFS: 600ms (slower, explores thoroughly)
- DFS: 600ms (slower, explores deeply)
- UCS: 500ms (medium, considers weights)
- Greedy: 400ms (faster, rushes toward goal)
- A*: 500ms (medium, optimal pathfinding)

**Features**:
- 28-node graph for strategic gameplay
- Hover tooltips showing node info, edge weights, and connections
- Tooltips work even when paused!
- Visual enemy path and cooldown indicators
- Survival time scoring

### 📊 Classic Mode
Watch pathfinding algorithms compute and visualize paths on a grid in real-time.

**Controls** (Both Modes):
- **1-5**: Switch pathfinding algorithms (BFS, DFS, UCS, Greedy, A*)
- **SPACE**: Pause/Unpause
- **ESC**: Return to menu (Arena mode) / Quit (Classic mode)
- **Hover**: See node details (Arena mode)
- **Click**: Move to adjacent node (Arena mode)

## Project Structure
```
project_ares/
├── main.py              # Entry point with menu system
├── config.py            # Global settings
├── core/                # Core game systems
│   ├── arena_mode.py    # Algorithm Arena gameplay
│   ├── menu.py          # Main menu
│   ├── tutorial.py      # Tutorial screen
│   ├── grid.py          # Grid & navigation
│   ├── models.py        # Data models
│   ├── gameplay.py      # Classic mode logic
│   ├── graphics.py      # Rendering
│   └── ui.py            # Input handling
├── algorithms/          # Pathfinding algorithms
│   ├── bfs.py           # Breadth-First Search
│   ├── dfs.py           # Depth-First Search
│   ├── ucs.py           # Uniform Cost Search
│   ├── greedy.py        # Greedy Best-First
│   ├── astar.py         # A* Search
│   └── locals_planner.py # Tactical planning
└── tests/               # Unit tests
    ├── test_algorithms.py  # Algorithm tests
    └── test_arena_mode.py  # Arena mode tests
```

## Algorithms Implemented
- ✅ BFS (Breadth-First Search)
- ✅ DFS (Depth-First Search)
- ✅ UCS (Uniform Cost Search)
- ✅ Greedy Best-First
- ✅ A* Search
- 🚧 DLS (Depth-Limited Search) - Coming soon
- 🚧 IDS (Iterative Deepening Search) - Coming soon
- 🚧 BDS (Bidirectional Search) - Coming soon
- 🚧 Hill Climbing (Tactical planner) - Coming soon

## Development

### Running Tests
```bash
pytest tests/
```

All 10 tests passing:
- 3 algorithm tests
- 7 arena mode tests (graph generation, pathfinding, abilities, UI)

### Branch Strategy
- `main` - Protected, requires review
- `feature/algorithms` - Abdul's work
- `feature/graphics-ui` - Asaad's work
- `feature/gameplay` - Basim's work

## Recent Updates

### Version 2.0 - Algorithm Arena
- ✨ New interactive game mode with survival gameplay
- 🎯 Player abilities system (Shield, Teleport, Block, Increase Weight)
- 🤖 Smart enemy AI with algorithm-specific speeds
- 💡 Windows-style hover tooltips with node information
- 📚 Comprehensive tutorial screen
- 🎨 Visual feedback for cooldowns and enemy movement
- 🎮 Menu system for easy navigation
- 🧪 Full test coverage for new features

## License
Educational project for AI coursework.
