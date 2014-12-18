import random
import sympy as sp
from rmath.util import list_constants, list_functions
from rmath.symbols import FUNCTIONS
from rmath.examples import Example

class Template:
    '''Template for randomly creating examples.'''

    def __init__(self, question, answer=None, conditions=(), not_constant=()):
        if answer is None:
            answer = sp.sympify(question).doit()
        self.question = question
        self.answer = answer
        self.conditions = list(conditions)
        self.not_constant = set(not_constant)
        self.constant_spec = {}
        self.function_spec = {}
        self.compound_conditions = []

        # Auxiliary initializer methods
        self.initialize_constants()
        self.initialize_functions()
        self.initialize_conditions()

    #===========================================================================
    # Public API
    #===========================================================================
    def new_example(self):
        '''Return a new random example'''

        funcs = self.propose_functions()
        consts = self.propose_constants()

        question = self.question.subs(funcs)
        question = question.subs(consts)

        answer = self.answer.subs(funcs)
        answer = answer.subs(consts)

        return Example(question, answer)

    def get_examples(self, num):
        '''Return a list of ``num`` unique examples.'''

        examples = set()
        for _ in range(10 * num):
            if len(examples) >= num:
                return list(examples)
            examples.add(self.new_example())
        else:
            raise RuntimeError('maximum number of iterations exceeded: maybe examples are not properly randomized')

    # Import some implementations from Example ---------------------------------
    responses = Example.responses
    alternatives = Example.alternatives
    add_alternative = Example.add_alternative
    suggest_alternative = Example.suggest_alternative
    pretty = Example.pretty
    pprint = Example.pprint

    #===========================================================================
    # Internal Functions
    #===========================================================================
    def initialize_constants(self):
        constants = set(list_constants(self.question))
        constants -= self.not_constant
        for cte in list_constants(self.answer):
            if cte in self.not_constant:
                continue
            if cte not in constants:
                constants.add(cte)
        for cte in constants:
            self.constant_spec[cte] = []

    def initialize_functions(self):
        functions = set(list_functions(self.question))
        for f in list_functions(self.answer):
            if f not in functions:
                functions.add(f)
        for f in functions:
            self.function_spec[f] = FUNCTIONS[f]

    def initialize_conditions(self):
        simple = self.constant_spec
        compound = self.compound_conditions
        for cond in self.conditions:
            atoms = list_constants(cond)
            if len(atoms) == 1:
                atom = atoms[0]
                try:
                    simple[atom].append(cond)
                except KeyError:
                    raise ValueError('condition for a non-template variable %s' % atom)
            else:
                compound.append(cond)
        return simple, compound

    def is_valid_constants(self, constants):
        '''Return True if all proposed constants are valid.'''

        # Assert simple conditions
        for c in constants:
            for scond in self.constant_spec[c]:
                #TODO: assert simple conditions
                print(c, scond)

        # Assert compound conditions
        for cond in self.compound_conditions:
            if not cond.subs(constants):
                return False

        return True

    def propose_constants(self, force_valid=True):
        '''Propose random values for the constants. The proposed values are 
        not necessarily valid if is_valid is set to False'''

        # 100 attempts to create a valid set of constants
        if force_valid:
            for _ in range(100):
                constants = self.propose_constants(force_valid=False)
                if self.is_valid_constants(constants):
                    return constants
            else:
                raise RuntimeError('maximum number of iterations exceeded trying to compute valid constants: are the conditions consistent?')

        # Propose constants without checking validity
        else:
            out = {}
            for cte in self.constant_spec:
                # Use proper generators
                out[cte] = random.randint(1, 10)
            return out

    def propose_functions(self):
        '''Propose randomly selected functions'''

        functions = {}
        for f, flist in self.function_spec.items():
            f = type(f(x))
            functions[f] = random.choice(flist)
        return functions

#===============================================================================
# Factories
#===============================================================================
class Factory:
    def __init__(self, level=0, category=None):
        self.level = level
        self.category = category
        self.simple_conditions, self.compound_conditions = self.get_conditions(level, classify=True)
        self.template = self.get_template(level)
        self.constant_names = self.template.list_constants()
        self.constants = self.propose_constants(force_valid=True)
        self.example = self.template.new(self.constants)

    def get_conditions(self, level, classify=False):
        '''Return a list of conditions for the given level.'''

        self.check_level_exists(level)

    def get_template(self, level):
        '''Return the template expression for the given ``level``'''

        self.check_level_exists(level)
        return Template(getattr(self, 'template_%s' % level))

    def check_level_exists(self, level):
        '''Checks if all templates up to the given ``level`` are defined'''

        if not hasattr(self, 'template_%s' % level):
            raise ValueError('level %s does not exist!')
        if level:
            for i in range(level):
                if not hasattr(self, 'template_%s' % i):
                    raise ValueError('invalid template definition: intermediate level %s does not exist!')

    def __str__(self):
        return str(self.expression)

    def pprint(self):
        print(self.pretty())

    def pretty(self):
        return self.example.pretty()

    def answer(self):
        return self.example.answer()

    def alternatives(self, num=4):
        return self.example.alternatives(num)

    def responses(self, num=5):
        return self.example.responses(num)

if __name__ == '__main__':
    from sympy.abc import x, y, z
    from rmath.symbols import BASIC_F2, aa
    ex = Template(BASIC_F2(x + aa))
    print(ex.new_example())

    import doctest
    doctest.testmod()
