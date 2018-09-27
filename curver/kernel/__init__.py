
''' The curver kernel.

Some of the functions and methods have assumptions on them. These are denoted in the docstrings
by "Assumes that ..." meaning that:

    - If the assumptions are met then this function is guaranteed to terminate correctly.
    - If not then a curver.AssumptionError will be raised. '''

from .arc import Arc, MultiArc  # noqa: F401
from .crush import Crush, Lift  # noqa: F401
from .curve import Curve, MultiCurve  # noqa: F401
from .curvegraph import CurveGraph  # noqa: F401
from .encoding import Encoding, Mapping, MappingClass  # noqa: F401
from .error import AssumptionError, AbortError  # noqa: F401
from .homology import HomologyClass  # noqa: F401
from .lamination import Lamination  # noqa: F401
from .mappingclassgroup import MappingClassGroup  # noqa: F401
from .moves import Move, FlipGraphMove, EdgeFlip, Isometry  # noqa: F401
from .partition import CurvePartitionGraph  # noqa: F401
from .permutation import Permutation  # noqa: F401
from .structures import UnionFind, StraightLineProgram  # noqa: F401
from .triangulation import Edge, Triangle, Triangulation, norm  # noqa: F401
from .twist import Twist, HalfTwist  # noqa: F401
from . import utilities  # noqa: F401

# Set up shorter names for all of the different classes.
MCG = MappingClassGroup  # Alias.

# Functions that help with construction.
create_triangulation = Triangulation.from_tuple
triangulation_from_sig = Triangulation.from_sig

