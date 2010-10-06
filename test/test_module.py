
from module_finder import find_module

def test_find_module():
    sys_path = ["/usr/lib/python2.6", '/home/stuff']
    path, modname = find_module('/usr/lib/python2.6/re.py', sys_path)
    assert path == sys_path[0]
    assert modname == 're'
    path, modname = find_module('/usr/lib/python2.6/stuff/re.py', sys_path)
    assert path == sys_path[0]
    assert modname == 'stuff.re'
    path, modname = find_module('/usr/lib/python2.6/stuff/re.pyc', sys_path)
    assert path == sys_path[0]
    assert modname == 'stuff.re'
