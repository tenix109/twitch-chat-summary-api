import time

class PomodoroTimer:
    def __init__(self):
        self.start_time = None
        self.duration = None  # in seconds
        self.active = False
        self.mode = "work"  # "work" or "break"

    def start(self, minutes=25, mode="work"):
        self.start_time = time.time()
        self.duration = minutes * 60
        self.active = True
        self.mode = mode

    def time_left(self):
        if not self.active:
            return 0
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)

    def is_done(self):
        return self.active and self.time_left() <= 0

    def reset(self):
        self.start_time = None
        self.duration = None
        self.active = False