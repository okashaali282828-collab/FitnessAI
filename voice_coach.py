import pyttsx3
import threading

class VoiceCoach:
    def __init__(self):
        self.speaking = False
        self.last_message = ""
        self.last_posture_msg = ""

    def _speak(self, text):
        self.speaking = True
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except:
            pass
        self.speaking = False

    def say(self, text):
        """Sirf bolega agar message naya ho aur abhi bol nahi raha"""
        if not self.speaking and text != self.last_message:
            self.last_message = text
            t = threading.Thread(target=self._speak, args=(text,))
            t.daemon = True
            t.start()

    def say_always(self, text):
        """Har baar bolega — rep count ke liye"""
        if not self.speaking:
            t = threading.Thread(target=self._speak, args=(text,))
            t.daemon = True
            t.start()

    def say_posture(self, issue):
        """Posture issue — sirf naya message bolega"""
        if not self.speaking and issue != self.last_posture_msg:
            self.last_posture_msg = issue
            t = threading.Thread(target=self._speak, args=(issue,))
            t.daemon = True
            t.start()