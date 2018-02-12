class rvsdg(object):
	__slots__ = (
		'arguments',
		'results',
		'result_values',
		'nodes',
		'containing_node',
	)
	
	class node(object):
		__slots__ = (
			'region',
			'input_names',
			'output_names',
			'operands',
			'index',
		)
		def __init__(self, input_names, output_names, operands):
			assert len(input_names) == len(set(input_names)), input_names
			assert len(output_names) == len(set(output_names)), output_names
			self.region = None
			self.input_names = tuple(input_names)
			self.output_names = tuple(output_names)
			self.operands = tuple(operands)
		
		def remove_input(self, name):
			index = self.input_names.index(name)
			self.input_names = self.input_names[:index] + self.input_names[index + 1:]
			self.operands = self.operands[:index] + self.operands[index + 1:]
		
		def remove_output(self, name):
			index = self.output_names.index(name)
			self.output_names = self.output_names[:index] + self.output_names[index + 1:]
		
		def divert_input(self, name, new_operand):
			index = self.input_names.index(name)
			assert (new_operand[0] is None or self.region.index(new_operand[0]) < self.region.index(self))
			self.operands = self.operands[:index] + (new_operand,) + self.operands[index + 1:]
		
		def get_operand_by_name(self, name):
			for input_name, operand in zip(self.input_names, self.operands):
				if name == input_name: return operand
		
		def try_remove_invariant(self, output_name): abstract
		def normalize(self, unused_outputs): abstract
		def uses(self, def_site):
			return any(o == def_site for o in self.operands)
		def get_use_sites(self, def_size):
			return tuple((self, i) for i, o in zip(self.input_names, self.operands) if o == def_site)
		def is_equivalent(self, other): abstract
		def node_count(self): abstract
		def gamma_count(self): abstract
		def theta_count(self): abstract
		def maximum_depth(self): abstract
	
	class opnode(node):
		__slots__ = (
			'operator',
		)
		def __init__(self, operator, input_names, output_names, operands):
			rvsdg.node.__init__(self, input_names, output_names, operands)
			self.operator = operator
		
		def try_remove_invariant(self, output_name): return None
		def normalize(self, unused_outputs): pass
		def is_equivalent(self, other):
			return (
				self.__class__ is other.__class__ and
				self.operator == other.operator and
				self.input_names == other.input_names and
				self.output_names == other.output_names)
		def node_count(self): return 1
		def gamma_count(self): return 0
		def theta_count(self): return 0
		def maximum_depth(self): return 0
	
	class selectnode(opnode):
		__slots__ = (
			'alternatives',
		)
		def __init__(self, alternatives, input_name, output_names, operand):
			rvsdg.opnode.__init__(self, 'select', (input_name,), output_names, (operand,))
			assert all(len(alt) == len(output_names) for alt in alternatives)
			self.alternatives = tuple(tuple(alt) for alt in alternatives)
		
		def get_selector_operand(self):
			return self.operands[0]
		def node_count(self): return 1
		def gamma_count(self): return 0
		def theta_count(self): return 0
		def maximum_depth(self): return 0
	
	class litnode(node):
		__slots__ = (
			'values',
		)
		def __init__(self, values, output_names):
			rvsdg.node.__init__(self, (), output_names, ())
			self.values = tuple(values)
		
		def try_remove_invariant(self, output_name): return None
		def normalize(self, unused_outputs): pass
		def is_equivalent(self, other):
			return (
				self.__class__ is other.__class__ and
				self.values == other.values and
				self.output_names == other.output_names)
		def node_count(self): return 1
		def gamma_count(self): return 0
		def theta_count(self): return 0
		def maximum_depth(self): return 0
	
	class gammanode(node):
		__slots__ = (
			'alternatives',
		)
		def __init__(self, alternatives, operands, predicate):
			input_names = list(alternatives[0].arguments)
			assert len(input_names) == len(operands)
			assert all(a.arguments == input_names for a in alternatives)
			
			output_names = list(alternatives[0].results)
			assert all(a.results == output_names for a in alternatives)
			input_names.append('$pred')
			operands = list(operands) + [predicate]
			rvsdg.node.__init__(self, input_names, output_names, operands)
			self.alternatives = alternatives
			for a in alternatives:
				assert a.containing_node is None
				a.containing_node = self
		
		def try_remove_invariant(self, name):
			if all(a.is_passthrough(name, name) for a in self.alternatives):
				v = self.get_operand_by_name(name)
				for a in self.alternatives:
					a.remove_passthrough(name, name)
				self.remove_input(name)
				self.remove_output(name)
				return v
			return None
		
		def mark_output_unused(self, output_name):
			index = self.output_names.index(output_name)
			self.output_names = self.output_names[:index] + self.output_names[index + 1:]
			for a in self.alternatives:
				del a.results[index]
				del a.result_values[index]
			
		def normalize(self, unused_outputs):
			for o in unused_outputs:
				self.mark_output_unused(o)
			for a in self.alternatives:
				a.normalize()
			for i in tuple(self.input_names[:-1]):
				if any(a.uses((None, i)) for a in self.alternatives): continue
				index = self.input_names.index(i)
				self.input_names = self.input_names[:index] + self.input_names[index + 1:]
				self.operands = self.operands[:index] + self.operands[index + 1:]
				for a in self.alternatives:
					del a.arguments[index]
		
		def is_equivalent(self, other):
			return (
				self.__class__ is other.__class__ and
				len(self.alternatives) == len(other.alternatives) and
				all(a1.is_equivalent(a2) for a1, a2 in zip(self.alternatives, other.alternatives)))
		
		def get_predicate_operand(self):
			return self.get_operand_by_name('$pred')
		
		def node_count(self):
			count = 0
			for alt in self.alternatives: count += alt.node_count()
			return count
		def gamma_count(self):
			count = 1
			for alt in self.alternatives: count += alt.gamma_count()
			return count
		def theta_count(self):
			count = 0
			for alt in self.alternatives: count += alt.theta_count()
			return count
		def maximum_depth(self):
			depth = 0
			for alt in self.alternatives: depth = max(depth, alt.maximum_depth())
			return depth
	
	class thetanode(node):
		__slots__ = (
			'body',
		)
		def __init__(self, body, operands):
			assert body.arguments == body.results[:-1]
			assert body.results[-1] == '$repeat'
			args = list(body.arguments)
			ress = list(body.arguments)
			rvsdg.node.__init__(self, args, ress, operands)
			self.body = body
			assert body.containing_node is None
			body.containing_node = self
		
		def try_remove_invariant(self, name):
			if self.body.is_passthrough(name, name):
				v = self.get_operand_by_name(name)
				self.body.remove_passthrough(name, name)
				self.remove_input(name)
				self.remove_output(name)
				return v
			return None
		
		def mark_output_unused(self, output_name):
			if output_name not in self.output_names: return
			if self.body.uses((None, output_name)): return
			index = self.output_names.index(output_name)
			del self.body.arguments[index]
			del self.body.results[index]
			del self.body.result_values[index]
			self.input_names = self.input_names[:index] + self.input_names[index + 1:]
			self.operands = self.operands[:index] + self.operands[index + 1:]
			self.output_names = self.output_names[:index] + self.output_names[index + 1:]
		
		def normalize(self, unused_outputs):
			for o in unused_outputs:
				self.mark_output_unused(o)
			self.body.normalize()
			for o in unused_outputs:
				self.mark_output_unused(o)
			# FIXME: we have a chicken-and-egg problem here if
			# loops are nested: we cannot remove a redundant
			# input/output pair of a loop unless we first
			# eliminate its uses *inside* and its uses *outside*;
			# this means that for nested loops, a redundant
			# var can only be removed in the inner if it is
			# removed in the outer first, and it can only be
			# removed in the outer when it is removed in the inner
			# first.
			# There are three possible solutions for breaking this
			# cycle:
			# - allow output-only vars in theta regions
			# - propgate thet 'output unused' information into
			#   the region and maybe let it somehow be 'confirmed'
			#   inside
			# - for all unused inputs into a loop, substitute their
			#   operand with an 'undefined' literal node in the
			#   parent so the cycle can be broken in the parent
			# The second call to mark unused outputs is a hack
			# that covers some, but not all of the cases
		
		def node_count(self):
			return self.body.node_count()
		def gamma_count(self):
			return self.body.gamma_count()
		def theta_count(self):
			return 1 + self.body.theta_count()
		def maximum_depth(self):
			return self.body.maximum_depth()
	
	def __init__(self, arguments):
		self.arguments = list(arguments)
		self.results = []
		self.result_values = []
		self.nodes = []
		self.containing_node = None
	
	def add_result(self, name, value):
		assert name not in self.results
		assert (value[0] is None and value[1] in self.arguments) or \
			(value[0].region is self and value[1] in value[0].output_names)
		self.results.append(name)
		self.result_values.append(value)
	
	def _add_node(self, node, before = None):
		if before:
			index = self.nodes.index(before)
		else:
			index = len(self.nodes)
		for op in node.operands:
			assert (
				(op[0] is None and op[1] in self.arguments) or
				(op[0] in self.nodes and op[1] in op[0].output_names)
			), op
			assert (op[0] is None or self.nodes.index(op[0]) < index)
		self.nodes.insert(index, node)
		node.region = self
		for n in range(index, len(self.nodes)):
			self.nodes[n].index = n
		return node
	
	def add_opnode(self, operator, input_names, output_names, operands, before = None):
		node = self.opnode(operator, input_names, output_names, operands)
		return self._add_node(node, before)
	
	def add_litnode(self, values, output_names, before = None):
		node = self.litnode(values, output_names)
		return self._add_node(node, before)
	
	def add_selectnode(self, alternatives, input_name, output_names, operand, before = None):
		node = self.selectnode(alternatives, input_name, output_names, operand)
		return self._add_node(node, before)
	
	def add_theta(self,  body, operands, before = None):
		node = self.thetanode(body, operands)
		return self._add_node(node, before)
	
	def add_gamma(self, alternatives, operands, predicate, before = None):
		node = self.gammanode(alternatives, operands, predicate)
		return self._add_node(node, before)
	
	def is_passthrough(self, argument_name, result_name):
		v = self.get_resultvalue_by_name(result_name)
		if any(n.uses((None, argument_name)) for n in self.nodes):
			return False
		return v == (None, argument_name)
	
	def remove_passthrough(self, argument_name, result_name):
		assert self.is_passthrough(argument_name, result_name)
		index = self.results.index(result_name)
		del self.results[index]
		del self.result_values[index]
		index = self.arguments.index(argument_name)
		del self.arguments[index]
	
	def get_resultvalue_by_name(self, name):
		for result, value in zip(self.results, self.result_values):
			if result == name: return value
		return None
	
	def normalize(self):
		use_map = {}
		for res, resval in zip(self.results, self.result_values):
			use = use_map.get(resval, [])
			use.append((None, res))
			use_map[resval] = use
		
		for n in reversed(self.nodes):
			# try to remove outputs that are unused entirely
			
			unused_outputs = [o for o in n.output_names if (n,o) not in use_map]
			
			n.normalize(unused_outputs)
			
			# try to reroute outputs that are invariant under
			# loops or branches
			for o in tuple(n.output_names):
				old_def = (n, o)
				new_def = n.try_remove_invariant(o)
				if new_def and (old_def in use_map):
					uses = use_map[old_def]
					for use in uses: self.update_use(use, new_def)
					del use_map[old_def]
					uses = use_map.get(new_def, []) + uses
					use_map[new_def] = uses
			
			# see if node is entirely unused now
			if all( (n, o) not in use_map for o in n.output_names):
				del self.nodes[self.nodes.index(n)]
				continue
			
			# register uses
			for i, val in zip(n.input_names, n.operands):
				use = use_map.get(val, [])
				use.append((n, i))
				use_map[val] = use
		for n in range(len(self.nodes)):
			self.nodes[n].index = n
	
	def update_use(self, use_site, def_site):
		if use_site[0]:
			n = use_site[0]
			i = use_site[1]
			index = n.input_names.index(i)
			o = n.operands
			n.operands = o[:index] + (def_site,) + o[index + 1:]
		else:
			index = self.results.index(use_site[1])
			self.result_values[index] = def_site
	
	def find_use_sites(self, def_site):
		node_use_sites = reduce(operator.add, (node.get_use_sites[def_site] for node in self.nodes), ())
		res_use_sites = tuple((None, r) for r, v in zip(self.results, self.result_values) if v == def_size)
		return node_use_sites + res_use_sites
	
	def uses(self, def_site):
		if any(n.uses(def_site) for n in self.nodes): return True
		if any(r == def_site for r in self.result_values): return True
		return False
	
	def is_equivalent(self, other):
		if self.arguments != other.arguments:
			return False
		if self.results != other.results:
			return False
		def_mapping = dict(((None, arg), (None, arg)) for arg in self.arguments)
		for node in self.nodes:
			matching_node = None
			operands_mapped = tuple(def_mapping[o] for o in node.operands)
			for other_node in other.nodes:
				if other_node.input_names != node.input_names:
					continue
				if other_node.output_names != node.output_names:
					continue
				if operands_mapped != tuple(other_node.operands):
					continue
				if not node.is_equivalent(other_node):
					continue
				matching_node = other_node
				break
			if not matching_node:
				return False
			for o in node.output_names:
				def_mapping[(node, o)] = (other_node, o)
		results_mapped = tuple(def_mapping[r] for r in self.result_values)
		return results_mapped == tuple(other.result_values)
	
	def __eq__(self, other):
		return self.is_equivalent(other)
	
	def node_count(self):
		count = 0
		for node in self.nodes:
			count += node.node_count()
		return count
	def gamma_count(self):
		count = 0
		for node in self.nodes:
			count += node.gamma_count()
		return count
	def theta_count(self):
		count = 0
		for node in self.nodes:
			count += node.theta_count()
		return count
	def maximum_depth(self):
		depth = 0
		for node in self.nodes:
			depth = max(depth, node.maximum_depth())
		return depth + 1
