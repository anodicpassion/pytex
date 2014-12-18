import sympy as sp

class Example:
    '''Example objects are realizations of problems/questions from a given 
    template. 
    
    Each example object must have ``question`` and ``answer`` attributes that 
    represents both the central point of a question and its respective 
    correct answer to a mathematical problem.
    
    In a problem that asks the sum of two numbers, the question part can be a 
    mathematical expression such as ``sp.Add(1, 2, evaluate=False)`` and the 
    answer would be the integer result ``3``::
    
        >>> ex = Example(sp.Add(2, 2, evaluate=False), 4); ex
        Example(2 + 2, 4)
    
    Examples can also register a series of false and unique alternatives that 
    can be given as distractors in a multiple choice question.
    '''

    def __init__(self, question, answer=None, template=None):
        if answer is None:
            answer = sp.sympify(question).doit()
        self._question = question
        self._answer = answer
        self._alternatives = []
        self._alternatives_hash = []
        self.template = template

    #===========================================================================
    # Attributes
    #===========================================================================
    @property
    def question(self):
        return self._question

    @property
    def answer(self):
        return self._answer

    #===========================================================================
    # Public API methods
    #===========================================================================
    def responses(self, num):
        '''Return a list of responses of the given size.
        
        The correct answer is the first element of this list.
        '''
        return [self.answer] + self.alternatives(num - 1)

    def alternatives(self, num):
        '''Return a list of unique alternatives with ``num`` elements.'''

        return NotImplemented

    def add_alternative(self, alternative):
        '''Adds an alternative to the example list.
        
        The alternatives must be unique and different from the answer, otherwise
        a ValueError is raised.'''

        raise NotImplementedError

    def suggest_alternative(self, alternative):
        '''Similar to `add_alternative`, but a repeated alternative is simply 
        ignored instead of raising an error.
        
        It returns True if the alternative was added and False otherwise.'''
        try:
            self.add_alternative(alternative)
        except ValueError:
            return False
        else:
            return True

    def pretty(self, view='question'):
        '''Return a pretty print representation of example. By default,
        it pretty prints the question.
        
        ``view`` can be any of "question", "answer", "responses", "full" or an 
        integer that refers to a specific response. '''

        if view == 'question':
            return sp.pretty(self.question)
        elif view == 'answer':
            return sp.pretty(self.answer)
        elif view == 'responses':
            raise NotImplementedError
        elif view == 'full':
            out = ['Question', '--------', self.pretty('question')]
            out.extend(['Responses', '---------', self.pretty('responses')])
            return '\n'.join(out)
        elif isinstance(view, int):
            return sp.pretty(self.alternatives[view])
        else:
            raise ValueError('unrecognized value: view=%r' % view)

    def pprint(self, view='question'):
        '''Pretty prints example object. Same arguments as in `meth:pretty()`'''

        print(self.pretty(view))

    #===========================================================================
    # Subclassing API
    #===========================================================================
    def response_spec(self, obj):
        '''A object uniquely computed from any response object. Used to test
        for mathematical equivalence: two response objects X and Y are 
        considered to be equivalent if either they pass a equality test
        X == Y or if response_spec(X) == response_spec(Y).'''

        # The default semantics is to do not use response_spec if comparison
        # does not work. Only objects that require it should use it.
        # In order to keep the implementation simple, there is no check if
        # this method is implemented. Rather, the default implementation simply
        # returns the object id and response_spec comparison should fail again
        # since different objects have different ids.
        return id(obj)

    def compute_alternative(self):
        return NotImplemented

    #===========================================================================
    # Internal methods
    #===========================================================================
    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.question, self.answer)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
