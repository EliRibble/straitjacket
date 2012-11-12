import subprocess
import signal
import os
import threading
import errno
import logging

from contextlib import contextmanager

LOGGER = logging.getLogger('timeout')

class TimeoutThread(object):
    def __init__(self, seconds):
        self.seconds = seconds
        self.cond = threading.Condition()
        self.cancelled = False
        self.thread = threading.Thread(target=self._wait)

    def run(self):
        """Begin the timeout."""
        self.thread.start()

    def _wait(self):
        with self.cond:
            self.cond.wait(self.seconds)

            if not self.cancelled:
                self.timed_out()

    def cancel(self):
        """Cancel the timeout, if it hasn't yet occured."""
        with self.cond:
            self.cancelled = True
            self.cond.notify()
        self.thread.join()

    def timed_out(self):
        """The timeout has expired."""
        raise NotImplementedError

class KillProcessThread(TimeoutThread):
    def __init__(self, seconds, pid):
        super(KillProcessThread, self).__init__(seconds)
        self.pid = pid
        self.timedout = False

    def timed_out(self):
        self.timedout = True
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError as e:
            # If the process is already gone, ignore the error.
            if e.errno not in (errno.EPERM, errno.ESRCH):
                raise e

class ProcessTimeout(object):
    def __init__(self, seconds, pid):
        self.timeout = KillProcessThread(seconds, pid)

    def __enter__(self):
        LOGGER.debug("Starting timeout process for %d with %d seconds timeout", self.timeout.pid, self.timeout.seconds)
        self.timeout.run()

    def __exit__(self, *args, **kwargs):
        self.timeout.cancel()

    @property
    def timedout(self):
        return self.timeout.timedout

@contextmanager
def ProcessTimeout(seconds, pid):
    timeout = KillProcessThread(seconds, pid)
    timeout.run()
    try:
        yield
    finally:
        timeout.cancel()
