
''' A module for representing and manipulating maps between Triangulations. '''

from fractions import Fraction

import curver

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'  # Strictly this  means 'reducible and not periodic'.
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

class Encoding(object):
    ''' This represents a map between two Triagulations.
    
    The map is given by a sequence of Moves which act from right to left. '''
    def __init__(self, sequence):
        assert(isinstance(sequence, (list, tuple)))
        assert(sequence)
        # assert(all(isinstance(item, curver.kernel.Move) for item in sequence))  # Quadratic.
        
        self.sequence = sequence
        
        self.source_triangulation = self.sequence[-1].source_triangulation
        self.target_triangulation = self.sequence[0].target_triangulation
        self.zeta = self.source_triangulation.zeta
        if self.is_mapping_class():  # Promote.
            self.__class__ = MappingClass
    
    def is_mapping_class(self):
        ''' Return if this encoding is a mapping class.
        
        That is, if it maps to the triangulation it came from. '''
        
        return self.source_triangulation == self.target_triangulation
    
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.sequence)
    def __iter__(self):
        return iter(self.sequence)
    def __len__(self):
        return len(self.sequence)
    def __getitem__(self, value):
        if isinstance(value, slice):
            # It turns out that handling all slices correctly is really hard.
            # We need to be very careful with "empty" slices. As Encodings require
            # non-empty sequences, we have to return just the id_encoding. This
            # ensures the Encoding that we return satisfies:
            #   self == self[:i] * self[i:j] * self[j:]
            # even when i == j.
            
            start = 0 if value.start is None else value.start if value.start >= 0 else len(self) + value.start
            stop = len(self) if value.stop is None else value.stop if value.stop >= 0 else len(self) + value.stop
            if start == stop:
                if 0 <= start < len(self):
                    return self.sequence[start].target_triangulation.id_encoding()
                elif start == len(self):
                    return self.source_triangulation.id_encoding()
                else:
                    raise IndexError('list index out of range')
            elif stop < start:
                raise IndexError('list index out of range')
            else:  # start < stop.
                return Encoding(self.sequence[value])
        elif isinstance(value, curver.IntegerType):
            return self.sequence[value]
        else:
            return NotImplemented
    def package(self):
        ''' Return a small amount of info that self.source_triangulation can use to reconstruct this triangulation. '''
        return [item.package() for item in self]
    def __reduce__(self):
        return (create_encoding, (self.source_triangulation, self.package()))
    
    def __eq__(self, other):
        if isinstance(other, Encoding):
            if self.source_triangulation != other.source_triangulation or self.target_triangulation != other.target_triangulation:
                raise ValueError('Cannot compare Encodings between different triangulations.')
            
            return all(self(arc) == other(arc) for arc in self.source_triangulation.edge_arcs()) and \
                all(self(hc) == other(hc) for hc in self.source_triangulation.edge_homologies())  # We only really need this for S_{1,1}.
        else:
            return NotImplemented
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        # In fact this hash is perfect unless the surface is S_{1,1}.
        return hash(tuple(entry for row in self.intersection_matrix() for entry in row))
    
    def __call__(self, other):
        if self.source_triangulation != other.triangulation:
            raise ValueError('Cannot apply an Encoding to something on a triangulation other than source_triangulation.')
        
        for item in reversed(self.sequence):
            other = item(other)
        
        return other
    def __mul__(self, other):
        if isinstance(other, Encoding):
            if self.source_triangulation != other.target_triangulation:
                raise ValueError('Cannot compose Encodings over different triangulations.')
            
            return Encoding(self.sequence + other.sequence)
        elif other is None:
            return self
        else:
            return NotImplemented
    def inverse(self):
        ''' Return the inverse of this encoding. '''
        
        return Encoding([item.inverse() for item in reversed(self.sequence)])
    def __invert__(self):
        return self.inverse()
    
    def intersection_matrix(self):
        ''' Return the matrix M = {signed_intersection(self(e_i), e'_j)}_{ij}.
        Here e_i and e'j are the edges of self.source_triangulation and self.target_triangulation respectively.
        
        Except when on S_{1,1}, this uniquely determines self. '''
        
        return [list(self(arc)) for arc in self.source_triangulation.edge_arcs()]
    
    def vertex_map(self):
        ''' Return the dictionary (vertex, self(vertex)) for each vertex in self.source_triangulation.
        
        When self is a MappingClass this is a permutation of the vertices. '''
        
        source_vertices = dict((vertex, self.source_triangulation.curve_from_cut_sequence(vertex)) for vertex in self.source_triangulation.vertices)
        target_vertices_inverse = dict((self.target_triangulation.curve_from_cut_sequence(vertex), vertex) for vertex in self.target_triangulation.vertices)
        
        return dict((vertex, target_vertices_inverse[self(source_vertices[vertex])]) for vertex in self.source_triangulation.vertices)

class MappingClass(Encoding):
    ''' An Encoding where self.source_triangulation == self.target_triangulation. '''
    def is_mapping_class(self):
        return True
    
    def __pow__(self, k):
        if k == 0:
            return self.source_triangulation.id_encoding()
        elif k > 0:
            return MappingClass(self.sequence * k)
        else:
            return self.inverse()**abs(k)
    
    def order(self):
        ''' Return the order of this mapping class.
        
        If this has infinite order then return 0. '''
        
        identity = self.source_triangulation.id_encoding()
        for i in range(1, self.source_triangulation.max_order() + 1):
            if self**i == identity:
                return i
        return 0
    
    def is_identity(self):
        ''' Return if this mapping class is the identity. '''
        
        return self.order() == 1
    
    def is_periodic(self):
        ''' Return if this mapping class has finite order. '''
        
        return self.order() > 0
    
    def is_reducible(self):
        ''' Return if this mapping class is reducible (and *not* periodic). '''
        
        return self.nielsen_thurston_type() == NT_TYPE_REDUCIBLE
    
    def is_pseudo_anosov(self):
        ''' Return if this mapping class is pseudo-Anosov. '''
        
        return self.nielsen_thurston_type() == NT_TYPE_PSEUDO_ANOSOV
    
    def nielsen_thurston_type(self):
        ''' Return the Nielsen--Thurston type of this mapping class. '''
        
        if self.is_periodic():
            return NT_TYPE_PERIODIC
        elif self.positive_asymptotic_translation_length():
            return NT_TYPE_PSEUDO_ANOSOV
        else:  # self.asymptotic_translation_length() == 0:
            return NT_TYPE_REDUCIBLE
    
    def asymptotic_translation_length(self):
        ''' Return the asymptotic translation length of this mapping class on the curve complex.
        
        From Algorithm 6 of [BellWebb16]_. '''
        
        C = curver.kernel.CurveComplex(self.source_triangulation)
        c = self.source_triangulation.edge_arc(0).boundary()  # A "short" curve.
        geodesic = C.geodesic(c, (self**C.M)(c))
        m = geodesic[len(geodesic)//2]  # midpoint
        
        numerator = C.distance(m, (self**C.M)(m))
        denominator = C.M
        return Fraction(numerator, denominator).limit_denominator(C.D)
    
    def positive_asymptotic_translation_length(self):
        ''' Return whether the asymptotic translation length of this mapping class on the curve complex is positive
        
        This uses Remark 4.7 of [BellWebb16]_ and so is more efficient than doing::
        
            self.asymptotic_translation_length() > 0 '''
        
        C = curver.kernel.CurveComplex(self.source_triangulation)
        c = self.source_triangulation.edge_arc(0).boundary()  # A "short" curve.
        geodesic = C.geodesic(c, (self**C.M2)(c))
        m = geodesic[len(geodesic)//2]  # midpoint
        
        return C.distance(m, (self**C.M2)(m)) > 4


def create_encoding(source_triangulation, sequence):
    ''' Return the encoding defined by sequence starting at source_triangulation.
    
    This is only really here to help with pickling. Users should use
    source_triangulation.encode(sequence) directly. '''
    
    assert(isinstance(source_triangulation, curver.kernel.Triangulation))
    
    return source_triangulation.encode(sequence)

