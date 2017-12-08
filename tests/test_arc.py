
from hypothesis import given, settings
import hypothesis.strategies as st
import pickle
import pytest
import unittest

import curver
import strategies

class TestArc(unittest.TestCase):
    @given(strategies.arcs())
    @settings(max_examples=25)
    def test_boundary_intersection(self, arc):
        boundary = arc.boundary()
        self.assertEqual(arc.intersection(boundary), 0)
    
    @given(strategies.arcs())
    @settings(max_examples=50)
    def test_halftwist(self, arc):
        if arc.connects_distinct_vertices():
            self.assertEqual(arc.boundary().encode_twist(), arc.encode_halftwist()**2)

