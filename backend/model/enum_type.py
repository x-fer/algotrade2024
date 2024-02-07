from enum import Enum


def enum_type(cls):
    class ClsField():
        def __init__(self, *, default=None):
            self._default = default

        def __set_name__(self, owner, name):
            self._name = "_" + name

        def __get__(self, obj, type):
            if obj is None:
                return self._default
            return cls(getattr(obj, self._name))

        def __set__(self, obj, value):
            if isinstance(value, Enum):
                setattr(obj, self._name, value.value)
            else:
                setattr(obj, self._name, value)
    return ClsField