import unittest

import cfg_model
import cfg_algorithm
import cfg_view
import stmts
import rvsdg2cfg
import rvsdg_model
import rvsdg_view

class TestRVSDG2CFG(unittest.TestCase):
	__slots__ = ()
	
	def test_simple1(self):
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		add = rvsdg.add_opnode('add', ('o1', 'o2'), ('sum',), ((None, 'v1'), (None, 'v2')))
		sub = rvsdg.add_opnode('sub', ('o1', 'o2'), ('dif',), ((None, 'v1'), (None, 'v2')))
		rvsdg.add_result('v1', (add, 'sum'))
		rvsdg.add_result('v2', (sub, 'dif'))
		
		cfg = rvsdg2cfg.convert(rvsdg)
		#cfg_view.show(cfg)
	
	def test_simple2(self):
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		lit = rvsdg.add_litnode((42,), ('c',))
		add = rvsdg.add_opnode('add', ('o1', 'o2'), ('sum',), ((None, 'v1'), (None, 'v2')))
		sub = rvsdg.add_opnode('sub', ('o1', 'o2'), ('dif',), ((None, 'v1'), (lit, 'c')))
		rvsdg.add_result('v1', (add, 'sum'))
		rvsdg.add_result('v2', (sub, 'dif'))
		
		cfg = rvsdg2cfg.convert(rvsdg)
		#cfg_view.show(cfg)
	
	def test_static_gamma(self):
		def refG():
			cfg = cfg_model.cfg()
			entry = cfg.make_node(stmts.null_stmt())
			l = cfg.make_node('let v3 := sub(v1, v2)')
			exit = cfg.make_node(stmts.null_stmt())
			cfg.make_edge(entry, l)
			cfg.make_edge(l, exit)
			return cfg
		
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		static_decide = rvsdg.add_litnode((1,), ('$r',))
		alt1 = rvsdg_model.rvsdg(('v1', 'v2'))
		add = alt1.add_opnode('add', ('o1', 'o2'), ('v3',), ((None, 'v1'), (None, 'v2')))
		alt1.add_result('v3', (add, 'v3'))
		alt2 = rvsdg_model.rvsdg(('v1', 'v2'))
		add = alt2.add_opnode('sub', ('o1', 'o2'), ('v3',), ((None, 'v1'), (None, 'v2')))
		alt2.add_result('v3', (add, 'v3'))
		gamma = rvsdg.add_gamma((alt1, alt2), ((None, 'v1'), (None, 'v2')), (static_decide, '$r'))
		rvsdg.add_result('v3', (gamma, 'v3'))
		#rvsdg_view.show(rvsdg)
		cfg = rvsdg2cfg.convert(rvsdg)
		cfg_algorithm.prune(cfg)
		#cfg_view.show(cfg)
		self.assertTrue(cfg_algorithm.equivalent(cfg, refG()))
	
	def test_dynamic_gamma(self):
		def refG():
			cfg = cfg_model.cfg()
			entry = cfg.make_node(stmts.null_stmt())
			c = cfg.make_node('let r := cmp(v1, v2)')
			b = cfg.make_node('branch r')
			alt1 = cfg.make_node('let v3 := add(v1, v2)')
			alt2 = cfg.make_node('let v3 := sub(v1, v2)')
			exit = cfg.make_node(stmts.null_stmt())
			
			cfg.make_edge(entry, c)
			cfg.make_edge(c, b)
			cfg.make_edge(b, alt1, index = 0)
			cfg.make_edge(b, alt2, index = 1)
			cfg.make_edge(alt1, exit)
			cfg.make_edge(alt2, exit)
			return cfg
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		compare = rvsdg.add_opnode('cmp', ('a', 'b'), ('r',), ((None, 'v1'), (None, 'v2')))
		dynamic_decide = rvsdg.add_selectnode(((0,), (1,)), 'r', ('$r',), (compare, 'r'))
		alt1 = rvsdg_model.rvsdg(('v1', 'v2'))
		add = alt1.add_opnode('add', ('o1', 'o2'), ('v3',), ((None, 'v1'), (None, 'v2')))
		alt1.add_result('v3', (add, 'v3'))
		alt2 = rvsdg_model.rvsdg(('v1', 'v2'))
		add = alt2.add_opnode('sub', ('o1', 'o2'), ('v3',), ((None, 'v1'), (None, 'v2')))
		alt2.add_result('v3', (add, 'v3'))
		gamma = rvsdg.add_gamma((alt1, alt2), ((None, 'v1'), (None, 'v2')), (dynamic_decide, '$r'))
		rvsdg.add_result('v3', (gamma, 'v3'))
		#rvsdg_view.show(rvsdg)
		cfg = rvsdg2cfg.convert(rvsdg)
		cfg_algorithm.prune(cfg)
		#cfg_view.show(cfg)
		self.assertTrue(cfg_algorithm.equivalent(cfg, refG()))
	
	def test_simple_theta(self):
		def refG():
			cfg = cfg_model.cfg()
			entry = cfg.make_node(stmts.null_stmt())
			a = cfg.make_node('let v1, z := dec(v1)')
			b = cfg.make_node('let v2 := sqr(v2)')
			c = cfg.make_node('branch z')
			exit = cfg.make_node(stmts.null_stmt())
			
			cfg.make_edge(entry, a)
			cfg.make_edge(a, b)
			cfg.make_edge(b, c)
			cfg.make_edge(c, a, index = 1)
			cfg.make_edge(c, exit, index = 0)
			return cfg
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		
		loop_body = rvsdg_model.rvsdg(('v1', 'v2'))
		dec = loop_body.add_opnode('dec', ('v1',), ('v1', 'z'), ((None, 'v1'),))
		mul = loop_body.add_opnode('sqr', ('v2',), ('v2',), ((None, 'v2'),))
		tst = loop_body.add_selectnode(((0,), (1,)), 'z', ('$repeat',), (dec, 'z'))
		loop_body.add_result('v1', (dec, 'v1'))
		loop_body.add_result('v2', (mul, 'v2'))
		loop_body.add_result('$repeat', (tst, '$repeat'))
		loop = rvsdg.add_theta(loop_body, ((None, 'v1'), (None, 'v2')))
		rvsdg.add_result('v1', (loop, 'v1'))
		rvsdg.add_result('v2', (loop, 'v2'))
		#rvsdg_view.show(rvsdg)
		cfg = rvsdg2cfg.convert(rvsdg)
		#cfg_algorithm.prune(cfg)
		#cfg_view.show(cfg)
		self.assertTrue(cfg_algorithm.equivalent(cfg, refG()))
	
	def test_multi_exit_theta(self):
		def refG():
			cfg = cfg_model.cfg()
			entry = cfg.make_node(stmts.null_stmt())
			a = cfg.make_node('let v2 := sqr(v2)')
			b = cfg.make_node('let c := cmp(v1, v2)')
			c = cfg.make_node('branch c')
			d = cfg.make_node('let r:= mov(v1)')
			e = cfg.make_node('let r:= mov(v2)')
			exit = cfg.make_node(stmts.null_stmt())
			
			cfg.make_edge(entry, a)
			cfg.make_edge(a, b)
			cfg.make_edge(b, c)
			cfg.make_edge(c, d, index = 0)
			cfg.make_edge(c, a, index = 1)
			cfg.make_edge(c, e, index = 2)
			cfg.make_edge(d, exit)
			cfg.make_edge(e, exit)
			return cfg
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		
		unused = rvsdg.add_litnode((0,), ('$d',))
		
		loop_body = rvsdg_model.rvsdg(('v1', 'v2', '$d'))
		mul = loop_body.add_opnode('sqr', ('v2',), ('v2',), ((None, 'v2'),))
		compare = loop_body.add_opnode('cmp', ('v1', 'v2'), ('c'), ((None, 'v1'),(mul, 'v2')))
		tst = loop_body.add_selectnode(((0, 0), (1, 0), (0, 1)), 'c', ('$repeat', '$d'), (compare, 'c'))
		loop_body.add_result('v1', (None, 'v1'))
		loop_body.add_result('v2', (mul, 'v2'))
		loop_body.add_result('$d', (tst, '$d'))
		loop_body.add_result('$repeat', (tst, '$repeat'))
		loop = rvsdg.add_theta(loop_body, ((None, 'v1'), (None, 'v2'), (unused, '$d')))
		
		alt1 = rvsdg_model.rvsdg(('v1', 'v2'))
		mov1 = alt1.add_opnode('mov', ('v1',), ('r',), ((None, 'v1'),))
		alt1.add_result('r', (mov1, 'r'))
		alt2 = rvsdg_model.rvsdg(('v1', 'v2'))
		mov1 = alt2.add_opnode('mov', ('v2',), ('r',), ((None, 'v2'),))
		alt2.add_result('r', (mov1, 'r'))
		gamma = rvsdg.add_gamma((alt1, alt2), ((loop, 'v1'), (loop, 'v2')), (loop, '$d'))
		
		rvsdg.add_result('r', (gamma, 'r'))
		#rvsdg_view.show(rvsdg)
		cfg = rvsdg2cfg.convert(rvsdg)
		#cfg_algorithm.prune(cfg)
		#cfg_view.show(cfg)
		#cfg_view.show(refG())
		self.assertTrue(cfg_algorithm.equivalent(cfg, refG()))
	
	def test_multi_entry_theta(self):
		def refG():
			cfg = cfg_model.cfg()
			entry = cfg.make_node(stmts.null_stmt())
			a = cfg.make_node('let c := gt(v1, v2)')
			b = cfg.make_node('branch c')
			c1 = cfg.make_node('let v1 := sub(v1, v2)')
			c2 = cfg.make_node('let v2 := sub(v2, v1)')
			d = cfg.make_node('let c := cmp(v1, v2)')
			e = cfg.make_node('branch c')
			exit = cfg.make_node(stmts.null_stmt())
			
			cfg.make_edge(entry, a)
			cfg.make_edge(a, b)
			cfg.make_edge(b, c1, index = 0)
			cfg.make_edge(b, c2, index = 1)
			cfg.make_edge(c1, d)
			cfg.make_edge(c2, d)
			cfg.make_edge(d, e)
			cfg.make_edge(e, c1, index = 0)
			cfg.make_edge(e, c2, index = 2)
			cfg.make_edge(e, exit, index = 1)
			return cfg
		rvsdg = rvsdg_model.rvsdg(('v1', 'v2'))
		
		loop_body = rvsdg_model.rvsdg(('v1', 'v2', '$d'))
		alt1 = rvsdg_model.rvsdg(('v1', 'v2'))
		sub1 = alt1.add_opnode('sub', ('v1', 'v2'), ('v1',), ((None, 'v1'), (None, 'v2')))
		alt1.add_result('v1', (sub1, 'v1'))
		alt1.add_result('v2', (None, 'v2'))
		alt2 = rvsdg_model.rvsdg(('v1', 'v2'))
		sub2 = alt2.add_opnode('sub', ('v2', 'v1'), ('v2',), ((None, 'v2'), (None, 'v1')))
		alt2.add_result('v1', (None, 'v1'))
		alt2.add_result('v2', (sub2, 'v2'))
		gamma = loop_body.add_gamma((alt1, alt2), ((None, 'v1'), (None, 'v2')), (None, '$d'))
		
		compare = loop_body.add_opnode('cmp', ('v1', 'v2'), ('c'), ((gamma, 'v1'),(gamma, 'v2')))
		tst = loop_body.add_selectnode(((1, 0), (0, 0), (1, 1)), 'c', ('$repeat', '$d'), (compare, 'c'))
		
		loop_body.add_result('v1', (gamma, 'v1'))
		loop_body.add_result('v2', (gamma, 'v2'))
		loop_body.add_result('$d', (tst, '$d'))
		loop_body.add_result('$repeat', (tst, '$repeat'))
		
		compare = rvsdg.add_opnode('gt', ('v1', 'v2'), ('c'), ((None, 'v1'),(None, 'v2')))
		tst = rvsdg.add_selectnode(((0,), (1,)), 'c', ('$d',), (compare, 'c'))
		loop = rvsdg.add_theta(loop_body, ((None, 'v1'), (None, 'v2'), (tst, '$d')))
		
		rvsdg.add_result('v1', (loop, 'v1'))
		rvsdg.add_result('v2', (loop, 'v2'))
		#rvsdg_view.show(rvsdg)
		cfg = rvsdg2cfg.convert(rvsdg)
		#cfg_algorithm.prune(cfg)
		#cfg_view.show(cfg)
		#cfg_view.show(refG())
		self.assertTrue(cfg_algorithm.equivalent(cfg, refG()))

if __name__ == '__main__':
	unittest.main()
