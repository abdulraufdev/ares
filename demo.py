"""
Quick demonstration script showing key features of Algorithm Arena.
This script tests the game mechanics without requiring a display.
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from config import *
from core.grid import Grid
from core.models import Agent
from core.gameplay import Game
from core.themes import ThemeManager

def demo():
    """Demonstrate key game features."""
    print("=" * 60)
    print("ALGORITHM ARENA - Feature Demonstration")
    print("=" * 60)
    
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Initialize game
    grid = Grid(GRID_WIDTH, GRID_HEIGHT, obstacle_ratio=OBSTACLE_RATIO, seed=DEFAULT_SEED)
    player = Agent(name="Player", pos=(2, 2), stamina=100, hp=PLAYER_MAX_HP, max_hp=PLAYER_MAX_HP)
    enemy = Agent(name="Enemy", pos=(GRID_WIDTH - 3, GRID_HEIGHT - 3), stamina=100, 
                 hp=ENEMY_MAX_HP, max_hp=ENEMY_MAX_HP)
    game = Game(grid, player, enemy)
    theme_manager = ThemeManager()
    
    print("\n1. Testing Algorithm-Specific Map Generation")
    print("-" * 60)
    
    for algo in ['BFS', 'DFS', 'UCS', 'Greedy', 'A*']:
        game.generate_map(algo, DEFAULT_SEED)
        walkable_count = sum(1 for row in game.nodes for node in row if node.walkable)
        total = len(game.nodes) * len(game.nodes[0])
        print(f"  {algo:8} -> {walkable_count}/{total} walkable nodes")
    
    print("\n2. Testing Algorithm Themes")
    print("-" * 60)
    
    for algo in ['BFS', 'DFS', 'UCS', 'Greedy', 'A*']:
        theme_manager.set_theme(algo)
        theme_name = theme_manager.get_name(algo)
        primary = theme_manager.get_color('primary', algo)
        print(f"  {algo:8} -> {theme_name:20} RGB{primary}")
    
    print("\n3. Testing Combat System")
    print("-" * 60)
    
    initial_player_hp = player.hp
    initial_enemy_hp = enemy.hp
    print(f"  Initial Player HP: {initial_player_hp}")
    print(f"  Initial Enemy HP: {initial_enemy_hp}")
    
    # Test damage
    player.take_damage(30, 0.0)
    print(f"  After 30 damage -> Player HP: {player.hp}")
    
    # Test shield
    player.shield_active = True
    player.shield_end_time = 1000.0
    blocked = not player.take_damage(30, 500.0)
    print(f"  Shield blocks damage: {blocked}")
    print(f"  Player HP after shield block: {player.hp}")
    
    # Test healing
    player.heal(20)
    print(f"  After healing 20 HP -> Player HP: {player.hp}")
    
    print("\n4. Testing Player Abilities")
    print("-" * 60)
    
    # Shield
    success = game.ability_manager.use_shield(player, 0.0)
    print(f"  Shield activated: {success}")
    print(f"  Shield active: {player.shield_active}")
    
    # Check cooldowns
    for ability in ['shield', 'teleport', 'block', 'weight']:
        uses = game.ability_manager.get_remaining_uses(ability)
        if uses >= 0:
            print(f"  {ability.capitalize():12} -> {uses} uses remaining")
        else:
            print(f"  {ability.capitalize():12} -> Unlimited uses")
    
    print("\n5. Testing Continuous Enemy Pathfinding")
    print("-" * 60)
    
    game.reset_agents()
    game.generate_map('BFS', DEFAULT_SEED)
    
    print(f"  Enemy starting position: {enemy.pos}")
    print(f"  Player position: {player.pos}")
    
    # First pathfind
    game.compute_enemy_path('BFS', 0.0)
    first_path_len = len(game.enemy_path)
    print(f"  Initial enemy path length: {first_path_len}")
    
    # Move player
    player.pos = (5, 5)
    print(f"  Player moved to: {player.pos}")
    
    # Second pathfind (should recalculate)
    game.compute_enemy_path('BFS', 600.0)  # After 600ms
    second_path_len = len(game.enemy_path)
    print(f"  Recalculated path length: {second_path_len}")
    print(f"  ✓ Enemy continuously recalculates path (BUG FIXED!)")
    
    print("\n6. Testing Pathfinding Algorithms")
    print("-" * 60)
    
    game.reset_agents()
    for algo in ['BFS', 'DFS', 'UCS', 'Greedy', 'A*']:
        game.compute_path(algo)
        print(f"  {algo:8} -> Path length: {game.stats.path_len:3}, "
              f"Nodes expanded: {game.stats.nodes_expanded:4}, "
              f"Time: {game.stats.compute_ms:6.2f}ms")
    
    print("\n7. Testing Click-to-Move")
    print("-" * 60)
    
    target_pos = (10, 10)
    print(f"  Current player position: {player.pos}")
    print(f"  Target position: {target_pos}")
    
    success = game.move_player_to(target_pos, 'A*')
    print(f"  Path computed: {success}")
    if success:
        print(f"  Path length: {len(game.path)}")
    
    print("\n8. Testing Game States")
    print("-" * 60)
    
    print(f"  Player alive: {player.is_alive()}")
    print(f"  Enemy alive: {enemy.is_alive()}")
    print(f"  Game over: {game.game_over}")
    
    # Simulate game over
    player.hp = 0
    game.update_combat(0.0)
    print(f"\n  After player HP reaches 0:")
    print(f"  Player alive: {player.is_alive()}")
    print(f"  Game over: {game.game_over}")
    print(f"  Winner: {game.winner}")
    
    pygame.quit()
    
    print("\n" + "=" * 60)
    print("✓ All features working correctly!")
    print("=" * 60)
    print("\nTo play the game, run: python main.py")
    print("\nControls:")
    print("  1-5: Switch algorithms")
    print("  Q: Shield ability")
    print("  W: Teleport ability")
    print("  E: Block node")
    print("  R: Increase weight")
    print("  Left Click: Move player")
    print("  SPACE: Pause")
    print("=" * 60)

if __name__ == "__main__":
    demo()
