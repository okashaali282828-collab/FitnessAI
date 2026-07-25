import csv
import os
from datetime import datetime

class ProgressTracker:
    def __init__(self):
        self.filepath = "data/workout_history.csv"
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["date", "reps", "avg_posture", "best_score", "duration"])

    def save_session(self, reps, avg_posture, best_score, duration):
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                reps, avg_posture, best_score, duration
            ])

    def load_history(self):
        history = []
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    history.append(row)
        return history