class bufferediter(object):
    """Buffered iterator. Items can be pushed to the main iteration."""

    def __init__(self, obj):
        self._iter = iter(obj)
        self._buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer:
            return self._buffer.pop()
        return next(self._iter)

    def push(self, value):
        '''Add a single value to the buffer'''

        self._buffer.append(value)

    def push_sequence(self, values):
        '''Add a sequence of values to buffer'''

        self._buffer.extend(values)


def getsource(obj):
    '''Calls obj.source(), when it exists or simply return str(obj) otherwise'''
    try:
        printer = obj.source
    except AttributeError:
        return str(obj)
    else:
        return printer()

