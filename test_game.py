import unittest
import pygame
from main import Game, Player, Platform, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_FALL_DISTANCE

class TestGame(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = Game()

    def test_player_starts_on_platform(self):
        """Test that the player starts properly positioned above a platform"""
        # Get the first platform (should be the starting platform)
        initial_platform = self.game.platforms[0]
        
        # Check player is above the platform
        self.assertEqual(self.game.player.rect.bottom, initial_platform.rect.top)
        
        # Check player is horizontally centered on the platform
        self.assertGreaterEqual(self.game.player.rect.left, initial_platform.rect.left)
        self.assertLessEqual(self.game.player.rect.right, initial_platform.rect.right)

    def test_fall_speed_limit(self):
        """Test that player's fall speed is limited"""
        # Move player up to create falling scenario
        self.game.player.y -= 500
        self.game.player.rect.y = self.game.player.y
        
        # Update several times to build up fall speed
        for _ in range(20):
            self.game.player.update()
        
        # Check fall speed doesn't exceed maximum
        self.assertLessEqual(self.game.player.vel_y, 20)

    def test_excessive_fall_ends_game(self):
        """Test that falling too far without hitting a platform ends the game"""
        # Move player up to create falling scenario
        self.game.player.y -= MAX_FALL_DISTANCE + 10
        self.game.player.rect.y = self.game.player.y
        self.game.player.is_falling = True
        self.game.player.fall_start_y = self.game.player.y - (MAX_FALL_DISTANCE + 5)
        
        # Update game
        self.game.update()
        
        # Game should end due to excessive falling
        self.assertFalse(self.game.running)

    def tearDown(self):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()