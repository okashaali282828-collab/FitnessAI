class BicepCurl:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.prev_count = 0

    def analyze(self, angle):
        feedback = ""
        new_rep = False

        if angle > 160:
            self.stage = "down"

        if angle < 40 and self.stage == "down":
            self.stage = "up"
            self.counter += 1
            feedback = "Good Rep!"
            new_rep = True

        if 40 <= angle <= 90:
            feedback = "Keep Going!"
        elif angle > 160:
            feedback = "Curl Up!"

        return self.counter, self.stage, feedback, new_rep

    def reset(self):
        self.counter = 0
        self.stage = None
        self.prev_count = 0