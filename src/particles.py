import pygame
import random
import math
from .constants import *

class Particle:
    def __init__(self, x, y, vel_x, vel_y, color, life):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.life = life
        self.max_life = life
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1  # gravity
        self.life -= 1
        
    def draw(self, screen, camera_y):
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        pygame.draw.circle(screen, self.color[:3], 
                         (int(self.x), int(self.y - camera_y)), 2)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_explosion(self, x, y, color=WHITE, count=10):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - 2
            life = random.randint(30, 60)
            self.particles.append(Particle(x, y, vel_x, vel_y, color, life))
    
    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self, screen, camera_y):
        for particle in self.particles:
            particle.draw(screen, camera_y)