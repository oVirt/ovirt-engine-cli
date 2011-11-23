
import sys

def create(cls, *args, **kwargs):
    """This is our default constructor. It takes care of instantiating the
    right subclass, and configuring it in the right way."""
    from cli.terminal import Terminal
    from optparse import OptionParser
    if issubclass(cls, Terminal):
        obj = cls(sys.stdin, sys.stdout, sys.stderr, **kwargs)
    elif issubclass(cls, OptionParser):
        obj = cls(*args, **kwargs)
        obj.disable_interspersed_args()
    else:
        obj = cls(*args, **kwargs)
    return obj
