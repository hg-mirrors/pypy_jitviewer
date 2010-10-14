
import os, sys, marshal, types

def _all_codes_from(code):
    res = {}
    more = [code]
    while more:
        next = more.pop()
        res[next.co_firstlineno] = next
        more += [co for co in next.co_consts
                 if isinstance(co, types.CodeType)]
    return res


def gather_all_code_objs(fname):
    """ Gathers all code objects from a give fname and sorts them by
    starting lineno
    """
    fname = str(fname)
    if fname.endswith('.pyc'):
        code = marshal.loads(open(fname).read()[8:])
        assert isinstance(code, types.CodeType)
    elif fname.endswith('.py'):
        code = compile(open(fname).read(), fname, 'exec')
    else:
        import pdb
        pdb.set_trace()
        raise Exception("Unknown file extension: %s" % fname)
    return _all_codes_from(code)

def load_code(fname, name, lineno):
    """ Loads a module code from a given description. If fname is a pyc file,
    just unmarshal it and find correct code, otherwise use ast module to
    get code. Insane hack, but works
    """
    return gather_all_code_objs(fname)[lineno]
