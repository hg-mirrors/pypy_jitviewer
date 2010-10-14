
import py
from module_finder import load_code, gather_all_code_objs
import re

def test_gather_code():
    fname = py.path.local(__file__).join('..', 'xre.pyc')
    codes = gather_all_code_objs(fname)
    assert len(codes) == 21
    assert sorted(codes.keys()) == [102, 134, 139, 144, 153, 164, 169, 181, 188, 192, 197, 206, 229, 251, 266, 271, 277, 285, 293, 294, 308]

def test_gather_code_py():
    fname = re.__file__
    if fname.endswith('.pyc'):
        fname = fname[:-1]
    codes = gather_all_code_objs(fname)
    assert len(codes) == 21
    assert sorted(codes.keys()) == [102, 134, 139, 144, 153, 164, 169, 181, 188, 192, 197, 206, 229, 251, 266, 271, 277, 285, 293, 294, 308]

def test_load_code():
    fname = py.path.local(__file__).join('..', 'xre.pyc')
    code = load_code(fname, 'name', 144)
    assert code.co_name == 'sub'
    assert code.co_filename == '/usr/lib/python2.6/re.py'
    assert code.co_firstlineno == 144
