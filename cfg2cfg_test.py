import unittest

import cfg2cfg
import cfg_algorithm
import cfg_model
import cfg_view
import stmts

class CFG2CFGTest(unittest.TestCase):
	__slots__ = ()
	
	def test_acyclic_simple(self):
		# graph consisting of a single node, no branches
		G = cfg_model.cfg()
		G.make_node('let a := 0')
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(cfg_algorithm.equivalent(G, newG))

	def test_acyclic_linear(self):
		# graph consisting of a linear node, no branches
		G = cfg_model.cfg()
		a = G.make_node('let a := 0')
		b = G.make_node('let b := 0')
		c = G.make_node('let c := 0')
		G.make_edge(a, b)
		G.make_edge(b, c)
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(cfg_algorithm.equivalent(G, newG))
	
	def test_acyclic_consistent_branch(self):
		# graph consisting of a single consistent branch
		G = cfg_model.cfg()
		a = G.make_node('branch p')
		b = G.make_node('let b := 0')
		c = G.make_node('let c := 0')
		d = G.make_node('let d := 0')
		G.make_edge(a, b, 0)
		G.make_edge(a, c, 1)
		G.make_edge(b, d)
		G.make_edge(c, d)
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(cfg_algorithm.equivalent(G, newG))

	def test_acyclic_consistent_nested_branch(self):
		# graph consisting of two nested branches, both
		# consistently joined
		G = cfg_model.cfg()
		n = G.make_node('branch p')
		n1 = G.make_node('branch p')
		n2 = G.make_node('let c := 0')
		n11 = G.make_node('let d := 0')
		n12 = G.make_node('let e := 0')
		n1c = G.make_node('let f := 0')
		nc = G.make_node('let g := 0')
		
		G.make_edge(n, n1, 0)
		G.make_edge(n, n2, 1)
		G.make_edge(n1, n11, 0)
		G.make_edge(n1, n12, 1)
		G.make_edge(n11, n1c)
		G.make_edge(n12, n1c)
		G.make_edge(n1c, nc)
		G.make_edge(n2, nc)
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(cfg_algorithm.equivalent(G, newG))
	
	def test_acyclic_break_join(self):
		# graph consisting of two nested branches, but the three
		# paths opened up by the two branches are joined into a single
		# node; need to insert a "null" stmt to strictly join the
		# inner nested branch, but no new branch is required
		def refG():
			G = cfg_model.cfg()
			n = G.make_node('branch p')
			n1 = G.make_node('branch p')
			n2 = G.make_node('let c := 0')
			n11 = G.make_node('let d := 0')
			n12 = G.make_node('let e := 0')
			n1c = G.make_node(stmts.null_stmt())
			nc = G.make_node('let g := 0')
			
			G.make_edge(n, n1, 0)
			G.make_edge(n, n2, 1)
			G.make_edge(n1, n11, 0)
			G.make_edge(n1, n12, 1)
			G.make_edge(n11, n1c)
			G.make_edge(n12, n1c)
			G.make_edge(n1c, nc)
			G.make_edge(n2, nc)
			
			return G
		
		G = cfg_model.cfg()
		n = G.make_node('branch p')
		n1 = G.make_node('branch p')
		n2 = G.make_node('let c := 0')
		n11 = G.make_node('let d := 0')
		n12 = G.make_node('let e := 0')
		nc = G.make_node('let g := 0')
		
		G.make_edge(n, n1, 0)
		G.make_edge(n, n2, 1)
		G.make_edge(n1, n11, 0)
		G.make_edge(n1, n12, 1)
		G.make_edge(n11, nc)
		G.make_edge(n12, nc)
		G.make_edge(n2, nc)
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(cfg_algorithm.equivalent(refG(), newG))
	
	def test_acyclic_inconsistent_nested_branches(self):
		def refG(pred):
			invpred = 1 - pred
			G = cfg_model.cfg()
			a = G.make_node('branch p')
			b = G.make_node('branch p')
			c = G.make_node('let c := 0')
			letp_c = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr(str(pred))))
			letp_d = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr(str(pred))))
			letp_e = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr(str(invpred))))
			n = G.make_node(stmts.null_stmt())
			d = G.make_node('let d := 0')
			e = G.make_node('let e := 0')
			rebranch = G.make_node(stmts.branch_stmt(stmts.var_expr('$p')))
			f = G.make_node('let f := 0')
			empty = G.make_node(stmts.null_stmt())
			g = G.make_node('let g := 0')
			G.make_edge(a, b, 0)
			G.make_edge(a, c, 1)
			G.make_edge(b, d, 0)
			G.make_edge(b, e, 1)
			G.make_edge(c, letp_c)
			G.make_edge(d, letp_d)
			G.make_edge(e, letp_e)
			G.make_edge(letp_d, n)
			G.make_edge(letp_e, n)
			G.make_edge(letp_c, rebranch)
			G.make_edge(n, rebranch)
			G.make_edge(rebranch, f, pred)
			G.make_edge(rebranch, empty, invpred)
			G.make_edge(f, g)
			G.make_edge(empty, g)
			
			return G
		
		G = cfg_model.cfg()
		a = G.make_node('branch p')
		b = G.make_node('branch p')
		c = G.make_node('let c := 0')
		d = G.make_node('let d := 0')
		e = G.make_node('let e := 0')
		f = G.make_node('let f := 0')
		g = G.make_node('let g := 0')
		G.make_edge(a, b, 0)
		G.make_edge(a, c, 1)
		G.make_edge(b, d, 0)
		G.make_edge(b, e, 1)
		G.make_edge(c, f)
		G.make_edge(d, f)
		G.make_edge(e, g)
		G.make_edge(f, g)
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(
			cfg_algorithm.equivalent(refG(1), newG) or
			cfg_algorithm.equivalent(refG(0), newG))
	
	def test_acyclic_inconsistent_defer(self):
		# graph consisting of two nested branches, with predicate
		# assignments before the exit node; must make sure to defer
		# processing of predicate assignments so that it still
		# ends up just before the end of the graph after regularization
		def refG(pred):
			invpred = 1 - pred
			G = cfg_model.cfg()
			entry = G.make_node(stmts.null_stmt())
			a = G.make_node('let v := a(P)')
			b = G.make_node('branch v')
			c = G.make_node('let w := b(P)')
			d = G.make_node('branch w')
			e = G.make_node('let P := e(P)')
			f = G.make_node('let P := f(P)')
			e2 = G.make_node(stmts.let_stmt(('$r',), stmts.parse_expr('0')))
			f2 = G.make_node(stmts.let_stmt(('$r',), stmts.parse_expr('1')))
			exit = G.make_node(stmts.null_stmt())
			
			letp_1 = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr(str(pred))))
			letp_2 = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr(str(pred))))
			letp_3 = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr(str(invpred))))
			null_23 = G.make_node(stmts.null_stmt())
			branchp = G.make_node(stmts.branch_stmt(stmts.var_expr('$p')))
			
			G.make_edge(entry, a)
			G.make_edge(a, b)
			G.make_edge(b, c, index = 0)
			G.make_edge(b, letp_1, index = 1)
			G.make_edge(letp_1, branchp)
			G.make_edge(c, d)
			G.make_edge(d, e, index = 0)
			G.make_edge(e, letp_3)
			G.make_edge(d, letp_2, index = 1)
			G.make_edge(letp_2, null_23)
			G.make_edge(letp_3, null_23)
			G.make_edge(null_23, branchp)
			G.make_edge(branchp, f, pred)
			G.make_edge(f, f2)
			G.make_edge(f2, exit)
			G.make_edge(branchp, e2, invpred)
			G.make_edge(e2, exit)
			
			return G
		
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let v := a(P)')
		b = G.make_node('branch v')
		c = G.make_node('let w := b(P)')
		d = G.make_node('branch w')
		e = G.make_node('let P := e(P)')
		f = G.make_node('let P := f(P)')
		e2 = G.make_node(stmts.let_stmt(('$r',), stmts.parse_expr('0')))
		f2 = G.make_node(stmts.let_stmt(('$r',), stmts.parse_expr('1')))
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
		
		newG = cfg2cfg.regularize_cfg_acyclic(G)
		self.assertTrue(
			cfg_algorithm.equivalent(refG(1), newG) or
			cfg_algorithm.equivalent(refG(0), newG))
	
	def _make_pseudo_loop_graph(self):
		G = cfg_model.cfg()
		entry = G.make_node('let v := a(P)')
		a = G.make_node('branch v')
		b = G.make_node('let P := b(P)')
		c = G.make_node(stmts.let_stmt(('$x',), stmts.parse_expr('0')))
		d = G.make_node(stmts.let_stmt(('$x',), stmts.parse_expr('1')))
		e = G.make_node(stmts.let_stmt(('P',), stmts.call_expr('e', (stmts.var_expr('$x'),))))
		f = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('0')))
		g = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('1')))
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b, 0)
		G.make_edge(a, c, 1)
		G.make_edge(a, d, 2)
		G.make_edge(b, f)
		G.make_edge(c, e)
		G.make_edge(d, e)
		G.make_edge(e, g)
		G.make_edge(f, exit)
		G.make_edge(g, exit)
		return G
	
	def _pseudo_loop_ref_graph(self, pred, dummy_predicate = False):
		invpred = 1 - pred
		G = cfg_model.cfg()
		entry = G.make_node('let v := a(P)')
		a = G.make_node('branch v')
		b = G.make_node('let P := b(P)')
		if dummy_predicate:
			bp = G.make_node(stmts.let_stmt(('$p', '$x'), stmts.parse_expr('%d,-1' % invpred)))
		else:
			bp = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('%d' % invpred)))
		c = G.make_node(stmts.let_stmt(('$p', '$x',), stmts.parse_expr('%d, 0' % pred)))
		d = G.make_node(stmts.let_stmt(('$p', '$x',), stmts.parse_expr('%d, 1' % pred)))
		rebranch = G.make_node(stmts.branch_stmt(stmts.var_expr('$p')))
		e = G.make_node(stmts.let_stmt(('P',), stmts.call_expr('e', (stmts.var_expr('$x'),))))
		f = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('0')))
		g = G.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('1')))
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b, 0)
		G.make_edge(a, c, 1)
		G.make_edge(a, d, 2)
		G.make_edge(b, bp)
		G.make_edge(bp, rebranch)
		G.make_edge(c, rebranch)
		G.make_edge(d, rebranch)
		G.make_edge(rebranch, e, pred)
		G.make_edge(rebranch, f, invpred)
		G.make_edge(e, g)
		G.make_edge(f, exit)
		G.make_edge(g, exit)
		return G
	
	def test_acyclic_loop_pred(self):
		G = self._make_pseudo_loop_graph()
		newG = cfg2cfg.regularize_cfg_acyclic(G, False)
		ref0 = self._pseudo_loop_ref_graph(0)
		ref1 = self._pseudo_loop_ref_graph(1)
		self.assertTrue(
			cfg_algorithm.equivalent(ref0, newG) or
			cfg_algorithm.equivalent(ref1, newG))
	
	def test_acyclic_loop_pred_pseudo_pred(self):
		G = self._make_pseudo_loop_graph()
		newG = cfg2cfg.regularize_cfg_acyclic(G, True)
		ref0 = self._pseudo_loop_ref_graph(0, True)
		ref1 = self._pseudo_loop_ref_graph(1, True)
		self.assertTrue(
			cfg_algorithm.equivalent(ref0, newG) or
			cfg_algorithm.equivalent(ref1, newG))

if __name__ == '__main__':
	unittest.main()
