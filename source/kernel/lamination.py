
''' A module for representing laminations on Triangulations.

Provides one class: Curve. '''

import curver

try:
	from Queue import Queue
except ImportError:
	from queue import Queue

INFTY = float('inf')

class Lamination(object):
	''' This represents a lamination on an triangulation.
	
	It is given by a list of its geometric intersection numbers and a
	list of its algebraic intersection numbers with the (oriented) edges
	of underlying triangulation. Note that:
	     ^L
	     |
	-----|------> e
	     |
	has algebraic intersection +1.
	
	Users should use Triangulation.lamination() to create laminations. '''
	def __init__(self, triangulation, geometric, algebraic):
		assert(isinstance(triangulation, curver.kernel.Triangulation))
		assert(isinstance(geometric, (list, tuple)))
		assert(isinstance(algebraic, (list, tuple)))
		# We should check that geometric / algebraic satisfies reasonable relations.
		
		self.triangulation = triangulation
		self.zeta = self.triangulation.zeta
		self.geometric = list(geometric)
		self.algebraic = list(algebraic)
		assert(len(self.geometric) == self.zeta)
		assert(len(self.algebraic) == self.zeta)
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(self.geometric)
	def __iter__(self):
		return iter(self.geometric)
	
	def __call__(self, item):
		''' Return the geometric measure assigned to item. '''
		if isinstance(item, curver.kernel.Edge):
			return self.geometric[item.index]
		else:
			return self.geometric[curver.kernel.norm(item)]
	
	def __getitem__(self, item):
		''' Return the algebraic measure assigned to item. '''
		if isinstance(item, curver.kernel.Edge):
			return self.algebraic[item.index] * item.sign()
		else:
			normalised = curver.kernel.norm(item)
			return self.algebraic[normalised] * (1 if normalised == item else -1)
	
	def __len__(self):
		return self.zeta
	
	def __eq__(self, other):
		return self.triangulation == other.triangulation and \
			all(v == w for v, w in zip(self.geometric, other.geometric)) and \
			all(v == w for v, w in zip(self.algebraic, other.algebraic))
	def __ne__(self, other):
		return not (self == other)
	
	def __hash__(self):
		# This should be done better.
		return hash(tuple(self.geometric) + tuple(self.algebraic))
	
	def __add__(self, other):
		if isinstance(other, Lamination):
			if other.triangulation != self.triangulation:
				raise ValueError('Laminations must be on the same triangulation to add them.')
			
			# Haken sum.
			geometric = [x + y for x, y in zip(self, other)]
			algebraic = [x + y for x, y in zip(self.algebraic, other.algebraic)]
			return Lamination(self.triangulation, geometric, algebraic)
		else:
			if other == 0:  # So we can use sum.
				return self
			else:
				return NotImplemented
	def __radd__(self, other):
		return self + other
	
	def is_empty(self):
		''' Return if this lamination is equal to the empty lamination. '''
		
		return not any(self)
	
	def isometries_to(self, other):
		''' Return a list of isometries taking this lamination to other. '''
		
		assert(isinstance(other, Lamination))
		
		return [isom for isom in self.triangulation.isometries_to(other.triangulation) if other== isom.encode()(self)]
	
	def self_isometries(self):
		''' Returns a list of isometries taking this lamination to itself. '''
		
		return self.isometries_to(self)
	
	def weight(self):
		''' Return the geometric intersection of this lamination with its underlying triangulation. '''
		
		return sum(abs(x) for x in self.geometric)
	
	def conjugate_short(self):
		''' Return an encoding which maps this lamination to a lamination with as little weight as possible. '''
		
		# Repeatedly flip to reduce the weight of this lamination as much as possible.
		# Needs to be made polynomial-time by taking advantage of spiralling.
		
		lamination = self
		conjugation = lamination.triangulation.id_encoding()
		
		def weight_change(lamination, edge_index):
			''' Return how much the weight would change by if this flip was done. '''
			
			if lamination(edge_index) == 0 or not lamination.triangulation.is_flippable(edge_index): return INFTY
			a, b, c, d = lamination.triangulation.square_about_edge(edge_index)
			return max(lamination(a) + lamination(c), lamination(b) + lamination(d)) - 2 * lamination(edge_index)
		
		weight = lamination.weight()
		old_weight = weight + 1
		old_old_weight = old_weight + 1
		possible_edges = lamination.triangulation.indices
		drops = sorted([(weight_change(lamination, i), i) for i in possible_edges])
		# If we ever fail to make progress more than once then the lamination is as short as it's going to get.
		while weight < old_old_weight:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the lamination.
			_, edge_index = drops[0]
			
			forwards = lamination.triangulation.encode_flip(edge_index)
			conjugation = forwards * conjugation
			lamination = forwards(lamination)
			weight, old_weight, old_old_weight = lamination.weight(), weight, old_weight
			
			# Update new neighbours.
			changed_indices = set([edge.index for edge in lamination.triangulation.square_about_edge(edge_index)] + [edge_index])
			drops = sorted([(d, i) if i not in changed_indices else (weight_change(lamination, i), i) for (d, i) in drops])  # This should be lightning fast since the list was basically sorted already.
			# If performance really becomes an issue then we could look at using heapq.
		
		return lamination, conjugation
	
	def components(self):
		return NotImplemented
	
	def skeleton(self):
		''' Return the lamination obtained by collapsing parallel components. '''
		
		return sum(self.components())
	
	def is_multicurve(self):
		return all(all(self(triangle.edges[i]) <= self(triangle.edges[(i+1)%3]) + self(triangle.edges[(i+2)%3]) for i in range(3))  for triangle in self.triangulation)
	
	def is_curve(self):
		''' Return if this multicurve is a curve. '''
		
		if not self.is_multicurve(): return False
		
		short_lamination, _ = self.conjugate_short()
		
		if short_lamination.weight() == 2: return True
		
		# See the conditions on conjugate_short as to why this works.
		if any(weight not in [0, 2] for weight in short_lamination): return False
		
		# If we have a longer lamination then all vertices must be on one side of it.
		# So if we collapse the edges with weight 0 we must end up with a
		# one vertex triangulation.
		triangulation = short_lamination.triangulation
		vertex_numbers = dict(zip(triangulation.vertex_classes, range(triangulation.num_vertices)))
		for edge_index in triangulation.indices:
			if self(edge_index) == 0:
				c1, c2 = triangulation.vertex_lookup[edge_index], triangulation.vertex_lookup[~edge_index]
				a, b = vertex_numbers[c1], vertex_numbers[c2]
				if a != b:
					x, y = max(a, b), min(a, b)
					for c in vertex_numbers:
						if vertex_numbers[c] == x: vertex_numbers[c] = y
		
		# If any corner class is numbered > 0 then we don't have a one vertex triangulation.
		if any(vertex_numbers.values()): return False
		
		# So either we have a single curve or we have a multicurve with two parallel components.
		# We can test for the former by looking for a triangle in which all sides have weight 2.
		return any(all(short_lamination(edge) == 2 for edge in triangle) for triangle in short_lamination.triangulation)
	
	def is_multiarc(self):
		return NotImplemented  # To do.
	
	def is_arc(self):
		if not self.is_multiarc(): return False
		
		return NotImplemented  # To do.
	
	def promote(self):
		if self.is_multicurve():
			if self.is_curve():
				self.__class__ = Curve
			else:
				self.__class__ = MultiCurve
		if self.is_multiarc():
			if self.is_arc():
				self.__class__ = Arc
			else:
				self.__class__ = MultiArc
		return self
	
	def components(self):
		''' Return a dictionary mapping the Curves and Arcs that appear in self to their multiplicities. '''
		
		return NotImplemented
	
	def intersection(self, lamination):
		''' Return the geometric intersection number between this lamination and the given one. '''
		
		return sum(multiplicity * component.intersection(lamination) for component, multiplicity in self.components().items())


class MultiCurve(Lamination):
	def is_multicurve(self):
		return True
	def is_multiarc(self):
		return False

class Curve(MultiCurve):
	def is_curve(self):
		return True
	
	def is_twistable(self):
		''' Return if this curve is a twistable curve. '''
		
		# This is based off of self.encode_twist(). See the documentation there as to why this works.
		if not self.is_curve(): return False
		
		short_curve, _ = self.conjugate_short()
		
		return short_curve.weight() == 2
	
	def is_halftwistable(self):
		''' Return if this curve is a half twistable curve. '''
		
		# This is based off of self.encode_halftwist(). See the documentation there as to why this works.
		
		short_curve, _ = self.conjugate_short()
		# We used to start with:
		#   if not self.is_twistable(): return False
		# But this wasted a lot of cycles repeating the calculation twice.
		if not short_curve.weight() == 2:
			return False
		
		triangulation = short_curve.triangulation
		
		e1, e2 = [edge_index for edge_index in short_curve.triangulation.indices if short_curve(edge_index) > 0]
		
		a, b, c, d = triangulation.square_about_edge(e1)
		if short_curve(a) == 1 and short_curve(c) == 1:
			e1, e2 = e2, e1
			a, b, c, d = triangulation.square_about_edge(e1)
		elif short_curve(b) == 1 and short_curve(d) == 1:
			pass
		
		_, _, z, w = triangulation.square_about_edge(a.label)
		_, _, x, y = triangulation.square_about_edge(c.label)
		
		return z == ~w or x == ~y
	
	def encode_twist(self, k=1):
		''' Return an Encoding of a left Dehn twist about this curve raised to the power k.
		
		This curve must be a twistable curve. '''
		
		assert(self.is_twistable())
		
		if k == 0: return self.triangulation.id_encoding()
		
		short_curve, conjugation = self.conjugate_short()
		
		triangulation = short_curve.triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in short_curve.triangulation.indices if short_curve(edge_index) > 0]
		
		a, b, c, d = triangulation.square_about_edge(e1)
		# If the curve is going vertically through the square then ...
		if short_curve(a) == 1 and short_curve(c) == 1:
			# swap the labels round so it goes horizontally.
			e1, e2 = e2, e1
			a, b, c, d = triangulation.square_about_edge(e1)
		elif short_curve(b) == 1 and short_curve(d) == 1:
			pass
		
		# We now have:
		# #<----------#
		# |     a    ^^
		# |         / |
		# |---->------|
		# |       /   |
		# |b    e/   d|
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /        |
		# | /         |
		# V/    c     |
		# #---------->#
		# And e.index = e1 and b.index = d.index = e2.
		
		# Used to do:
		# twist = triangulation.encode([{i: i for i in triangulation.indices if i not in [e1, e2]}, e1]))
		# return conjugation.inverse() * twist**k * conjugation
		
		twist_k = triangulation.encode([(e1, k)])
		return conjugation.inverse() * twist_k * conjugation
	
	def encode_halftwist(self, k=1):
		''' Return an Encoding of a left half twist about this curve raised to the power k.
		
		This curve must be a half-twistable curve. '''
		
		assert(self.is_halftwistable())
		
		if k % 2 == 0:  # k is even so use a Dehn twist
			return self.encode_twist(k // 2)
		
		# This first section is the same as in self.encode_flip.
		
		short_curve, conjugation = self.conjugate_short()
		
		triangulation = short_curve.triangulation
		e1, e2 = [edge_index for edge_index in short_curve.triangulation.indices if short_curve(edge_index) > 0]
		
		a, b, c, d = triangulation.square_about_edge(e1)
		# If the curve is going vertically through the square then ...
		if short_curve(a) == 1 and short_curve(c) == 1:
			# swap the labels round so it goes horizontally.
			e1, e2 = e2, e1
			a, b, c, d = triangulation.square_about_edge(e1)
		elif short_curve(b) == 1 and short_curve(d) == 1:
			pass
		
		# Get some more edges.
		_, _, z, w = triangulation.square_about_edge(a.label)
		_, _, x, y = triangulation.square_about_edge(c.label)
		
		# But now we have to go one further and worry about a, b, c, d Vs. c, d, a, b.
		# We want it so that x == ~y.
		if z.index == w.index:
			a, b, c, d = c, d, a, b
			w, x, y, z = y, z, w, x
		
		# So we now have:
		#       #
		#      / ^
		#     /   \
		#    /w   z\
		#   /       \
		#  V         \
		# #<----------#
		# |     a    ^^
		# |         / |
		# |---->------|
		# |       /   |
		# |b    e/   d|
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /        |
		# | /         |
		# V/    c     |
		# #---------->#
		#  \         ^
		#   \       /
		#    \x   y/
		#     \   /
		#      V /
		#       #
		# Where e.index = e1 and b.index = d.index = e2,
		# and additionally x.index = y.index.
		
		half_twist = triangulation.encode([{i: i for i in triangulation.indices if i not in [e1, e2, c.index, x.index]}, e2, e1, c.index])
		
		# We accelerate large powers by replacting (T^1/2_self)^2 with T_self which includes acceleration.
		if abs(k) == 1:
			return conjugation.inverse() * half_twist**k * conjugation
		else:  # k is odd so we need to add in an additional half twist.
			# Note: k // 2 always rounds down, so even if k < 0 the additional half twist we need to do is positive.
			return conjugation.inverse() * short_curve.encode_twist(k // 2) * half_twist * conjugation
	
	def intersection(self, lamination):
		''' Return the geometric intersection between self and the given lamination.
		
		Currently assumes (and checks) that self is a twistable curve. '''
		
		assert(isinstance(lamination, Lamination))
		assert(lamination.triangulation == self.triangulation)
		
		if not self.is_twistable():
			raise curver.AssumptionError('Can only compute geometric intersection number between a twistable curve and a curve.')
		
		short_self, conjugator = self.conjugate_short()
		short_lamination = conjugator(lamination)
		
		triangulation = short_self.triangulation
		e1, e2 = [edge_index for edge_index in triangulation.indices if short_self(edge_index) > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		if triangulation.corner_of_edge(e1).indices[2] != e2: e1, e2 = e2, e1
		
		a, b, c, d = triangulation.square_about_edge(e1)
		e = e1
		
		x = (short_lamination(a) + short_lamination(b) - short_lamination(e)) // 2
		y = (short_lamination(b) + short_lamination(e) - short_lamination(a)) // 2
		z = (short_lamination(e) + short_lamination(a) - short_lamination(b)) // 2
		x2 = (short_lamination(c) + short_lamination(d) - short_lamination(e)) // 2
		y2 = (short_lamination(d) + short_lamination(e) - short_lamination(c)) // 2
		z2 = (short_lamination(e) + short_lamination(c) - short_lamination(d)) // 2
		
		intersection_number = short_lamination(a) - 2 * min(x, y2, z)
		
		# Check that the other formula gives the same answer.
		assert(intersection_number == short_lamination(c) - 2 * min(x2, y, z2))
		
		return intersection_number
	
	def quasiconvex(self, other):
		''' Return a polynomial-sized quasiconvex subset of the curve complex that contains self and other. '''
		
		return NotImplemented
	
	def geodesic(self, other):
		''' Return a geodesic in the curve complex from self to other.
		
		The geodesic will always come from a tight geodesic. '''
		
		assert(isinstance(other, Curve))
		
		return NotImplemented
	
	def distance(self, other):
		''' Return the distance from self to other in the curve complex. '''
		
		return len(self.geodesic(other))
	
	def crush(self):
		''' Return the crush map. '''
		
		return NotImplemented


class MultiArc(Lamination):
	def is_multicurve(self):
		return False
	def is_multiarc(self):
		return True

class Arc(MultiArc):
	def is_arc(self):
		return True
	
	def intersection(self, lamination):
		''' Return the geometric intersection between self and the given lamination. '''
		
		assert(isinstance(lamination, Lamination))
		assert(lamination.triangulation == self.triangulation)
		
		# short_self = [0, 0, ..., 0, -1, 0, ..., 0]
		short_self, conjugator = self.conjugate_short()
		short_lamination = conjugator(lamination)
		
		return sum(b for a, b in zip(short_self, short_lamination) if a == -1 and b >= 0)
