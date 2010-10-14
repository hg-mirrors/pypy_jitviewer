
import re, sys
from pypy.jit.metainterp.resoperation import rop
from module_finder import load_code
from disassembler import dis

class Bytecode(object):
    filename = None
    startlineno = 0
    name = None
    code = None
    bytecode_no = 0
    
    def __init__(self, operations):
        self.operations = operations
        if self.operations[0].getopnum() == rop.DEBUG_MERGE_POINT:
            m = re.match("<code object ([<>\w]+), file '(.+?)', line (\d+)> #(\d+)",
                         operations[0].getarg(0)._get_str())
            self.name, self.filename, lineno, bytecode_no = m.groups()
            self.startlineno = int(lineno)
            self.bytecode_no = int(bytecode_no)

    def repr(self):
        if self.filename is None:
            return "Unknown"
        return "%s, file '%s', line %d" % (self.name, self.filename,
                                           self.startlineno)

    def getcode(self):
        if self.code is None:
            self.code = dis(load_code(self.filename, self.name,
                                      self.startlineno))
        return self.code

    def getlineno(self):
        code = self.getcode()
        return code.map[self.bytecode_no].lineno
    lineno = property(getlineno)

    def __repr__(self):
        return "[%s]" % ", ".join([repr(op) for op in self.operations])

    def pretty_print(self, out):
        pass

class Loop(object):
    filename = None
    name = None
    startlineno = 0
    
    def __init__(self, chunks):
        self.chunks = chunks
        for chunk in self.chunks:
            if chunk.filename is not None:
                self.startlineno = chunk.startlineno
                self.filename = chunk.filename
                self.name = chunk.name
                break

    def repr(self):
        if self.filename is None:
            return "Unknown"
        return "%s, file '%s', line %d" % (self.name, self.filename,
                                           self.startlineno)

    def key(self):
        pass

    def __repr__(self):
        return "[%s]" % ", ".join([repr(chunk) for chunk in self.chunks])

    def pretty_print(self, out):
        print >>out, "Loop starting at %s in %s at %d" % (self.name,
                                        self.filename, self.startlineno)
        lineno = -1
        for chunk in self.chunks:
            if chunk.filename is not None and chunk.lineno != lineno:
                lineno = chunk.lineno
                source = chunk.getcode().source[chunk.lineno -
                                                chunk.startlineno]
                print >>out, "  ", source
            chunk.pretty_print(out)

def slice_debug_merge_points(loop):
    so_far = []
    res = []
    for op in loop.operations:
        if op.getopnum() == rop.DEBUG_MERGE_POINT:
            if so_far:
                res.append(Bytecode(so_far))
                so_far = []
        so_far.append(op)
    if so_far:
        res.append(Bytecode(so_far))
    return Loop(res)

def parse_log_counts(lines):
    for line in lines:
        pass

if __name__ == '__main__':
    from pypy.tool.logparser import parse_log_file, extract_category
    from pypy.jit.metainterp.test.oparser import parse

    log = parse_log_file('log')
    loops = [parse(l, no_namespace=True, nonstrict=True) for l in
             extract_category(log, "jit-log-opt-")]
    loops = [slice_debug_merge_points(loop) for loop in loops]
    for i, loop in enumerate(loops):
        loop.pretty_print(sys.stdout)
