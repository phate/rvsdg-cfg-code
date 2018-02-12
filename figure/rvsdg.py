from . import base
from . import digraph

import rvsdg_model

class connect_box(base.shape, base.single_container):
	__slots__ = (
		'vspacing',
		'w', 'h',
		'top_container', 'top_origins', 'top_targets',
		'bot_container', 'bot_origins', 'bot_targets')
	
	def __init__(self, child, top_container, top_origins, top_targets, bot_container, bot_origins, bot_targets, vspacing = 15):
		base.shape.__init__(self)
		base.single_container.__init__(self)
		self.vspacing = vspacing
		if child: self.add(child)
		self.top_container = top_container
		self.top_origins = tuple(top_origins)
		self.top_targets = tuple(top_targets)
		self.bot_container = bot_container
		self.bot_origins = tuple(bot_origins)
		self.bot_targets = tuple(bot_targets)
	
	def extents(self):
		width, height = self.child.minimum_extents
		return (width, height + 2 * self.vspacing)
	
	def layout(self, w, h):
		vspacing = self.vspacing
		self.child.layout(w, h - 2 * vspacing)
		self.child.x_in_parent = 0
		self.child.y_in_parent = vspacing
		self.w, self.h = w, h
	
	def render(self, x, y, tgt):
		w, h = self.w, self.h
		
		pts = '%f,%f %f,%f %f,%f %f,%f %f,%f' % (
			x, y,
			x + w, y,
			x + w, y + h,
			x, y + h,
			x, y)
		box = '<polygon points="%s" stroke="black" fill="none" />\n' % pts
		tgt.write(box)
		
		for a in self.top_targets:
			for origin, target in zip(self.top_origins, a):
				origin_x, origin_y = origin.translate_xy_in(origin.w * 0.5, 0, self.top_container)
				target_x, target_y = target.translate_xy_in(0, 0, self)
				tgt.write('<path style="stroke:#000000;stroke-width:1;fill:none" d="m %f,%f %f,%f" />\n'
					% (x + origin_x, y + origin_y, target_x - origin_x, target_y - origin_y))
		
		for a in self.bot_origins:
			for origin, target in zip(a, self.bot_targets):
				origin_x, origin_y = origin.translate_xy_in(0, 0, self)
				target_x, target_y = target.translate_xy_in(target.w * 0.5, 0, self.bot_container)[0], h
				tgt.write('<path style="stroke:#000000;stroke-width:1;fill:none" d="m %f,%f %f,%f" />\n'
					% (x + origin_x, y + origin_y, target_x - origin_x, target_y - origin_y))
		
		child = self.child
		child.render(x + child.x_in_parent, y + child.y_in_parent, tgt)

class rvsdg_slot_layouter(digraph.node_slot_layouter):
	__slots__ = (
		'inputs',
		'outputs',
	)
	
	def __init__(self, inputs, outputs):
		self.inputs = inputs
		self.outputs = outputs
	
	def input_slot_xminmax(self, node, index):
		i = self.inputs[index]
		xmin = i.translate_xy_in(0, 0, node.visible_shape)[0]
		xmax = i.translate_xy_in(i.w, 0, node.visible_shape)[0]
		return xmin, xmax
	
	def output_slot_xminmax(self, node, index):
		o = self.outputs[index]
		xmin = o.translate_xy_in(0, 0, node.visible_shape)[0]
		xmax = o.translate_xy_in(o.w, 0, node.visible_shape)[0]
		return xmin, xmax

def render_opnode(opnode):
	inputs = [base.make_text_box(name) for name in opnode.input_names]
	outputs = [base.make_text_box(name) for name in opnode.output_names]
	vb = base.vbox([
		base.hbox(inputs),
		base.make_text_box(opnode.operator),
		base.hbox(outputs),
	])
	return vb

def render_selectnode(selectnode):
	inputs = [base.make_text_box(name) for name in selectnode.input_names]
	outputs = [base.make_text_box(name) for name in selectnode.output_names]
	vb = base.vbox([
		base.hbox(inputs),
		base.make_text_box(str(selectnode.alternatives)),
		base.hbox(outputs),
	])
	return vb

def render_gammanode(gammanode):
	inputs = [base.make_text_box(name) for name in gammanode.input_names]
	outputs = [base.make_text_box(name) for name in gammanode.output_names]
	regions = []
	args = []
	results = []
	for a in gammanode.alternatives:
		region, arg, res = render_rvsdg_interior_connectors(a)
		regions.append(region)
		args.append(tuple(arg))
		results.append(tuple(res))
	inputs_box = base.hbox(inputs)
	outputs_box = base.hbox(outputs)
	hb = base.hbox([base.box(r) for r in regions], hpad = 4.0, vpad = 4.0)
	
	cb = connect_box(hb, inputs_box, inputs[:-1], args, outputs_box, results, outputs)
	
	vb = base.vbox([
		inputs_box,
		cb,
		outputs_box,
	])
	return vb

def render_thetanode(thetanode):
	inputs = [base.make_text_box(name) for name in thetanode.input_names]
	outputs = [base.make_text_box(name) for name in thetanode.output_names]
	region, args, results = render_rvsdg_interior_connectors(thetanode.body)
	inputs_box = base.hbox(inputs)
	outputs_box = base.hbox(outputs)
	hb = base.hbox([base.box(region)], hpad = 4.0, vpad = 4.0)
	
	cb = connect_box(hb, inputs_box, inputs, [args], outputs_box, [results[:-1]], outputs)
	
	vb = base.vbox([
		inputs_box,
		cb,
		outputs_box,
	])
	return vb

def render_node(node):
	if isinstance(node, rvsdg_model.rvsdg.opnode):
		return render_opnode(node)
	elif isinstance(node, rvsdg_model.rvsdg.selectnode):
		return render_selectnode(node)
	elif isinstance(node, rvsdg_model.rvsdg.gammanode):
		return render_gammanode(node)
	elif isinstance(node, rvsdg_model.rvsdg.thetanode):
		return render_thetanode(node)
	else:
		assert False

# TODO: introduce box shape that connects args and results
# TODO: layout edges to port

def render_rvsdg_interior_connectors(rvsdg):
	args = []
	results = []
	
	dg = digraph.digraph()
	dg._vpad = (-dg._vsep * 0.5, -dg._vsep * 0.5)
	def_site_map = {}
	for arg in rvsdg.arguments:
		ns = base.nullshape()
		args.append(ns)
		nc = dg.add_node(ns)
		def_site_map[(None, arg)] = (nc, 0)
	
	for node in rvsdg.nodes:
		ns = render_node(node)
		nc = dg.add_node(ns, rvsdg_slot_layouter(ns.children[0].children, ns.children[2].children))
		for op, n in zip(node.operands, range(len(node.operands))):
			origin_nc, origin_index = def_site_map[op]
			target_nc, target_index = nc, n
			dg.add_edge(origin_nc, target_nc, origin_index = origin_index, target_index = target_index)
		for o, n in zip(node.output_names, range(len(node.output_names))):
			def_site_map[(node, o)] = (nc, n)
	
	for res in rvsdg.result_values:
		ns = base.nullshape()
		results.append(ns)
		nc = dg.add_node(ns)
		origin_nc, origin_index = def_site_map[res]
		target_nc, target_index = nc, 0
		dg.add_edge(origin_nc, target_nc, origin_index = origin_index, target_index = target_index)
	
	return dg, args, results

def render_rvsdg_interior(rvsdg):
	return render_rvsdg_interior_connectors(rvsdg)[0]
