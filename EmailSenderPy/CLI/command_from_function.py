import inspect
from typing import Callable


class Command():
    def __init__(self, func: Callable, **args):
        self.func = func
        self.args = dict()
        self.name = func.__name__
        self.params = list(inspect.signature(self.func).parameters.keys())
        # Only have the default parameters set if they exist in the function
        for arg in args:
            if arg in self.params:
                self.args[arg] = args[arg]

    def call_command(self, **args):

        current_args = self.args | args
        return self.func(**current_args)


def create_commands_by_imports(_import, black_list=[], **args):
    # get the functions
    functions = [obj for name, obj in inspect.getmembers(
        _import, inspect.isfunction) if not name in black_list]
    return [Command(func=func, **args) for func in functions]
