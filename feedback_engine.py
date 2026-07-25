class FeedbackEngine:
    def __init__(self):
        self.issues = []

    def analyze_posture(self, landmarks, frame_shape, analyzer):
        self.issues = []
        h, w = frame_shape[:2]

        def pt(idx):
            lm = landmarks[idx]
            return (lm.x * w, lm.y * h)

        # ── Shoulder level check ──────────────────────────
        l_shoulder = pt(11)
        r_shoulder = pt(12)
        shoulder_diff = abs(l_shoulder[1] - r_shoulder[1])
        if shoulder_diff > h * 0.05:
            self.issues.append("Kandhe seedhe karo!")

        # ── Neck / Head forward check ─────────────────────
        nose = pt(0)
        mid_shoulder_x = (l_shoulder[0] + r_shoulder[0]) / 2
        if abs(nose[0] - mid_shoulder_x) > w * 0.08:
            self.issues.append("Gardan seedhi rakhо!")

        # ── Back straight check (hip-shoulder alignment) ──
        l_hip = pt(23)
        r_hip = pt(24)
        mid_hip_x = (l_hip[0] + r_hip[0]) / 2
        if abs(mid_shoulder_x - mid_hip_x) > w * 0.07:
            self.issues.append("Kamar seedhi karo!")

        # ── Elbow symmetry check ──────────────────────────
        l_elbow = pt(13)
        r_elbow = pt(14)
        elbow_diff = abs(l_elbow[1] - r_elbow[1])
        if elbow_diff > h * 0.12:
            self.issues.append("Dono kohni barabar rakhо!")

        return self.issues

    def get_posture_score(self):
        """0-100 score — jitni zyada issues, utna kam score"""
        max_issues = 4
        score = max(0, 100 - (len(self.issues) * 25))
        return score

    def get_score_color(self, score):
        if score >= 75:
            return (0, 255, 100)    # Green — acha
        elif score >= 50:
            return (0, 200, 255)    # Yellow — theek
        else:
            return (0, 80, 255)     # Red — kharab