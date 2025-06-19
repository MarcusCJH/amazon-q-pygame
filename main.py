import pygame
from src.game import Game
from src.menu import Menu
from src.settings import Settings
from src.constants import *

pygame.init()

class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Endless Jumper - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"  # MENU, PLAYING, SETTINGS
        
        self.menu = Menu(self.screen)
        self.settings = Settings(self.screen)
        self.game = None
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == "MENU":
                    choice = self.menu.handle_input(event)
                    if choice == 0:  # Start Game
                        self.state = "PLAYING"
                        self.game = Game()
                    elif choice == 1:  # Settings
                        self.state = "SETTINGS"
                    elif choice == 2:  # Quit
                        self.running = False
                
                elif self.state == "SETTINGS":
                    if self.settings.handle_input(event):
                        self.state = "MENU"
                
                elif self.state == "PLAYING" and self.game:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.game.game_over:
                        self.state = "MENU"
                    else:
                        # Pass event to game for handling
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r and self.game.game_over:
                                self.game.game_over = False
                                self.game.init_game()
                            elif event.key == pygame.K_p and not self.game.game_over:
                                self.game.paused = not self.game.paused
            
            if self.state == "MENU":
                self.menu.draw()
            elif self.state == "SETTINGS":
                self.settings.draw()
            elif self.state == "PLAYING" and self.game:
                # Handle continuous key presses
                if not self.game.paused and not self.game.game_over:
                    keys = pygame.key.get_pressed()
                    self.game.player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED
                    
                    if keys[pygame.K_UP] and self.game.player.double_jumps_left > 0:
                        self.game.player.jump()
                        self.game.total_jumps += 1
                
                self.game.update()
                self.game.draw()
                if not self.game.running:
                    self.state = "MENU"
            
            self.clock.tick(60)
        
        pygame.quit()

def main():
    game_manager = GameManager()
    game_manager.run()

if __name__ == "__main__":
    main()