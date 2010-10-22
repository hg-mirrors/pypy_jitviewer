
from display import CodeRepr

class MockLoop(object):
    pass

class MockCode(object):
    pass

class MockChunk(object):
    def __init__(self, operations, lineno):
        self.operations = operations
        self.lineno = lineno

SOURCE = """def f():
return a + b
"""

def test_code_repr():
    loop = MockLoop()
    loop.chunks = [MockChunk([], 3), MockChunk(['a', 'b', 'c'], 4),
                   MockChunk(['a', 'b'], 4)]
    MockLoop.linerange = (4, 5)
    code = MockCode()
    code.co_firstlineno = 3
    repr = CodeRepr(SOURCE, code, loop)
    assert len(repr.lines) == 3
    assert repr.lines[1].in_loop
    assert not repr.lines[0].in_loop
    assert repr.lines[0].chunks == [loop.chunks[0]]
    assert repr.lines[1].chunks == [loop.chunks[1], loop.chunks[2]]