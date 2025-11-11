# Algorithm Arena - Game Flow

## Main Menu
```
┌─────────────────────────────────────┐
│       PROJECT ARES                  │
│   AI Responsive Enemy System        │
│                                     │
│  ┌───────────────────────────┐     │
│  │   ALGORITHM ARENA         │     │
│  └───────────────────────────┘     │
│  ┌───────────────────────────┐     │
│  │   CLASSIC MODE            │     │
│  └───────────────────────────┘     │
│  ┌───────────────────────────┐     │
│  │   HOW TO PLAY             │     │
│  └───────────────────────────┘     │
│  ┌───────────────────────────┐     │
│  │   QUIT                    │     │
│  └───────────────────────────┘     │
└─────────────────────────────────────┘
```

## Algorithm Arena Gameplay
```
┌──────────────────────────────────────────────────────────┐
│ Algorithm Arena - BFS          Time: 45s                 │
│ 1-5: Algorithm | SPACE: Pause | ESC: Menu               │
│ Q: Shield | W: Teleport | E: Block | R: Inc Weight      │
│                                                          │
│     N0 ──3── N1        Shield: READY                     │
│     │        │         Teleport: 2.5s                    │
│     2        4         Block Node: READY                 │
│     │        │         Increase Weight: READY            │
│     N2 ──5── N3                                          │
│     │    ╱   │                                           │
│     │  ╱  1  │        [Player] = You (blue circle)      │
│     │╱       │        [Enemy] = AI (red circle)         │
│     N4 ──2── N5       Red line = Enemy's planned path   │
│     │                                                    │
│   [Player]            Yellow bar = Enemy move cooldown  │
│                                                          │
│     N6 ──1── N7                                          │
│              │                                           │
│            [Enemy]                                       │
│              ▓▓▓░░ (60% charged)                        │
│                                                          │
│ Hover over nodes to see details!                        │
│ Click adjacent nodes to move                            │
└──────────────────────────────────────────────────────────┘
```

## Tooltip Example (on hover)
```
┌────────────────────────┐
│ Node N4                │
│ Connections: 3         │
│ Status: Open           │
│ Edge Weights:          │
│   -> N2: 2             │
│   -> N3: 1             │
│   -> N6: 1             │
│                        │
│ Enemy Algorithm: BFS   │
└────────────────────────┘
```

## Tutorial Screen
```
┌──────────────────────────────────────────────────────────┐
│                    HOW TO PLAY                           │
│                                                          │
│ OBJECTIVE                                                │
│   Survive as long as possible! The enemy uses           │
│   pathfinding algorithms to chase you.                  │
│                                                          │
│ MOVEMENT                                                 │
│   Click on adjacent nodes to move.                      │
│                                                          │
│ ABILITIES                                                │
│   • Q - Shield: Become invincible for 3 seconds         │
│   • W - Teleport: Jump to a nearby node                 │
│   • E - Block Node: Place obstacle to trap enemy        │
│   • R - Increase Weight: Make paths costly for enemy    │
│                                                          │
│ ALGORITHMS                                               │
│   • 1 - BFS: Slower enemy, explores breadth-first      │
│   • 2 - DFS: Slower enemy, explores depth-first        │
│   • 3 - UCS: Medium speed, considers edge weights      │
│   • 4 - Greedy: Faster enemy, rushes toward goal       │
│   • 5 - A*: Medium speed, optimal pathfinding          │
│                                                          │
│ CONTROLS                                                 │
│   • Click: Move to adjacent node                        │
│   • Hover: See node details                             │
│   • SPACE: Pause game                                   │
│   • ESC: Return to menu                                 │
│                                                          │
│ STRATEGY                                                 │
│   Use low-weight paths for quick escapes. Trap the      │
│   enemy by blocking nodes or increasing weights.        │
│                                                          │
│              ┌─────────────────────┐                    │
│              │   BACK TO MENU      │                    │
│              └─────────────────────┘                    │
└──────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Enemy Movement Delay (0.4-0.6s per algorithm)
- Gives player time to think and strategize
- Different algorithms have different speeds
- Visual cooldown bar shows when enemy moves next

### 2. Tooltips Work While Paused
- Hover over any node to see details
- Works in both playing and paused states
- Shows connections, weights, and status

### 3. Windows-Style Tooltips
- Light yellow background (classic Windows style)
- Follows mouse cursor
- Smart positioning (stays on screen)
- Shows algorithm-specific information

### 4. Tutorial Screen Layout
- Comprehensive instructions
- Proper spacing and layout
- Back button at bottom (no overlap)
- Easy to read and understand

### 5. Strategic Gameplay
- 28 nodes for exploration
- Random edge weights (1-5)
- Click to move to adjacent nodes
- Use abilities to outsmart enemy
- Survival scoring based on time

## Technical Highlights

- **Graph-based arena**: 28 nodes with weighted edges
- **BFS pathfinding**: Enemy uses graph traversal to chase player
- **Hashable nodes**: Efficient lookups and comparisons
- **Ability system**: Cooldowns, durations, visual feedback
- **Event-driven**: Clean separation of concerns
- **Tested**: 10 passing tests covering all features
