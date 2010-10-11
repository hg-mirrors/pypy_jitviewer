
import re
import flask
from pypy.tool.logparser import parse_log_file, extract_category
from pypy.jit.metainterp.test.oparser import parse
from pypy.jit.metainterp.resoperation import rop
from module_finder import load_code

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class LoopChunk(object):
    filename = None
    lineno = 0
    name = None
    
    def __init__(self, operations):
        self.operations = operations
        if self.operations[0].getopnum() == rop.DEBUG_MERGE_POINT:
            m = re.match("<code object ([<>\w]+), file '(.+?)', line (\d+)>",
                         operations[0].getarg(0)._get_str())
            self.name, self.filename, lineno = m.groups()
            self.lineno = int(lineno)

    def repr(self):
        if self.filename is None:
            return "Unknown"
        return "%s, file '%s', line %d" % (self.name, self.filename, self.lineno)

    def __repr__(self):
        return "[%s]" % ", ".join([repr(op) for op in self.operations])

class Loop(object):
    filename = None
    name = None
    lineno = 0
    
    def __init__(self, chunks):
        self.chunks = chunks
        for chunk in self.chunks:
            if chunk.filename is not None:
                self.lineno = chunk.lineno
                self.filename = chunk.filename
                self.name = chunk.name
                break

    def repr(self):
        if self.filename is None:
            return "Unknown"
        return "%s, file '%s', line %d" % (self.name, self.filename, self.lineno)

    def key(self):
        pass

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

class Server(object):
    def __init__(self, loops):
        self.loops = loops

    def index(self):
        return flask.render_template('index.html', loops=self.loops)

    def loop(self):
        no = int(flask.request.args.get('no', '0'))
        # gather all functions
        loop = self.loops[no]
        startline = loop.lineno - 1
        import pdb
        pdb.set_trace()
        code = highlight(open(loop.filename).read(),
                         PythonLexer(), HtmlFormatter(lineanchors='line'))
        #mod = import_module
        return flask.render_template('loop.html', code=code,
                                     startline=startline)

def parse_log_counts(lines):
    for line in lines:
        pass

def main():
    log = parse_log_file('log')
    log_counts = parse_log_counts(open('log.count').readlines())
    loops = [parse(l, no_namespace=True, nonstrict=True) for l in
             extract_category(log, "jit-log-opt-")]
    loops = [slice_debug_merge_points(loop) for loop in loops]
    app = flask.Flask(__name__)
    server = Server(loops)
    app.debug = True
    app.route('/')(server.index)
    app.route('/loop')(server.loop)
    app.run()

if __name__ == '__main__':
    main()
