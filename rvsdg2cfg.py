import cfg_model
import rvsdg_model
import stmts

class ssa_mapping(object):
	__slots__ = ('_mapping', '_used')
	
	def __init__(self):
		self._mapping = {}
		self._used = set()
	
	def find_unique_name(self, name):
		# FIXME
		return name
		if name not in self._used: return name
		n = 0
		while '%s%d' % (name, n) in self._used: n += 1
		return '%s%d' % (name, n)
	
	def get_ssavar(self, def_site):
		return def_site[2]
		return self._mapping[def_site]
	
	def make_ssavar(self, def_site):
		#assert def_site not in self._mapping, (def_site, self._mapping)
		region, node, output = def_site
		if output != 'S':
			var = self.find_unique_name(output)
		else:
			var = 'S'
		self.set_ssavar(def_site, var)
		return var
	
	def set_ssavar(self, def_site, name):
		self._mapping[def_site] = name
		self._used.add(name)

def sequentialize_region_nodes(rvsdg):
	"""Return sequence of nodes consistent with dependence edges."""
	
	# FIXME: currently, rely on stored sequence of nodes to be always consistent
	# that is currently true only by accident, though
	return list(rvsdg.nodes)

class rvsdg_converter(object):
	__slots__ = (
		'cfg',
		'var_mapping',
		'rvsdg',
		'node_mapping',
		'extra_edges',
		'entry',
		'exit',
	)
	
	def __init__(self, rvsdg):
		self.rvsdg = rvsdg
		self.cfg = cfg_model.cfg()
		self.entry = self.cfg.make_node(stmts.null_stmt())
		self.exit= self.cfg.make_node(stmts.null_stmt())
		self.var_mapping = ssa_mapping()
		self.node_mapping = {}
		self.extra_edges = {}
	
	def connect_incoming(self, cfg_node, cfg_pred_edges):
		for cfg_pred_node, cfg_pred_index in cfg_pred_edges:
			self.cfg.make_edge(cfg_pred_node, cfg_node, cfg_pred_index)
	
	def maybe_assign(self, origin, target, cfg_pred_edges):
		if origin == target:
			return cfg_pred_edges
		cfg_node = self.cfg.make_node(stmts.let_stmt((target,), stmts.var_expr(origin)))
		self.connect_incoming(cfg_node, cfg_pred_edges)
		return ((cfg_node, 0),)
	
	def emit_literal_node(self, node, cfg_pred_edges):
		ress = tuple(self.var_mapping.make_ssavar((node.region, node, o)) for o in node.output_names)
		literals = [stmts.literal_expr(v) for v in node.values]
		if len(literals) > 1:
			literals = stmts.tuple_expr(literals)
		else:
			literals = literals[0]
		let_stmt = stmts.let_stmt(ress, literals)
		cfg_node = self.cfg.make_node(let_stmt)
		self.node_mapping[node] = cfg_node
		self.connect_incoming(cfg_node, cfg_pred_edges)
		return ((cfg_node, 0),)
	
	def emit_opnode(self, node, cfg_pred_edges):
		assert len(node.output_names) == len(set(node.output_names))
		args = [self.var_mapping.get_ssavar((node.region,) + o) for o in node.operands]
		ress = [self.var_mapping.make_ssavar((node.region, node, o)) for o in node.output_names]
		args = [stmts.var_expr(v) for v in args]
		rhs = stmts.call_expr(node.operator, args)
		stmt = stmts.let_stmt(ress, rhs)
		cfg_node = self.cfg.make_node(stmt)
		self.node_mapping[node] = cfg_node
		self.connect_incoming(cfg_node, cfg_pred_edges)
		return ((cfg_node, 0),)
	
	def emit_branchnode(self, node, predicate, cfg_pred_edges):
		stmt = stmts.branch_stmt(stmts.var_expr(predicate))
		cfg_node = self.cfg.make_node(stmt)
		self.node_mapping[node] = cfg_node
		self.connect_incoming(cfg_node, cfg_pred_edges)
		return cfg_node
	
	def handle_node_nopred(self, node, cfg_pred_edges):
		if isinstance(node, rvsdg_model.rvsdg.litnode):
			return self.emit_literal_node(node, cfg_pred_edges)
		elif isinstance(node, rvsdg_model.rvsdg.opnode):
			return self.emit_opnode(node, cfg_pred_edges)
		else:
			assert False
	
	def _defines_pred(self, node):
		"""Returns true if node defines a predicate."""
		return any(o[:1] == '$' for o in node.output_names)
	
	def _add_extra_edges(self, rvsdg_node, cfg_pred_edges):
		if rvsdg_node is None:
			for cfg_origin_node, cfg_origin_index in cfg_pred_edges:
				self.cfg.make_edge(cfg_origin_node, self.exit, index = cfg_origin_index)
			return
		if rvsdg_node in self.node_mapping:
			cfg_target_node = self.node_mapping[rvsdg_node]
			for cfg_origin_node, cfg_origin_index in cfg_pred_edges:
				self.cfg.make_edge(cfg_origin_node, cfg_target_node, index = cfg_origin_index)
		else:
			self.extra_edges[rvsdg_node] = self.extra_edges.get(rvsdg_node, ()) + cfg_pred_edges
	
	def _trace_successor(self, node, predicate_mapping):
		index = node.index + 1
		if index == len(node.region.nodes):
			return self._trace_outof(node.region, predicate_mapping)
		else:
			return node.region.nodes[index]
	
	def _trace_outof(self, region, predicate_mapping):
		node = region.containing_node
		if not node: return None
		if isinstance(node, rvsdg_model.rvsdg.thetanode):
			pred = (region,) + region.get_resultvalue_by_name('$repeat')
			value = predicate_mapping[pred]
			del predicate_mapping[pred]
			
			if value:
				# translate predicates on re-entry
				for pn, pv in tuple(predicate_mapping.items()):
					del predicate_mapping[pn]
					def_site = (None, pn[2])
					if region.uses(def_site):
						predicate_mapping[(region,) + def_site] = pv
				return self._trace_region_start(region, predicate_mapping)
		
		# translate predicates on exit
		for pn, pv in tuple(predicate_mapping.items()):
			del predicate_mapping[pn]
			def_site = (node, pn[2])
			if node.region.uses(def_site):
				predicate_mapping[(node.region,) + def_site] = pv
		return self._trace_successor(node, predicate_mapping)
	
	def _trace_region_start(self, region, predicate_mapping):
		# Note: expects predicates to be translated already
		if len(region.nodes):
			return region.nodes[0]
		else:
			return self._trace_outof(region, predicate_mapping)
	
	def _trace_into(self, region, predicate_mapping):
		node = region.containing_node
		for i, def_site in zip(node.input_names, node.operands):
			pred = (node.region,) + def_site
			if pred in predicate_mapping:
				value = predicate_mapping[pred]
				del predicate_mapping[pred]
				def_site = (None, def_site[1])
				if region.uses(def_site):
					predicate_mapping[(region,) + def_site] = value
		return self._trace_region_start(region, predicate_mapping)
	
	def _trace_step_node(self, node, cfg_pred_edges, predicate_mapping):
		if isinstance(node, rvsdg_model.rvsdg.litnode):
			assert not self._defines_pred(node)
			cfg_pred_edges = self.emit_literal_node(node, cfg_pred_edges)
			return self._trace_successor(node, predicate_mapping), cfg_pred_edges
		elif isinstance(node, rvsdg_model.rvsdg.opnode):
			assert not self._defines_pred(node)
			cfg_pred_edges = self.emit_opnode(node, cfg_pred_edges)
			return self._trace_successor(node, predicate_mapping), cfg_pred_edges
		elif isinstance(node, rvsdg_model.rvsdg.gammanode):
			pred = (node.region,) + node.get_predicate_operand()
			value = predicate_mapping[pred]
			del predicate_mapping[pred]
			alt = node.alternatives[value]
			return self._trace_into(alt, predicate_mapping), cfg_pred_edges
		elif isinstance(node, rvsdg_model.rvsdg.thetanode):
			return self._trace_into(node.body, predicate_mapping), cfg_pred_edges
		else:
			assert False
	
	def handle_node(self, node, cfg_pred_edges):
		cfg_pred_edges += self.extra_edges.get(node, ())
		if isinstance(node, rvsdg_model.rvsdg.litnode):
			if self._defines_pred(node):
				predicate_mapping = {}
				for o, value in zip(node.output_names, node.values):
					predicate_mapping[(node.region, node, o)] = value
				tgt = self._trace_successor(node, predicate_mapping)
				while tgt and predicate_mapping:
					tgt, cfg_pred_edges = self._trace_step_node(tgt, cfg_pred_edges, predicate_mapping)
				self._add_extra_edges(tgt, cfg_pred_edges)
				return ()
			else:
				return self.emit_literal_node(node, cfg_pred_edges)
		elif isinstance(node, rvsdg_model.rvsdg.selectnode):
			if self._defines_pred(node):
				pred = (node.region,) + node.get_selector_operand()
				pred = self.var_mapping.get_ssavar(pred)
				cfg_branch_node = self.emit_branchnode(node, pred, cfg_pred_edges)
				for index in range(len(node.alternatives)):
					alt_values = node.alternatives[index]
					predicate_mapping = {}
					for o, value in zip(node.output_names, alt_values):
						predicate_mapping[(node.region, node, o)] = value
					tgt = self._trace_successor(node, predicate_mapping)
					cfg_pred_edges = (cfg_branch_node, index),
					while tgt and predicate_mapping:
						tgt, cfg_pred_edges = self._trace_step_node(tgt, cfg_pred_edges, predicate_mapping)
					self._add_extra_edges(tgt, cfg_pred_edges)
				return ()
			else:
				assert False
				# FIXME: implement emitting of select node
				return self.emit_opnode(node, cfg_pred_edges)
		elif isinstance(node, rvsdg_model.rvsdg.opnode):
			if False and self._defines_pred(node):
				assert False
			else:
				return self.emit_opnode(node, cfg_pred_edges)
		elif isinstance(node, rvsdg_model.rvsdg.gammanode):
			resulting_edges = ()
			resulting_edge_lists = []
			for alternative in node.alternatives:
				for i, op in zip(node.input_names, node.operands):
					self.var_mapping.set_ssavar((alternative, None, i), self.var_mapping.get_ssavar((node.region,) + op))
				resulting_edge_lists.append(self.handle_region(alternative, ()))
			resulting_edges = tuple(e for sl in resulting_edge_lists for e in sl)
			for o in node.output_names:
				self.var_mapping.set_ssavar((node.region, node, o), o)
			return resulting_edges
		elif isinstance(node, rvsdg_model.rvsdg.thetanode):
			body = node.body
			for i, op in zip(node.input_names, node.operands):
				self.var_mapping.set_ssavar((body, None, i), self.var_mapping.get_ssavar((node.region,) + op))
			resulting_edges = self.handle_region(body, cfg_pred_edges)
			for o in node.output_names:
				self.var_mapping.set_ssavar((node.region, node, o), o)
			return resulting_edges
		else:
			assert False
	
	def handle_region(self, region, cfg_pred_edges):
		for cfg_node in sequentialize_region_nodes(region):
			cfg_pred_edges = self.handle_node(cfg_node, cfg_pred_edges)
		return cfg_pred_edges
	
	def convert(self):
		for arg in self.rvsdg.arguments:
			self.var_mapping.set_ssavar((self.rvsdg, None, arg), arg)
		cfg_pred_edges = self.handle_region(self.rvsdg, ((self.entry, 0),))
		for result, result_value in zip(self.rvsdg.results, self.rvsdg.result_values):
			cfg_pred_edges = self.maybe_assign(self.var_mapping.get_ssavar((self.rvsdg,) + result_value), result, cfg_pred_edges)
		self.connect_incoming(self.exit, cfg_pred_edges)
		
		return self.cfg
	
	def _handle_region_naive(self, region, cfg_pred_edges):
		for cfg_node in sequentialize_region_nodes(region):
			cfg_pred_edges = self.handle_node_nopred(cfg_node, cfg_pred_edges)
		return cfg_pred_edges
	
	def _convert_naive(self):
		for arg in self.rvsdg.arguments:
			self.var_mapping.set_ssavar((self.rvsdg, None, arg), arg)
		cfg_pred_edges = self._handle_region_naive(self.rvsdg, ((self.entry, 0),))
		for result, result_value in zip(self.rvsdg.results, self.rvsdg.result_values):
			cfg_pred_edges = self.maybe_assign(self.var_mapping.get_ssavar((self.rvsdg,) + result_value), result, cfg_pred_edges)
		self.connect_incoming(self.exit, cfg_pred_edges)
		return self.cfg

def _convert_naive(rvsdg):
	# only useful for generating some graphs for the paper
	converter = rvsdg_converter(rvsdg)
	return converter._convert_naive()

def convert(rvsdg):
	converter = rvsdg_converter(rvsdg)
	return converter.convert()
