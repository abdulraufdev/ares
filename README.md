# Project ARES
**AI Responsive Enemy System**

A Python-based grid combat AI simulation demonstrating multiple pathfinding strategies and tactical combat decisions.

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

## Controls
- **1-5**: Switch pathfinding algorithms (BFS, DFS, UCS, Greedy, A*)
- **SPACE**: Pause/Unpause
- **M**: Cycle maps (coming soon)

## Project Structure
```
project_ares/
├── main.py              # Entry point
├── config.py            # Global settings
├── core/                # Core game systems
│   ├── grid.py          # Grid & navigation
│   ├── models.py        # Data models
│   ├── gameplay.py      # Game logic
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

### Branch Strategy
- `main` - Protected, requires review
- `feature/algorithms` - Abdul's work
- `feature/graphics-ui` - Asaad's work
- `feature/gameplay` - Basim's work

## License
Educational project for AI coursework.
