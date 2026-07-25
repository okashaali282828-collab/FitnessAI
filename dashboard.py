import cv2
import time

class Dashboard:
    def __init__(self):
        self.start_time = time.time()
        self.best_score = 0
        self.total_score_sum = 0
        self.score_count = 0

    def get_elapsed_time(self):
        elapsed = int(time.time() - self.start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        return f"{mins:02d}:{secs:02d}"

    def update_score(self, score):
        if score > self.best_score:
            self.best_score = score
        self.total_score_sum += score
        self.score_count += 1

    def get_avg_score(self):
        if self.score_count == 0:
            return 0
        return int(self.total_score_sum / self.score_count)

    def draw(self, frame, reps, posture_score):
        self.update_score(posture_score)
        h, w = frame.shape[:2]

        # ── BOTTOM RIGHT DASHBOARD CARD ────────────────────
        card_x = w - 280
        card_y = h - 200
        card_w = w - 10
        card_h = h - 60

        # Semi transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (card_x, card_y), (card_w, card_h), (10, 10, 10), -1)
        cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
        cv2.rectangle(frame, (card_x, card_y), (card_w, card_h), (0, 255, 100), 2)

        # Title
        cv2.putText(frame, "SESSION STATS", (card_x + 15, card_y + 28),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)

        # Divider line
        cv2.line(frame,
            (card_x + 10, card_y + 38),
            (card_w - 10, card_y + 38),
            (0, 255, 100), 1)

        # ⏱ Timer
        cv2.putText(frame, "TIME", (card_x + 15, card_y + 65),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, self.get_elapsed_time(), (card_x + 15, card_y + 95),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        #Reps
        cv2.putText(frame, "TOTAL REPS", (card_x + 140, card_y + 65),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, str(reps), (card_x + 155, card_y + 95),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 255), 2)

        # Avg posture score
        avg = self.get_avg_score()
        avg_color = (0, 255, 100) if avg >= 75 else (0, 200, 255) if avg >= 50 else (0, 80, 255)
        cv2.putText(frame, "AVG POSTURE", (card_x + 15, card_y + 120),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, f"{avg}%", (card_x + 15, card_y + 150),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, avg_color, 2)

        # Best score
        best_color = (0, 255, 100) if self.best_score >= 75 else (0, 200, 255)
        cv2.putText(frame, "BEST SCORE", (card_x + 140, card_y + 120),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, f"{self.best_score}%", (card_x + 140, card_y + 150),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, best_color, 2)

        return frame