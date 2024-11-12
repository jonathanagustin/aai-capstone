import importlib

__all__ = [

# TODO: DEFINE STAGES HERE

]


def __getattr__(name):
    if name in __all__:
        # Import module dynamically based on the class name
        module = importlib.import_module(f"pipeline.stages.{name.lower()}")
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
