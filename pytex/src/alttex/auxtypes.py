if __name__ == '__main__' and __package__ is None:
    import pytex.alttex; __package__ = 'pytex.alttex'  # @UnusedImport @ReservedAssignment

from pytex.textypes import TeXString
from pytex.util.texfy import TeXfy
from pytex.lib import latex
import random

class Choice:
    def __init__(self, value, feedback=None, score=None):
        self.value = value
        self.feedback = feedback
        self.score = score

    @classmethod
    def aschoice(cls, x, score=None, feedback=None):
        if isinstance(x, cls):
            if score is not None:
                x.value = score
            if feedback is not None:
                x.feedback = feedback
            return x
        else:
            return Choice(x, score=score, feedback=feedback)

    def texfy(self):
        out = []

        # Adds score
        if self.score == 1:
            out.append(self.tex_correct())
        elif self.score:
            out.append(self.tex_score(self.score))

        # Adds value
        import sympy
        if isinstance(self.value, sympy.Basic):
            data = '$%s$' % sympy.latex(self.value)
            out.append(TeXString(data))
        else:
            out.append(TeXfy(self.value))

        # Adds value and feedback
        if self.feedback:
            out.append(self.tex_feedback(TeXfy(self.feedback)))

        return latex.item(out)

    def __eq__(self, other):
        return self.value == getattr(other, 'value', other)

    def __str__(self):
        data = str(self.value)
        return '[%.0f%%] %s' % (self.score * 100, data) if self.score else data

class Choices:
    '''A choices environment that can be used in scripts'''
    def __init__(self, choices=[], size=None):
        self.choices = []
        for x in choices:
            self.add(x)
        self.size = size

    def add(self, choice, feedback=None, score=None):
        '''Adds an element to choices'''

        if not self.choices:
            score = 1 if score is None else score
            self.choices.append(Choice.aschoice(choice, score=score, feedback=feedback))
        elif choice not in self:
            self.choices.append(Choice.aschoice(choice, score=score, feedback=feedback))
        else:
            raise ValueError('duplicated choice')

    def suggest(self, choice, feedback=None, score=0):
        '''Suggest a distractor.
        
        Similar to .add(), but ignores exception if choice already exist.'''

        if score == 1:
            raise ValueError('can only suggest wrong alternatives')
        try:
            self.add(choice, score=score, feedback=feedback)
        except ValueError:
            pass

    def distractors(self, choices, feedback=None):
        '''Suggestst a list of distractors'''

        for c in choices:
            self.suggest(c, feedback=feedback)

    def sort(self, method=None, reverse=False):
        '''Sort alternatives using the given method'''

        self.choices.sort(key=lambda x: x.value, reverse=reverse)

    def shuffle(self):
        '''Shuffle options'''

        random.shuffle(self.choices)

    def texfy(self):
        '''Convert itself to a choices() object'''

        out = self.tex_choices()
        for choice in self.choices:
            out.add(TeXfy(choice))
        return out

    def fill(self, size):
        '''Fill with alternatives up to the given size'''
        # TODO: implementação tosca
        import random, string, sympy
        from pytex.alttex.script import oneof
        if isinstance(size, str):
            size = string.ascii_letters.find(size.lower())  # @UndefinedVariable

        def prefix(x, L=None):
            if L is None:
                L = []
            if x.args:
                L.append((x.func, len(x.args)))
                for arg in x.args:
                    prefix(arg, L)
            else:
                L.append(x)
            return L

        def fromprefix(L):
            head = L.pop(0)
            if isinstance(head, tuple):
                func, N = head
                args = []
                for _ in range(N):
                    args.append(fromprefix(L))
                return func(*args)
            else:
                return head

        def mutate(expr):
            ast = prefix(expr)
            for i, x in enumerate(ast):
                if isinstance(x, sympy.Rational):
                    mutations = set()
                    mutations.add(x * oneof(2, 3, 4))
                    mutations.add(x / oneof(2, 3, 4))
                    mutations.add(x + oneof(1, -1, 2, -2))
                    new = sorted([(len(str(y)), y) for y in mutations if (y != x and y) ])
                    new = [ y for y in new if y[0] == new[0][0] ]
                    new = random.choice(new)[1]
                    ast[i] = new

            return fromprefix(ast)

        data = [ sympy.sympify(c.value) for c in self.choices ]
        L = len(data)
        while len(data) < size:
            print(data)
            base = random.choice(data)
            new = mutate(base)
            if new not in data:
                data.append(new)

        for c in data[L:]:
            self.add(c)

    def check(self):
        '''Check if the choices object is consistent'''

        raise NotImplementedError

    @property
    def correct(self):
        for choice in self:
            if choice.score == 1:
                return choice

    @correct.setter
    def correct(self, value):
        self.add(value, score=1)

    #===========================================================================
    # Magic methods
    #===========================================================================
    def __len__(self):
        return len(self.choices)

    def __contains__(self, item):
        if isinstance(item, Choice):
            return item in self.choices
        else:
            for c in self.choices:
                if c.value == item:
                    return True
            else:
                return False

    def __str__(self):
        st = ['Choices:']
        st.extend('  %2i: ' % (i + 1) + str(c) for (i, c) in enumerate(self.choices))
        return '\n'.join(st)

    def __iter__(self):
        for c in self.choices:
            yield c

if __name__ == '__main__':
    from .script import oneof
    from sympy import integrate, diff, Symbol
    choices = Choices()
    x, y = Symbol('x'), Symbol('y')

    fx = oneof(1, 2, 3, 4) * x ** oneof(1, 2, 3) * y ** oneof(1, 2, 3) / 2
    fy = oneof(1, 2, 3, 4) * x ** oneof(1, 2, 3) * y ** oneof(1, 2, 3) / 2

    # Compute choices
    aux = integrate(diff(fy, x) - diff(fx, y), (x, 0, 1), (y, 0, 1))
    choices.correct = aux
    aux = integrate(diff(fx, x) + diff(fy, y), (x, 0, 1), (y, 0, 1))
    choices.add(aux, 'Usou o teorema de Green para fluxo')
    choices.fill(8)
