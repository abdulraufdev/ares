"""Particle effects for abilities."""
import pygame
import random
from typing import Optional


class Particle:
    """Single particle for effects."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: tuple[int, int, int], lifetime: float, size: int = 3):
        """
        Initialize particle.
        
        Args:
            x: X position
            y: Y position
            vx: X velocity
            vy: Y velocity
            color: RGB color
            lifetime: Lifetime in milliseconds
            size: Particle size in pixels
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self, dt: float) -> bool:
        """
        Update particle.
        
        Args:
            dt: Delta time in milliseconds
            
        Returns:
            True if particle is still alive
        """
        self.x += self.vx * dt / 1000.0
        self.y += self.vy * dt / 1000.0
        self.lifetime -= dt
        
        return self.lifetime > 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw particle.
        
        Args:
            screen: Pygame surface
        """
        if self.lifetime <= 0:
            return
        
        # Fade alpha based on lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha)
        
        # Draw circle
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(screen, self.color, pos, self.size)


class ParticleSystem:
    """Manages particle effects."""
    
    def __init__(self):
        """Initialize particle system."""
        self.particles: list[Particle] = []
    
    def emit_shield(self, x: float, y: float, cell_size: int) -> None:
        """
        Emit shield activation particles.
        
        Args:
            x: Center X position
            y: Center Y position
            cell_size: Size of grid cell
        """
        cx = x * cell_size + cell_size // 2
        cy = y * cell_size + cell_size // 2
        
        # Blue particles radiating outward
        for _ in range(20):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(50, 150)
            vx = speed * random.uniform(-1, 1)
            vy = speed * random.uniform(-1, 1)
            color = (100, 150, 255)
            lifetime = random.uniform(300, 600)
            
            self.particles.append(Particle(cx, cy, vx, vy, color, lifetime))
    
    def emit_teleport(self, from_pos: tuple[float, float], to_pos: tuple[float, float], 
                     cell_size: int) -> None:
        """
        Emit teleport particles.
        
        Args:
            from_pos: Starting position (grid coords)
            to_pos: Ending position (grid coords)
            cell_size: Size of grid cell
        """
        fx, fy = from_pos
        tx, ty = to_pos
        
        fx_px = fx * cell_size + cell_size // 2
        fy_px = fy * cell_size + cell_size // 2
        tx_px = tx * cell_size + cell_size // 2
        ty_px = ty * cell_size + cell_size // 2
        
        # Purple particles at both locations
        for pos_x, pos_y in [(fx_px, fy_px), (tx_px, ty_px)]:
            for _ in range(15):
                vx = random.uniform(-100, 100)
                vy = random.uniform(-100, 100)
                color = (180, 50, 255)
                lifetime = random.uniform(200, 400)
                
                self.particles.append(Particle(pos_x, pos_y, vx, vy, color, lifetime))
    
    def emit_block(self, x: float, y: float, cell_size: int) -> None:
        """
        Emit block placement particles.
        
        Args:
            x: Grid X position
            y: Grid Y position
            cell_size: Size of grid cell
        """
        cx = x * cell_size + cell_size // 2
        cy = y * cell_size + cell_size // 2
        
        # Red/orange particles
        for _ in range(10):
            vx = random.uniform(-50, 50)
            vy = random.uniform(-50, 50)
            color = (255, 100, 50)
            lifetime = random.uniform(200, 400)
            
            self.particles.append(Particle(cx, cy, vx, vy, color, lifetime, size=4))
    
    def emit_damage(self, x: float, y: float, cell_size: int) -> None:
        """
        Emit damage particles.
        
        Args:
            x: Grid X position
            y: Grid Y position
            cell_size: Size of grid cell
        """
        cx = x * cell_size + cell_size // 2
        cy = y * cell_size + cell_size // 2
        
        # Red particles
        for _ in range(8):
            vx = random.uniform(-80, 80)
            vy = random.uniform(-80, 80)
            color = (255, 50, 50)
            lifetime = random.uniform(150, 300)
            
            self.particles.append(Particle(cx, cy, vx, vy, color, lifetime, size=3))
    
    def update(self, dt: float) -> None:
        """
        Update all particles.
        
        Args:
            dt: Delta time in milliseconds
        """
        # Update and filter dead particles
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw all particles.
        
        Args:
            screen: Pygame surface
        """
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self) -> None:
        """Clear all particles."""
        self.particles.clear()
