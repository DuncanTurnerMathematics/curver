
import re

import curver

REGEX_IS_SPHERE_BRAID = re.compile(r'SB_(?P<num_strands>\d+)$')

# Based on code by William Worden.

# TODO: 3) Document all of these cases.

def S_0_n(n):
    # A triangulation of S_{0,n}.
    assert(n >= 3)
    
    # We'll build the following triangulation of S_{0,n}:
    #
    # |      |      |      |       |
    # |0     |1     |2     |3      |n-3
    # |      |      |      |       |
    # | 2n-4 | 2n-3 | 2n-2 |       | 3n-7
    # X------X------X------X- ... -X------X
    #        |      |      |       |      |
    #        |      |      |       |      |
    #        |n-2   |n-1   |n      |2n-6  |2n-5
    #        |      |      |       |      |
    #
    # Note that the (n-1)st puncture is not shown here and is on the "boundary" of the disk.
    # There are two families of triangles on the top and the bottom and two exceptional cases:
    #  1) Top triangles are given by [i, i+2n-4, ~(i+1)] for i in range(0, n-3)],
    #  2) Bottom triangles are given by [i, ~(i+1), ~(i+n-1)] for i in range(n-2, 2n-5),
    #  3) Left triangle given by [~0, ~(n-2), ~(2n-4)], and
    #  4) Right triangle given by [n-3, 3n-7, 2n-5].
    T = curver.create_triangulation(
        [(i, i + 2 * n - 4, ~(i + 1)) for i in range(0, n - 3)] + \
        [(i, ~(i + 1), ~(i + n - 1)) for i in range(n-2, 2*n - 5)] + \
        [(~0, ~(n - 2), ~(2 * n - 4)), (n - 3, 3 * n - 7, 2 * n - 5)]
        )
    
    # We'll then create an arc connecting the ith to (i+1)st punctures.
    # Note that the arcs connecting (n-2)nd & (n-1)st and (n-1)st & 0th are special.
    
        
    arcs = [T.edge_arc(2*n-4+i) for i in range(n-2)] + [T.edge_arc(2*n-5), T.edge_arc(0)]
    
    # We take the half-twist about each of these curves as the generator \sigma_i of SB_n.
    mapping_classes = dict(('s_%d' % index, arc.encode_halftwist()) for index, arc in enumerate(arcs))
    
    return curver.kernel.MappingClassGroup(mapping_classes)

def S_1_n(n):
    assert(n >= 1)
    
    if n == 1:
        T = curver.create_triangulation((0, 1, 2), (~0, ~1, ~2))
        
        a_0 = T.lamination([1, 0, 1])
        b_0 = T.lamination([1, 1, 0])
        
        return curver.kernel.MappingClassGroup({
            'a_0': a_0.encode_twist(),
            'b_0': b_0.encode_twist()
            })
    else:  # n > 1:
        T = curver.create_triangulation(
            [(0, 1, 2)] + \
            [(~(1+2*i), 1+2*i+2, 1+2*i+3) for i in range(n-1)] + \
            [(2*n+1, ~(2*n), ~(2*n-1))] + \
            [(2*n+1 + i, ~(2*n-2*i), ~(2*n + i)) for i in range(1, n-1)] + \
            [(~0, ~(3*n-1), ~2)]
            )
        
        mapping_classes = dict()
        mapping_classes['a_0'] = T.lamination_from_cut_sequence([0, 1] + [3 + 2*j for j in range(n-1)] + [] + [2*n+1 + j for j in range(n-1)]).encode_twist()
        mapping_classes['b_0'] = T.lamination_from_cut_sequence([0, 2]).encode_twist()
        # The twists obtained by pushing a_0 across the punctures.
        # Note that if the loop ran with i=0 then it would create p_0 == a_0.
        for i in range(1, n):
            mapping_classes['p_%d' % i] = T.lamination_from_cut_sequence([0, 1] + [3 + 2*j for j in range(n-1-i)] + [2*n + 2 - 2*i] + [2*n+i + j for j in range(n-i)]).encode_twist()
        # The half-twists that permute the ith and (i+1)st punctures.
        mapping_classes['s_0'] = T.edge_arc(2*n - 1).encode_halftwist()
        for i in range(1, n):
            mapping_classes['s_%d' % i] = T.edge_arc(2*n + 2 - 2*i).encode_halftwist()
        
        return curver.kernel.MappingClassGroup(mapping_classes)

def S_2_n(n):
    assert(n >= 1)
    
    if n == 1:
        T = curver.create_triangulation(
            (0, 1, 2), (~1, 3, 4), (~2, ~3, ~4),
            (~0, 5, 6), (~5, 7, 8), (~6, ~7, ~8)
            )
        
        a_0 = T.lamination([0, 1, 1, 1, 0, 0, 0, 0, 0])
        b_0 = T.lamination([0, 1, 1, 0, 1, 0, 0, 0, 0])
        c_0 = T.lamination([2, 1, 1, 1, 0, 1, 1, 1, 0])
        a_1 = T.lamination([0, 0, 0, 0, 0, 1, 1, 1, 0])
        b_1 = T.lamination([0, 0, 0, 0, 0, 1, 1, 0, 1])
        
        return curver.kernel.MappingClassGroup({
            'a_0': a_0.encode_twist(),
            'a_1': a_1.encode_twist(),
            'b_0': b_0.encode_twist(),
            'b_1': b_1.encode_twist(),
            'c_0': c_0.encode_twist()
            })
    else:  # n > 1:
        T = curver.create_triangulation(
            [(0, 1, 2), (~1, 3, 4), (~2, ~3, ~4), (~0, 5, 6), (~6, ~(3*n+5), ~8)] + \
            [(~(5+2*i), 5+2*i+2, 5+2*i+3) for i in range(n)] + \
            [(2*n+7, ~(2*n+6), ~(2*n+5))] + \
            [(2*n+7+i, ~(2*n+6 - 2*i), ~(2*n+6+i)) for i in range(1, n-1)]
            )
        
        mapping_classes = dict()
        mapping_classes['a_0'] = T.lamination_from_cut_sequence([1, 2, 3]).encode_twist()
        mapping_classes['a_1'] = T.lamination_from_cut_sequence([6, 5] + [7 + j*2 for j in range(n)] + [] + [2*n+7 + j for j in range(n-1)]).encode_twist()
        mapping_classes['b_0'] = T.lamination_from_cut_sequence([1, 2, 4]).encode_twist()
        mapping_classes['b_1'] = T.lamination_from_cut_sequence([5, 6, 8]).encode_twist()
        mapping_classes['c_0'] = T.lamination_from_cut_sequence([6, 0, 2, 4, 1, 2, 3, 4, 2, 0, 5] + [7 + j*2 for j in range(n)] + [] + [2*n+7 + j for j in range(n-1)]).encode_twist()
        # The twists obtained by pushing a_1 across the punctures.
        # Note that if the loop ran with i=0 then it would create p_0 == a_1.
        for i in range(1, n):
            mapping_classes['p_%d' % i] = T.lamination_from_cut_sequence([6, 5] + [7 + j*2 for j in range(n-i)] + [2*n + 8 - 2*i] + [2*n+6+i + j for j in range(n-i)]).encode_twist()
        # The half-twists that permute the ith and (i+1)st punctures.
        mapping_classes['s_0'] = T.edge_arc(2*n + 5).encode_halftwist()
        for i in range(1, n):
            mapping_classes['s_%d' % i] = T.edge_arc(2*n + 8 - 2*i).encode_halftwist()
        
        return curver.kernel.MappingClassGroup(mapping_classes)

def S_3_n(n):
    assert(n >= 1)
    
    if n == 1:
        T = curver.create_triangulation(
            (0, 1, 2), (~1, 3, 4), (~2, ~3, ~4),
            (5, 6, 7), (~6, 8, 9), (~7, ~8, ~9),
            (10, 11, 12), (~11, 13, 14), (~12, ~13, ~14),
            (~0, ~5, ~10)
            )
        #                   0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14
        a_0 = T.lamination([0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        a_1 = T.lamination([0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0])
        a_2 = T.lamination([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0])
        b_0 = T.lamination([0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        b_0 = T.lamination([0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0])
        b_0 = T.lamination([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1])
        c_0 = T.lamination([2, 1, 3, 1, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0])
        c_1 = T.lamination([0, 0, 0, 0, 0, 2, 1, 3, 1, 2, 2, 1, 1, 1, 0])
        
        return curver.kernel.MappingClassGroup({
            'a_0': a_0.encode_twist(),
            'a_1': a_1.encode_twist(),
            'a_2': a_2.encode_twist(),
            'b_0': b_0.encode_twist(),
            'b_1': b_1.encode_twist(),
            'b_2': b_2.encode_twist(),
            'c_0': c_0.encode_twist(),
            'c_1': c_1.encode_twist()
            })
    else:  # n > 1:
        T = curver.create_triangulation(
            [(0, 1, 2), (~1, 3, 4), (~2, ~3, ~4), (5, 6, 7), (~6, 8, 9), (~7, ~8, ~9)] + \
            [(10, 11, 12), (~11, 13, 14), (~12, ~(3*n+11), ~14)] + \
            [(~(13+2*i), 13+2*i+2, 13+2*i+3) for i in range(n-1)] + \
            [(2*n+13, ~(2*n+12), ~(2*n+11))] + \
            [(2*n+13+i, ~(2*n+12-2*i), ~(2*n+12+i)) for i in range(1, n-1)] + \
            [(~0, ~5, ~10)]
            )
        
        mapping_classes = dict()
        mapping_classes['a_0'] = T.lamination_from_cut_sequence([1, 2, 3]).encode_twist()
        mapping_classes['a_1'] = T.lamination_from_cut_sequence([6, 7, 8]).encode_twist()
        mapping_classes['a_2'] = T.lamination_from_cut_sequence([12, 11] + [13 + j*2 for j in range(n)] + [] + [2*n+13 + j for j in range(n-1)]).encode_twist()
        mapping_classes['b_0'] = T.lamination_from_cut_sequence([1, 2, 4]).encode_twist()
        mapping_classes['b_1'] = T.lamination_from_cut_sequence([6, 7, 9]).encode_twist()
        mapping_classes['b_2'] = T.lamination_from_cut_sequence([11, 12, 14]).encode_twist()
        mapping_classes['c_0'] = T.lamination_from_cut_sequence([0, 2, 4, 3, 2, 1, 4, 2, 0, 5, 7, 8, 6, 5]).encode_twist()
        mapping_classes['c_1'] = T.lamination_from_cut_sequence([12, 10, 5, 7, 9, 6, 7, 8, 9, 7, 5, 10, 11] + [13 + j*2 for j in range(n)] + [] + [2*n+13 + j for j in range(n-1)]).encode_twist()
        # The twists obtained by pushing a_2 across the punctures.
        # Note that if the loop ran with i=0 then it would create p_0 == a_2.
        for i in range(1, n):
            mapping_classes['p_%d' % i] = T.lamination_from_cut_sequence([12, 11] + [13 + j*2 for j in range(n-i)] + [2*n + 14 - 2*i] + [2*n+12+i + j for j in range(n-i)]).encode_twist()
        # The half-twists that permute the ith and (i+1)st punctures.
        mapping_classes['s_0'] = T.edge_arc(2*n + 11).encode_halftwist()
        for i in range(1, n):
            mapping_classes['s_%d' % i] = T.edge_arc(2*n + 14 - 2*i).encode_halftwist()
        
        return curver.kernel.MappingClassGroup(mapping_classes)

def S_g_n(g, n):
    assert(g >= 4)
    assert(n >= 1)
    
    if n == 1:
        T = curver.create_triangulation(
            # Build the fins using the first 5g edges.
            [(5*i+0, 5*i+1, 5*i+2) for i in range(g)] + \
            [(~(5*i+1), 5*i+3, 5*i+4) for i in range(g)] + \
            [(~(5*i+2), ~(5*i+3), ~(5*i+4)) for i in range(g)] + \
            # Finally triangulate the centre polygon using the last g - 3 edges.
            [(~0, ~5, 5*g)] + \
            [(5*g+1+i, ~(5*g+i), ~(5*i+10)) for i in range(g-4)] + \
            [(~(5*g+g-4), ~(5*g-10), ~(5*g-5))]
            )  # 0, ..., 6g - 4.
        
        mapping_classes = dict()
        for i in range(g):
            mapping_classes['a_%d' % i] = T.lamination_from_cut_sequence([5*i+1, 5*i+2, 5*i+3]).encode_twist()
            mapping_classes['b_%d' % i] = T.lamination_from_cut_sequence([5*i+1, 5*i+2, 5*i+4]).encode_twist()
        mapping_classes['c_%d' % 0] = T.lamination_from_cut_sequence([5*0+j for j in [0, 2, 4, 3, 2, 1, 4, 2, 0, 5, 6, 8, 7, 5]]).encode_twist()
        for i in range(1, g-2):
            mapping_classes['c_%d' % i] = T.lamination_from_cut_sequence([5*i+j for j in [0, 2, 4, 3, 2, 1, 4, 2, 0, 5, 6, 8, 7, 5]] + [5*g + i - 1, 5*g + i - 1]).encode_twist()
        mapping_classes['c_%d' % (g-2)] = T.lamination_from_cut_sequence([5*(g-2)+j for j in [0, 2, 4, 3, 2, 1, 4, 2, 0, 5, 6, 8, 7, 5]]).encode_twist()
        
        return curver.kernel.MappingClassGroup(mapping_classes)
    else:  # n > 1:
        T = curver.create_triangulation(
            # Build the fins using the first 5g edges.
            [(5*i+0, 5*i+1, 5*i+2) for i in range(g)] + \
            [(~(5*i+1), 5*i+3, 5*i+4) for i in range(g)] + \
            [(~(5*i+2), ~(5*i+3), ~(5*i+4)) for i in range(g-1)] + \
            # Don't forget the last one is special.
            [(~(5*(g-1)+2), ~(5*(g-1)+4+(3*n-3)), ~(5*(g-1)+4))] + \
            # Now fold to put in the additional punctures using the next 3n - 3 edges.
            [(~(5*g-2 + 2*i), 5*g-2 + 2*i + 2, 5*g-2 + 2*i + 3)  for i in range(n-1)] + \
            [(5*g-2 + 2*(n-1) + 2, ~(5*g-2 + 2*(n-1) + 1), ~(5*g-2 + 2*(n-1)))] + \
            [(5*g-2 + 2*(n-1) + 2 + i, ~(5*g-2 + 2*(n-1) + 1 - 2*i), ~(5*g-2 + 2*(n-1) + 2 + i - 1)) for i in range(1, n-1)] + \
            # Finally triangulate the centre polygon using the last g - 3 edges.
            [(~0, ~5, 5*g+3*n-3)] + \
            [(5*g+3*n-3+1+i, ~(5*g+3*n-3+i), ~(5*i+10)) for i in range(g-4)] + \
            [(~(5*g+3*n-3+g-4), ~(5*g-10), ~(5*g-5))]
            )
        
        mapping_classes = dict()
        for i in range(g-1):
            mapping_classes['a_%d' % i] = T.lamination_from_cut_sequence([5*i+1, 5*i+2, 5*i+3]).encode_twist()
        mapping_classes['a_%d' % (g-1)] = T.lamination_from_cut_sequence([5*(g-1)+1, 5*(g-1)+2] + [5*(g-1)+3 + j*2 for j in range(n)] + [] + [5*g+2*n-2 + j for j in range(n-1)]).encode_twist()
        
        for i in range(g):
            mapping_classes['b_%d' % i] = T.lamination_from_cut_sequence([5*i+1, 5*i+2, 5*i+4]).encode_twist()
        mapping_classes['c_%d' % 0] = T.lamination_from_cut_sequence([5*0+j for j in [0, 2, 4, 3, 2, 1, 4, 2, 0, 5, 6, 8, 7, 5]]).encode_twist()
        for i in range(1, g-2):
            mapping_classes['c_%d' % i] = T.lamination_from_cut_sequence([5*i+j for j in [0, 2, 4, 3, 2, 1, 4, 2, 0, 5, 6, 8, 7, 5]] + [5*g + 3*n - 3 + i - 1, 5*g + 3*n - 3 + i - 1]).encode_twist()
        
        mapping_classes['c_%d' % (g-2)] = T.lamination_from_cut_sequence([5*(g-2) + j for j in [7, 5, 0, 2, 4, 1, 2, 3, 4, 2, 0, 5, 6]] + [5*(g-1)+3 + j*2 for j in range(n)] + [] + [5*g+2*n-2 + j for j in range(n-1)]).encode_twist()
        
        # The twists obtained by pushing a_{g-1} across the punctures.
        # Note that if the loop ran with i=0 then it would create p_0 == a_{g-1}.
        for i in range(1, n):
            mapping_classes['p_%d' % i] = T.lamination_from_cut_sequence([5*(g-1)+1, 5*(g-1)+2] + [5*(g-1)+3 + j*2 for j in range(n-i)] + [5*g + 2*n - 1 - 2*i] + [5*g+2*n-3+i + j for j in range(n-i)]).encode_twist()
        # The half-twists that permute the ith and (i+1)st punctures.
        mapping_classes['s_0'] = T.edge_arc(5*g + 2*n - 4).encode_halftwist()
        for i in range(1, n):
            mapping_classes['s_%d' % i] = T.edge_arc(5*g + 2*n - 1 - 2*i).encode_halftwist()
        
        return curver.kernel.MappingClassGroup(mapping_classes)

def load_old(surface):
    if surface == 'S_0_4':
        S = load(0, 4)
        return curver.kernel.MappingClassGroup({
            'a': S('s_1'),
            'b': S('s_2'),
            'c': S('s_3'),
            'd': S('s_0'),
            })
    elif surface == 'S_1_1':
        S = load(1, 1)
        return curver.kernel.MappingClassGroup({
            'a': S('a_0'),
            'b': S('b_0'),
            })
    elif surface == 'S_1_2':
        S = load(1, 2)
        return curver.kernel.MappingClassGroup({
            'a': S('a_0'),
            'b': S('b_0'),
            'c': S('p_1'),
            'x': S('s_1'),
            })
    elif surface == 'S_1_2p':
        S = load(1, 2)
        return curver.kernel.MappingClassGroup({
            'a': S('a_0'),
            'b': S('b_0'),
            'c': S('p_0'),
            })
    elif surface == 'S_2_1':
        S = load(2, 1)
        return curver.kernel.MappingClassGroup({
            'a': S('b_0'),
            'b': S('c_0'),
            'c': S('b_1'),
            'd': S('a_1'),
            'e': S('(a_0.b_0.c_0)^4.A_1'),
            'f': S('a_0'),
            })
    elif surface == 'S_3_1':
        S = load(3, 1)
        return curver.kernel.MappingClassGroup({
            'a': S('b_0'),
            'b': S('c_0'),
            'c': S('b_1'),
            'd': S('c_1'),
            'e': S('b_2'),
            'f': S('(a_0.b_0.c_0.b_1.c_1)^6.A_2'),
            'g': S('a_2'),
            'h': S('a_1'),
            })
    elif surface == 'S_4_1':
        S = load(4, 1)
        return curver.kernel.MappingClassGroup({
            'a': S('b_0'),
            'b': S('c_0'),
            'c': S('b_1'),
            'd': S('c_1'),
            'e': S('b_2'),
            'f': S('c_2'),
            'g': S('b_3'),
            'h': S('(a_0.b_0.c_0.b_1.c_1.b_2.c_2)^8.A_3'),
            'i': S('a_3'),
            'j': S('a_2'),
            })
    elif surface == 'S_5_1':
        S = load(5, 1)
        return curver.kernel.MappingClassGroup({
            'a': S('b_0'),
            'b': S('c_0'),
            'c': S('b_1'),
            'd': S('c_1'),
            'e': S('b_2'),
            'f': S('c_2'),
            'g': S('b_3'),
            'h': S('c_3'),
            'i': S('b_4'),
            'j': S('(a_0.b_0.c_0.b_1.c_1.b_2.c_2.b_3.c_3)^10.A_4'),
            'k': S('a_4'),
            'l': S('a_3'),
            })
    elif REGEX_IS_SPHERE_BRAID.match(surface):
        return S_0_n(int(REGEX_IS_SPHERE_BRAID.match(surface).groupdict()['num_strands']))
    else:
        raise ValueError('Unknown surface: %s' % surface)

def load(*args):
    ''' Return the requested example MappingClassGroup.
    
    The mapping class group can either be specified by:
    
        - a pair (g, n) in which case the Lickorish generating set is returned (see Figures 4.5 and 4.10 of [FarbMarg12]), or
        - a string 'S_g_n' in which case the corresponding flipper / Twister generating set is returned.
    
    '''
    
    if len(args) == 1:  # Load an old flipper surface.
        surface = args[0]
        return load_old(surface)
    elif len(args) == 2:  # Build Mod(S_{g, n}).
        g, n = args
        assert(isinstance(g, curver.IntegerType))
        assert(isinstance(n, curver.IntegerType))
        
        zeta = 6*g + 3*n - 6
        if g < 0 or n < 0 or zeta < 3:
            raise curver.AssumptionError('Surface cannot be triangulated.')
        
        if g == 0:  # and n >= 3.
            return S_0_n(n)
        elif g == 1:
            return S_1_n(n)
        elif g == 2:
            return S_2_n(n)
        elif g == 3:
            return S_3_n(n)
        else:  # g >= 4:
            return S_g_n(g, n)
    else:  # len(args) > 2:
        raise ValueError('Expected a string or pair of integers.')

