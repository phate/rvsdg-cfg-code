import os
import pygraphviz
import unittest

import rvsdg_model
import rvsdg_view

class TestTransforms(unittest.TestCase):
	__slots__ = ()
	
	def _example_graph1(self):
		G = rvsdg_model.rvsdg(('arg1', 'arg2'))
		return G
	
	def test_graph1(self):
		G = self._example_graph1()
	
	def test_passthrough_removal(self):
		G = rvsdg_model.rvsdg(('v1', 'v2'))
		G.add_result('v1', (None, 'v1'))
		G.add_result('v2', (None, 'v2'))
		self.assertTrue(G.is_passthrough('v1', 'v1'))
		G.remove_passthrough('v1', 'v1')
		self.assertTrue(G.is_passthrough('v2', 'v2'))
		G.remove_passthrough('v2', 'v2')
		self.assertFalse(G.arguments)
		self.assertFalse(G.results)
		self.assertFalse(G.result_values)
	
	def test_litnode(self):
		G = rvsdg_model.rvsdg(())
		n = G.add_litnode((1,), ('$r',))
		self.assertEquals(n.output_names, ('$r',))
	
	def test_simple_display(self):
		G = rvsdg_model.rvsdg(('v1', 'v2'))
		add = G.add_opnode('add', ('o1', 'o2'), ('sum',), ((None, 'v1'), (None, 'v2')))
		sub = G.add_opnode('sub', ('o1', 'o2'), ('dif',), ((None, 'v1'), (None, 'v2')))
		G.add_result('v1', (add, 'sum'))
		G.add_result('v2', (sub, 'dif'))
		
		rvsdg_view.make_gvg(G)
	
	def test_theta_display(self):
		G = rvsdg_model.rvsdg(('v1',))
		
		body = rvsdg_model.rvsdg(('v1',))
		dec = body.add_opnode('dec', ('v1',), ('r', '$pred'), ((None, 'v1'),))
		body.add_result('v1', (dec, 'r'))
		body.add_result('$repeat', (dec, '$pred'))
		theta = G.add_theta(body, ((None, 'v1'),))
		G.add_result('v1', (theta, 'v1'))
		
		rvsdg_view.make_gvg(G)
		#rvsdg_view.show(G)
	
	def test_gamma_display(self):
		G = rvsdg_model.rvsdg(('v1', 'v2'))
		c = G.add_opnode('gt', ('v1', 'v2'), ('pred',), ((None, 'v1'), (None, 'v2')))
		
		a1 = rvsdg_model.rvsdg(('v1', 'v2'))
		add = a1.add_opnode('add', ('o1', 'o2'), ('r',), ((None, 'v1'), (None, 'v2')))
		a1.add_result('r', (add, 'r'))
		
		a2 = rvsdg_model.rvsdg(('v1', 'v2'))
		sub = a2.add_opnode('sub', ('o1', 'o2'), ('r',), ((None, 'v1'), (None, 'v2')))
		a2.add_result('r', (sub, 'r'))
		
		g = G.add_gamma((a1, a2), ((None, 'v1'), (None, 'v2')), (c, 'pred'))
		G.add_result('r', (g, 'r'))
		
		rvsdg_view.make_gvg(G)
		#rvsdg_view.show(G)
	
	def test_gamma_normalize(self):
		G = rvsdg_model.rvsdg(('v1', 'v2'))
		c = G.add_opnode('gt', ('v1', 'v2'), ('pred',), ((None, 'v1'), (None, 'v2')))
		
		a1 = rvsdg_model.rvsdg(('v1', 'v2'))
		dec = a1.add_opnode('dec', ('v1',), ('r',), ((None, 'v1'),))
		a1.add_result('v1', (dec, 'r'))
		a1.add_result('v2', (None, 'v2'))
		
		a2 = rvsdg_model.rvsdg(('v1', 'v2'))
		a2.add_result('v1', (None, 'v1'))
		a2.add_result('v2', (None, 'v2'))
		
		g = G.add_gamma((a1, a2), ((None, 'v1'), (None, 'v2')), (c, 'pred'))
		G.add_result('v1', (g, 'v1'))
		G.add_result('v2', (g, 'v2'))
		
		#rvsdg_view.show(G)
		G.normalize()
		self.assertEqual(G.get_resultvalue_by_name('v2'), (None, 'v2'))
		#rvsdg_view.show(G)

if __name__ == '__main__':
	unittest.main()
