class tarjan_state(object):
	__slots__ = (
		'maxdfs',
		'visited',
		'stack',
		'dfs',
		'lowlink',
		'clusters'
	)
	def __init__(self):
		self.maxdfs = 0
		self.visited = set()
		self.stack = []
		self.dfs = {}
		self.lowlink = {}
		self.clusters = []

def strongly_connected(cfg):
	s = tarjan_state()
	
	def process(state, node):
		state.dfs[node] = state.maxdfs
		state.lowlink[node] = state.maxdfs
		state.maxdfs += 1
		state.stack.append(node)
		state.visited.add(node)
		for e in node.outgoing:
			tgt = e.target
			if tgt not in state.visited:
				process(state, tgt)
				state.lowlink[node] = min(state.lowlink[node], state.lowlink[tgt])
			elif tgt in state.stack:
				state.lowlink[node] = min(state.lowlink[node], state.dfs[tgt])
		if state.lowlink[node] == state.dfs[node]:
			cluster = set()
			while True:
				n = state.stack.pop()
				cluster.add(n)
				if n is node: break
			if len(cluster) > 1:
				state.clusters.append(cluster)
			elif node in node.succ:
				state.clusters.append(cluster)
	
	entry, = cfg.entries
	process(s, entry)
	return s.clusters

def visit(entries, exits, handler):
	"""Visit all nodes in [entry, exit)."""
	front = set(entries)
	visited = set(exits)
	while front:
		node = front.pop()
		visited.add(node)
		handler(node)
		for n in node.succ:
			if n not in visited:
				front.add(n)

def visit_preorder(entry, exit, handler, edge_filter=(lambda e: True)):
	"""Visit all nodes  in preorder."""
	
	front = set((entry,))
	visited = set((exit,))
	while front:
		node = None
		for cand in front:
			if all(e.origin in visited for e in cand.incoming if edge_filter(e)):
				node = cand
				break
		if not node:
			break
		front.remove(node)
		visited.add(node)
		handler(node)
		for e in node.outgoing:
			if not edge_filter(e):
				continue
			if not e.target in visited:
				front.add(e.target)

def search_difference(cfg1, cfg2):
	if len(cfg1.entries) != len(cfg2.entries):
		return (cfg1.entries, cfg2.entries)
	if len(cfg1.exits) != len(cfg2.exits):
		return (cfg1.exits, cfg2.exits)
	check_pairs = set()
	for (e1, e2) in zip(cfg1.entries, cfg2.entries):
		check_pairs.add((e1, e2))
	done_nodes1 = set()
	
	while check_pairs:
		node1, node2 = check_pairs.pop()
		if node1.stmt != node2.stmt:
			return node1, node2
		outgoing1 = dict((e.index, e) for e in node1.outgoing)
		outgoing2 = dict((e.index, e) for e in node2.outgoing)
		if sorted(outgoing1.keys()) != sorted(outgoing2.keys()):
			return node1, node2
		done_nodes1.add(node1)
		for index in outgoing1.keys():
			e1 = outgoing1[index]
			e2 = outgoing2[index]
			if e1.target not in done_nodes1:
				check_pairs.add((e1.target, e2.target))
	
	if len(done_nodes1) != len(cfg1.nodes):
		return set(cfg1.nodes).symmetric_difference(cfg2.nodes2)
	if len(done_nodes1) != len(cfg2.nodes):
		return set(cfg1.nodes).symmetric_difference(cfg2.nodes)
	
	return None

def equivalent(cfg1, cfg2):
	return search_difference(cfg1, cfg2) is None

def prune(cfg):
	entry = cfg.entries[0]
	exit, = cfg.exits
	unreachable = set(cfg.nodes)
	def mark_reachable(node):
		unreachable.remove(node)
	unreachable.remove(exit)
	visit([entry], [exit], mark_reachable)
	for node in unreachable: node.remove()

def edge_dominators(cfg, e):
	"""Return pair (N, E) of node and edge sets that dominate the
	given edge (this includes the given edge)."""
	
	N = set()
	E = set((e,))
	candidate_N = set((e.target,))
	
	while candidate_N:
		n = candidate_N.pop()
		assert n not in N
		if n in N: continue
		accept = all(i in E for i in n.incoming)
		if accept:
			N.add(n)
			for o in n.outgoing:
				E.add(o)
				candidate_N.add(o.target)
	
	return N, E

def out_edges(N):
	"""Return a list of edges that originate within the given set of
	nodes, but point to a node outside this set."""
	return [edge for node in N for edge in node.outgoing if edge.target not in N]
	
def border_edges(N, E):
	"""Return pair (I, O) of edge lists that point into (I) or out of (O)
	the given set of nodes. ("where point into" means: does not originate
	in the set N of nodes; accordingly for "out of")."""
	
	I = [e for e in E if e.origin not in N]
	O = [e for e in E if e.target not in N]
	return I, O
