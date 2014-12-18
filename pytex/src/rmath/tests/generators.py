import nose
from nose.tools import nottest
from rmath import complexity, r_int
from rmath.generators import r_integer, r_rational

@nottest
def generator_test_maker(func, compl=5):
    '''Test numeric random generators:
    
        * By default, outputs must be positive
        * Some negative values must appear when force_pos=False
        * Complexity of returned objects must be within proper bounds 
    '''
    def tester():
        # Test for correct complexity bound
        for _ in range(100):
            x = func(compl)
            assert round(complexity(x)) <= compl, complexity(x)
            assert x > 0

        # If force_pos is False, generate some negative numbers
        assert any(func(5, force_pos=False) < 0 for _ in range(20))
    tester.__name__ = 'test_' + func.__name__
    return tester

test_int = generator_test_maker(r_integer)
test_rat = generator_test_maker(r_rational)

if __name__ == '__main__':
    nose.runmodule()
