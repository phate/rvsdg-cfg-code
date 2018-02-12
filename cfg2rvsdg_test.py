import unittest

import cfg2rvsdg
import cfg_model
import cfg_view
import rvsdg_model
import rvsdg_view
import stmts

class CFG2RVSDGTest(unittest.TestCase):
	__slots__ = ()
	
	def _linear_refgraph(self):
		rvsdg = rvsdg_model.rvsdg(('P',))
		a = rvsdg.add_opnode('a', ('P',), ('P',), ((None, 'P'),))
		l1 = rvsdg.add_litnode((1,), ('x',))
		l2 = rvsdg.add_litnode((2, 3), ('y', 'z'))
		c = rvsdg.add_opnode('c', ('P', 'x', 'y', 'z'), ('P'), ((a, 'P'), (l1, 'x'), (l2, 'y'), (l2, 'z')))
		rvsdg.add_result('P', (c, 'P'))
		return rvsdg
	
	def test_linear(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let P := a(P)')
		b = G.make_node('let x := 1')
		c = G.make_node('let y, z := 2, 3')
		d = G.make_node('let P := c(P, x, y, z)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c)
		G.make_edge(c, d)
		G.make_edge(d, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		ref = self._linear_refgraph()
		self.assertEquals(rvsdg, ref)
	
	def _simple_branch_refgraph(self):
		rvsdg = rvsdg_model.rvsdg(('P',))
		a = rvsdg.add_opnode('a', ('P',), ('p',), ((None, 'P'),))
		alt1 = rvsdg_model.rvsdg(('P',))
		c = alt1.add_opnode('c', ('P',), ('P',), ((None, 'P'),))
		alt1.add_result('P', (c, 'P'))
		alt2 = rvsdg_model.rvsdg(('P',))
		d = alt2.add_opnode('d', ('P',), ('P',), ((None, 'P'),))
		alt2.add_result('P', (d, 'P'))
		p = rvsdg.add_selectnode(((0,), (1,)), 'p', ('$p',), (a, 'p'))
		gamma = rvsdg.add_gamma([alt1, alt2], ((None, 'P'),), (p, '$p'))
		rvsdg.add_result('P', (gamma, 'P'))
		return rvsdg
	
	def test_simple_branch(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let p := a(P)')
		b = G.make_node('branch p')
		c = G.make_node('let P := c(P)')
		d = G.make_node('let P := d(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c, index = 0)
		G.make_edge(b, d, index = 1)
		G.make_edge(c, exit)
		G.make_edge(d, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		ref = self._simple_branch_refgraph()
		self.assertEquals(rvsdg, ref)
	
	def test_empty_branch(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let p := a(P)')
		b = G.make_node('branch p')
		c = G.make_node('let P := c(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c, index = 0)
		G.make_edge(b, exit, index = 1)
		G.make_edge(c, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		#rvsdg_view.show(rvsdg)
	
	def test_nested_merge_branch(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let x, y := a(P)')
		b = G.make_node('branch x')
		c = G.make_node('branch y')
		d = G.make_node('let P := d(P)')
		e = G.make_node('let P := e(P)')
		f = G.make_node('let P := f(P)')
		g = G.make_node('let P := g(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c, index = 0)
		G.make_edge(b, d, index = 1)
		G.make_edge(c, e, index = 0)
		G.make_edge(c, f, index = 1)
		
		G.make_edge(d, g)
		G.make_edge(e, g)
		G.make_edge(f, g)
		G.make_edge(g, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		#rvsdg_view.show(rvsdg)

	def _inconsistent_merge_branch_refgraph(self, swap):
		rvsdg = rvsdg_model.rvsdg(('P',))
		a = rvsdg.add_opnode('a', ('P',), ('x', 'y',), ((None, 'P'),))
		
		alt0 = rvsdg_model.rvsdg(('P', 'y'))
		
		alt00 = rvsdg_model.rvsdg(('P',))
		n = alt00.add_opnode('e', ('P',), ('P',), ((None, 'P'),))
		l = alt00.add_litnode((1 if not swap else 0,), ('$p',))
		alt00.add_result('P', (n, 'P'))
		alt00.add_result('$p', (l, '$p'))
		
		alt01 = rvsdg_model.rvsdg(('P',))
		n = alt01.add_opnode('f', ('P',), ('P',), ((None, 'P'),))
		l = alt01.add_litnode((0 if not swap else 1,), ('$p',))
		alt01.add_result('P', (n, 'P'))
		alt01.add_result('$p', (l, '$p'))
		
		alt0y = alt0.add_selectnode(((0,), (1,)), 'y', ('$p',), (None, 'y'))
		gamma = alt0.add_gamma([alt00, alt01], ((None, 'P'),), (alt0y, '$p'))
		
		alt0.add_result('P', (gamma, 'P'))
		alt0.add_result('$p', (gamma, '$p'))
		
		alt1 = rvsdg_model.rvsdg(('P', 'y'))
		n = alt1.add_opnode('d', ('P',), ('P',), ((None, 'P'),))
		l = alt1.add_litnode((1 if not swap else 0,), ('$p',))
		alt1.add_result('P', (n, 'P'))
		alt1.add_result('$p', (l, '$p'))
		
		xp = rvsdg.add_selectnode(((0,), (1,)), 'x', ('$p',), (a, 'x'))
		gamma = rvsdg.add_gamma([alt0, alt1], ((None, 'P'), (a, 'y')), (xp, '$p'))
		
		alt0 = rvsdg_model.rvsdg(('P',))
		alt0.add_result('P', (None, 'P'))
		
		alt1 = rvsdg_model.rvsdg(('P',))
		n = alt1.add_opnode('g', ('P',), ('P',), ((None, 'P'),))
		alt1.add_result('P', (n, 'P'))
		
		gamma = rvsdg.add_gamma([alt0, alt1] if not swap else [alt1, alt0], ((gamma, 'P'),), (gamma, '$p'))
		h = rvsdg.add_opnode('h', ('P',), ('P',), ((gamma, 'P'),))
		
		rvsdg.add_result('P', (h, 'P'))
		return rvsdg
	
	def test_inconsistent_merge_branch(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let x, y := a(P)')
		b = G.make_node('branch x')
		c = G.make_node('branch y')
		d = G.make_node('let P := d(P)')
		e = G.make_node('let P := e(P)')
		f = G.make_node('let P := f(P)')
		g = G.make_node('let P := g(P)')
		h = G.make_node('let P := h(P)')
		exit = G.make_node(stmts.null_stmt())
		
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c, index = 0)
		G.make_edge(b, d, index = 1)
		G.make_edge(c, e, index = 0)
		G.make_edge(c, f, index = 1)
		
		G.make_edge(d, g)
		G.make_edge(e, g)
		G.make_edge(f, h)
		G.make_edge(g, h)
		G.make_edge(h, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		ref0 = self._inconsistent_merge_branch_refgraph(0)
		ref1 = self._inconsistent_merge_branch_refgraph(1)
		#rvsdg_view.show(rvsdg)
		#rvsdg_view.show(ref1)
		self.assertTrue(rvsdg == ref0 or rvsdg == ref1)
		
	def test_pseudo_branch(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let p := a(P)')
		b = G.make_node('branch p')
		c = G.make_node('let P := C(P)')
		exit = G.make_node(stmts.null_stmt())
		
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c)
		G.make_edge(c, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		#rvsdg_view.show(rvsdg)
	
	def test_simple_loop(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let P := a(P)')
		b = G.make_node('let p, P := b(P)')
		c = G.make_node('branch p')
		d = G.make_node('let P := d(P)')
		exit = G.make_node(stmts.null_stmt())
		
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c)
		G.make_edge(c, d, index = 0)
		G.make_edge(c, b, index = 1)
		G.make_edge(d, exit)
		
		#cfg_view.show(G)
		#cfg2rvsdg.convert_loops(G, cfg2rvsdg.predicate_generator())
		#cfg_view.show(G)
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		#rvsdg_view.show(rvsdg)
	
	def test_multi_exit_loop(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let P := a(P)')
		b = G.make_node('let p, P := b(P)')
		b_ = G.make_node('branch p')
		c = G.make_node('let p, P := c(P)')
		c_ = G.make_node('branch p')
		d = G.make_node('let P := d(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, b_)
		G.make_edge(b_, c, index = 0)
		G.make_edge(b_, d, index = 1)
		G.make_edge(c, c_)
		G.make_edge(c_, b, index = 0)
		G.make_edge(c_, d, index = 1)
		G.make_edge(d, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
	
	def test_alt_exits_loop(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let P := a(P)')
		b = G.make_node('let p, P := b(P)')
		b_ = G.make_node('branch p')
		c = G.make_node('let p, P := c(P)')
		c_ = G.make_node('branch p')
		d = G.make_node('let P := d(P)')
		e = G.make_node('let P := e(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, b_)
		G.make_edge(b_, c, index = 0)
		G.make_edge(b_, d, index = 1)
		G.make_edge(c, c_)
		G.make_edge(c_, b, index = 0)
		G.make_edge(c_, e, index = 1)
		G.make_edge(d, exit)
		G.make_edge(e, exit)
		
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		#rvsdg_view.show(rvsdg)
	
	def test_nico1(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		n0 = G.make_node('let v1, v2, v3, v4, v5, v6 := f(P)')
		n1 = G.make_node('branch v1')
		n2 = G.make_node('let v2 := 2')
		n3 = G.make_node('branch v3')
		n4 = G.make_node('let v4 := 4')
		n5 = G.make_node('let v5 := 5')
		n6 = G.make_node('let v6 := 6')
		n7 = G.make_node('let P := g(v1, v2, v3, v4, v5, v6, P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, n0)
		G.make_edge(n0, n1)
		G.make_edge(n1, n2, index = 0)
		G.make_edge(n1, n3, index = 1)
		G.make_edge(n2, n4)
		G.make_edge(n3, n4, index = 0)
		G.make_edge(n3, n5, index = 1)
		G.make_edge(n4, n6)
		G.make_edge(n5, n6)
		G.make_edge(n6, n7)
		G.make_edge(n7, exit)
		
		#cfg_view.show(G)
		rvsdg = cfg2rvsdg.convert(G)
		rvsdg.normalize()
		#rvsdg_view.show(rvsdg)
	
	def test_empty_branch_fail(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let v := a(P)')
		b = G.make_node('branch v')
		c = G.make_node('let x := 0')
		d = G.make_node('let w := d(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, d, index = 0)
		G.make_edge(b, c, index = 1)
		G.make_edge(c, d)
		G.make_edge(d, exit)
		
		# Test is considered to succeed if w is indeed defined at end
		# of region, no need to explicitly add expectations here.
		rvsdg = cfg2rvsdg.convert(G, ('P',), ('P', 'w'), ('P', 'w'))
	
	def test_inconsistent_merge_vardef(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let v := a(P)')
		b = G.make_node('branch v')
		c = G.make_node('let w := b(P)')
		d = G.make_node('branch w')
		e = G.make_node('let P := e(P)')
		f = G.make_node('let P := f(P)')
		e2 = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('0')))
		f2 = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('1')))
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(b, c, index = 0)
		G.make_edge(b, f, index = 1)
		G.make_edge(c, d)
		G.make_edge(d, e, index = 0)
		G.make_edge(d, f, index = 1)
		G.make_edge(e, e2)
		G.make_edge(f, f2)
		G.make_edge(e2, exit)
		G.make_edge(f2, exit)
		
		#cfg_view.show(G)
		rvsdg = cfg2rvsdg.convert(G, ('P',), ('P', '$p'), ('P', '$p'))
		#rvsdg.normalize()
		#rvsdg_view.show(rvsdg)
	
if __name__ == '__main__':
	unittest.main()
