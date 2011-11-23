
_super = super

def super(type, self):
    if issubclass(type, object):
        return _super(type, self)
    class proxy(object):
        def __init__(self, type, obj):
            object.__setattr__(self, '__type__', type)
            object.__setattr__(self, '__obj__', obj)
        def __getattribute__(self, name):
            def bind(func, self):
                def _f(*args):
                    func(self, *args)
                return _f
            type = object.__getattribute__(self, '__type__')
            obj = object.__getattribute__(self, '__obj__')
            return bind(getattr(type, name), obj)
    base = type.__bases__[0]
    return proxy(base, self)
