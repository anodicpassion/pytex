import inspect

RENDER_IMPLEMENTATION = set()

def indent(level, st, first=False):
    '''Indent a string 'st' by prepending each line with the string "level"
    
    If level is an integer, it is interpreted as the number of whitespaces'''

    level = ' ' * level if isinstance(level, int) else level
    if first:
        return level + indent(level, st)
    else:
        lines = st.splitlines()
        st = ('\n' + level).join(lines)
        return st

def keep_implementation(func):
    '''Decorator that marks a function to preserve its implementation'''

    RENDER_IMPLEMENTATION.add(func)
    return func

def render_function(func):
    '''Renders the source code of a function possibly removing its implementation'''

    srclines = inspect.getsource(func).splitlines()
    if func in RENDER_IMPLEMENTATION:
        # Remove the @keep_implementation decorator from func
        srclines = [ L for L in srclines
                    if not (L.lstrip().startswith('@') and 'keep_implementation' in L) ]
        return '\n'.join(srclines)

    # Remove implementation from function
    for idx, L in enumerate(srclines):
        if L.lstrip().startswith('def'):
            srclines = srclines[:idx + 1]
            indent_ws, _, _ = L.partition('def')
            indent_ws += '    '
            func_doc = inspect.getdoc(func)
            if "'''" not in func_doc:
                func_doc = "'''%s'''" % func_doc
            else:
                func_doc = '"""%s"""' % func_doc
            srclines.append(indent(indent_ws, func_doc, True))
            srclines.append('\n' + indent_ws + 'return NotImplemented')
            break
    else:
        print('\n'.join(srclines))
        raise RuntimeError('unrecognized source for a function')
    return '\n'.join(srclines) + '\n'


def render_class(obj):
    '''Renders the source code of a class possibly removing its implementation'''

    src = inspect.getsource(obj)
    funcs = []
    for func in obj.__dict__.values():
        try:
            subsrc = inspect.getsource(func)
        except TypeError:
            continue

        src = src.replace(subsrc, '{%s}' % len(funcs))
        funcs.append(render_function(func))

    return src.format(*funcs)
