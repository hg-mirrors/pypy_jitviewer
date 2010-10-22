
import re, sys
from pypy.jit.metainterp.resoperation import rop, opname
from module_finder import load_code
from disassembler import dis
from pypy.jit.tool.oparser import OpParser

def _new_binop(name):
    def f(self):
        return '%s = %s %s %s' % (self.res, self.args[0], name, self.args[1])
    return f

class Op(object):
    def __init__(self, name, args, res, descr):
        self.name = name
        self.args = args
        self.res = res
        self.descr = descr

    def setfailargs(self, _):
        pass

    def html_repr(self):
        return getattr(self, 'repr_' + self.name, self.generic_repr)()

    for bin_op, name in [('<', 'int_lt'),
                         ('>', 'int_gt'),
                         ('<=', 'int_le'),
                         ('>=', 'int_ge'),
                         ('+', 'int_add'),
                         ('+', 'float_add'),
                         ('-', 'int_sub'),
                         ('-', 'float_sub'),
                         ('&', 'int_and')]:
        locals()['repr_' + name] = _new_binop(bin_op)

    def repr_guard_true(self):
        return '%s is true' % self.args[0]

    def repr_guard_false(self):
        return '%s is false' % self.args[0]

    def repr_guard_value(self):
        return '%s is %s' % (self.args[0], self.args[1])

    def repr_guard_isnull(self):
        return '%s is null' % self.args[0]

    def repr_getfield_raw(self):
        name, field = self.descr.split(' ')[1].rsplit('.', 1)
        return '%s = ((%s)%s).%s' % (self.res, name, self.args[0], field[2:])

    def repr_getfield_gc(self):
        name, field = self.descr.split(' ')[1].rsplit('.', 1)
        return '%s = ((%s)%s).%s' % (self.res, name, self.args[0], field)
    repr_getfield_gc_pure = repr_getfield_gc

    def repr_setfield_raw(self):
        name, field = self.descr.split(' ')[1].rsplit('.', 1)
        return '((%s)%s).%s = %s' % (name, self.args[0], field[2:], self.args[1])

    def repr_setfield_gc(self):
        name, field = self.descr.split(' ')[1].rsplit('.', 1)
        return '((%s)%s).%s = %s' % (name, self.args[0], field, self.args[1])        

    def generic_repr(self):
        if self.res is not None:
            return '%s = %s(%s)' % (self.res, self.name, ', '.join(self.args))
        else:
            return '%s(%s)' % (self.name, ', '.join(self.args))

    def __repr__(self):
        return '<%s (%s)>' % (self.name, ', '.join([repr(a) for a in self.args]))

    def extra_style(self):
        if self.name.startswith('guard_'):
            return 'guard'
        return ''

class SimpleParser(OpParser):
    def parse_args(self, opname, argspec):
        if not argspec.strip():
            return [], None
        if opname == 'debug_merge_point':
            return [argspec], None
        else:
            args = argspec.split(', ')
            descr = None
            if args[-1].startswith('descr='):
                descr = args[-1][len('descr='):]
                args = args[:-1]
            return (args, descr)

    def box_for_var(self, res):
        return res

    def create_op(self, opnum, args, res, descr):
        return Op(intern(opname[opnum].lower()), args, res, descr)
        
class NonCodeLoop(Exception):
    """ An exception raised in case the loop is not associated with
    applevel code
    """

class Bytecode(object):
    filename = None
    startlineno = 0
    name = None
    code = None
    bytecode_no = 0
    bytecode_name = None
    is_bytecode = True
    
    def __init__(self, operations):
        if operations[0].name == 'debug_merge_point':
            m = re.search('<code object ([<>\w]+), file \'(.+?)\', line (\d+)> #(\d+) (\w+)',
                         operations[0].args[0])
            if m is None:
                # a non-code loop, like StrLiteralSearch or something, ignore
                # for now
                raise NonCodeLoop()
            self.name, self.filename, lineno, bytecode_no, self.bytecode_name = m.groups()
            self.startlineno = int(lineno)
            self.bytecode_no = int(bytecode_no)
        self.operations = operations

    def key(self):
        return self.startlineno, self.name, self.filename

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

    def html_repr(self):
        return self.bytecode_name

class Function(object):
    filename = None
    name = None
    startlineno = 0
    _linerange = None
    is_bytecode = False
    
    def __init__(self, chunks, path):
        self.chunks = chunks
        self.path = path
        for chunk in self.chunks:
            if chunk.filename is not None:
                self.startlineno = chunk.startlineno
                self.filename = chunk.filename
                self.name = chunk.name
                break

    def key(self):
        return self.startlineno, self.name, self.filename

    def getlinerange(self):
        if self._linerange is None:
            minline = sys.maxint
            maxline = -1
            for chunk in self.chunks:
                if isinstance(chunk, Bytecode) and chunk.filename is not None:
                    lineno = chunk.lineno
                    minline = min(minline, lineno)
                    maxline = max(maxline, lineno)
            self._linerange = minline, maxline
        return self._linerange
    linerange = property(getlinerange)

    def html_repr(self):
        return "inlined call to %s in %s" % (self.name, self.filename)

    def repr(self):
        if self.filename is None:
            return "Unknown"
        return "%s, file '%s', line %d" % (self.name, self.filename,
                                           self.startlineno)
        
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
    stack = []

    def getpath(stack):
        return ','.join([str(len(v)) for (k, v) in stack])
    
    def append_to_res(bc):
        if not stack:
            stack.append((bc.key(), []))
        else:
            if stack[-1][0] != bc.key():
                previous_bytecode = stack[-1][1][-1]
                # XXX PRETTY FRAGILE
                # if any of those bytecodes were encountered and next bytecode
                # is from somewhere else, then we need to pop one block
                if (previous_bytecode.bytecode_name in
                    ['RAISE_VARARGS', 'RETURN_VALUE', 'YIELD_VALUE']):
                    _, last = stack.pop()
                    stack[-1][1].append(Function(last, getpath(stack)))
                else:
                    stack.append((bc.key(), []))
        stack[-1][1].append(bc)

    so_far = []
    stack = []
    for op in loop.operations:
        if op.name == 'debug_merge_point':
            if so_far:
                append_to_res(Bytecode(so_far))
                so_far = []
        so_far.append(op)
    if so_far:
        append_to_res(Bytecode(so_far))
    # wrap stack back up
    while True:
        _, next = stack.pop()
        if not stack:
            return Function(next, getpath(stack))
        stack[-1][1].append(Function(next, getpath(stack)))

def parse_log_counts(lines):
    for line in lines:
        pass

def parse(input):
    return SimpleParser(input, None, {}, 'lltype', None,
                        nonstrict=True).parse()

if __name__ == '__main__':
    # XXX kill probably
    from pypy.tool.logparser import parse_log_file, extract_category

    log = parse_log_file('log')
    loops = [parse(l) for l in
             extract_category(log, "jit-log-opt-")]
    loops = [slice_debug_merge_points(loop) for loop in loops]
    for i, loop in enumerate(loops):
        loop.pretty_print(sys.stdout)
