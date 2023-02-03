from time import time


class Timer:
    def __init__(self):
        self._next_time = None

    def set_timer(self, seconds):
        self._next_time = time() + seconds

    def is_done(self):
        if self._next_time is None:
            return True
        if self._next_time <= time():
            self._next_time = None
            return True
        else:
            return False
