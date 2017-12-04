
from hypothesis import given, settings
import hypothesis.strategies as st
import pickle
import pytest
import unittest

import curver
import strategies

class TestLamination(unittest.TestCase):
    @pytest.mark.slow
    @given(strategies.laminations())
    def test_pickle(self, lamination):
        self.assertEqual(lamination, pickle.loads(pickle.dumps(lamination)))
    
    @pytest.mark.slow
    @given(st.data())
    def test_hash(self, data):
        lamination1 = data.draw(strategies.laminations())
        lamination2 = data.draw(strategies.laminations(lamination1.triangulation))
        self.assertTrue(hash(lamination1) != hash(lamination2) or lamination1 == lamination2)
    
    @pytest.mark.slow
    @given(st.data())
    def test_orientation(self, data):
        lamination = data.draw(strategies.laminations())
        edge = data.draw(st.sampled_from(lamination.triangulation.edges))
        self.assertEqual(lamination(edge), lamination(~edge))

    @pytest.mark.slow
    @given(strategies.laminations())
    def test_components(self, lamination):
        self.assertEqual(lamination.triangulation.sum([multiplicity * component for component, multiplicity in lamination.components().items()]), lamination)
        self.assertEqual(lamination.triangulation.disjoint_sum([multiplicity * component for component, multiplicity in lamination.components().items()]), lamination)
        for component in lamination:
            self.assertEqual(component.intersection(component), 0)
    
    @pytest.mark.slow
    @given(st.data())
    def test_components_image(self, data):
        lamination = data.draw(strategies.laminations())
        encoding = data.draw(strategies.encodings(lamination.triangulation))
        self.assertEqual(set(encoding(lamination).components()), {encoding(component) for component in lamination.components()})
    
    @pytest.mark.slow
    @given(st.data())
    def test_intersection(self, data):
        lamination1 = data.draw(strategies.laminations())
        lamination2 = data.draw(strategies.laminations(lamination1.triangulation))
        encoding = data.draw(strategies.encodings(lamination1.triangulation))
        self.assertGreaterEqual(lamination1.intersection(lamination2), 0)
        self.assertEqual(lamination1.intersection(lamination2), encoding(lamination1).intersection(encoding(lamination2)))

