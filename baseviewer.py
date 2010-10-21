
import cgi
import flask
import inspect
from pypy.tool.logparser import parse_log_file, extract_category
from pypy.jit.metainterp.test.oparser import parse
from module_finder import load_code
from loops import slice_debug_merge_points, parse_log_counts
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
        no = int(flask.request.args.get('no', '0'))
        # gather all functions
        loop = self.loops[no]
        startline, endline = loop.linerange
        code = load_code(loop.filename, loop.name, loop.startlineno)
        source = inspect.getsource(code)
        return flask.render_template('loop.html',
                                     source=CodeRepr(source, code, loop),
                                     startline=startline)
        
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
    app.run(use_reloader=False)

if __name__ == '__main__':
    main()
