
import os, sys

class NotFound(Exception):
    """ An exception raised when module was not found in sys.path
    """

def find_module(name, sys_path=sys.path):
    """ Searches sys.path for possible parent paths for name (which is
    a filesystem name). Returns a pair (entry in sys.path, name of module)
    where name of module is a reasonable name to be passed as argument for
    __import__
    """
    sys_path_dict = {}
    for path in sys_path:
        sys_path_dict[path] = None
    bases = name.split(os.path.sep)
    for i in range(len(bases) - 1, -1, -1):
        prefix = os.path.sep.join(bases[:i])
        if prefix in sys_path_dict:
            modname = ".".join(bases[i:])
            if modname.endswith('.pyc'):
                modname = modname[:-4]
            else:
                assert modname.endswith(".py")
                modname = modname[:-3]
            return prefix, modname
    raise NotFound

def import_module(name):
    """ Finds a module based on it's name. Looks for all paths above if they're
    on sys.path. if so, loads the parent sys.path and then module. Might
    not be 100% proof, but should work in most cases
    """
    sys_path_entry, modname = find_module(name)
