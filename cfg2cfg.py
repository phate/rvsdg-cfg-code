import operator

import cfg_algorithm
import cfg_model
import stmts

artificial_branches = 0
artificial_branchjoin_nulls = 0
artificial_branch_letps = 0

def _stmt_used_predicate(stmt):
	if isinstance(stmt, stmts.let_stmt):
		for v in stmt.expr.variables():
			if v.startswith('$'): return v
	elif isinstance(stmt, stmts.branch_stmt):
		for v in stmt.expr.variables():
			if v.startswith('$'): return v
	return None

def _stmt_is_predicate_use(stmt):
	return _stmt_used_predicate(stmt) is not None

def _stmt_is_predicate_assignment(stmt):
	if isinstance(stmt, stmts.let_stmt):
		return any(v.startswith('$') for v in stmt.vars)
	else:
		return False

def _unwind_predicate_assignments(N, except_for_node = None):
	new_N = set()
	for node in N:
		if all(edge.target in N for edge in node.outgoing):
			new_N.add(node)
		elif all(edge.target is except_for_node for edge in node.outgoing):
			new_N.add(node)
		elif not _stmt_is_predicate_assignment(node.stmt):
			new_N.add(node)

	return new_N

def edge_tuple(edge):
	return (edge.origin, edge.index, edge.target)

def acyclic_cfg_branch_partition(cfg, mangle_cfg=False):
	"""Partition a cfg into "branching" components as described below.

	Returns a tuple (r, [(i_k,N_k,O_k), ...], N_R), where

	- r is the root node (unique entry point) to the cfg
	- i_k are the out-edges from the root node
	- N_k are the vertices of the dominator subgraph of
	  i_k, subject to the "predicate constraint" below
	- N_R are the vertices of the remainder subgraph
	- O_k are the edges from the subgraph N_k to N_R
	
	With N the vertices of the full graph, the following
	holds:
	
	N = {r} + N_1 + N_2 + ... + N_R
	
	If the given graph consists of a single node, then there will be
	zero branches.
	
	"predicate constraint": if any of the N_k contain a predicate
	assignment as the "last" node in any branch, then all branches of all
	(N_k, E_k) must contain such an assignment
	
	At least one of the N_k is guaranteed to be non-empty.
	
	Note that if mangle_cfg=True, then the tail nodeset will not
	be computed.
	"""
	assert len(cfg.entries) == 1 and len(cfg.exits) == 1
	
	# find first branch (or exit) node, starting from entry into cfg
	branch_node, = cfg.entries
	head_nodeset = set()
	while True:
		head_nodeset.add(branch_node)
		if len(branch_node.outgoing) != 1:
			break
		edge, = branch_node.outgoing
		branch_node = edge.target
	
	# determine all branch subgraphs, their nodes and outgoing edges
	root_out_edges = list(branch_node.outgoing)
	branch_graphs = tuple(cfg_algorithm.edge_dominators(cfg, edge)[0] for edge in root_out_edges)
	
	# check for predicate consistency -- first determine all 'out' edges
	all_branch_nodes = reduce(operator.or_, (set(g) for g in branch_graphs), set())
	all_branch_out_edges = tuple(edge for node in (all_branch_nodes|set((branch_node,))) for edge in node.outgoing if edge.target not in all_branch_nodes)
	all_continuations = set(edge.target for edge in all_branch_out_edges)
	
	# check all continuation points; it must be ensured that either all
	# or none of the predicate-defining predecessors are in the branch_graphs
	for node in all_continuations:
		is_predicate_successor = any(_stmt_is_predicate_assignment(edge.origin.stmt) for edge in node.incoming)
		if not is_predicate_successor: continue
		all_in_branch_subgraphs = all(edge.origin in all_branch_nodes for edge in node.incoming)
		if all_in_branch_subgraphs: continue
		preds = set(edge.origin for edge in node.incoming)
		branch_graphs = tuple(g - preds for g in branch_graphs)
	
	# determine if any successor node uses a predicate defined immediately
	# before
	predicate_use_target = None
	for edge in all_branch_out_edges:
		if _stmt_is_predicate_use(edge.target.stmt):
			predicate_use_target = edge.target
			break
	
	# determine exit edges from all branch subgraphs
	branch_exit_edges = [
		[edge_tuple(e) for e in cfg_algorithm.out_edges(g)] if g else [edge_tuple(edge)]
		for g, edge in zip(branch_graphs, root_out_edges) ]
	
	# determine nodes of tail graph
	if mangle_cfg:
		tail_nodeset = ()
	else:
		tail_nodeset = reduce(operator.sub, (g for g in branch_graphs), set(cfg.nodes))
		tail_nodeset -= head_nodeset
	
	return head_nodeset, zip(root_out_edges, branch_graphs, branch_exit_edges), tail_nodeset

mangle_cfg = False

def _splice_off_cfg(cfg, nodes):
	new_cfg = cfg_model.cfg()
	
	for node in nodes:
		for e in tuple(node.incoming):
			if e.origin not in nodes:
				e.remove()
		for e in tuple(node.outgoing):
			if e.target not in nodes:
				e.remove()
		
		if not node.incoming:
			cfg.entries.remove(node)
			new_cfg.entries.add(node)
		
		if not node.outgoing:
			cfg.exits.remove(node)
			new_cfg.exits.add(node)
		
		node.cfg = new_cfg
		cfg.nodes.remove(node)
		new_cfg.nodes.add(node)
		
		for e in node.outgoing:
			assert e.target in nodes
			del cfg.edges[(e.origin, e.target)]
			new_cfg.edges[(e.origin, e.target)] = e
	
	#cfg._check()
	#new_cfg._check()
	return new_cfg

def acyclic_cfg_branch_xformed_partition(cfg, insert_dummy_predicate_assignments=False, mangle_cfg=False):
	#assert len(cfg.entries) == 1 and len(cfg.exits) == 1
	
	head_nodeset, branches, tail_nodeset = acyclic_cfg_branch_partition(cfg, mangle_cfg)
	
	if mangle_cfg:
		_splice_off_cfg(cfg, head_nodeset)
	
	global artificial_branch_letps
	global artificial_branchjoin_nulls
	global artificial_branches
	
	orig_tail_cont = list(set((edge[2] for branch in branches for edge in branch[2])))
	dont_rebranch = len(orig_tail_cont) <= 1
	
	# determine if any successor node uses a predicate defined immediately
	# before
	predicate_def = None
	for node in orig_tail_cont:
		predicate_def = _stmt_used_predicate(node.stmt)
		if predicate_def:
			break
		if _stmt_is_predicate_use(node.stmt):
			predicate_use_target = node
			break
	
	#assert all(node in tail_nodeset for node in orig_tail_cont)
	if mangle_cfg:
		tail, tail_cont = cfg, orig_tail_cont
	else:
		tail, tail_cont = cfg.subgraph(tail_nodeset, orig_tail_cont)
	if len(tail_cont) > 1:
		rebranch = tail.make_node(stmts.branch_stmt(stmts.var_expr('$p')))
		artificial_branches += 1
		for n in range(len(tail_cont)):
			tail.make_edge(rebranch, tail_cont[n], n)
	
	xformed_branches = []
	for ik, Nk, Ok in branches:
		if Nk:
			if mangle_cfg:
				sub_cfg = _splice_off_cfg(cfg, Nk)
				exits = [edge[0] for edge in Ok]
			else:
				sub_cfg, exits = cfg.subgraph(Nk, [edge[0] for edge in Ok])
			Xk = []
			exit_nodes = []
			for (old_edge, node) in zip(Ok, exits):
				edge_index = old_edge[1]
				tgt_index = orig_tail_cont.index(old_edge[2])
				if insert_dummy_predicate_assignments and predicate_def and not _stmt_is_predicate_assignment(node.stmt):
					let_node = sub_cfg.make_node(stmts.let_stmt((predicate_def,), stmts.parse_expr('-1')))
					sub_cfg.make_edge(node, let_node, edge_index)
					node = let_node
					edge_index = 0
				if not dont_rebranch:
					expr = stmts.parse_expr('%d' % tgt_index)
					if _stmt_is_predicate_assignment(node.stmt):
						let_node = sub_cfg.make_node(stmts.let_stmt(('$p',) + node.stmt.vars, stmts.tuple_expr((expr, node.stmt.expr))))
						artificial_branch_letps += 1
						if node.incoming:
							edge, = node.incoming
							idx = edge.index
							origin = edge.origin
							edge.remove()
							sub_cfg.make_edge(origin, let_node, idx)
						node.remove()
					else:
						let_node = sub_cfg.make_node(stmts.let_stmt(('$p',), expr))
						artificial_branch_letps += 1
						sub_cfg.make_edge(node, let_node, edge_index)
					node = let_node
					edge_index = 0
				Xk.append((node, edge_index))
			
			if len(Xk) != 1:
				join_node = sub_cfg.make_node(stmts.null_stmt())
				artificial_branchjoin_nulls += 1
				for node, index in Xk:
					sub_cfg.make_edge(node, join_node, index)
		else:
			tgt_index = orig_tail_cont.index(ik.target)
			sub_cfg = cfg_model.cfg()
			if dont_rebranch:
				if insert_dummy_predicate_assignments and predicate_def:
					sub_cfg.make_node(stmts.let_stmt((predicate_def,), stmts.parse_expr('-1')))
				else:
					sub_cfg.make_node(stmts.null_stmt())
			else:
				artificial_branch_letps += 1
				if insert_dummy_predicate_assignments and predicate_def:
					sub_cfg.make_node(stmts.let_stmt(('$p', predicate_def,), stmts.parse_expr('%d, -1' % tgt_index)))
				else:
					sub_cfg.make_node(stmts.let_stmt(('$p',), stmts.parse_expr('%d' % tgt_index)))
		
		xformed_branches.append((ik.index, sub_cfg))
	
	nbranches = len(branches)
	if nbranches == 0:
		assert not tail.nodes
		assert not xformed_branches
	elif nbranches == 1:
		assert not tail.nodes
	else:
		assert tail.nodes
	
	head = cfg.subgraph(head_nodeset)[0]
	return head, xformed_branches, tail

def regularize_cfg_acyclic(cfg, insert_dummy_predicate_assignments=False):
	head, branch_cfgs, tail = acyclic_cfg_branch_xformed_partition(cfg, insert_dummy_predicate_assignments)
	
	new_cfg = cfg_model.cfg()
	
	_, (head_exit,) = new_cfg.insert_from(head)
	if tail.nodes:
		(tail_entry,), _ = new_cfg.insert_from(regularize_cfg_acyclic(tail, insert_dummy_predicate_assignments))
	else:
		tail_entry = None
	for branch_index, branch_cfg in branch_cfgs:
		(branch_entry,), (branch_exit,), = new_cfg.insert_from(regularize_cfg_acyclic(branch_cfg, insert_dummy_predicate_assignments))
		new_cfg.make_edge(head_exit, branch_entry, branch_index)
		if tail_entry:
			new_cfg.make_edge(branch_exit, tail_entry)
	
	return new_cfg
