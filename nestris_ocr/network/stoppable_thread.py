import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super().__init__()
        self._mystopEvent = threading.Event()

    def stop(self):
        self._mystopEvent.set()

    def stopped(self):
        return self._mystopEvent.isSet()
