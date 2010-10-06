
from pypy.jit.metainterp.test.oparser import parse
from baseviewer import slice_debug_merge_points, parse_log_counts

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
    assert res.lineno == 200
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

LINES = """19883   <code object _optimize_charset, file '/home/fijal/src/pypy-trunk/lib-python/modified-2.5.2/sre_compile.py', line 214> #290 FOR_ITER
645     <code object _optimize_charset, file '/home/fijal/src/pypy-trunk/lib-python/modified-2.5.2/sre_compile.py', line 214> #290 FOR_ITER
3810    <code object _mk_bitmap, file '/home/fijal/src/pypy-trunk/lib-python/modified-2.5.2/sre_compile.py', line 265> #66 FOR_ITER
334     <code object _mk_bitmap, file '/home/fijal/src/pypy-trunk/lib-python/modified-2.5.2/sre_compile.py', line 265> #66 FOR_ITER
5       <code object _optimize_charset, file '/home/fijal/src/pypy-trunk/lib-python/modified-2.5.2/sre_compile.py', line 214> #346 POP_TOP
2256920 <code object <genexp>, file '/home/fijal/src/pypy-benchmarks/unladen_swallow/performance/bm_ai.py', line 67> #24 POP_TOP
2256864 <code object <genexp>, file '/home/fijal/src/pypy-benchmarks/unladen_swallow/performance/bm_ai.py', line 46> #20 POP_TOP
1955880 <code object <genexp>, file '/home/fijal/src/pypy-benchmarks/unladen_swallow/performance/bm_ai.py', line 67> #9 STORE_FAST
1956214 <code object <genexp>, file '/home/fijal/src/pypy-benchmarks/unladen_swallow/performance/bm_ai.py', line 46> #9 STORE_FAST
""".split("\n")

#def test_parse_log_count():
#    parse_log_counts(LINES)
