import logging
import threading
from typing import List, Callable


class WorkQueue:
    """A rudimentary work queue"""

    def __init__(self):
        """Constructor"""

        self._queue: List[Callable] = []
        self._queue_lock = threading.Lock()
        self._condition = threading.Condition()

    def push(self, func: Callable):
        """
        Function that pushes a Callable to the queue,
        then notifies all waiting threads
        """

        with self._condition:

            # atomic write
            with self._queue_lock:
                logging.info(f"Pushing job... ({func.__name__})")
                self._queue.append(func)

            # notify a thread
            self._condition.notify()

    def pop(self):
        """
        Function that waits thread until Callable is available,
        then returns said callable
        """

        with self._condition:

            # wait for notification/timeout, whichever comes first
            self._condition.wait(timeout=5.0)

            # atomic read
            func = None
            with self._queue_lock:
                if len(self._queue) > 0:
                    func = self._queue.pop(0)
                    logging.info(f"Popping job... ({func.__name__})")

            # return callable for thread
            return func


class WorkerThread(threading.Thread):
    """Main Worker Thread Class"""

    def __init__(self, name):
        """Constructor"""

        super().__init__()
        self.name = name
        self.daemon = True

    def run(self):
        """
        Main thread event loop
        NOTE: This function should never be called directly
        """
        global queue

        logging.info("Starting...")
        while True:
            func = queue.pop()
            if callable(func):
                func()


# Static Initialization
queue = None
if queue is None:
    queue = WorkQueue()
