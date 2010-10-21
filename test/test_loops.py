
from pypy.jit.metainterp.test.oparser import parse
from loops import slice_debug_merge_points, parse_log_counts
import py

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
    assert res.chunks[2].bytecode_no == 11
    
def test_name():
    ops = parse('''
    [i0]
    debug_merge_point("<code object stuff, file '/tmp/x.py', line 200> #10 ADD")
    debug_merge_point("<code object stuf, file '/tmp/x.py', line 201> #11 SUB")
    i1 = int_add(i0, 1)
    debug_merge_point("<code object stuf, file '/tmp/x.py', line 202> #11 SUB")
    i2 = int_add(i1, 1)
    ''')
    res = slice_debug_merge_points(ops)
    assert res.repr() == res.chunks[0].repr()
    assert res.repr() == "stuff, file '/tmp/x.py', line 200"
    assert res.startlineno == 200
    assert res.filename == '/tmp/x.py'
    assert res.name == 'stuff'

def test_name_no_first():
    ops = parse('''
    [i0]
    i3 = int_add(i0, 1)
    debug_merge_point("<code object stuff, file '/tmp/x.py', line 200> #10 ADD")
    debug_merge_point("<code object stuf, file '/tmp/x.py', line 201> #11 SUB")
    i1 = int_add(i0, 1)
    debug_merge_point("<code object stuf, file '/tmp/x.py', line 202> #11 SUB")
    i2 = int_add(i1, 1)
    ''')
    res = slice_debug_merge_points(ops)
    assert res.repr() == res.chunks[1].repr()


#def test_parse_log_count():
#    parse_log_counts(LINES)

def test_lineno():
    fname = str(py.path.local(__file__).join('..', 'x.py'))
    ops = parse('''
    [i0, i1]
    debug_merge_point("<code object f, file '%(fname)s', line 2> #0 LOAD_FAST")
    debug_merge_point("<code object f, file '%(fname)s', line 2> #3 LOAD_FAST")
    debug_merge_point("<code object f, file '%(fname)s', line 2> #6 BINARY_ADD")
    debug_merge_point("<code object f, file '%(fname)s', line 2> #7 RETURN_VALUE")
    ''' % locals())
    res = slice_debug_merge_points(ops)
    assert res.chunks[1].lineno == 3

def test_linerange():
    fname = str(py.path.local(__file__).join('..', 'x.py'))
    ops = parse('''
    [i0, i1]
    debug_merge_point("<code object f, file '%(fname)s', line 5> #9 LOAD_FAST")
    debug_merge_point("<code object f, file '%(fname)s', line 5> #12 LOAD_CONST")
    debug_merge_point("<code object f, file '%(fname)s', line 5> #22 LOAD_CONST")
    debug_merge_point("<code object f, file '%(fname)s', line 5> #6 SETUP_LOOP")
    ''' % locals())
    res = slice_debug_merge_points(ops)
    assert res.linerange == (7, 8)
