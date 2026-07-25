import cv2
import threading
from pose_detector import PoseDetector
from exercise_analyzer import ExerciseAnalyzer
from exercises.bicep_curl import BicepCurl
from feedback_engine import FeedbackEngine
from voice_coach import VoiceCoach
from dashboard import Dashboard
from web_dashboard import send_update, run_server

detector  = PoseDetector()
analyzer  = ExerciseAnalyzer()
curl      = BicepCurl()
feedback  = FeedbackEngine()
voice     = VoiceCoach()
dashboard = Dashboard()

# Web dashboard background mein start karo
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

WINDOW_NAME = "AI Gym Trainer"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

voice.say("Okasha! Apka AI Gym Trainer ready hai. Ap gym start kar sakte hain!")
print("AI Gym Trainer chal raha hai...")
print("Browser mein yeh kholo: http://localhost:5000")

posture_alert_counter = 0
web_update_counter    = 0
count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = detector.find_pose(frame)
    h, w  = frame.shape[:2]

    if detector.is_detected():
        shoulder = detector.get_landmark(11, frame.shape)
        elbow    = detector.get_landmark(13, frame.shape)
        wrist    = detector.get_landmark(15, frame.shape)

        issues  = feedback.analyze_posture(detector.landmarks, frame.shape, analyzer)
        score   = feedback.get_posture_score()
        s_color = feedback.get_score_color(score)

        posture_alert_counter += 1
        if posture_alert_counter >= 60 and issues:
            if "Kandhe" in issues[0]:
                voice.say_posture("Okasha! Apne kandhe seedhe karo!")
            elif "Gardan" in issues[0]:
                voice.say_posture("Okasha! Apni gardan seedhi rakho!")
            elif "Kamar" in issues[0]:
                voice.say_posture("Okasha! Apni kamar seedhi karo!")
            elif "kohni" in issues[0]:
                voice.say_posture("Okasha! Dono kohni barabar rakho!")
            else:
                voice.say_posture(f"Okasha! {issues[0]}")
            posture_alert_counter = 0

        if shoulder and elbow and wrist:
            angle = analyzer.calculate_angle(shoulder, elbow, wrist)
            count, stage, fb_text, new_rep = curl.analyze(angle)

            if new_rep:
                voice.say_always(f"{count}")

            # ── TOP LEFT — Reps card ───────────────────────
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (190, 100), (15, 15, 15), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
            cv2.rectangle(frame, (10, 10), (190, 100), (0, 255, 100), 2)
            cv2.putText(frame, "REPS", (22, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 100), 2)
            cv2.putText(frame, str(count), (22, 88),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3)
            stage_color = (0, 200, 255) if stage == "down" else (0, 255, 150)
            cv2.putText(frame, stage.upper() if stage else "---", (105, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, stage_color, 2)

            # ── ANGLE badge ────────────────────────────────
            ex, ey = elbow
            cv2.circle(frame, (ex, ey), 22, (255, 200, 0), -1)
            cv2.circle(frame, (ex, ey), 22, (255, 255, 255), 2)
            angle_txt = str(int(angle))
            cv2.putText(frame, angle_txt,
                (ex - len(angle_txt) * 6, ey + 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

            # ── Progress bar ───────────────────────────────
            bar_x, bar_y = w - 40, 20
            bar_h2 = h - 80
            cv2.rectangle(frame, (bar_x, bar_y),
                (bar_x + 18, bar_y + bar_h2), (40, 40, 40), -1)
            fill = int((1 - angle / 180) * bar_h2)
            cv2.rectangle(frame,
                (bar_x, bar_y + bar_h2 - fill),
                (bar_x + 18, bar_y + bar_h2), (0, 255, 100), -1)
            cv2.rectangle(frame, (bar_x, bar_y),
                (bar_x + 18, bar_y + bar_h2), (100, 100, 100), 1)

            # ── Bottom feedback ────────────────────────────
            bar_ov = frame.copy()
            cv2.rectangle(bar_ov, (0, h - 55), (w, h), (10, 10, 10), -1)
            cv2.addWeighted(bar_ov, 0.75, frame, 0.25, 0, frame)
            fb_color = (0, 255, 100) if "Good" in fb_text else (0, 220, 255)
            cv2.putText(frame, fb_text, (20, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, fb_color, 2)

        # ── Posture score top right ────────────────────────
        cv2.putText(frame, f"Posture: {score}%", (w - 220, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, s_color, 2)

        if issues:
            for i, issue in enumerate(issues):
                cv2.putText(frame, f"! {issue}", (w - 420, 80 + i * 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 80, 255), 2)
        else:
            cv2.putText(frame, "Posture Perfect!", (w - 260, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 100), 2)

        # ── OpenCV Dashboard ───────────────────────────────
        frame = dashboard.draw(frame, count, score)

        # ── Web dashboard update har 15 frames ────────────
        web_update_counter += 1
        if web_update_counter >= 15:
            send_update(
                reps    = count,
                timer   = dashboard.get_elapsed_time(),
                posture = score,
                best    = dashboard.best_score,
                issues  = issues
            )
            web_update_counter = 0

    else:
        ov = frame.copy()
        cv2.rectangle(ov, (0, h//2 - 30), (w, h//2 + 30), (0, 0, 0), -1)
        cv2.addWeighted(ov, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, "Camera ke saamne aao - Poora upper body dikhao",
            (20, h//2 + 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 200, 255), 2)

    cv2.imshow(WINDOW_NAME, frame)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()