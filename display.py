
from pypy.jit.metainterp.resoperation import rop

class LineRepr(object):
    """ A representation of a single line
    """
    def __init__(self, line, in_loop, chunks=None):
        self.line = line
        self.in_loop = in_loop
        if chunks is None:
            self.chunks = []
        else:
            self.chunks = chunks

class CodeRepr(object):
    """ A representation of a single code object suitable for display
    """
    def __init__(self, source, code, loop):
        startline, endline = loop.linerange
        self.lines = []
        self.firstlineno = code.co_firstlineno
        for i, line in enumerate(source.split("\n")):
            no = i + code.co_firstlineno
            if no < startline or no > endline:
                self.lines.append(LineRepr(line, False))
            else:
                self.lines.append(LineRepr(line, True))

        last_lineno = -1
        for chunk in loop.chunks:
            no = chunk.lineno
            if no < last_lineno:
                no = last_lineno
            else:
                last_lineno = no
            # only non-trivial chunks please
            if (len(chunk.operations) > 1 or
                (len(chunk.operations) > 0 and
                 chunk.operations[0].getopnum() != rop.DEBUG_MERGE_POINT)):
                self.lines[no - self.firstlineno].chunks.append(chunk)
    
        
