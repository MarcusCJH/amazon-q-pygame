import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.8
JUMP_SPEED = -15
MOVE_SPEED = 5
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
MAX_FALL_SPEED = 20  # Maximum falling speed
MAX_FALL_DISTANCE = 300  # Maximum distance to fall before game over

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

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
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
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

        # Create initial platforms first
        self.platforms = []
        self.camera_y = 0
        self.score = 0
        self.highest_point = SCREEN_HEIGHT

        # Create initial platform at a fixed position for the player to start on
        initial_platform = Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.platforms.append(initial_platform)

        # Create additional platforms
        for i in range(1, 10):
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = SCREEN_HEIGHT - (i * 100)
            self.platforms.append(Platform(x, y))

        # Initialize player on the first platform
        self.player = Player(initial_platform.rect.centerx - 20, initial_platform.rect.top - 40)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Handle keyboard input
        keys = pygame.key.get_pressed()
        self.player.vel_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED

    def update(self):
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

        # Generate new platforms
        while len(self.platforms) < 10:
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = self.platforms[-1].y - random.randint(100, 200)
            self.platforms.append(Platform(x, y))

        # Remove off-screen platforms
        self.platforms = [p for p in self.platforms
                          if p.y - self.camera_y < SCREEN_HEIGHT + 100]

        # Check game over conditions
        if self.player.y - self.camera_y > SCREEN_HEIGHT:
            self.running = False
        # Check if player has fallen too far without hitting a platform
        elif self.player.is_falling and (self.player.y - self.player.fall_start_y) > MAX_FALL_DISTANCE:
            self.running = False

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