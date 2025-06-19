import pygame
from .constants import *

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = powerup_type
        self.color = {
            POWERUP_DOUBLE_JUMP: BLUE,
            POWERUP_BIG_PLATFORMS: ORANGE,
            POWERUP_SLOW_MOTION: PURPLE
        }[powerup_type]
        
    def draw(self, screen, camera_y):
        pygame.draw.rect(screen, self.color,
                         pygame.Rect(self.rect.x,
                                     self.rect.y - camera_y,
                                     self.rect.width,
                                     self.rect.height))
        center_x = self.rect.x + self.rect.width // 2
        center_y = self.rect.y - camera_y + self.rect.height // 2
        
        if self.type == POWERUP_DOUBLE_JUMP:
            pygame.draw.circle(screen, WHITE, (center_x, center_y - 5), 5)
            pygame.draw.circle(screen, WHITE, (center_x, center_y + 5), 5)
        elif self.type == POWERUP_BIG_PLATFORMS:
            pygame.draw.rect(screen, WHITE, (center_x - 8, center_y - 3, 16, 6))
        elif self.type == POWERUP_SLOW_MOTION:
            font = pygame.font.Font(None, 20)
            text = font.render("S", True, WHITE)
            screen.blit(text, (center_x - 5, center_y - 8))