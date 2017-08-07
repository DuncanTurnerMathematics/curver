
DEFAULT_OBJECT_COLOUR = 'black'
DEFAULT_VERTEX_COLOUR = 'black'
DEFAULT_EDGE_COLOUR = 'black'
DEFAULT_TRIANGLE_COLOUR = 'gray80'
DEFAULT_CURVE_COLOUR = 'grey40'

ARROW_FRAC = 0.55

def dot(a, b):
	return a[0] * b[0] + a[1] * b[1]

def lines_intersect(s1, e1, s2, e2, float_error, equivalent_edge):
	dx1, dy1 = e1[0] - s1[0], e1[1] - s1[1]
	dx2, dy2 = e2[0] - s2[0], e2[1] - s2[1]
	D = dx2*dy1 - dx1*dy2
	if D == 0: return (-1, False)
	
	xx = s2[0] - s1[0]
	yy = s2[1] - s1[1]
	
	s = float(yy*dx1 - xx*dy1)/D
	t = float(yy*dx2 - xx*dy2)/D
	
	return (t if 0-float_error <= s <= 1+float_error and 0-float_error <= t <= 1+float_error else -1, equivalent_edge and 0+float_error <= s <= 1-float_error and 0+float_error <= t <= 1-float_error)

def intersection(A, d, B, d2):
	# Find the intersection parameters of A + t d and B + t2 d2
	# Want t & t2 such that:
	#   A[0] + t d[0] = B[0] + t2 d2[0]
	#   A[1] + t d[1] = B[1] + t2 d2[1]
	# So:
	#   (d[0] -d2[0]) (t ) = (B[0] - A[0])
	#   (d[1] -d2[1]) (t2)   (B[1] - A[1])
	# The inverse of this matrix is:
	#   (-d2[1] d2[0])
	#   ( -d[1]  d[0]) / det
	# where:
	det = d2[0] * d[1] - d[0] * d2[1]
	# So:
	t  = ((B[0] - A[0]) * -d2[1] + (B[1] - A[1]) * d2[0]) / det
	t2 = ((B[0] - A[0]) *  -d[1] + (B[1] - A[1]) *  d[0]) / det
	
	return t, t2

def interpolate(A, B, C, r, s):
	# Given points A, B, C and parameters r, s
	# Let X := rB + (1-r)A and
	# Y := sB + (1-s)C
	dx, dy = A[0] - B[0], A[1] - B[1]
	dx2, dy2 = C[0] - B[0], C[1] - B[1]
	
	X = (B[0] + r*dx, B[1] + r*dy)
	Y = (B[0] + s*dx2, B[1] + s*dy2)
	
	d1a = intersection(X, (-dy, dx), B, (dx+dx2, dy+dy2))[0]
	d1b = intersection(X, (-dy, dx), A, (-2*A[0] + B[0] + C[0], -2*A[1] + B[1] + C[1]))[0]
	t = min([x for x in [d1a, d1b] if x > 0]) / 2
	
	d2a = intersection(Y, (dy2, -dx2), B, (dx+dx2, dy+dy2))[0]
	d2b = intersection(Y, (dy2, -dx2), C, (-2*C[0] + A[0] + B[0], -2*C[1] + A[1] + B[1]))[0]
	t2 = min([x for x in [d2a, d2b] if x > 0]) / 2
	
	P = (X[0] + t * -dy, X[1] + t * dx)
	Q = (Y[0] + t2 * dy2, Y[1] + t2 * -dx2)
	
	return X, P, Q, Y

class DrawableObject(object):
	def __init__(self, canvas, vertices, options):
		self.options = options
		self.canvas = canvas
		self.vertices = vertices
		self.colour = DEFAULT_OBJECT_COLOUR
		self.drawn = None
	
	def __repr__(self):
		return str(self)
	# Note that this means that CanvasTriangle will NOT have the same convention as AbstractTriangle,
	# there iterating and index accesses return edges.
	def __getitem__(self, index):
		return self.vertices[index % len(self)]
	
	def __iter__(self):
		return iter(self.vertices)
	
	def __len__(self):
		return len(self.vertices)
	
	def set_colour(self, colour=None):
		self.colour = colour
		self.canvas.itemconfig(self.drawn, fill=self.colour)
	
	def centre(self):
		return (sum(x[0] for x in self.vertices) / len(self), sum(x[1] for x in self.vertices) / len(self))
	
	def update(self):
		self.canvas.coords(self.drawn, *[c for v in self for c in v])

class CanvasVertex(DrawableObject):
	def __init__(self, canvas, vertex, options):
		super(CanvasVertex, self).__init__(canvas, [vertex], options)
		self.colour = DEFAULT_VERTEX_COLOUR
		self.vertex = list(vertex)
		self.drawn = self.canvas.create_oval(
			[p + scale*self.options.dot_size for scale in [-1, 1] for p in self],
			outline=self.colour, fill=self.colour, tag='oval'
			)
	
	def __str__(self):
		return str(self.vertex)
	
	def __sub__(self, other):
		return (self[0] - other[0], self[1] - other[1])
	
	# We have to redo these manually.
	def __iter__(self):
		return iter(self.vertex)
	
	def __getitem__(self, key):
		return self.vertex[key]
	
	def __setitem__(self, key, value):
		self.vertex[key] = value
	
	def __contains__(self, point):
		return all(abs(c - v) < self.options.epsilon for c, v in zip(point, self))
	
	def update(self):
		self.canvas.coords(self.drawn, *[p + scale*self.options.dot_size for scale in [-1, 1] for p in self])

class CanvasEdge(DrawableObject):
	def __init__(self, canvas, vertices, label, colour, options):
		super(CanvasEdge, self).__init__(canvas, vertices, options)
		self.label = label
		self.colour = DEFAULT_EDGE_COLOUR if colour is None else colour
		m = ((1-ARROW_FRAC)*self.vertices[0][0] + ARROW_FRAC*self.vertices[1][0], (1-ARROW_FRAC)*self.vertices[0][1] + ARROW_FRAC*self.vertices[1][1])
		self.drawn = [  # Need two lines really so arrows work correctly.
			self.canvas.create_line(
				[c for v in [self.vertices[0], m] for c in v],
				width=self.options.line_size,
				fill=self.colour,
				tags=['line', 'line_start'],
				arrowshape=self.options.arrow_shape
			),
			self.canvas.create_line(
				[c for v in [self.vertices[0], self.vertices[1]] for c in v],
				width=self.options.line_size,
				fill=self.colour,
				tags=['line', 'line_end'],
				arrowshape=self.options.arrow_shape
			)
			]
		
		self.in_triangles = []
	
	def __str__(self):
		return str(self.vertices)
	
	def hide(self, hide=False):
		for drawn in self.drawn:
			self.canvas.itemconfig(drawn, state='hidden' if hide else 'normal')
	
	def update(self):
		m = ((1-ARROW_FRAC)*self.vertices[0][0] + ARROW_FRAC*self.vertices[1][0], (1-ARROW_FRAC)*self.vertices[0][1] + ARROW_FRAC*self.vertices[1][1])
		self.canvas.coords(self.drawn[0], *[c for v in [self.vertices[0], m] for c in v])
		self.canvas.coords(self.drawn[1], *[c for v in [self.vertices[0], self.vertices[1]] for c in v])

class CanvasTriangle(DrawableObject):
	def __init__(self, canvas, edges, options):
		super(CanvasTriangle, self).__init__(canvas, list(set(v for e in edges for v in e)), options)
		self.colour = DEFAULT_TRIANGLE_COLOUR
		self.edges = edges
		
		# We reorder the vertices to guarantee that the vertices are cyclically ordered anticlockwise in the plane.
		d10, d20 = self[1] - self[0], self[2] - self[0]
		if d10[0]*d20[1] - d10[1]*d20[0] > 0: self.vertices = [self[0], self[2], self[1]]
		# Now we reorder the edges such that edges[i] does not meet vertices[i].
		self.edges = [edge for vertex in self for edge in self.edges if vertex not in edge.vertices]
		
		# And check to make sure everyone made it through alive.
		assert(len(self.edges) == 3)
		assert(self[0] != self[1] and self[1] != self[2] and self[2] != self[0])
		assert(self.edges[0] != self.edges[1] and self.edges[1] != self.edges[2] and self.edges[2] != self.edges[0])
		
		self.drawn = self.canvas.create_polygon([c for v in self for c in v], fill=self.colour, tag='polygon')
		# Add this triangle to each edge involved.
		for edge in self.edges:
			edge.in_triangles.append(self)

class CurveComponent(DrawableObject):
	def __init__(self, canvas, vertices, options, thin=True, smooth=False):
		super(CurveComponent, self).__init__(canvas, vertices, options)
		self.colour = DEFAULT_CURVE_COLOUR
		if thin:
			self.drawn = self.canvas.create_line(
				[c for v in self.vertices for c in v],
				width=self.options.line_size,
				fill=self.colour,
				tag='curve',
				smooth=smooth,
				splinesteps=50
				)
		else:
			self.drawn = self.canvas.create_polygon(
				[c for v in self.vertices for c in v],
				fill=self.colour,
				tag='curve',
				outline=self.colour,
				smooth=smooth,
				splinesteps=50
				)
