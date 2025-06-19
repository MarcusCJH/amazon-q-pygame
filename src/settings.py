import pygame
from .constants import *

class Settings:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.selected = 0
        self.options = ["Music Volume", "SFX Volume", "Back"]
        self.music_volume = 70
        self.sfx_volume = 80
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                if self.selected == 0 and self.music_volume > 0:
                    self.music_volume -= 10
                elif self.selected == 1 and self.sfx_volume > 0:
                    self.sfx_volume -= 10
            elif event.key == pygame.K_RIGHT:
                if self.selected == 0 and self.music_volume < 100:
                    self.music_volume += 10
                elif self.selected == 1 and self.sfx_volume < 100:
                    self.sfx_volume += 10
            elif event.key == pygame.K_RETURN and self.selected == 2:
                return True
        return False
    
    def draw(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("SETTINGS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Music Volume
        color = YELLOW if self.selected == 0 else WHITE
        music_text = self.small_font.render(f"Music Volume: {self.music_volume}%", True, color)
        music_rect = music_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(music_text, music_rect)
        
        # SFX Volume
        color = YELLOW if self.selected == 1 else WHITE
        sfx_text = self.small_font.render(f"SFX Volume: {self.sfx_volume}%", True, color)
        sfx_rect = sfx_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(sfx_text, sfx_rect)
        
        # Back
        color = YELLOW if self.selected == 2 else WHITE
        back_text = self.small_font.render("Back", True, color)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(back_text, back_rect)
        
        # Instructions
        inst_text = self.small_font.render("Use Left/Right arrows to adjust, Enter to select", True, GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        self.screen.blit(inst_text, inst_rect)
        
        pygame.display.flip()