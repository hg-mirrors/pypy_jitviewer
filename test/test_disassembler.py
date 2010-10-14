
import disassembler, sys
import py

def f(a, b):
    return a + b

def test_disassembler():
    res = disassembler.dis(f)
    if sys.version_info[:2] != (2, 6):
        py.test.skip("2.6 only test")
    assert len(res.opcodes) == 4
    assert [x.__class__.__name__ for x in res.opcodes] == [
        'LOAD_FAST', 'LOAD_FAST', 'BINARY_ADD', 'RETURN_VALUE']
    for i in range(4):
        assert res.opcodes[i].lineno == f.func_code.co_firstlineno + 1
    
