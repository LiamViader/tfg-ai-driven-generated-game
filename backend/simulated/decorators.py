def requires_modification(method):
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "_is_modifiable", False):
            raise RuntimeError(
                f"Cannot call '{method.__name__}' on read-only SimulatedMap. "
                "Use `modify_map()` from SimulatedGameState to obtain a writable version."
            )
        return method(self, *args, **kwargs)
    return wrapper