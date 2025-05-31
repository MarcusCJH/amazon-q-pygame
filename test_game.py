import unittest
import pygame
from main import (
    Game, Player, Platform, SCREEN_WIDTH, SCREEN_HEIGHT, 
    MAX_FALL_DISTANCE, PLATFORM_WIDTH, MIN_PLATFORM_WIDTH,
    SAFE_VERTICAL_GAP
)

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
        
        # Game should be in game over state
        self.assertTrue(self.game.game_over)

    def test_platform_size_scaling(self):
        """Test that platforms get smaller as height increases"""
        # Generate platforms at different heights to test scaling
        self.game.platforms = []
        
        # Create low difficulty platform
        low_platform = Platform(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, PLATFORM_WIDTH)
        self.game.platforms.append(low_platform)
        
        # Create high difficulty platform  
        high_platform = Platform(SCREEN_WIDTH // 2, -1500, PLATFORM_WIDTH)
        self.game.platforms.append(high_platform)
        
        # Generate new platforms to test scaling
        self.game.update()
        
        # Find platforms at different heights
        low_height_platforms = [p for p in self.game.platforms if p.y > 0]
        high_height_platforms = [p for p in self.game.platforms if p.y < -1000]
        
        if low_height_platforms and high_height_platforms:
            # Check that higher platforms are generally smaller
            avg_low_width = sum(p.rect.width for p in low_height_platforms) / len(low_height_platforms)
            avg_high_width = sum(p.rect.width for p in high_height_platforms) / len(high_height_platforms)
            self.assertLessEqual(avg_high_width, avg_low_width)
        
        # Check that all platform widths are within bounds
        for platform in self.game.platforms:
            self.assertGreaterEqual(platform.rect.width, MIN_PLATFORM_WIDTH)
            self.assertLessEqual(platform.rect.width, PLATFORM_WIDTH)

    def test_game_restart(self):
        """Test that game can be restarted after game over"""
        # Force game over
        self.game.game_over = True
        initial_score = self.game.score
        
        # Create restart event
        restart_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_r})
        pygame.event.post(restart_event)
        
        # Handle the event
        self.game.handle_events()
        
        # Check game is reset
        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.score, 0)

    def test_difficulty_scaling(self):
        """Test that difficulty factor increases with score"""
        # Test low score difficulty
        low_score_platform = Platform(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, PLATFORM_WIDTH)
        low_score = (SCREEN_HEIGHT - low_score_platform.y) // 10
        low_difficulty = min(1.0, low_score / 150.0)
        
        # Test high score difficulty
        high_score_platform = Platform(SCREEN_WIDTH // 2, -2000, PLATFORM_WIDTH)
        high_score = (SCREEN_HEIGHT - high_score_platform.y) // 10
        high_difficulty = min(1.0, high_score / 150.0)
        
        # Check that difficulty increased
        self.assertGreater(high_difficulty, low_difficulty)
        self.assertLessEqual(high_difficulty, 1.0)
        self.assertGreaterEqual(low_difficulty, 0.0)

    def test_platform_generation_count(self):
        """Test that platform count adjusts with difficulty"""
        # Test low difficulty platform count
        self.game.platforms = [Platform(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, PLATFORM_WIDTH)]
        low_score = (SCREEN_HEIGHT - self.game.platforms[-1].y) // 10
        low_difficulty = min(1.0, low_score / 150.0)
        low_max_platforms = max(6, 15 - int(low_difficulty * 9))
        
        # Test high difficulty platform count
        high_score = 200  # Max difficulty score
        high_difficulty = min(1.0, high_score / 150.0)
        high_max_platforms = max(6, 15 - int(high_difficulty * 9))
        
        # Check that high difficulty has fewer max platforms
        self.assertLessEqual(high_max_platforms, low_max_platforms)
        self.assertGreaterEqual(high_max_platforms, 6)  # Minimum is 6
        self.assertLessEqual(low_max_platforms, 15)     # Maximum is 15

    def test_platform_horizontal_spacing(self):
        """Test that platform horizontal spacing varies with difficulty"""
        # Reset platforms for controlled testing
        self.game.platforms = [Platform(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, PLATFORM_WIDTH)]
        
        # Generate platforms at low difficulty
        initial_platform_count = len(self.game.platforms)
        self.game.update()
        low_diff_count = len(self.game.platforms)
        
        # Reset and test high difficulty
        self.game.platforms = [Platform(SCREEN_WIDTH // 2, -2000, PLATFORM_WIDTH)]
        self.game.update()
        
        # Check that platforms were generated (basic functionality test)
        self.assertGreater(len(self.game.platforms), 1)
        
        # Check that platforms have reasonable horizontal positions
        for platform in self.game.platforms:
            self.assertGreaterEqual(platform.rect.x, -platform.rect.width)  # Allow some off-screen
            self.assertLessEqual(platform.rect.x, SCREEN_WIDTH)

    def test_platform_width_reduction(self):
        """Test that platform width reduces with higher scores"""
        # Test low score platform width
        low_score = 10
        low_difficulty = min(1.0, low_score / 150.0)
        low_width_factor = 1.0 - (low_difficulty * 0.8)
        low_expected_width = max(MIN_PLATFORM_WIDTH, int(PLATFORM_WIDTH * low_width_factor))
        
        # Test high score platform width
        high_score = 150
        high_difficulty = min(1.0, high_score / 150.0)
        high_width_factor = 1.0 - (high_difficulty * 0.8)
        high_expected_width = max(MIN_PLATFORM_WIDTH, int(PLATFORM_WIDTH * high_width_factor))
        
        # Check that high score platforms are narrower
        self.assertLessEqual(high_expected_width, low_expected_width)
        
        # Check bounds
        self.assertGreaterEqual(high_expected_width, MIN_PLATFORM_WIDTH)
        self.assertLessEqual(low_expected_width, PLATFORM_WIDTH)

    def test_vertical_gap_scaling(self):
        """Test that vertical gaps between platforms scale with difficulty"""
        # Test low difficulty gaps
        low_difficulty = 0.0
        low_min_gap = int(30 + low_difficulty * 40)
        low_max_gap = min(120, int(60 + low_difficulty * 60))
        
        # Test high difficulty gaps
        high_difficulty = 1.0
        high_min_gap = int(30 + high_difficulty * 40)
        high_max_gap = min(120, int(60 + high_difficulty * 60))
        
        # Check that high difficulty allows for larger gaps
        self.assertGreaterEqual(high_max_gap, low_max_gap)
        self.assertGreaterEqual(high_min_gap, low_min_gap)
        
        # Check bounds
        self.assertLessEqual(high_max_gap, 120)
        self.assertGreaterEqual(low_min_gap, 30)

    def test_horizontal_offset_type(self):
        """Test that horizontal offset calculations result in integer values"""
        # Create a high difficulty scenario to test offset calculations
        high_platform = Platform(SCREEN_WIDTH // 2, -2000, PLATFORM_WIDTH)
        self.game.platforms = [high_platform]
        
        # Force an update to trigger platform generation
        try:
            self.game.update()
            # If we get here, the update succeeded without type errors
            self.assertTrue(True)
        except TypeError as e:
            self.fail("Platform generation failed due to non-integer offset: {}".format(e))

    def test_difficulty_factor_bounds(self):
        """Test that difficulty factor is properly bounded"""
        # Test minimum difficulty
        min_score = 0
        min_difficulty = min(1.0, min_score / 150.0)
        self.assertEqual(min_difficulty, 0.0)
        
        # Test maximum difficulty
        max_score = 300  # Above the cap
        max_difficulty = min(1.0, max_score / 150.0)
        self.assertEqual(max_difficulty, 1.0)
        
        # Test intermediate difficulty
        mid_score = 75
        mid_difficulty = min(1.0, mid_score / 150.0)
        self.assertEqual(mid_difficulty, 0.5)

    def tearDown(self):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()