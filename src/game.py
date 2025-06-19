import pygame
import random
import json
import os
from .constants import *
from .player import Player
from .platform import Platform
from .powerup import PowerUp
from .particles import ParticleSystem

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
        
        self.high_score = self.load_high_score()
        self.start_time = pygame.time.get_ticks()
        self.end_time = None
        self.total_jumps = 0
        self.powerups_collected = 0
        self.particles = ParticleSystem()
        
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
        self.platforms = []
        self.powerups = []
        self.camera_y = 0
        self.score = 0
        self.highest_point = SCREEN_HEIGHT
        self.start_time = pygame.time.get_ticks()
        self.end_time = None
        self.total_jumps = 0
        self.powerups_collected = 0

        initial_platform = Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2, 
                                 SCREEN_HEIGHT - 100, 
                                 PLATFORM_WIDTH)
        self.platforms.append(initial_platform)

        for i in range(1, 10):
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = SCREEN_HEIGHT - (i * 100)
            platform_width = max(MIN_PLATFORM_WIDTH, 
                               PLATFORM_WIDTH * (PLATFORM_WIDTH_SCALE ** i))
            platform_type = "special" if random.random() < 0.1 else "normal"
            self.platforms.append(Platform(x, y, platform_width, platform_type))

        self.player = Player(initial_platform.rect.centerx - 20, initial_platform.rect.top - 40)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.game_over = False
                    self.init_game()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused

        if not self.paused and not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED
            
                if keys[pygame.K_UP] and self.player.double_jumps_left > 0:
                self.player.jump()
                self.total_jumps += 1
                # Skip sound for web compatibility

    def spawn_powerup(self, platform):
        if random.random() < 0.15:
            powerup_type = random.choice([POWERUP_DOUBLE_JUMP, POWERUP_BIG_PLATFORMS, POWERUP_SLOW_MOTION])
            powerup_x = platform.rect.x + platform.rect.width // 2 - 15
            powerup_y = platform.rect.y - 35
            self.powerups.append(PowerUp(powerup_x, powerup_y, powerup_type))

    def update(self):
        if self.game_over or self.paused:
            return

        prev_y = self.player.rect.y
        self.player.update()
        self.particles.update()

        # Platform collisions
        for platform in self.platforms:
            prev_bottom = prev_y + self.player.rect.height
            platform_width = platform.get_display_width(self.player.big_platforms_timer > 0)

            if (self.player.vel_y > 0 and
                    prev_bottom <= platform.rect.top and
                    self.player.rect.bottom >= platform.rect.top and
                    self.player.rect.bottom <= platform.rect.bottom and
                    self.player.rect.right >= platform.rect.left and
                    self.player.rect.left <= platform.rect.left + platform_width):
                self.player.y = platform.rect.top - self.player.rect.height
                self.player.rect.bottom = platform.rect.top
                self.player.vel_y = JUMP_SPEED
                self.total_jumps += 1
                self.particles.add_explosion(self.player.rect.centerx, self.player.rect.bottom, GREEN, 5)
                
                if self.player.double_jumps_left == 0:
                    self.player.double_jumps_left = 1 if self.player.double_jumps_left > 0 else 0

        # Power-up collisions
        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                self.powerups.remove(powerup)
                self.powerups_collected += 1
                
                if powerup.type == POWERUP_DOUBLE_JUMP:
                    self.player.double_jumps_left = 2
                elif powerup.type == POWERUP_BIG_PLATFORMS:
                    self.player.big_platforms_timer = 600
                elif powerup.type == POWERUP_SLOW_MOTION:
                    self.player.slow_motion_timer = 300

        # Update score
        if self.player.y < self.highest_point:
            self.highest_point = self.player.y
            self.score = (SCREEN_HEIGHT - self.highest_point) // 10
            
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

        self.camera_y = self.player.y - SCREEN_HEIGHT // 2

        # Generate platforms
        if len(self.platforms) > 0:
            current_score = (SCREEN_HEIGHT - self.platforms[-1].y) // 10
            difficulty_factor = min(1.0, current_score / 150.0)
        else:
            difficulty_factor = 0.0
            
        max_platforms = max(6, 15 - int(difficulty_factor * 9))
        while len(self.platforms) < max_platforms:
            prev_platform = self.platforms[-1]
            current_score = (SCREEN_HEIGHT - prev_platform.y) // 10
            difficulty_factor = min(1.0, current_score / 150.0)
            
            base_min_gap = 30
            base_max_gap = 60
            min_gap = int(base_min_gap + difficulty_factor * 40)
            max_gap = int(base_max_gap + difficulty_factor * 60)
            max_gap = min(max_gap, 120)
            min_gap = min(min_gap, max_gap - 10)
            
            vertical_gap = random.randint(min_gap, max_gap)
            y = prev_platform.y - vertical_gap
            
            width_reduction_factor = 1.0 - (difficulty_factor * 0.8)
            platform_width = max(MIN_PLATFORM_WIDTH, 
                               int(PLATFORM_WIDTH * width_reduction_factor))
            
            prev_center = prev_platform.rect.centerx
            base_range = SCREEN_WIDTH * 0.2
            max_range = SCREEN_WIDTH * 0.8
            current_range = base_range + (max_range - base_range) * difficulty_factor
            max_horizontal_offset = int(min(500, current_range))
            
            potential_positions = []
            
            if difficulty_factor < 0.2:
                spread_offset = random.randint(-100, 100)
                x1 = prev_center + spread_offset - platform_width // 2
                potential_positions.append(x1)
                
                wider_offset = random.randint(-160, 160)
                x2 = prev_center + wider_offset - platform_width // 2
                potential_positions.append(x2)
                
            elif difficulty_factor < 0.5:
                wide_offset = random.randint(-180, 180)
                x1 = prev_center + wide_offset - platform_width // 2
                potential_positions.append(x1)
                
                very_wide_offset = random.randint(-280, 280)
                x2 = prev_center + very_wide_offset - platform_width // 2
                potential_positions.append(x2)
                
            else:
                extreme_offset = random.randint(-250, 250)
                x1 = prev_center + extreme_offset - platform_width // 2
                potential_positions.append(x1)
                
                massive_offset = random.randint(-400, 400)
                x2 = prev_center + massive_offset - platform_width // 2
                potential_positions.append(x2)
                
                if random.random() < 0.5:
                    if prev_center < SCREEN_WIDTH // 2:
                        far_right_x = random.randint(SCREEN_WIDTH - platform_width - 50, SCREEN_WIDTH - platform_width - 10)
                        potential_positions.append(far_right_x)
                    else:
                        far_left_x = random.randint(10, 50)
                        potential_positions.append(far_left_x)
            
            max_offset = min(max_horizontal_offset, 450)
            extreme_random_offset = random.randint(-max_offset, max_offset)
            x3 = prev_center + extreme_random_offset - platform_width // 2
            potential_positions.append(x3)
            
            best_x = None
            best_score = -1
            
            for x in potential_positions:
                x_clamped = max(0, min(x, SCREEN_WIDTH - platform_width))
                
                on_screen_ratio = 1.0
                if x < 0:
                    on_screen_ratio = max(0, (platform_width + x) / platform_width)
                elif x + platform_width > SCREEN_WIDTH:
                    on_screen_ratio = max(0, (SCREEN_WIDTH - x) / platform_width)
                
                distance_penalty = abs(x_clamped + platform_width//2 - prev_center) / SCREEN_WIDTH
                penalty_weight = 0.15 + difficulty_factor * 0.1
                score = on_screen_ratio - distance_penalty * penalty_weight
                
                if score > best_score:
                    best_score = score
                    best_x = x_clamped
            
            platform_type = "special" if random.random() < 0.08 else "normal"
            new_platform = Platform(best_x, y, platform_width, platform_type)
            self.platforms.append(new_platform)
            self.spawn_powerup(new_platform)

        self.platforms = [p for p in self.platforms
                          if p.y - self.camera_y < SCREEN_HEIGHT + 200]
        self.powerups = [p for p in self.powerups
                        if p.rect.y - self.camera_y < SCREEN_HEIGHT + 100]

        # Game over conditions
        if self.player.y - self.camera_y > SCREEN_HEIGHT:
            if not self.game_over:
                self.end_time = pygame.time.get_ticks()
            self.game_over = True
        elif self.player.is_falling and (self.player.y - self.player.fall_start_y) > MAX_FALL_DISTANCE:
            if not self.game_over:
                self.end_time = pygame.time.get_ticks()
            self.game_over = True

    def draw_ui(self):
        score_text = self.font.render(f'Score: {int(self.score)}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.small_font.render(f'High Score: {int(self.high_score)}', True, YELLOW)
        self.screen.blit(high_score_text, (10, 50))
        
        if self.end_time:
            game_time = (self.end_time - self.start_time) // 1000
        else:
            game_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.small_font.render(f'Time: {game_time}s', True, WHITE)
        self.screen.blit(time_text, (10, 75))
        
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
        
        controls_text = self.small_font.render('Controls: Left/Right arrows, P to pause', True, GRAY)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))

    def draw(self):
        self.screen.fill(BLACK)

        for platform in self.platforms:
            platform.draw(self.screen, self.camera_y, self.player.big_platforms_timer > 0)
            
        for powerup in self.powerups:
            powerup.draw(self.screen, self.camera_y)
            
        self.particles.draw(self.screen, self.camera_y)
        self.player.draw(self.screen, self.camera_y)
        self.draw_ui()

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

        if self.game_over:
            game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_over_surface.set_alpha(200)
            game_over_surface.fill(BLACK)
            self.screen.blit(game_over_surface, (0, 0))
            
            game_over_text = self.font.render('Game Over!', True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(game_over_text, game_over_rect)
            
            final_score_text = self.font.render(f'Final Score: {int(self.score)}', True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(final_score_text, final_score_rect)
            
            if self.score == self.high_score and self.score > 0:
                new_record_text = self.small_font.render('NEW HIGH SCORE!', True, YELLOW)
                new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
                self.screen.blit(new_record_text, new_record_rect)
            
            game_time = (self.end_time - self.start_time) // 1000
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