
import inspect

from ovirtsdk.xml import params

class TypeHelper():
    __known_wrapper_types = None

    @staticmethod
    def _getKnownTypes():
        known_wrapper_types = {}
        for name, obj in inspect.getmembers(params):
            if inspect.isclass(obj):
                known_wrapper_types[name.lower()] = name
        return known_wrapper_types

    @staticmethod
    def isKnownType(typ):
        if TypeHelper.__known_wrapper_types == None:
            TypeHelper.__known_wrapper_types = TypeHelper._getKnownTypes()
        return TypeHelper.__known_wrapper_types.has_key(typ.lower())

    @staticmethod
    def getKnownTypes():
        if TypeHelper.__known_wrapper_types == None:
            TypeHelper.__known_wrapper_types = TypeHelper._getKnownTypes()
        return TypeHelper.__known_wrapper_types.values()
