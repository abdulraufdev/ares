# Project ARES - Algorithm Arena
**AI Responsive Enemy System - Combat Edition**

A Python-based algorithm learning game featuring pathfinding visualization, combat mechanics, and interactive abilities. Transform learning algorithms into an engaging gaming experience!

## 🎮 Game Features

### Core Gameplay
- **5 Pathfinding Algorithms**: BFS, DFS, UCS, Greedy, A*
- **Click-to-Move**: Control your character by clicking on the map
- **Continuous Enemy AI**: Enemy recalculates path every 500ms using selected algorithm
- **Combat System**: Health bars, contact damage, and melee combat
- **Win/Lose Conditions**: Survive and defeat the enemy!

### Player Abilities
- **Shield (Q)**: 3 seconds of immunity, 10s cooldown
- **Teleport (W)**: Jump up to 5 cells, 8s cooldown
- **Block Node (E)**: Place an obstacle, 5 uses per game
- **Increase Weight (R)**: Make terrain 5x more costly, 3 uses per game

### Visual Features
- **Algorithm-Specific Themes**: Each algorithm has unique color schemes
  - BFS: Ocean Blue
  - DFS: Purple Mystery
  - UCS: Green Mountain
  - Greedy: Yellow Lightning
  - A*: Orange Desert
- **Health Bars**: Visual HP indicators for player and enemy
- **Particle Effects**: Visual feedback for ability usage
- **Dynamic Maps**: Different terrain types (maze, weighted, open) based on algorithm

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

### Run the Game
```bash
python main.py
```

## 🎯 Controls

### Algorithm Selection
- **1**: BFS (Breadth-First Search)
- **2**: DFS (Depth-First Search)
- **3**: UCS (Uniform Cost Search)
- **4**: Greedy Best-First
- **5**: A* Search

### Gameplay Controls
- **Left Click**: Move player to clicked position
- **Q**: Activate Shield (immunity for 3 seconds)
- **W**: Teleport to nearby location
- **E**: Block a node (place obstacle)
- **R**: Increase edge weight (make terrain costly)
- **SPACE**: Pause/Unpause

## 📊 Game Stats
- **Player HP**: 100
- **Enemy HP**: 150
- **Contact Damage**: 10 HP per collision
- **Melee Damage**: 25 HP
- **Damage Cooldown**: 1 second between hits

## Project Structure
```
project_ares/
├── main.py              # Entry point & game loop
├── config.py            # Global settings & constants
├── core/                # Core game systems
│   ├── grid.py          # Grid & navigation
│   ├── node.py          # Node-based graph system
│   ├── graph.py         # Map generation (maze, weighted, open)
│   ├── models.py        # Data models (Agent, Stats)
│   ├── gameplay.py      # Game logic & pathfinding
│   ├── combat.py        # Combat system
│   ├── abilities.py     # Player abilities manager
│   ├── themes.py        # Algorithm visual themes
│   ├── particles.py     # Particle effects
│   ├── graphics.py      # Rendering & visualization
│   └── ui.py            # Input handling
├── algorithms/          # Pathfinding algorithms
│   ├── bfs.py           # Breadth-First Search
│   ├── dfs.py           # Depth-First Search
│   ├── ucs.py           # Uniform Cost Search
│   ├── greedy.py        # Greedy Best-First
│   ├── astar.py         # A* Search
│   ├── common.py        # Heuristics & utilities
│   └── locals_planner.py # Tactical planning
└── tests/               # Unit tests (20 tests)
    ├── test_algorithms.py      # Algorithm tests
    ├── test_new_systems.py     # System tests
    └── test_game_init.py       # Integration test
```

## Algorithms Implemented
- ✅ **BFS** (Breadth-First Search) - Explores all neighbors level by level
- ✅ **DFS** (Depth-First Search) - Explores as far as possible along each branch
- ✅ **UCS** (Uniform Cost Search) - Finds lowest-cost path
- ✅ **Greedy Best-First** - Uses heuristic to guide search
- ✅ **A* Search** - Combines actual cost + heuristic for optimal paths

## 🧪 Development

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_new_systems.py -v

# Run with coverage
pytest tests/ --cov=core --cov=algorithms
```

All tests passing: **20/20** ✅

### Test Coverage
- Algorithm correctness (3 tests)
- Node & graph generation (6 tests)
- Combat system (4 tests)
- Abilities & cooldowns (2 tests)
- Theme management (2 tests)
- Game initialization (1 test)
- Agent health & damage (2 tests)

### Code Quality
- ✅ All tests passing
- ✅ CodeQL security scan: 0 vulnerabilities
- ✅ Type hints throughout codebase
- ✅ Comprehensive docstrings

## 🎓 Educational Value

This game teaches:
1. **Pathfinding Algorithms**: Visual comparison of different search strategies
2. **Algorithm Complexity**: See nodes expanded and computation time
3. **Heuristics**: Understand how estimates guide search (A*, Greedy)
4. **Cost Functions**: Weighted terrain demonstrates UCS and A* behavior
5. **Graph Theory**: Nodes, edges, connectivity, and traversal

## 🚀 Future Enhancements
- [ ] Additional algorithms (IDS, BDS, Hill Climbing)
- [ ] Sound effects for actions
- [ ] Map editor
- [ ] Multiplayer mode
- [ ] Algorithm performance charts
- [ ] More abilities and power-ups

## Branch Strategy
- `main` - Protected, requires review
- `feature/algorithms` - Abdul's work
- `feature/graphics-ui` - Asaad's work
- `feature/gameplay` - Basim's work

## License
Educational project for AI coursework.
