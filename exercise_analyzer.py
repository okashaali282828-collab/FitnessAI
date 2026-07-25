import numpy as np

class ExerciseAnalyzer:
    def __init__(self):
        pass

    def calculate_angle(self, a, b, c):
        """3 points ke beech angle calculate karo"""
        a = np.array(a)  # Upar wala point (e.g. shoulder)
        b = np.array(b)  # Beech wala point (e.g. elbow)
        c = np.array(c)  # Neeche wala point (e.g. wrist)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
                  np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return round(angle, 2)
    