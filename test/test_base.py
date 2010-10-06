
from pypy.jit.metainterp.test.oparser import parse
from baseviewer import slice_debug_merge_points

def test_split():
    ops = parse('''
    [i0]
    debug_merge_point("<code object stuff, file '/tmp/x.py', line 200> #10 ADD")
    debug_merge_point("<code object stuf, file '/tmp/x.py', line 201> #11 SUB")
    i1 = int_add(i0, 1)
    debug_merge_point("<code object stuf, file '/tmp/x.py', line 202> #11 SUB")
    i2 = int_add(i1, 1)
    ''', no_namespace=True, nonstrict=True)
    res = slice_debug_merge_points(ops)
    assert len(res.chunks) == 3
    assert len(res.chunks[0].operations) == 1
    assert len(res.chunks[1].operations) == 2
    assert len(res.chunks[2].operations) == 2
    
