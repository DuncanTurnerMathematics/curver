
''' A module for representing permutations in Sym(N). '''

from bisect import bisect
from itertools import combinations
from math import factorial

import curver

class Permutation(object):
    ''' This represents a permutation on 0, 1, ..., N-1. '''
    def __init__(self, perm):
        self.perm = perm
        assert(len(self.perm) == len(set(self.perm)))
    
    def __str__(self):
        return str(self.perm)
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.perm)
    def __getitem__(self, item):
        return self.perm[item]
    def __iter__(self):
        return iter(self.perm)
    
    @classmethod
    def from_index(cls, N, index):
        ''' Return the permutation in Sym(N) with the given index. '''
        
        P = []
        f = factorial(N)
        symbols = list(range(N))
        while symbols:
            f = f // len(symbols)
            i, index = divmod(index, f)
            P.append(symbols[i])
            symbols = symbols[:i] + symbols[i+1:]
        return cls(P)
    
    def index(self):
        ''' Return the index of this permutation in the (sorted) list of all permutations on this many symbols. '''
        
        symbols = sorted(self.perm)
        index = 0
        for p in self:
            i = bisect(symbols, p) - 1
            index = index * len(symbols) + i
            symbols = symbols[:i] + symbols[i+1:]
        return index
    
    def is_even(self):
        ''' Return whether this permutation is the composition of an even number of transposiions. '''
        
        return sum(1 if a > b else 0 for a, b in combinations(self, r=2) if a > b) % 2 == 0

