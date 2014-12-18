def readfile(source, path=None):
    '''Return a tuple (data, path) with the data and path name for the input 
    file or string.'''

    if isinstance(source, str):
        if path is None:
            path = '<string>'
        return source, path
    else:
        data = source.read()
        path = getattr(source, 'name', path)
        return (data, path)
