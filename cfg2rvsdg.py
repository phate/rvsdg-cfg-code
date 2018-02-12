import itertools
import operator

import cfg2cfg
import cfg_algorithm
import cfg_model
import rvsdg_model
import stmts
import cfg_view

artificial_loop_entry_mux = 0
artificial_loop_exit_mux = 0
artificial_loop_repeat = 0
artificial_loop_letqs = 0
artificial_loop_letqrs = 0
artificial_loop_letrs = 0

def process_let_stmt(rvsdg_region, var_mapping, stmt):
	e = stmt.expr
	if isinstance(e, stmts.tuple_expr):
		assert all(isinstance(v, stmts.literal_expr) for v in e.items)
		values = [v.value for v in e.items]
		assert len(stmt.vars) == len(values)
		node = rvsdg_region.add_litnode(values, stmt.vars)
	elif isinstance(e, stmts.literal_expr):
		name = stmt.vars[0]
		node = rvsdg_region.add_litnode((e.value,), (name,))
	elif isinstance(e, stmts.call_expr):
		assert all(isinstance(v, stmts.var_expr) for v in e.operands)
		opnames = [v.var for v in e.operands]
		ops = [var_mapping[op] for op in opnames]
		node = rvsdg_region.add_opnode(e.fn, opnames, stmt.vars, ops)
	elif isinstance(e, stmts.rvsdg_loop_expr):
		ops = [var_mapping[op.var] for op in e.operands]
		node = rvsdg_region.add_theta(e.region, ops)
	else:
		assert False
	for name in stmt.vars:
		var_mapping[name] = (node, name)
	
	return rvsdg_region, var_mapping

def _splice_off_cfg(cfg, entry, exit):
	new_cfg = cfg_model.cfg()
	
	assert not entry.incoming
	assert not exit.outgoing
	
	nodes = set([exit])
	def transfer(node):
		nodes.add(node)
	cfg_algorithm.visit([entry], [exit], transfer)
	
	for node in nodes:
		node.cfg = new_cfg
		cfg.nodes.remove(node)
		new_cfg.nodes.add(node)
		assert (e.origin in nodes for e in node.incoming)
		assert (e.target in nodes for e in node.outgoing)
		for e in node.outgoing:
			assert e.target in nodes
			del cfg.edges[(e.origin, e.target)]
			new_cfg.edges[(e.origin, e.target)] = e
	
	cfg.entries.remove(entry)
	new_cfg.entries.add(entry)
	cfg.exits.remove(exit)
	new_cfg.exits.add(exit)
	
	#cfg._check()
	#new_cfg._check()
	return new_cfg

def _convert_loop_cluster(cfg, cluster, vars):
	"""Convert loop to single-entry/single-exit."""
	
	assert len(cfg.entries) == 1
	assert len(cfg.exits) == 1
	
	# Filter out predicates; that's a bit hackish, but whatever
	vars = tuple([v for v in vars if v[0] != '$'])
	
	loop_repeat_pred = '$repeat'
	loop_cross_pred = '$demux'
	
	entry_edges = set(itertools.chain(*((e for e in n.incoming if e.origin not in cluster) for n in cluster)))
	exit_edges = set(itertools.chain(*((e for e in n.outgoing if e.target not in cluster) for n in cluster)))
	
	exits = set(e.target for e in exit_edges)
	entries = set(e.target for e in entry_edges)
	for e in exit_edges: e.remove()
	for e in entry_edges: e.remove()
	
	entries_ordered = tuple(entries)
	entry_index_map = dict(zip(entries_ordered, range(len(entries_ordered))))
	
	exits_ordered = tuple(exits)
	exit_index_map = dict(zip(exits_ordered, range(len(exits_ordered))))
	
	# build inner graph
	
	global artificial_loop_entry_mux
	global artificial_loop_exit_mux
	global artificial_loop_repeat
	global artificial_loop_letqrs
	global artificial_loop_letqs
	global artificial_loop_letrs
	
	# create loop head, demux to real entry points
	loop_stmt = stmts.branch_stmt(stmts.var_expr(loop_cross_pred))
	loop_head = cfg.make_node(loop_stmt)
	if len(entries) > 1:
		artificial_loop_exit_mux += 1
	for node, index in entry_index_map.items():
		cfg.make_edge(loop_head, node, index)
	
	# create loop tail and set/clear loop repetition predicate
	loop_tail = cfg.make_node('null')
	# note: exit node accounted below
	
	exit_aux_lets = 0
	
	# divert exit edges to setting the crossing predicate and exiting from loop
	for e in exit_edges:
		origin, target, index = e.origin, e.target, e.index
		let_stmt = stmts.let_stmt((loop_repeat_pred, loop_cross_pred),
			stmts.tuple_expr((
				stmts.literal_expr(0),
				stmts.literal_expr(exit_index_map[target])
			))
		)
		s = cfg.make_node(let_stmt)
		exit_aux_lets += 1
		cfg.make_edge(origin, s, index)
		cfg.make_edge(s, loop_tail)
	
	repeat_aux_lets = 0
	
	nrepetition_edges = 0
	# divert repetition edges to setting the crossing predicate and repeating the loop
	for entry in entries:
		# do nothing if no outgoing edges remain
		if all(e.target not in cluster for e in entry.outgoing):
			continue
		for e in tuple(entry.incoming):
			if e.origin not in cluster: continue
			e.remove()
			nrepetition_edges += 1
			origin, target, index = e.origin, e.target, e.index
			let_stmt = stmts.let_stmt((loop_repeat_pred, loop_cross_pred),
				stmts.tuple_expr((
					stmts.literal_expr(1),
					stmts.literal_expr(entry_index_map[target])
				))
			)
			s = cfg.make_node(let_stmt)
			repeat_aux_lets += 1
			cfg.make_edge(origin, s, index)
			cfg.make_edge(s, loop_tail)
	if nrepetition_edges > 1 or len(entries) > 1 or len(exits) > 1:
		artificial_loop_repeat += 1
	if nrepetition_edges:
		if len(entries) > 1:
			artificial_loop_letqrs += repeat_aux_lets
		else:
			artificial_loop_letrs += repeat_aux_lets
		if len(exits) > 1:
			artificial_loop_letqrs += exit_aux_lets
		else:
			artificial_loop_letrs += exit_aux_lets
	else:
		if len(entries) > 1:
			artificial_loop_letqs += repeat_aux_lets
		if len(exits) > 1:
			artificial_loop_letqs += exit_aux_lets
	
	# inner graph now between loop_head and loop_tail, convert it
	# to rvsdg region, and build stmt
	
	inner_cfg = _splice_off_cfg(cfg, loop_head, loop_tail)
	
	argvars = vars + (loop_cross_pred,)
	resvars = argvars + (loop_repeat_pred,)
	resnames = argvars + ('$repeat',)
	assert len(inner_cfg.entries) == 1, len(inner_cfg.exits) == 1
	inner_rvsdg = _convert(inner_cfg, argvars, resvars, resnames)
	loop_expr = stmts.rvsdg_loop_expr(inner_rvsdg, 'loop',
		tuple(stmts.var_expr(v) for v in vars + (loop_cross_pred,)))
	loop_stmt = stmts.let_stmt(vars + (loop_cross_pred,), loop_expr)
	
	# build outer graph
	loop_node = cfg.make_node(loop_stmt)
	exit_demux = cfg.make_node(stmts.branch_stmt(stmts.var_expr(loop_cross_pred)))
	if len(exits) > 1:
		artificial_loop_exit_mux += 1
	cfg.make_edge(loop_node, exit_demux)
	
	for e in entry_edges:
		origin, target, index = e.origin, e.target, e.index
		let_stmt = stmts.let_stmt(
			(loop_cross_pred,),
			stmts.literal_expr(entry_index_map[target])
		)
		s = cfg.make_node(let_stmt)
		if len(entries) > 1:
			artificial_loop_letqs += 1
		cfg.make_edge(origin, s, index)
		cfg.make_edge(s, loop_node)
	
	for node, index in exit_index_map.items():
		cfg.make_edge(exit_demux, node, index)
	
	#cfg._check()

def regularize_cfg_acyclic_region(cfg, vars):
	rvsdg_region = rvsdg_model.rvsdg(vars)
	var_mapping = dict((v, (None, v)) for v in vars)
	regularize_cfg_acyclic(cfg, rvsdg_region, var_mapping)
	return rvsdg_region, var_mapping

def regularize_cfg_acyclic(cfg, rvsdg_region, var_mapping):
	head, branch_cfgs, tail = cfg2cfg.acyclic_cfg_branch_xformed_partition(cfg, True, mangle_cfg=True)
	
	node, = head.entries
	
	branch_predicate = None
	
	while True:
		stmt = node.stmt
		if isinstance(stmt, stmts.let_stmt):
			rvsdg_region, var_mapping = process_let_stmt(rvsdg_region, var_mapping, stmt)
		elif isinstance(stmt, stmts.branch_stmt):
			predicate_var = stmt.expr.var
			branch_predicate = var_mapping[predicate_var]
			if not predicate_var.startswith('$'):
				sn = rvsdg_region.add_selectnode(
					[(n,) for n in range(len(branch_cfgs))],
					predicate_var,
					('$p',),
					branch_predicate)
				branch_predicate = (sn, '$p')
				# due to the structure of our test graphs,
				# we know that the predicate variable will
				# not be reused; we can safely delete it
				del var_mapping[predicate_var]
			else:
				del var_mapping[predicate_var]
		
		if node.outgoing:
			branch_predicate = None
			edge, = node.outgoing
			node = edge.target
		else:
			break
	if not branch_predicate:
		return
	
	assert tail
	assert branch_cfgs
	
	var_names = sorted(var_mapping.keys())
	assert len(var_names) < 30, var_names
	branches = [(edge_index,) + regularize_cfg_acyclic_region(sub_cfg, var_names) for edge_index, sub_cfg in branch_cfgs]
	branches.sort()
	# FIXME: add assertion that all intermediate values are covered
	
	common_vars = reduce(operator.and_, (set(sub_var_mapping.keys()) for _, _, sub_var_mapping in branches))
	assert common_vars
	assert len(common_vars) < 30, common_vars
	
	for index, sub_rvsdg_region, sub_var_mapping in branches:
		for var in common_vars:
			sub_rvsdg_region.add_result(var, sub_var_mapping[var])
	
	gamma = rvsdg_region.add_gamma(
		[sub_rvsdg_region for _, sub_rvsdg_region, _ in branches], 
		[var_mapping[var] for var in var_names],
		branch_predicate)
	for var in common_vars:
		var_mapping[var] = (gamma, var)
	
	return regularize_cfg_acyclic(tail, rvsdg_region, var_mapping)

def _convert_no_loops(cfg, argvars, resvars, resnames):
	rvsdg_region, var_mapping = regularize_cfg_acyclic_region(cfg, argvars)
	for var, name in zip(resvars, resnames):
		rvsdg_region.add_result(name, var_mapping[var])
	return rvsdg_region

def _convert_only_loops(cfg, vars):
	assert len(cfg.entries) == 1
	clusters = cfg_algorithm.strongly_connected(cfg)
	for cluster in clusters:
		_convert_loop_cluster(cfg, cluster, vars)
	#assert not cfg_algorithm.strongly_connected(cfg)

def _convert(cfg, argvars, resvars, resnames):
	assert len(cfg.entries) == 1, cfg.entries
	assert len(argvars) == len(set(argvars)), argvars
	_convert_only_loops(cfg, argvars)
	return _convert_no_loops(cfg, argvars, resvars, resnames)

def convert(cfg, argvars = ('P',), resvars = ('P',), resnames = ('P',)):
	global _cfg
	_cfg = cfg
	rvsdg = _convert(cfg, argvars, resvars, resnames)
	return rvsdg
