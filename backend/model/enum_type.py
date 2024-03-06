def get_enum(value, *args):
    for cls in args:
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError:
            pass
    raise ValueError("Expected string that is enum in ", args)