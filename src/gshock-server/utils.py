_run_once_registry = set()

def run_once_key(key, func, *args, **kwargs):
    if key in _run_once_registry:
        return
    _run_once_registry.add(key)
    return func(*args, **kwargs)