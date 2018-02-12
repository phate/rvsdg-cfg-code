import unittest

import cfg_algorithm
import cfg_model
import cfg_view
import stmts

class TestAlgoBase(unittest.TestCase):
	__slots__ = ()
	
	def test_strongly_connected1(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('branch a')
		b = G.make_node('let P := b(P)')
		c = G.make_node('branch c')
		d = G.make_node('let P := d(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, b)
		G.make_edge(a, c, index = 1)
		G.make_edge(b, c)
		G.make_edge(c, b)
		G.make_edge(c, d, index = 1)
		G.make_edge(d, exit)
		
		clusters = cfg_algorithm.strongly_connected(G)
		self.assertEqual(clusters, [set((b, c))])
	
	def test_strongly_connected2(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('let p, P := a(P)')
		head = G.make_node('branch p')
		b = G.make_node('let P := b(P)')
		c = G.make_node('let p, P := c(P)')
		tail = G.make_node('branch p')
		d = G.make_node('let P := d(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, head)
		G.make_edge(head, b)
		G.make_edge(head, c, index = 1)
		G.make_edge(b, tail)
		G.make_edge(c, tail)
		G.make_edge(tail, head)
		G.make_edge(tail, d, index = 1)
		G.make_edge(d, exit)
		
		clusters = cfg_algorithm.strongly_connected(G)
		self.assertEqual(clusters, [set((head, b, c, tail))])
	
	def test_visit(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node(stmt = 'let p, P := a(P)')
		head = G.make_node(stmt = 'branch p')
		b = G.make_node('let P := b(P)')
		c = G.make_node('let p, P := c(P)')
		tail = G.make_node('branch p')
		d = G.make_node('let P := d(P)')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, head)
		G.make_edge(head, b)
		G.make_edge(head, c, index = 1)
		G.make_edge(b, tail)
		G.make_edge(c, tail)
		G.make_edge(tail, head)
		G.make_edge(tail, d, index = 1)
		G.make_edge(d, exit)
		
		visited = set()
		cfg_algorithm.visit((entry,), (exit,), lambda x: visited.add(x))
		self.assertEqual(visited, set((entry, a, head, b, c, tail, d)))
		
		visited = set()
		cfg_algorithm.visit((head,), (tail,), lambda x: visited.add(x))
		self.assertEqual(visited, set((head, b, c)))
	
	def test_strongly_connected_selfloop(self):
		G = cfg_model.cfg()
		entry = G.make_node(stmts.null_stmt())
		a = G.make_node('branch p')
		exit = G.make_node(stmts.null_stmt())
		G.make_edge(entry, a)
		G.make_edge(a, a, index = 1)
		G.make_edge(a, exit, index = 0)
		
		clusters = cfg_algorithm.strongly_connected(G)
		self.assertEqual(clusters, [set((a,))])
	
	def test_edge_dominators(self):
		G = cfg_model.cfg()
		entry = G.make_node('let p := A(p)')
		branch = G.make_node('branch p')
		a = G.make_node(stmts.null_stmt())
		b = G.make_node('branch p')
		c = G.make_node(stmts.null_stmt())
		exit = G.make_node(stmts.null_stmt())
		
		e1 = G.make_edge(entry, branch)
		e2 = G.make_edge(branch, a, 0)
		e3 = G.make_edge(branch, b, 1)
		e4 = G.make_edge(branch, exit, 2)
		e5 = G.make_edge(b, c, 0)
		e6 = G.make_edge(b, exit, 1)
		e7 = G.make_edge(c, exit)
		e8 = G.make_edge(a, exit)
		
		N, E = cfg_algorithm.edge_dominators(G, e2)
		self.assertEqual(set((a,)), N)
		self.assertEqual(set((e2, e8)), E)
		I, O = cfg_algorithm.border_edges(N, E)
		self.assertEqual([e2], I)
		self.assertEqual([e8], O)
		
		N, E = cfg_algorithm.edge_dominators(G, e3)
		self.assertEqual(set((b, c)), N)
		self.assertEqual(set((e3, e5, e6, e7)), E)
		I, O = cfg_algorithm.border_edges(N, E)
		self.assertEqual([e3], I)
		self.assertEqual(set((e6, e7)), set(O))
		
		N, E = cfg_algorithm.edge_dominators(G, e4)
		self.assertEqual(set(), N)
		self.assertEqual(set((e4,)), E)
		I, O = cfg_algorithm.border_edges(N, E)
		self.assertEqual([e4], I)
		self.assertEqual([e4], O)

if __name__ == '__main__':
	unittest.main()
