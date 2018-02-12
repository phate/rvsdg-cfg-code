# expressions occuring in a cfg

import stmts

class cfg(object):
	__slots__ = (
		'nodes',
		'edges',
		'entries',
		'exits',
	)
	
	class node(object):
		__slots__ = ('cfg', 'incoming', '_outgoing', 'stmt', '_outgoing_sorted')
		
		def __init__(self, cfg, stmt):
			assert isinstance(stmt, stmts.stmt)
			self.cfg = cfg
			self.incoming = []
			self._outgoing = []
			self.stmt = stmt
			cfg.nodes.add(self)
			self._outgoing_sorted = True
		
		def __str__(self):
			return 'node(%s)' % str(self.stmt)
		
		def get_successors(self):
			return (e.target for e in self.outgoing)
		succ = property(get_successors)
		
		def get_predecessors(self):
			return (e.origin for e in self.incoming)
		pred = property(get_predecessors)
		
		def get_successor_by_index(self, index):
			for e in self.outgoing:
				if e.index == index: return e.target
			return None
		
		def remove(self):
			for e in tuple(self.incoming): e.remove()
			for e in tuple(self.outgoing): e.remove()
			self.cfg.nodes.remove(self)
			self.cfg.entries.remove(self)
			self.cfg.exits.remove(self)
		
		def _get_outgoing(self):
			if not self._outgoing_sorted:
				# verify uniqueness of indices
				indices = set(e.index for e in self._outgoing)
				assert len(indices) == len(self._outgoing)
				
				# sort by indices
				self._outgoing.sort(lambda x, y: cmp(x.index, y.index))
				self._outgoing_sorted = True
			return self._outgoing
		
		outgoing = property(_get_outgoing)
	
	class edge(object):
		__slots__ = ('origin', 'target', 'index')
		
		def __init__(self, origin, target, index=0):
			assert index == 0 or isinstance(origin.stmt, stmts.branch_stmt)
			
			self.origin = origin
			self.target = target
			self.index = index
			origin._outgoing.append(self)
			origin._outgoing_sorted = False
			target.incoming.append(self)
		
		def __str__(self):
			return 'edge(%d)' % self.index
		
		def remove(self):
			del self.origin.cfg.edges[(self.origin, self.target)]
			self.origin.outgoing.remove(self)
			if not self.origin.outgoing:
				self.origin.cfg.exits.add(self.origin)
			self.target.incoming.remove(self)
			if not self.target.incoming:
				self.target.cfg.entries.add(self.target)
		
		def change_origin(self, new_origin):
			del self.origin.cfg.edges[(self.origin, self.target)]
			self.origin.outgoing.remove(self)
			self.origin = new_origin
			self.origin.outgoing.append(self)
			self.origin.cfg.edges[(self.origin, self.target)] = self
		
		def change_target(self, new_target):
			del self.origin.cfg.edges[(self.origin, self.target)]
			self.target.incoming.remove(self)
			self.target = new_target
			self.target.incoming.append(self)
			self.origin.cfg.edges[(self.origin, self.target)] = self
	
	def __init__(self):
		self.nodes = set()
		self.edges = {}
		self.entries = set()
		self.exits = set()
	
	def _check(self):
		for e in self.entries: assert not e.incoming
		for e in self.exits: assert not e.outgoing
		for (o,t), e in self.edges.items():
			assert e in o.outgoing
			assert e in t.incoming
		for n in self.nodes:
			if not n.incoming: assert n in self.entries
			if not n.outgoing: assert n in self.exits
			for e in n.incoming:
				assert (e.origin, e.target) in self.edges, (str(e.origin.stmt), str(e.target.stmt))
				assert e.target in self.nodes
			for e in n.outgoing:
				assert (e.origin, e.target) in self.edges
				assert e.origin in self.nodes
	
	def make_node(self, stmt):
		if isinstance(stmt, str):
			stmt = stmts.parse_stmt(stmt)
		node = self.node(self, stmt)
		self.entries.add(node)
		self.exits.add(node)
		#self._check()
		return node
	
	def make_edge(self, origin, target, index = 0):
		assert origin in self.nodes
		assert target in self.nodes
		assert (origin, target) not in self.edges
		if len(origin._outgoing) == 0:
			self.exits.remove(origin)
		if len(target.incoming) == 0:
			self.entries.remove(target)
		e = self.edge(origin, target, index)
		self.edges[(origin, target)] = e
		#self._check()
		return e
	
	def copy(self):
		other = cfg()
		other.insert_from(self)
		return other
	
	def insert_from(self, other):
		"""Insert other graph into this, and return list of nodes
		corresponding to entries/exits of inserted graph."""
		node_map = {}
		for node in other.nodes:
			node_map[node] = self.make_node(node.stmt)
		for edge in other.edges.values():
			self.make_edge(node_map[edge.origin], node_map[edge.target], edge.index)
		return [node_map[node] for node in other.entries], [node_map[node] for node in other.exits]
	
	def subgraph(self, nodes, map_nodes = ()):
		"""Generate subgraph; returns pair of created subgraph
		and list of nodes to be mapped."""
		new_cfg = cfg()
		node_map = {}
		for node in nodes:
			node_map[node] = new_cfg.make_node(node.stmt)
		for node in nodes:
			for edge in node.outgoing:
				if edge.target in nodes:
					new_cfg.make_edge(node_map[edge.origin], node_map[edge.target], edge.index)
		
		return new_cfg, [node_map[node] for node in map_nodes]
