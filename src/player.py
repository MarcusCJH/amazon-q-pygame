import pygame
from .constants import *

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.y = y
        self.fall_start_y = y
        self.is_falling = False
        
        # Power-up states
        self.double_jumps_left = 0
        self.big_platforms_timer = 0
        self.slow_motion_timer = 0
        
        # Visual effects
        self.trail_positions = []

    def update(self):
        gravity_multiplier = 0.5 if self.slow_motion_timer > 0 else 1.0
        self.vel_y += GRAVITY * gravity_multiplier

        max_fall = MAX_FALL_SPEED * gravity_multiplier
        if self.vel_y > max_fall:
            self.vel_y = max_fall

        if self.vel_y > 0:
            if not self.is_falling:
                self.is_falling = True
                self.fall_start_y = self.y
        else:
            self.is_falling = False

        self.rect.x += self.vel_x * gravity_multiplier
        self.y += self.vel_y
        self.rect.y = self.y

        # Screen wrapping
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
            
        # Update power-up timers
        if self.big_platforms_timer > 0:
            self.big_platforms_timer -= 1
        if self.slow_motion_timer > 0:
            self.slow_motion_timer -= 1
            
        # Update trail
        self.trail_positions.append((self.rect.centerx, self.rect.centery))
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)

    def jump(self):
        if self.vel_y > 0 and self.double_jumps_left > 0:
            self.vel_y = JUMP_SPEED * 0.8
            self.double_jumps_left -= 1

    def draw(self, screen, camera_y):
        # Draw trail
        for i, (x, y) in enumerate(self.trail_positions):
            alpha = int(255 * (i + 1) / len(self.trail_positions) * 0.3)
            trail_surface = pygame.Surface((5, 5))
            trail_surface.set_alpha(alpha)
            trail_surface.fill(CYAN)
            screen.blit(trail_surface, (x - 2, y - camera_y - 2))
        
        # Draw player with power-up effects
        player_color = WHITE
        if self.slow_motion_timer > 0:
            player_color = PURPLE
        elif self.big_platforms_timer > 0:
            player_color = ORANGE
        elif self.double_jumps_left > 0:
            player_color = BLUE
            
        pygame.draw.rect(screen, player_color,
                         pygame.Rect(self.rect.x,
                                     self.rect.y - camera_y,
                                     self.rect.width,
                                     self.rect.height))