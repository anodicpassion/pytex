from rmath.complexity import complexity_integer, icomplexity_mul, icomplexity_add
import scipy.optimize
import numpy as np

RANK_MUL = [1, 2, 3, 4, 5, 10, 6, 8, 9, 12, 20, 16, 15, 7, 25, 18, 30, 24, 11, 14, 27, 21, 13, 22, 28, 26, 17, 19, 23, 29 ]
RANK_ADD = [1, 2, 3, 4, 5, 10, 9, 6, 7, 8, 11, 20, 30, 12, 21, 22, 13, 23, 14, 24, 15, 25, 16, 26, 19, 29, 17, 27, 18, 28 ]
RANK_TOTAL = RANK_MUL

def dist(L1, L2):
    '''Rank distance between two sequences of elements'''

    Nerrors = 0
    for i, x in enumerate(L1):
        i1, i2 = L1.index(x), L2.index(x)
        s1, s2 = set(L1[:i1]), set(L2[:i2])
        g1, g2 = set(L1[i1 + 1:]), set(L2[i2 + 1:])
        s1.symmetric_difference_update(s2)
        g1.symmetric_difference_update(g2)
        Nerrors += (len(s1) + len(g1)) * 1.015 ** (-i)
    return Nerrors / 4

def fmin_mul(x):
    '''Count errors from reference list using parameters a, b, c in icomplexity_mul'''

    L = sorted((icomplexity_mul(n, *x), n) for n in range(1, 31))
    L2 = [ n for (_, n) in L ]
    return dist(RANK_MUL, L2)

def fmin_add(x):
    '''Count errors from reference list using parameters a, b, c in icomplexity_add'''

    L1 = RANK_ADD
    L2 = sorted((icomplexity_add(n, *x), n) for n in range(1, 31))
    L2 = [ n for (_, n) in L2 ]
    return dist(L1, L2)

def fmin_cmpl(w):
    '''Count errors from reference list in integer complexity'''

    L1 = RANK_TOTAL
    L2 = sorted((complexity_integer(n, w), n) for n in range(1, 31))
    L2 = [ n for (_, n) in L2 ]
    return dist(L1, L2)

def render_ranks(L):
    return ' '.join('%2i' % x for x in L)

def compare_ranks(L1, L2):
    eq = lambda x, y: '##' if x != y else '  '
    print('Target:', render_ranks(L1))
    if any(x != y for (x, y) in zip(L1, L2)):
        print('       ', ' '.join(eq(x, y) for (x, y) in zip(L1, L2)))
        print('Rank:  ', render_ranks(L2))
    else:
        print('Rank: *acomplished*')

def compute_mul():
    print('Computing optimal multiplication parameters')
    a, b, c, d, e = fmin_genetic(fmin_mul, disp=2, bounds=[(0, 5)] * 5, pop_size=500)
    print('Result: a=%s, b=%s, c=%s, d=%s, e=%s' % (a, b, c, d, e))

    # Print ranks
    L = sorted((icomplexity_mul(n, a, b, c, d, e), n) for n in range(1, 31))
    compare_ranks(RANK_MUL, [ n for (c, n) in L ])
    print('Errors:', dist(RANK_MUL, [ n for (c, n) in L ]))

def compute_add():
    print('Computing optimal multiplication parameters')
    a, b, c = fmin_genetic(fmin_add, disp=2, bounds=[(0, 2)] * 3)
    print('Result: a=%s, b=%s, c=%s' % (a, b, c))

    # Print ranks
    L = sorted((icomplexity_add(n, a, b, c), n) for n in range(1, 31))
    compare_ranks(RANK_ADD, [ n for (c, n) in L ])
    print('Errors:', dist(RANK_ADD, [ n for (c, n) in L ]))

#===============================================================================
# Genetic minimizer
#===============================================================================
def fmin_genetic(func, bounds, pop_size=100, niter=None, maximize=False, disp=0, top=10, fastconv=True):
    '''
    
    Observations
    ------------
    
    Internally, it uses a 63 bit number
    '''
    # Population size must be even
    if pop_size % 2:
        pop_size += 1
    half_pop = pop_size // 2

    # Define bounds, deltas and a minimization function that accepts genetic
    # code arguments
    bounds = np.asarray(bounds, dtype=float)
    deltas = bounds[:, 1] - bounds[:, 0]
    Ndim = bounds.shape[0]
    R = 1 if maximize else -1

    # Helper constants that facilitates conversion between genetic code and
    # phenotype
    maxgen = np.uint64(2 ** 62 - 1)
    not_mask = np.ones((half_pop, Ndim), dtype=np.uint64) * maxgen

    def fitness(code):
        return R * func(phenotype(code))

    def phenotype(code):
        x = code * deltas
        x /= maxgen
        x += bounds[:, 0]
        return x

    # Initialize population
    codes = np.random.randint(0, maxgen, size=Ndim * pop_size).reshape((pop_size, Ndim))
    codes = np.asarray(codes, dtype=np.uint64)
    fvalues = np.ones(pop_size)

    # Initialize main loop
    for iter_n in range(niter or 2 ** 32):
        fvalues[:] = [ fitness(c) for c in codes ]
        forder = fvalues.argsort()[::-1]
        codes = codes.take(forder, axis=0, out=codes)
        ftop = fvalues[forder[0:min(top, pop_size)]]

        # Display convergence messages
        if disp > 1:
            bvalue = R * ftop
            bvalue = ' '.join('%.2e' % x for x in bvalue)
            wvalue = R * fvalues[forder[-min(top, pop_size):]]
            wvalue = ' '.join('%.2e' % x for x in wvalue)
            print('Iteration %s (fitness values)\n'
                  '     best  = %s\n'
                  '     worst = %s\n' % (iter_n, bvalue, wvalue))

        # Select the best to mate
        best = codes[:half_pop]
        other = best.copy()
        np.random.shuffle(other)

        # Create offspring from crossover
        # 0 -- takes from father, 1 -- takes from mother
        m = np.random.randint(0, maxgen, size=(half_pop, Ndim))
        m = np.asarray(m, dtype=np.uint64)
        not_m = m ^ not_mask
        other = not_m & other
        other |= m & best

        # Mutate 1 bit of the resulting object
        dim_idx = np.random.randint(0, Ndim, size=half_pop)
        for i in range(half_pop):
            if np.random.rand() < 0.25:
                other[i, dim_idx[i]] = not other[i, dim_idx[i]]

        # Saves offspring in the tail of population
        codes[half_pop:] = other

        # Test convergence from top 10 individuals if no maximum number of
        # iterations is attained
        if (niter is None or fastconv) and len(set(ftop)) == 1:
            break

    # Return best individual
    fvalues[:] = [ fitness(c) for c in codes ]
    idx_best = fvalues.argmax()
    x = (codes[idx_best] * deltas) / maxgen + bounds[:, 0]
    return x

if __name__ == '__main__':
    # compute_mul()
    compute_add()
    pass
