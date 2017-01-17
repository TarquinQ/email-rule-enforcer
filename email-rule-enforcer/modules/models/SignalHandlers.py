
# need to handle SIGHUP, SIGTERM, SIGQUIT, SIGUSR1, SIGUSR2
# NB Windows Support: On Windows, signal() can only be called with SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, or SIGTERM. A ValueError will be raised in any other case.
# Note that not all systems define the same set of signal names; an AttributeError will be raised if a signal name is not defined as SIG* module level constant.

import signal


class Signal_GlobalShutdown(Exception):
    '''An exception thrown in main thread to signal a shutdown'''
    pass


def receive_sigterm(signum, stack):
    print ('ALERT:  Received signal to shut down (Signal {0}, SIGTERM. Time to shut down.'.format(signnum))
    raise Signal_GlobalShutdown


def register_sighandlers():
    try:
        signal.signal(signal.SIGTERM, receive_sigterm)
    except ValueError:
        pass
