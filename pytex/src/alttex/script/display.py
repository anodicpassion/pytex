import contextlib
import inspect

__all__ = ['display_enable', 'display_disable', 'display_vars', 'no_display']

DISPLAY_VARS_ENABLE = True
def display_enable():
    'Enable the display blocks'

    global DISPLAY_VARS_ENABLE
    DISPLAY_VARS_ENABLE = False

def display_disable():
    'Disable printing the variables in the display blocks'

    global DISPLAY_VARS_ENABLE
    DISPLAY_VARS_ENABLE = False

@contextlib.contextmanager
def no_display():
    '''Temporarily disable displaying variables inside this with block
    
    Examples
    --------
    >>> with no_display():
    ...     with display_vars('Foo', 'x', 'y'):
    ...         x, y = 1, 2
    '''

    # Store the current state and disable display
    enabled = DISPLAY_VARS_ENABLE
    display_disable()
    yield

    # __exit__
    if enabled:
        display_enable()

@contextlib.contextmanager
def display_vars(name, *args):
    '''
    Display the value of the given global variables defined inside a with 
    block
    
    Examples
    --------
    
    >>> with display_vars('Foo'):
    ...     x = 2
    ...     y = 3
    <BLANKLINE>
    Foo
    ---
        x = 2
        y = 3
    
    >>> with display_vars('Foo', 'x', 'z'):
    ...     x = 1
    ...     y = 2
    ...     z = 3
    <BLANKLINE>
    Foo
    ---
        x = 1
        z = 3

    '''
    # Disable printing vars globally on demand
    if not DISPLAY_VARS_ENABLE:
        yield
        return

    # __enter__
    if not args:
        old_globals = dict(inspect.currentframe().f_back.f_back.f_globals)
        old_globals = { k: v for (k, v) in old_globals.items() }

    # execute block
    yield

    # __exit__
    new_globals = dict(inspect.currentframe().f_back.f_back.f_globals)
    if args:
        print_items = [ (v, new_globals.get(v, NotImplemented)) for v in args ]
    else:
        diff = {}
        for (k, v) in new_globals.items():
            if old_globals.get(k, None) is not v:
                diff[k] = v
        print_items = sorted(diff.items(), key=lambda item: item[0])

    print('\n' + name)
    print('-' * len(name))

    for item in print_items:
        print('    %s = %s' % item)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
