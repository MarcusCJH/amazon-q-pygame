import pygame
from .constants import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.selected = 0
        self.options = ["Start Game", "Settings", "Quit"]
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected
        return -1
    
    def draw(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("ENDLESS JUMPER", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        for i, option in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            text = self.small_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 250 + i * 50))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()