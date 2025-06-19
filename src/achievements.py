import json
import os

class Achievement:
    def __init__(self, name, description, condition, unlocked=False):
        self.name = name
        self.description = description
        self.condition = condition
        self.unlocked = unlocked

class AchievementManager:
    def __init__(self):
        self.achievements = {
            "first_jump": Achievement("First Steps", "Make your first jump", lambda stats: stats["jumps"] >= 1),
            "score_100": Achievement("Century", "Reach score of 100", lambda stats: stats["score"] >= 100),
            "score_500": Achievement("High Flyer", "Reach score of 500", lambda stats: stats["score"] >= 500),
            "powerup_collector": Achievement("Power Hunter", "Collect 10 power-ups", lambda stats: stats["powerups"] >= 10),
            "time_survivor": Achievement("Endurance", "Survive for 5 minutes", lambda stats: stats["time"] >= 300),
        }
        self.load_achievements()
    
    def check_achievements(self, stats):
        newly_unlocked = []
        for key, achievement in self.achievements.items():
            if not achievement.unlocked and achievement.condition(stats):
                achievement.unlocked = True
                newly_unlocked.append(achievement)
        
        if newly_unlocked:
            self.save_achievements()
        return newly_unlocked
    
    def save_achievements(self):
        data = {key: ach.unlocked for key, ach in self.achievements.items()}
        with open("achievements.json", "w") as f:
            json.dump(data, f)
    
    def load_achievements(self):
        try:
            if os.path.exists("achievements.json"):
                with open("achievements.json", "r") as f:
                    data = json.load(f)
                    for key, unlocked in data.items():
                        if key in self.achievements:
                            self.achievements[key].unlocked = unlocked
        except:
            pass