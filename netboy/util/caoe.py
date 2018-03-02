

import errno
import os
import sys
import time
from signal import signal, SIGINT, SIGQUIT, SIGTERM, SIGCHLD, SIGHUP, pause, SIG_DFL

__all__ = ['install']

PARENT_POLL_INTERVAL = 5  # only used if no prctl available


def install(fork=True, sig=SIGTERM):
    def _reg(gid):
        handler = make_quit_signal_handler(gid, sig)
        signal(SIGINT, handler)
        signal(SIGQUIT, handler)
        signal(SIGTERM, handler)
        signal(SIGCHLD, make_child_die_signal_handler(gid, sig))

    if not fork:
        _reg(os.getpid())
        return

    pid = os.fork()
    if pid == 0:
        # child process
        os.setpgrp()
        pid = os.fork()
        if pid != 0:
            # still in child process
            exit_when_parent_or_child_dies(sig)

        # grand child process continues...

    else:
        # parent process
        gid = pid
        _reg(gid)
        while True:
            pause()


def make_quit_signal_handler(gid, sig=SIGTERM):
    def handler(signum, frame):
        signal(SIGTERM, SIG_DFL)
        try:
            os.killpg(gid, sig)
        except os.error as ex:
            if ex.errno != errno.ESRCH:
                raise
    return handler


def make_child_die_signal_handler(gid, sig=SIGTERM):
    def handler(signum, frame):
        try:
            pid, status = os.wait()
        except OSError:
            # sometimes there is no child processes already
            status = 0

        try:
            signal(SIGTERM, SIG_DFL)
            os.killpg(gid, sig)
        finally:
            sys.exit((status & 0xff00) >> 8)
    return handler


def exit_when_parent_or_child_dies(sig):
    gid = os.getpgrp()
    signal(SIGCHLD, make_child_die_signal_handler(gid))

    try:
        import prctl
        signal(SIGHUP, make_quit_signal_handler(gid))
        # give me SIGHUP if my parent dies
        prctl.set_pdeathsig(SIGHUP)
        while True:
            pause()

    except ImportError:
        # fallback to polling status of parent
        while True:
            if os.getppid() == 1:
                # parent died, suicide
                signal(SIGTERM, SIG_DFL)
                os.killpg(gid, sig)
                sys.exit()
            time.sleep(PARENT_POLL_INTERVAL)
