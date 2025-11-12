#!/usr/bin/env python
"""Quick verification that all 7 algorithms are configured correctly."""

from config import ALGORITHMS, THEMES, ENEMY_SPEEDS
from core.graph import Graph
from algorithms.graph_algorithms import find_path

print("=" * 60)
print("Algorithm Arena - Configuration Verification")
print("=" * 60)

print("\n1. Configured Algorithms:")
for i, algo in enumerate(ALGORITHMS, 1):
    print(f"   {i}. {algo}")

print(f"\nTotal: {len(ALGORITHMS)} algorithms")

print("\n2. Checking Themes:")
all_themed = True
for algo in ALGORITHMS:
    has_theme = algo in THEMES
    status = "✓" if has_theme else "✗"
    print(f"   {status} {algo}: {'has theme' if has_theme else 'MISSING THEME'}")
    if not has_theme:
        all_themed = False

print("\n3. Checking Enemy Speeds:")
all_speeds = True
for algo in ALGORITHMS:
    has_speed = algo in ENEMY_SPEEDS
    status = "✓" if has_speed else "✗"
    speed = f"{ENEMY_SPEEDS[algo]}ms" if has_speed else "MISSING"
    print(f"   {status} {algo}: {speed}")
    if not has_speed:
        all_speeds = False

print("\n4. Testing Pathfinding Algorithms:")
try:
    graph = Graph(960, 720, 10, seed=42)
    start = graph.nodes[0]
    goal = graph.nodes[-1]
    
    for algo in ALGORITHMS:
        try:
            path, stats = find_path(algo, graph, start, goal)
            status = "✓" if path else "○"
            result = f"path found ({len(path)} nodes)" if path else "no path (might be stuck)"
            print(f"   {status} {algo}: {result}")
        except Exception as e:
            print(f"   ✗ {algo}: ERROR - {e}")
            all_speeds = False
except Exception as e:
    print(f"   ERROR creating graph: {e}")
    all_speeds = False

print("\n" + "=" * 60)
if all_themed and all_speeds:
    print("✓ ALL CHECKS PASSED - Configuration is complete!")
else:
    print("✗ SOME CHECKS FAILED - Please review errors above")
print("=" * 60)
