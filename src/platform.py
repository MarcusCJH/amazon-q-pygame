import pygame
from .constants import *

class Platform:
    def __init__(self, x, y, width, platform_type="normal"):
        self.rect = pygame.Rect(x, y, width, PLATFORM_HEIGHT)
        self.y = y
        self.type = platform_type
        self.original_width = width

    def get_display_width(self, big_platforms_active):
        if big_platforms_active and self.type == "normal":
            return min(self.original_width * 1.5, PLATFORM_WIDTH)
        return self.original_width

    def draw(self, screen, camera_y, big_platforms_active=False):
        width = self.get_display_width(big_platforms_active)
        
        if self.type == "special":
            color = YELLOW
        elif width < 100:
            color = RED
        elif width < 150:
            color = ORANGE
        else:
            color = GREEN
            
        self.rect.width = width
        
        pygame.draw.rect(screen, color,
                         pygame.Rect(self.rect.x,
                                     self.rect.y - camera_y,
                                     width,
                                     self.rect.height))
        
        if self.type == "special":
            pygame.draw.rect(screen, WHITE,
                           pygame.Rect(self.rect.x + 2,
                                      self.rect.y - camera_y + 2,
                                      width - 4,
                                      self.rect.height - 4), 2)