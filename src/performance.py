import time
import pygame
from collections import deque

class PerformanceMonitor:
    def __init__(self, max_samples=60):
        self.max_samples = max_samples
        self.frame_times = deque(maxlen=max_samples)
        self.last_frame_time = time.time()
        self.font = pygame.font.Font(None, 24)
        
    def update(self):
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        
    def get_fps(self):
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
    def get_frame_time_ms(self):
        if not self.frame_times:
            return 0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000
        
    def draw_stats(self, screen, x=10, y=10):
        fps = self.get_fps()
        frame_time = self.get_frame_time_ms()
        
        fps_text = self.font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        frame_time_text = self.font.render(f"Frame: {frame_time:.1f}ms", True, (255, 255, 255))
        
        screen.blit(fps_text, (x, y))
        screen.blit(frame_time_text, (x, y + 25))