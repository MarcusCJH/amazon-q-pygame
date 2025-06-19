import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
    def load_sound(self, name, file_path):
        if os.path.exists(file_path):
            self.sounds[name] = pygame.mixer.Sound(file_path)
            self.sounds[name].set_volume(self.sfx_volume)
    
    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
    
    def play_music(self, file_path, loop=-1):
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loop)