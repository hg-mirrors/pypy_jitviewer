
import cgi
import flask
import inspect
from pypy.tool.logparser import parse_log_file, extract_category
from module_finder import load_code
from loops import (slice_debug_merge_points, parse_log_counts, NonCodeLoop,
                   parse)
from display import CodeRepr

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class Server(object):
    def __init__(self, loops):
        self.loops = loops

    def index(self):
        return flask.render_template('index.html', loops=self.loops)

    def loop(self):
        no = int(flask.request.args.get('no', '1'))
        path = [i for i in flask.request.args.get('path', '').split(',')
                if i]
        scroll_to = int(flask.request.args.get('scroll_to', '0'))
        # gather all functions
        loop = self.loops[no - 1]
        upper_start = 0
        for elem in path:
            nr = int(elem)
            if nr:
                upper_start = loop.chunks[nr - 1].lineno # XXX what if it's
                # also a Function? is it even possible without a bytecode
                # in between?
            loop = loop.chunks[nr]
        startline, endline = loop.linerange
        code = load_code(loop.filename, loop.name, loop.startlineno)
        source = inspect.getsource(code)
        return flask.render_template('loop.html',
                                     source=CodeRepr(source, code, loop),
                                     startline=scroll_to or startline,
                                     current_loop=no,
                                     upper_path=','.join(path[:-1]),
                                     upper_start=upper_start)
        
def main():
    log = parse_log_file('log')
    #log_counts = parse_log_counts(open('log.count').readlines())
    loops = [parse(l) for l in
             extract_category(log, "jit-log-opt-")]
    parsed = []
    for loop in loops:
        try:
            parsed.append(slice_debug_merge_points(loop))
        except NonCodeLoop:
            pass
    app = flask.Flask(__name__)
    server = Server(parsed)
    app.debug = True
    app.route('/')(server.index)
    app.route('/loop')(server.loop)
    app.run(use_reloader=False)

if __name__ == '__main__':
    main()
