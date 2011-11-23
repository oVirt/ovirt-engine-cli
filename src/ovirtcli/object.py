

def create(cls, *args, **kwargs):
    """Create ovirtcli objects."""
    from ovirtcli.format import Formatter, get_formatter
    if issubclass(cls, Formatter):
        format = args[0]
        cls = get_formatter(format)
        obj = cls(**kwargs)
    else:
        obj = cls(*args, **kwargs)
    return obj
