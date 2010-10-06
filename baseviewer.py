
from pypy.tool.logparser import parse_log_file, extract_category
from pypy.jit.metainterp.test.oparser import parse
from pypy.jit.metainterp.resoperation import rop

class LoopChunk(object):
    def __init__(self, operations):
        self.operations = operations

    def __repr__(self):
        return "[%s]" % ", ".join([repr(op) for op in self.operations])

class Loop(object):
    def __init__(self, chunks):
        self.chunks = chunks

    def __repr__(self):
        return "[%s]" % ", ".join([repr(chunk) for chunk in self.chunks])

def slice_debug_merge_points(loop):
    so_far = []
    res = []
    for op in loop.operations:
        if op.getopnum() == rop.DEBUG_MERGE_POINT:
            if so_far:
                res.append(LoopChunk(so_far))
                so_far = []
        so_far.append(op)
    if so_far:
        res.append(LoopChunk(so_far))
    return Loop(res)

def main():
    log = parse_log_file('log')
    loops = [parse(l, no_namespace=True, nonstrict=True) for l in
             extract_category(log, "jit-log-opt-")]
    find_first_debug_merge_point(loops[0])

if __name__ == '__main__':
    main()
