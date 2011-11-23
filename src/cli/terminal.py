
class Terminal(object):
    """Base class for terminal objects."""

    width = None
    height = None

    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def clear(self):
        raise NotImplementedError

    def set_echo(self, echo):
        raise NotImplementedError

    def readline(self, prompt):
        raise NotImplementedError
