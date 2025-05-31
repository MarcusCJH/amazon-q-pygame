import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.6  # Reduced gravity for higher, longer jumps
JUMP_SPEED = -16  # Increased jump power
MOVE_SPEED = 6  # Increased horizontal movement speed
PLATFORM_WIDTH = 200  # Increased base platform width
PLATFORM_HEIGHT = 20
MAX_FALL_SPEED = 20  # Maximum falling speed
MAX_FALL_DISTANCE = 400  # Increased fall distance tolerance
MIN_PLATFORM_WIDTH = 90  # Smaller minimum for challenge at high levels
PLATFORM_WIDTH_SCALE = 0.96  # More aggressive platform width reduction
SAFE_HORIZONTAL_DISTANCE = 280  # Slightly reduced safe distance
SAFE_VERTICAL_GAP = 75  # Increased maximum vertical gap for challenge

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.y = y  # Actual y position for camera tracking
        self.fall_start_y = y  # Track where falling began
        self.is_falling = False

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY

        # Limit fall speed
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Track falling state
        if self.vel_y > 0:
            if not self.is_falling:
                self.is_falling = True
                self.fall_start_y = self.y
        else:
            self.is_falling = False

        # Update position
        self.rect.x += self.vel_x
        self.y += self.vel_y
        self.rect.y = self.y

        # Screen wrapping for horizontal movement
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0

    def draw(self, screen, camera_y):
        # Draw player relative to camera position
        pygame.draw.rect(screen, WHITE,
                         pygame.Rect(self.rect.x,
                                     self.rect.y - camera_y,
                                     self.rect.width,
                                     self.rect.height))

class Platform:
    def __init__(self, x, y, width):
        self.rect = pygame.Rect(x, y, width, PLATFORM_HEIGHT)
        self.y = y  # Actual y position

    def draw(self, screen, camera_y):
        pygame.draw.rect(screen, GREEN,
                         pygame.Rect(self.rect.x,
                                     self.rect.y - camera_y,
                                     self.rect.width,
                                     self.rect.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Endless Jumper")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.init_game()

    def init_game(self):
        # Create initial platforms first
        self.platforms = []
        self.camera_y = 0
        self.score = 0
        self.highest_point = SCREEN_HEIGHT

        # Create initial platform at a fixed position for the player to start on
        initial_platform = Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2, 
                                 SCREEN_HEIGHT - 100, 
                                 PLATFORM_WIDTH)
        self.platforms.append(initial_platform)

        # Create additional platforms
        for i in range(1, 10):
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = SCREEN_HEIGHT - (i * 100)
            # Calculate platform width based on height
            platform_width = max(MIN_PLATFORM_WIDTH, 
                               PLATFORM_WIDTH * (PLATFORM_WIDTH_SCALE ** i))
            self.platforms.append(Platform(x, y, platform_width))

        # Initialize player on the first platform
        self.player = Player(initial_platform.rect.centerx - 20, initial_platform.rect.top - 40)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.game_over = False
                    self.init_game()

        # Handle keyboard input
        keys = pygame.key.get_pressed()
        self.player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED

    def update(self):
        if self.game_over:
            return

        # Store previous position before update
        prev_y = self.player.rect.y

        self.player.update()

        # Check platform collisions
        for platform in self.platforms:
            # Calculate previous bottom position
            prev_bottom = prev_y + self.player.rect.height

            if (self.player.vel_y > 0 and  # Moving downward
                    prev_bottom <= platform.rect.top and  # Was above platform in previous frame
                    self.player.rect.bottom >= platform.rect.top and
                    self.player.rect.bottom <= platform.rect.bottom and
                    self.player.rect.right >= platform.rect.left and
                    self.player.rect.left <= platform.rect.right):
                # Adjust position to top of platform
                self.player.y = platform.rect.top - self.player.rect.height
                self.player.rect.bottom = platform.rect.top
                self.player.vel_y = JUMP_SPEED

        # Update camera and score
        if self.player.y < self.highest_point:
            self.highest_point = self.player.y
            self.score = (SCREEN_HEIGHT - self.highest_point) // 10

        # Camera follows player
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2

        # Generate new platforms with improved reachability
        # Calculate difficulty factor first
        if len(self.platforms) > 0:
            current_score = (SCREEN_HEIGHT - self.platforms[-1].y) // 10
            difficulty_factor = min(1.0, current_score / 150.0)
        else:
            difficulty_factor = 0.0
            
        # Fewer platforms at higher difficulty for more challenging gaps
        max_platforms = max(6, 15 - int(difficulty_factor * 9))  # 15 at start, 6 at max difficulty
        while len(self.platforms) < max_platforms:
            prev_platform = self.platforms[-1]
            
            # Recalculate difficulty factor for this specific platform
            current_score = (SCREEN_HEIGHT - prev_platform.y) // 10
            difficulty_factor = min(1.0, current_score / 150.0)
            
            # Calculate safe vertical gap (much more aggressive)
            base_min_gap = 30
            base_max_gap = 60
            # Increase gaps dramatically as score gets higher
            min_gap = int(base_min_gap + difficulty_factor * 40)  # Can go up to 70
            max_gap = int(base_max_gap + difficulty_factor * 60)  # Can go up to 120
            max_gap = min(max_gap, 120)  # Allow larger gaps than SAFE_VERTICAL_GAP
            
            # Ensure min_gap never exceeds max_gap
            min_gap = min(min_gap, max_gap - 10)  # Keep at least 10 pixel difference
            
            vertical_gap = random.randint(min_gap, max_gap)
            
            # Calculate next platform y position
            y = prev_platform.y - vertical_gap
            
            # Calculate platform width with more aggressive shrinking
            # At score 0: full width (200), at score 150+: minimum width (90)
            width_reduction_factor = 1.0 - (difficulty_factor * 0.8)  # Reduce by up to 80%
            platform_width = max(MIN_PLATFORM_WIDTH, 
                               int(PLATFORM_WIDTH * width_reduction_factor))
            
            # Improved horizontal positioning with much more spread
            prev_center = prev_platform.rect.centerx
            
            # Calculate horizontal range based on difficulty (much more aggressive)
            base_range = SCREEN_WIDTH * 0.2   # Start more spread out
            max_range = SCREEN_WIDTH * 0.8    # Can get extremely challenging
            current_range = base_range + (max_range - base_range) * difficulty_factor
            max_horizontal_offset = int(min(500, current_range))  # Convert to int and ensure it's capped at 500
            
            # Generate potential positions with extreme variation
            potential_positions = []
            
            # At low heights, moderate spread. At high heights, extreme spread
            if difficulty_factor < 0.2:  # Early game - moderate spread
                spread_offset = random.randint(-100, 100)
                x1 = prev_center + spread_offset - platform_width // 2
                potential_positions.append(x1)
                
                wider_offset = random.randint(-160, 160)
                x2 = prev_center + wider_offset - platform_width // 2
                potential_positions.append(x2)
                
            elif difficulty_factor < 0.5:  # Mid game - wide spread
                wide_offset = random.randint(-180, 180)
                x1 = prev_center + wide_offset - platform_width // 2
                potential_positions.append(x1)
                
                very_wide_offset = random.randint(-280, 280)
                x2 = prev_center + very_wide_offset - platform_width // 2
                potential_positions.append(x2)
                
            else:  # Late game - extreme spread
                # Much wider spreads for high difficulty
                extreme_offset = random.randint(-250, 250)
                x1 = prev_center + extreme_offset - platform_width // 2
                potential_positions.append(x1)
                
                massive_offset = random.randint(-400, 400)
                x2 = prev_center + massive_offset - platform_width // 2
                potential_positions.append(x2)
                
                # Force platforms to opposite sides of screen more often
                if random.random() < 0.5:  # 50% chance
                    if prev_center < SCREEN_WIDTH // 2:
                        # Previous was on left, put new one on right
                        far_right_x = random.randint(SCREEN_WIDTH - platform_width - 50, SCREEN_WIDTH - platform_width - 10)
                        potential_positions.append(far_right_x)
                    else:
                        # Previous was on right, put new one on left
                        far_left_x = random.randint(10, 50)
                        potential_positions.append(far_left_x)
            
            # Add one extremely random position
            max_offset = min(max_horizontal_offset, 450)
            extreme_random_offset = random.randint(-max_offset, max_offset)
            x3 = prev_center + extreme_random_offset - platform_width // 2
            potential_positions.append(x3)
            
            # Choose the best position
            best_x = None
            best_score = -1
            
            for x in potential_positions:
                # Clamp to screen bounds
                x_clamped = max(0, min(x, SCREEN_WIDTH - platform_width))
                
                # Score based on platform visibility and reasonable distance
                on_screen_ratio = 1.0
                if x < 0:
                    on_screen_ratio = max(0, (platform_width + x) / platform_width)
                elif x + platform_width > SCREEN_WIDTH:
                    on_screen_ratio = max(0, (SCREEN_WIDTH - x) / platform_width)
                
                # Distance penalty varies with difficulty
                distance_penalty = abs(x_clamped + platform_width//2 - prev_center) / SCREEN_WIDTH
                penalty_weight = 0.15 + difficulty_factor * 0.1  # Less penalty at higher levels
                score = on_screen_ratio - distance_penalty * penalty_weight
                
                if score > best_score:
                    best_score = score
                    best_x = x_clamped
            
            # Add the new platform
            self.platforms.append(Platform(best_x, y, platform_width))

        # Remove off-screen platforms
        self.platforms = [p for p in self.platforms
                          if p.y - self.camera_y < SCREEN_HEIGHT + 200]  # Keep more platforms in memory

        # Check game over conditions
        if self.player.y - self.camera_y > SCREEN_HEIGHT:
            self.game_over = True
        # Check if player has fallen too far without hitting a platform
        elif self.player.is_falling and (self.player.y - self.player.fall_start_y) > MAX_FALL_DISTANCE:
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw platforms and player
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_y)
        self.player.draw(self.screen, self.camera_y)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over message and restart prompt
        if self.game_over:
            font = pygame.font.Font(None, 48)
            game_over_text = font.render('Game Over!', True, RED)
            restart_text = font.render('Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()