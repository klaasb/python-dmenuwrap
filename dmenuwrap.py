"""Easily provide selection options to dmenu and handle them with python
scripts."""

import subprocess
import inspect
from collections import OrderedDict


DEFAULT_DMENU_PATH = "/usr/bin/dmenu"


def dmenu(options, args=[], path=DEFAULT_DMENU_PATH):
    """
    Displays an options menu with the given options by executing dmenu
    with the provided list of arguments. Returns the chosen option
    or None if none of the given options was chosen.
    """
    dmenu = subprocess.Popen([path] + args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    option_lines = '\n'.join(map(str, options))
    option = dmenu.communicate(option_lines.encode('utf-8'))[0] \
        .decode('utf-8').rstrip()
    return option if option in options else None


class DMenu:
    """Provides common functions for executing dmenu with a list of options.
    Subclasses should override create_options and handle_option.
    """

    def create_options(self):
        """
        Returns a list of options. Each option should have a __str__ function.
        To be overwritten by subclasses.
        """
        return []

    def handle_option(self, option, options):
        """
        Handles the option chosen in the dmenu.
        To be overwritten by subclasses.
        """
        pass

    def run(self, args=[], path=DEFAULT_DMENU_PATH):
        """
        Creates the options with the create_options function and passes
        them to dmenu with the additional arguments.
        If an option was selected it is passed to the handle_option function.
        """
        options = self.create_options()
        option = dmenu(options, args=args, path=path)
        if option:
            self.handle_option(option, options)


class HandlerListDMenu(DMenu):
    """
    Defines a dmenu based on a given list of handler functions.
    Only functions without arguments are considered, the rest is ignored.
    The displayed options are the function names. The chosen function is
    then called without any argument.
    """

    def __init__(self, option_handlers, sort=True):
        handler_list = [(fn.__name__, fn) for fn in option_handlers
                        if len(inspect.signature(fn).parameters) == 0]
        if sort:
            handler_list = sorted(handler_list)
        self.option_handlers = OrderedDict(handler_list)

    def create_options(self):
        return(self.option_handlers.keys())

    def handle_option(self, option, options):
        if option:
            handler = self.option_handlers[option]
            handler()


class HandlerDMenu(HandlerListDMenu):
    """
    Defines a dmenu based on the member functions defined in the given object.
    Only functions without arguments are considered and any functions
    with names beginning in '__' are ignored.
    The functions will always be sorted by name.
    """

    def __init__(self, option_handlers):
        fn_list = [fn for (name, fn) in
                   inspect.getmembers(option_handlers,
                                      inspect.isfunction)
                   if not name.startswith('__')]
        HandlerListDMenu.__init__(self, fn_list, sort=False)
