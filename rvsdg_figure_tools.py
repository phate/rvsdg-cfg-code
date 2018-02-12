import figure

class rvsdg_region(object):
	def __init__(self, args, ress, root = False):
		nargs = len(args)
		nress = len(ress)
		self.tab = figure.base.tabular(hpad=0.2, vpad=0.3, canvas=cv)
		if root: style = figure.base.INVISIBLE
		else: style = figure.base.DOTTED
		self.box = figure.base.box(contains=self.tab, canvas=cv, hpad = 0.1, vpad=0.4, style=style)
		
		self.args = []
		self.ress = []
		for n in range(len(args)):
			if args[n][0] == '$':
				label = '{\\tiny %s}' % args[n][1:]
				fill = True
			else:
				label = '{\\tiny %s}' % args[n]
				fill = False
			s = figure.base.socket(self.box, (n+0.5)/nargs, 0, False, fill = fill, canvas=cv)
			self.args.append(s)
			figure.base.anchored_label(label, s, 0.5, -.5, 'B', canvas = cv)
		
		for n in range(len(ress)):
			if ress[n][0] == '$':
				label = '{\\tiny %s}' % ress[n][1:]
				fill = True
			else:
				label = '{\\tiny %s}' % ress[n]
				fill = False
			s = figure.base.socket(self.box, (n+0.5)/nress, 1, True, fill = fill, canvas=cv)
			self.ress.append(s)
			figure.base.anchored_label(label, s, 0.5, 1.5, 't', canvas = cv)

	def attach(self, node, col, row, *args, **kwargs):
		self.tab.attach(node, col, row, *args, **kwargs)
 
def make_edge(origin, target, origin_rel = 0.5, target_rel = 0.5, origin_y = 1, target_y = 0, origin_label = None, origin_label_orient = 0, style = figure.base.SOLID, intermediate_stops = []):
	e = figure.base.connector_line([(origin, origin_rel, origin_y)] + intermediate_stops + [(target, target_rel, target_y)], style = style, canvas = cv)
	if origin_label:
		w = figure.base.label(origin_label, canvas = cv)
		a = figure.base.attach_layout(w, origin, origin_rel, origin_y, origin_label_orient, +1 if origin_y else -1, canvas = cv)

def virtual_edge(origin, target):
	make_edge(origin, target, style = figure.base.DOTTED)

class visual_node(object):
	__slots__ = ('inputs', 'outputs', 'node', 'mux')
	def __init__(self, inputs, outputs, node, mux = ()):
		self.inputs = inputs
		self.outputs = outputs
		self.node = node
		self.mux = mux

def make_entrynode(outputs):
	outputs = [figure.base.make_text_box(name, canvas = cv) for name in outputs]
	node = figure.base.box(contains = figure.base.hbox(outputs), canvas = cv, style = figure.base.THICK)
	return visual_node([], outputs, node)

def make_exitnode(inputs):
	inputs = [figure.base.make_text_box(name, canvas = cv) for name in inputs]
	node = figure.base.box(contains = figure.base.hbox(inputs), canvas = cv, style = figure.base.THICK)
	return visual_node(inputs, [], node)

def make_gennode(inputs, node_box, outputs):
	inputs = [figure.base.socket(node_box, (n+0.5)/len(inputs), 0, up=True, fill=(inputs[n][0]=='$'), canvas=cv) for n in range(len(inputs))]
	outputs = [figure.base.socket(node_box, (n+0.5)/len(outputs), 1, up=False, fill=(outputs[n][0]=='$'), canvas=cv) for n in range(len(outputs))]
	
	return visual_node(inputs, outputs, node_box)

def make_gammanode(inputs, regions, outputs):
	t = figure.base.tabular(hpad=0.1, vpad=0.1, canvas=cv)
	
	for n in range(len(regions)):
		t.attach(regions[n].box, n, 0, 1, 1, True)
	
	node_box = figure.base.box(contains = t, hpad = 0.1, vpad = 0.5, canvas = cv, style = figure.base.THICK)
	node = make_gennode(inputs, node_box, outputs)
	
	for n in range(len(inputs)):
		if n == 0: label = '{\\large $\\gamma$}'
		else:
			label = inputs[n]
			if label[0] == '$': label = label[1:]
			label = '{\\tiny %s}' % label
		figure.base.anchored_label(label, node.inputs[n], 0.5, 1.5, 't', canvas = cv)
	
	for n in range(len(outputs)):
		label = outputs[n]
		if label[0] == '$': label = label[1:]
		label = '{\\tiny %s}' % label
		figure.base.anchored_label(label, node.outputs[n], 0.5, -0.5, 'B', canvas = cv)
	
	return node

def make_thetanode(inputs, region, outputs):
	t = figure.base.tabular(hpad=0.1, vpad=0.1, canvas=cv)
	
	t.attach(region.box, 0, 0, 1, 1, True)
	
	node_box = figure.base.box(contains = t, hpad = 0.1, vpad = 0.5, canvas = cv, style = figure.base.THICK)
	node = make_gennode(inputs, node_box, outputs)
	
	for n in range(len(inputs)):
		label = inputs[n]
		if label[0] == '$': label = label[1:]
		label = '{\\tiny %s}' % label
		figure.base.anchored_label(label, node.inputs[n], 0.5, 1.5, 't', canvas = cv)
	
	for n in range(len(outputs)):
		label = outputs[n]
		if label[0] == '$': label = label[1:]
		label = '{\\tiny %s}' % label
		figure.base.anchored_label(label, node.outputs[n], 0.5, -0.5, 'B', canvas = cv)
	
	return node

def make_opnode(inputs, operator, outputs):
	node_box = figure.base.make_text_box(operator, canvas = cv, style = figure.base.THICK)
	
	return make_gennode(inputs, node_box, outputs)

def box_region(region):
	return figure.base.box(contains = region, canvas = cv, pad = 0.1, style = figure.base.DOTTED)

def subregions(regions):
	contents = figure.base.hbox([box_region(region) for region in regions], hpad = 0.1, vpad = 0.1)
	return contents
