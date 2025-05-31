import pygame
import random
import json
import os

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
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Power-up types
POWERUP_DOUBLE_JUMP = "double_jump"
POWERUP_BIG_PLATFORMS = "big_platforms"
POWERUP_SLOW_MOTION = "slow_motion"

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
        # Draw power-up symbol
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

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.y = y  # Actual y position for camera tracking
        self.fall_start_y = y  # Track where falling began
        self.is_falling = False
        
        # Power-up states
        self.double_jumps_left = 0
        self.big_platforms_timer = 0
        self.slow_motion_timer = 0
        
        # Visual effects
        self.trail_positions = []

    def update(self):
        # Apply gravity (affected by slow motion)
        gravity_multiplier = 0.5 if self.slow_motion_timer > 0 else 1.0
        self.vel_y += GRAVITY * gravity_multiplier

        # Limit fall speed
        max_fall = MAX_FALL_SPEED * gravity_multiplier
        if self.vel_y > max_fall:
            self.vel_y = max_fall

        # Track falling state
        if self.vel_y > 0:
            if not self.is_falling:
                self.is_falling = True
                self.fall_start_y = self.y
        else:
            self.is_falling = False

        # Update position
        self.rect.x += self.vel_x * gravity_multiplier
        self.y += self.vel_y
        self.rect.y = self.y

        # Screen wrapping for horizontal movement
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
        # Only allow double jump if player has double jumps available and is in mid-air
        if self.vel_y > 0 and self.double_jumps_left > 0:  # Falling and has double jumps
            self.vel_y = JUMP_SPEED * 0.8  # Slightly weaker double jump
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

class Platform:
    def __init__(self, x, y, width, platform_type="normal"):
        self.rect = pygame.Rect(x, y, width, PLATFORM_HEIGHT)
        self.y = y  # Actual y position
        self.type = platform_type
        self.original_width = width

    def get_display_width(self, big_platforms_active):
        if big_platforms_active and self.type == "normal":
            return min(self.original_width * 1.5, PLATFORM_WIDTH)
        return self.original_width

    def draw(self, screen, camera_y, big_platforms_active=False):
        # Choose color based on platform size and type
        width = self.get_display_width(big_platforms_active)
        
        if self.type == "special":
            color = YELLOW
        elif width < 100:
            color = RED  # Small platforms
        elif width < 150:
            color = ORANGE  # Medium platforms
        else:
            color = GREEN  # Large platforms
            
        # Update rect for collision detection
        self.rect.width = width
        
        pygame.draw.rect(screen, color,
                         pygame.Rect(self.rect.x,
                                     self.rect.y - camera_y,
                                     width,
                                     self.rect.height))
        
        # Add visual details
        if self.type == "special":
            pygame.draw.rect(screen, WHITE,
                           pygame.Rect(self.rect.x + 2,
                                      self.rect.y - camera_y + 2,
                                      width - 4,
                                      self.rect.height - 4), 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Endless Jumper - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.paused = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load high score
        self.high_score = self.load_high_score()
        
        # Game statistics
        self.start_time = pygame.time.get_ticks()
        self.total_jumps = 0
        self.powerups_collected = 0
        
        self.init_game()

    def load_high_score(self):
        try:
            if os.path.exists("high_score.json"):
                with open("high_score.json", "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except:
            pass
        return 0

    def save_high_score(self):
        try:
            with open("high_score.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass

    def init_game(self):
        # Create initial platforms first
        self.platforms = []
        self.powerups = []
        self.camera_y = 0
        self.score = 0
        self.highest_point = SCREEN_HEIGHT
        self.start_time = pygame.time.get_ticks()
        self.total_jumps = 0
        self.powerups_collected = 0

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
            platform_type = "special" if random.random() < 0.1 else "normal"
            self.platforms.append(Platform(x, y, platform_width, platform_type))

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
                elif event.key == pygame.K_p and not self.game_over:
                    # Pause/unpause
                    self.paused = not self.paused

        # Handle keyboard input
        if not self.paused and not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED
            
            # Allow double jump power-up usage only (UP arrow)
            if keys[pygame.K_UP] and self.player.double_jumps_left > 0:
                self.player.jump()
                self.total_jumps += 1

    def spawn_powerup(self, platform):
        """Randomly spawn power-ups on platforms"""
        if random.random() < 0.15:  # 15% chance
            powerup_type = random.choice([POWERUP_DOUBLE_JUMP, POWERUP_BIG_PLATFORMS, POWERUP_SLOW_MOTION])
            powerup_x = platform.rect.x + platform.rect.width // 2 - 15
            powerup_y = platform.rect.y - 35
            self.powerups.append(PowerUp(powerup_x, powerup_y, powerup_type))

    def update(self):
        if self.game_over or self.paused:
            return

        # Store previous position before update
        prev_y = self.player.rect.y

        self.player.update()

        # Check platform collisions
        for platform in self.platforms:
            # Calculate previous bottom position
            prev_bottom = prev_y + self.player.rect.height
            
            # Use current platform width for collision
            platform_width = platform.get_display_width(self.player.big_platforms_timer > 0)

            if (self.player.vel_y > 0 and  # Moving downward
                    prev_bottom <= platform.rect.top and  # Was above platform in previous frame
                    self.player.rect.bottom >= platform.rect.top and
                    self.player.rect.bottom <= platform.rect.bottom and
                    self.player.rect.right >= platform.rect.left and
                    self.player.rect.left <= platform.rect.left + platform_width):
                # Adjust position to top of platform
                self.player.y = platform.rect.top - self.player.rect.height
                self.player.rect.bottom = platform.rect.top
                self.player.vel_y = JUMP_SPEED
                self.total_jumps += 1  # Count automatic jumps
                
                # Reset double jump when landing on platform
                if self.player.double_jumps_left == 0:
                    self.player.double_jumps_left = 1 if self.player.double_jumps_left > 0 else 0

        # Check power-up collisions
        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                self.powerups.remove(powerup)
                self.powerups_collected += 1
                
                # Apply power-up effect
                if powerup.type == POWERUP_DOUBLE_JUMP:
                    self.player.double_jumps_left = 2
                elif powerup.type == POWERUP_BIG_PLATFORMS:
                    self.player.big_platforms_timer = 600  # 10 seconds at 60 FPS
                elif powerup.type == POWERUP_SLOW_MOTION:
                    self.player.slow_motion_timer = 300  # 5 seconds at 60 FPS

        # Update camera and score
        if self.player.y < self.highest_point:
            self.highest_point = self.player.y
            self.score = (SCREEN_HEIGHT - self.highest_point) // 10
            
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

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
            
            # Create platform type
            platform_type = "special" if random.random() < 0.08 else "normal"
            
            # Add the new platform
            new_platform = Platform(best_x, y, platform_width, platform_type)
            self.platforms.append(new_platform)
            
            # Spawn power-up on some platforms
            self.spawn_powerup(new_platform)

        # Remove off-screen platforms and power-ups
        self.platforms = [p for p in self.platforms
                          if p.y - self.camera_y < SCREEN_HEIGHT + 200]  # Keep more platforms in memory
        self.powerups = [p for p in self.powerups
                        if p.rect.y - self.camera_y < SCREEN_HEIGHT + 100]

        # Check game over conditions
        if self.player.y - self.camera_y > SCREEN_HEIGHT:
            self.game_over = True
        # Check if player has fallen too far without hitting a platform
        elif self.player.is_falling and (self.player.y - self.player.fall_start_y) > MAX_FALL_DISTANCE:
            self.game_over = True

    def draw_ui(self):
        """Draw user interface elements"""
        # Score
        score_text = self.font.render(f'Score: {int(self.score)}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # High Score
        high_score_text = self.small_font.render(f'High Score: {int(self.high_score)}', True, YELLOW)
        self.screen.blit(high_score_text, (10, 50))
        
        # Game time
        game_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.small_font.render(f'Time: {game_time}s', True, WHITE)
        self.screen.blit(time_text, (10, 75))
        
        # Power-up indicators
        y_offset = 100
        if self.player.double_jumps_left > 0:
            double_jump_text = self.small_font.render(f'Double Jumps: {self.player.double_jumps_left}', True, BLUE)
            self.screen.blit(double_jump_text, (10, y_offset))
            y_offset += 25
            
        if self.player.big_platforms_timer > 0:
            big_platform_text = self.small_font.render(f'Big Platforms: {self.player.big_platforms_timer // 60}s', True, ORANGE)
            self.screen.blit(big_platform_text, (10, y_offset))
            y_offset += 25
            
        if self.player.slow_motion_timer > 0:
            slow_motion_text = self.small_font.render(f'Slow Motion: {self.player.slow_motion_timer // 60}s', True, PURPLE)
            self.screen.blit(slow_motion_text, (10, y_offset))
            y_offset += 25
        
        # Controls
        controls_text = self.small_font.render('Controls: Left/Right arrows, P to pause', True, GRAY)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))

    def draw(self):
        self.screen.fill(BLACK)

        # Draw platforms and power-ups
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_y, self.player.big_platforms_timer > 0)
            
        for powerup in self.powerups:
            powerup.draw(self.screen, self.camera_y)
            
        self.player.draw(self.screen, self.camera_y)

        # Draw UI
        self.draw_ui()

        # Draw pause screen
        if self.paused:
            pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            pause_surface.set_alpha(128)
            pause_surface.fill(BLACK)
            self.screen.blit(pause_surface, (0, 0))
            
            pause_text = self.font.render('PAUSED', True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(pause_text, pause_rect)
            
            resume_text = self.small_font.render('Press P to resume', True, WHITE)
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(resume_text, resume_rect)

        # Draw game over message and statistics
        if self.game_over:
            game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_over_surface.set_alpha(200)
            game_over_surface.fill(BLACK)
            self.screen.blit(game_over_surface, (0, 0))
            
            # Game Over text
            game_over_text = self.font.render('Game Over!', True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Statistics
            final_score_text = self.font.render(f'Final Score: {int(self.score)}', True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(final_score_text, final_score_rect)
            
            if self.score == self.high_score and self.score > 0:
                new_record_text = self.small_font.render('NEW HIGH SCORE!', True, YELLOW)
                new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
                self.screen.blit(new_record_text, new_record_rect)
            
            game_time = (pygame.time.get_ticks() - self.start_time) // 1000
            stats_text = self.small_font.render(f'Time: {game_time}s | Jumps: {self.total_jumps} | Power-ups: {self.powerups_collected}', True, WHITE)
            stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(stats_text, stats_rect)
            
            restart_text = self.small_font.render('Press R to Restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
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