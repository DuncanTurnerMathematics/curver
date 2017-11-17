
''' A module for representing laminations on Triangulations. '''

from itertools import permutations

import curver
from curver.kernel.utilities import memoize  # Special import needed for decorating.

class Lamination(object):
    ''' This represents an (integral) lamination on a triangulation.
    
    Users should create these via Triangulation.lamination(). '''
    def __init__(self, triangulation, geometric):
        assert(isinstance(triangulation, curver.kernel.Triangulation))
        
        self.triangulation = triangulation
        self.zeta = self.triangulation.zeta
        self.geometric = geometric
        
        # Store some additional weights that are often used.
        self._dual = dict()
        self._side = dict()
        for triangle in self.triangulation:
            i, j, k = triangle  # Edges.
            a, b, c = self.geometric[i.index], self.geometric[j.index], self.geometric[k.index]
            a, b, c = max(a, 0), max(b, 0), max(c, 0)  # Correct for negatives.
            correction = min(a + b - c, b + c - a, c + a - b, 0)
            assert((a + b + c + correction) % 2 == 0)
            self._dual[i] = self._side[k] = (b + c - a + correction) // 2
            self._dual[j] = self._side[i] = (c + a - b + correction) // 2
            self._dual[k] = self._side[j] = (a + b - c + correction) // 2
    
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.geometric)
    def __iter__(self):
        return iter(self.geometric)
    def __call__(self, edge):
        ''' Return the geometric measure assigned to item. '''
        if isinstance(edge, curver.IntegerType): edge = curver.kernel.Edge(edge)  # If given an integer instead.
        
        return self.geometric[edge.index]
    def __eq__(self, other):
        return self.triangulation == other.triangulation and self.geometric == other.geometric
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash(tuple(self.geometric))
    def __add__(self, other):
        # Haken sum.
        if isinstance(other, Lamination):
            if other.triangulation != self.triangulation:
                raise ValueError('Laminations must be on the same triangulation to add them.')
            
            geometric = [x + y for x, y in zip(self.geometric, other.geometric)]
            return self.triangulation.lamination(geometric)  # Have to promote.
        else:
            return NotImplemented
    def __radd__(self, other):
        return self + other  # Commutative.
    def __mul__(self, other):
        geometric = [other * x for x in self]
        # TODO: 2) Could save components if they have already been computed.
        return self.__class__(self.triangulation, geometric)  # Preserve promotion.
    def __rmul__(self, other):
        return self * other  # Commutative.
    
    def weight(self):
        ''' Return the geometric intersection of this lamination with its underlying triangulation. '''
        
        return sum(max(weight, 0) for weight in self)
    
    def dual_weight(self, edge):
        ''' Return the number of component of this lamination dual to the given edge.
        
        Note that when there is a terminal normal arc then we record this weight with a negative sign. '''
        
        if isinstance(edge, curver.IntegerType): edge = curver.kernel.Edge(edge)  # If given an integer instead.
        
        return self._dual[edge]
    
    def side_weight(self, edge):
        ''' Return the number of component of this lamination dual to the given edge.
        
        Note that when there is a terminal normal arc then we record this weight with a negative sign. '''
        
        if isinstance(edge, curver.IntegerType): edge = curver.kernel.Edge(edge)  # If given an integer instead.
        
        return self._side[edge]
    
    def is_empty(self):
        ''' Return if this lamination has no components. '''
        
        return not any(self)  # self.num_components() == 0
    
    def is_multicurve(self):
        ''' Return if this lamination is actually a multicurve. '''
        
        return not self.is_empty() and all(isinstance(component, curver.kernel.Curve) for component in self.components())
    
    def is_curve(self):
        ''' Return if this lamination is actually a curve. '''
        
        return self.is_multicurve() and self.num_components() == 1
    
    def is_multiarc(self):
        ''' Return if this lamination is actually a multiarc. '''
        
        return not self.is_empty() and all(isinstance(component, curver.kernel.Arc) for component in self.components())
    
    def is_arc(self):
        ''' Return if this lamination is actually a multiarc. '''
        
        return self.is_multiarc() and self.num_components() == 1
    
    def promote(self):
        ''' Return this lamination in its finest form. '''
        
        if self.is_multicurve():
            if self.is_curve():
                other = curver.kernel.Curve(self.triangulation, self.geometric)
            else:
                other = curver.kernel.MultiCurve(self.triangulation, self.geometric)
        elif self.is_multiarc():
            if self.is_arc():
                other = curver.kernel.Arc(self.triangulation, self.geometric)
            else:
                other = curver.kernel.MultiArc(self.triangulation, self.geometric)
        else:
            other = self
        
        # Move cache across.
        try:
            other.__cache = self.__cache
        except AttributeError:
            pass  # No cache.
        
        return other
    
    def remove_peripheral(self):
        ''' Return a new lamination with any peripheral components removed.
        
        Most functions will assume that any lamination they are given does not have any peripheral components. '''
        
        peripherals = [0] * self.zeta
        geometric = list(self)
        for vertex in self.triangulation.vertices:
            peripheral = max(min(self.side_weight(edge) for edge in vertex), 0)
            for edge in vertex:
                geometric[edge.index] -= peripheral
        
        return Lamination(self.triangulation, geometric)
    
    def skeleton(self):
        ''' Return the lamination obtained by collapsing parallel components. '''
        
        return self.triangulation.sum(self.components())
    
    def peek_component(self):
        ''' Return one component of this Lamination. '''
        
        return next(iter(self.components()))
    
    def intersection(self, lamination):
        ''' Return the geometric intersection number between this lamination and the given one. '''
        
        assert(isinstance(lamination, Lamination))
        
        return sum(multiplicity * component.intersection(lamination) for component, multiplicity in self.components().items())
    
    def no_common_component(self, lamination):
        ''' Return that self does not share any components with the given Lamination. '''
        
        assert(isinstance(lamination, Lamination))
        
        self_components = self.components()
        return not any(component in self_components for component in lamination.components())
    
    def train_track(self):
        ''' Return the train track underlying this lamination. '''
        # In each triangle where this lamination looks like:
        # We introduce new edges to subdivide a triangle (p, q, r) as follows:
        #            #                         #
        #           / \                       /^\
        #          /   \                     / | \
        #         /     \                   /  |  \
        #        /-------\                 /   |s(i)
        #       /         \     ===>>     /    |    \
        #      /\         /\           r /    / \    \ q
        #     /  \       /  \           /   /     \   \
        #    /    |     |    \         /  /t(j) u(k)\  \
        #   /     |     |     \       /</             \>\
        #  #-------------------#     #-------------------#
        #                                      p
        # So that afterwards every complementary region can reach a vertex.
        
        geometric = list(self.geometric)
        triangles = []
        num_subdivided = 0  # Number of subdivided triangles.
        for triangle in self.triangulation:
            dual_weights = [self.dual_weight(label) for label in triangle.labels]
            if all(weight > 0 for weight in dual_weights):  # Type 3).
                p, q, r = [curver.kernel.Edge(label) for label in triangle.labels]
                s, t, u = [curver.kernel.Edge(i) for i in range(self.zeta + 3*num_subdivided, self.zeta + 3*num_subdivided + 3)]
                triangles.append(curver.kernel.Triangle([p, ~u, t]))
                triangles.append(curver.kernel.Triangle([q, ~s, u]))
                triangles.append(curver.kernel.Triangle([r, ~t, s]))
                num_subdivided += 1
                
                geometric.extend(dual_weights)  # Record intersections with new edges.
            else:
                p, q, r = [curver.kernel.Edge(label) for label in triangle.labels]
                triangles.append(curver.kernel.Triangle([p, q, r]))
        
        T = curver.kernel.Triangulation(triangles)
        return curver.kernel.TrainTrack(T, geometric)
    
    @memoize
    def components(self):
        ''' Return a dictionary mapping components to their multiplicities '''
        
        components = dict()
        for component, multiplicity in self.train_track().components().items():
            assert(component not in components)
            # Project an Arc or Curve on T back to self.triangulation.
            if isinstance(component, curver.kernel.Curve):
                components[curver.kernel.Curve(self.triangulation, component.geometric[:self.zeta])] = multiplicity
            elif isinstance(component, curver.kernel.Arc):
                components[curver.kernel.Arc(self.triangulation, component.geometric[:self.zeta])] = multiplicity
            else:
                raise RuntimeError('self.train_track().components() returned a non Curve / Arc.')
        
        return components
    
    def num_components(self):
        ''' Return the total number of components. '''
        
        return sum(self.components().values())
    
    def sublaminations(self):
        ''' Return all sublaminations that appear within self. '''
        
        components = self.components()
        return [self.triangulation.sum(sub) for i in range(len(components)) for sub in permutations(components, i+1)]
    
    def multiarc(self):
        ''' Return the maximal MultiArc contained within this lamination. '''
        
        return self.triangulation.sum([multiplicity * component for component, multiplicity in self.components().items() if isinstance(component, curver.kernel.Arc)])
    
    def multicurve(self):
        ''' Return the maximal MultiCurve contained within this lamination. '''
        
        return self.triangulation.sum([multiplicity * component for component, multiplicity in self.components().items() if isinstance(component, curver.kernel.Curve)])
    
    def boundary(self):
        ''' Return the boundary of a regular neighbourhood of this lamination. '''
        
        multiarc = self.multiarc()  # Might be empty.
        multicurve = self.multicurve()  # Might be empty.
        empty = self.triangulation.empty_lamination()  # Definitely empty.
        
        return (empty if multicurve.is_empty() else multicurve.boundary()) + (empty if multiarc.is_empty() else multiarc.boundary())
    
    def is_filling(self):
        ''' Return if this Lamination fills the surface, that is, if it cuts the surface into polygons and once-punctured polygons. '''
        
        for component in self.triangulation.components():
            V, E = len([vertex for vertex in self.triangulation.vertices if vertex[0] in component]), len(component) // 2
            if (V, E) != (3, 3):  # component != S_{0, 3}:
                if all(self(edge) == 0 for edge in component):
                    return False
        
        return self.boundary().is_empty()
    
    def fills_with(self, other):
        ''' Return whether self \\cup other fills. '''
        assert(isinstance(other, Lamination))
        
        return NotImplemented  # TODO: 3) Implement!
    
    def trace(self, edge, intersection_point, length):
        ''' Return the sequence of edges encountered by following along this lamination.
        
        We start at the given edge and intersection point for the specified number of steps.
        However we terminate early if the lamination closes up before this number of steps is completed. '''
        
        if isinstance(edge, curver.IntegerType): edge = curver.kernel.Edge(edge)  # If given an integer instead.
        
        start = (edge, intersection_point)
        
        assert(0 <= intersection_point < self(edge))  # Sanity.
        dual_weights = dict((edge, self.dual_weight(edge)) for edge in self.triangulation.edges)
        edges = []
        for _ in range(length):
            x, y, z = self.triangulation.corner_lookup[~edge.label]
            if intersection_point < dual_weights[z]:  # Turn right.
                edge, intersection_point = y, intersection_point
            elif dual_weights[x] < 0 and dual_weights[z] <= intersection_point < dual_weights[z] - dual_weights[x]:  # Terminate.
                break
            else:  # Turn left.
                edge, intersection_point = z, self(z) - self(x) + intersection_point
            if (edge, intersection_point) == start:  # Closes up.
                break
            edges.append(edge)
            assert(0 <= intersection_point < self(edge))  # Sanity.
        
        return edges
    
    def topological_type(self):
        ''' Return the topological type of this lamination..
        
        Two laminations are in the same mapping class group orbit if and only their topological types are equal.
        These are labelled graphs and so equal means 'label isomorphic', so we return a custom class that uses networkx.is_isomorphic to determine equality. '''
        
        return NotImplemented  # TODO: 3) Implement.
        
        if self.is_empty():
            return curver.kernel.CurvePartitionGraph(self, networkx.MultiGraph())  # Empty graph.
        
        components = self.components()  # The components of this multicurves.
        crush = self.multicurve().crush()
        lift = crush.inverse()
        short, conjugator = crush(self).shorten()
        triangulation = conjugator.target_triangulation
        
        graph = networkx.MultiGraph()
        half_edges = defaultdict(list)
        for index, component in enumerate(triangulation.components()):
            vertices = [vertex for vertex in triangulation.vertices if vertex[0] in component]  # The vertices that are in this component.
            V, E = len(vertices), len(component) // 2  # Number of vertices and edges in this component.
            G = (2 - V + E // 3) // 2  # Genus.
            
            # !?! This node also needs to be decorated with the topological type of short|_component.
            graph.add_node(index, genus=G, vertices=V)
            
            for vertex in vertices:
                curve = triangulation.peripheral_curve(vertex)
                lifted_curve = lift(conjugator.inverse()(curve))
                if lifted_curve in components:
                    half_edges[lifted_curve].append(index)
        
        for curve, (i, j) in half_edges.items():
            graph.add_edge(i, j, weight=components[curve])
        
        return curver.kernel.CurvePartitionGraph(self, graph)

class Shortenable(Lamination):
    ''' A special lamination that we can put into a canonical 'short' form. '''
    
    def is_short(self):
        ''' Return whether this lamination is already short. '''
        
        return all(self.shorten_strategy(edge) == 0 for edge in self.triangulation.edges)
    
    def shorten_strategy(self, edge):
        ''' Return a float in [0, 1] describing how good flipping this edge is for making this lamination short.
        
        The higher the score, the better this flip is for reducing weight.
        Specific laminations should implement the correct strategy for getting to the minimal weight configuration. '''
        
        return NotImplemented
    
    def generic_shorten_strategy(self, edge):
        ''' Return a float in [0, 1] describing how good flipping this edge is for making this lamination short. '''
        
        if isinstance(edge, curver.IntegerType): edge = curver.kernel.Edge(edge)  # If given an integer instead.
        
        if not self.triangulation.is_flippable(edge): return 0
        
        a, b, c, d, e = self.triangulation.square(edge)
        ad, bd, cd, dd, ed = [self.dual_weight(edgy) for edgy in self.triangulation.square(edge)]
        
        if ed < 0 or (ed == 0 and ad > 0 and bd > 0):
            return 1
        
        return 0
    
    @memoize
    def shorten(self):
        ''' Return an encoding which maps this lamination to a short one, together with its image. '''
        
        lamination = self
        conjugator = None  # We used to set conjugator = lamination.triangulation.id_encoding() but this is more efficient.
        
        # Theorem: Suppose that self is not an isolating multicurve. If self.weight() > 2*self.zeta then there is a place to split.
        # Proof: TODO.
        
        # Remark: This is part of the reason why we can shorten Curves, Multiarcs and TrainTracks but not MultiCurves.
        extra = []
        edges = set([edge for edge in lamination.triangulation.edges if lamination(edge) > 0])
        while any(lamination.dual_weight(edge) < 0 for edge in edges) or any(len([edge for edge in triangle if lamination.dual_weight(edge) > 0]) == 2 for triangle in lamination.triangulation):
            edge = curver.kernel.utilities.maximum(extra + list(edges), key=lamination.generic_shorten_strategy, upper_bound=1)
            # This edge is always flippable.
            a, b, c, d, e = lamination.triangulation.square(edge)
            
            intersection_point = lamination.side_weight(e) if lamination.side_weight(e) > 0 else -lamination.dual_weight(a)
            trace = lamination.trace(edge, intersection_point, 2*self.zeta)
            try:  # Accelerate!
                trace = trace[:trace.index(edge)+1]  # Will raise a ValueError if edge is not in trace.
                
                curve = lamination.triangulation.lamination_from_cut_sequence(trace)  # Avoids promote.
                if not isinstance(curve, curver.kernel.Curve):
                    raise ValueError
                
                slope = curve.slope(lamination)  # Will raise a curver.AssumptionError if these are disjoint.
                if -1 <= slope <= 1:  # Can't accelerate. We should probably also skip cases where slope is too close to small to be efficient.
                    raise ValueError
                else:  # slope < -1 or 1 < slope:
                    move = curve.encode_twist(power=-int(slope))  # Round towards zero.
            except (ValueError, curver.AssumptionError):
                move = lamination.triangulation.encode_flip(edge)
                extra = [c, d]
            
            conjugator = move * conjugator
            lamination = move(lamination)
            if lamination(edge) <= 0:
                edges.discard(edge)
                edges.discard(~edge)
        
        extra = []
        while not lamination.is_short():
            edge = curver.kernel.utilities.maximum(extra + list(edges), key=lamination.shorten_strategy, upper_bound=1)
            # This edge is always flippable.
            a, b, c, d, e = lamination.triangulation.square(edge)
            
            move = lamination.triangulation.encode_flip(edge)
            extra = [c, d]
            conjugator = move * conjugator
            lamination = move(lamination)
            if lamination(edge) <= 0:
                edges.discard(edge)
                edges.discard(~edge)
        
        if conjugator is None: conjugator = self.triangulation.id_encoding()  # Just in case we haven't done any moves at all.
        
        return lamination, conjugator

