import itertools

from . import base

class element(object):
	'''Element of a digraph'''
	__slots__ = ()
	
	def extents(self): abstract
	def layout(self): abstract

class node_slot_layouter(object):
	__slots__ = ()
	
	def input_slot_xminmax(self, node, index):
		w = node.minimum_extents[0]
		count = max(e.target_index for e in node.incoming) + 1
		return index * w / count, (index + 1) * w / count
	
	def output_slot_xminmax(self, node, index):
		w = node.minimum_extents[0]
		count = max(e.origin_index for e in node.outgoing) + 1
		return index * w / count, (index + 1) * w / count

default_node_slot_layouter = node_slot_layouter()

class node(element):
	__slots__ = (
		'visible_shape',
		'rank',
		'incoming',
		'outgoing',
		'grid_attach',
		'_extents',
		'_node_slot_layouter',
	)
	
	def __init__(self, visible_shape, slot_layouter):
		self.visible_shape = visible_shape
		self.incoming = []
		self.outgoing = []
		self._extents = None
		self._node_slot_layouter = slot_layouter
	
	def extents(self):
		if self._extents is None:
			self._extents = self.visible_shape.minimum_extents
		return self._extents
	
	def input_slot_xminmax(self, index):
		return self._node_slot_layouter.input_slot_xminmax(self, index)
	
	def output_slot_xminmax(self, index):
		return self._node_slot_layouter.output_slot_xminmax(self, index)
	
	def layout(self):
		self.visible_shape.layout(*self.visible_shape.minimum_extents)

class edge(element):
	__slots__ = (
		'origin',
		'origin_index',
		'target',
		'target_index',
		'rank_weight',
		'pts',
		'label_shape',
		'origin_x_min', 'origin_x_max',
		'target_x_min', 'target_x_max',
	)
	
	def __init__(self, origin, target, label_shape, rank_weight = True, origin_index = -1, target_index = -1):
		self.origin = origin
		if origin_index == -1: self.origin_index = len(origin.outgoing)
		else: self.origin_index = origin_index
		self.target = target
		if target_index == -1: self.target_index = len(target.incoming)
		else: self.target_index = target_index
		self.label_shape = label_shape
		self.rank_weight = rank_weight
		origin.outgoing.append(self)
		target.incoming.append(self)
	
	def extents(self):
		return 0, 0
	
	def layout(self):
		self.label_shape.layout(*self.label_shape.minimum_extents)

class row_reservation(object):
	__slots__ = (
		'column', 'row',
		'x', 'y', 
		'width', 'height',
		'fx',
		'x_iterated',
		'constraints',
	)
	def __init__(self, column, row, width, height):
		self.column = column
		self.row = row
		self.x = 0
		self.width = width
		self.height = height
		self.constraints = []

class layout_grid(object):
	__slots__ = (
		'rows',
	)
	
	def __init__(self, nranks):
		self.rows = [[] for n in range(nranks)]
	
	def add(self, rank, obj, width, height):
		total = sum(r.width for r in self.rows[rank])
		rsv = row_reservation(len(self.rows[rank]), rank, width, height)
		self.rows[rank].append(rsv)
		
		return rsv
	
	def add_constraint(self, r1, r2, x, y):
		r1.constraints.append((r2, x, y))
		r2.constraints.append((r1, -x, -y))
	
	def compute_heights(self):
		current_y = 0.0
		for row in self.rows:
			row_height = max(r.height for r in row)
			for r in row:
				r.y = current_y + (row_height - r.height) / 2.0
			current_y += row_height
	
	def row_height(self, row):
		return max(i.height for i in self.rows[row])
	
	def row_width(self, rank):
		return sum(r.width for r in self.rows[rank])
	
	def max_width(self):
		return max(self.row_width(rank) for rank in range(len(self.rows)))
	
	def relax_row(self, row, max_width):
		for i in range(32):
			for n in range(len(row)):
				p1 = row[n]
				if p1.x + p1.fx < 0:
					p1.fx = -p1.x
				if p1.x + p1.fx + p1.width > max_width:
					p1.fx = max_width - p1.width - p1.x
				if n >= len(row) - 1:
					continue
				p2 = row[n + 1]
				if p1.x + p1.fx + p1.width > p2.x + p2.fx:
					f2 = 0.5*(p1.x - p2.x + p1.fx + p2.fx + p1.width)
					f1 = p1.fx + p2.fx - f2
					p1.fx = 0.5 * p1.fx + 0.5 * f1
					p2.fx = 0.5 * p2.fx + 0.5 * f2
	
	def fix_boundaries(self, w):
		for n in range(len(self.rows[0])):
			top = self.rows[0][n]
			top.x = (n + 0.5) * w / (len(self.rows[0])) - top.width / 2
		for n in range(len(self.rows[-1])):
			bottom = self.rows[-1][n]
			bottom.x = (n + 0.5) * w / (len(self.rows[-1])) - bottom.width / 2
	
	def relax_iter(self, w):
		self.fix_boundaries(self.max_width())
		for row in self.rows:
			for p1 in row:
				fx = 0
				x1, y1 = p1.x, p1.y
				for p2, edx, edy in p1.constraints:
					x2, y2 = p2.x, p2.y
					dx = x2 - x1 - edx
					fx += dx
				if p1.constraints: fx /= len(p1.constraints)
				p1.fx = fx * 0.5
		for row in self.rows:
			self.relax_row(row, w)
		for row in self.rows:
			for p1 in row:
				p1.x = p1.x + p1.fx
		self.fix_boundaries(self.max_width())

class digraph(base.shape):
	__slots__ = (
		'_nodes',
		'_edges',
		'_vsep',
		'_hsep',
		'_vpad',
		'_hpad',
		'_arrowsize',
		
		'_grid',
		'_layouted_extents',
	)
	
	def __init__(self):
		self._nodes = []
		self._edges = []
		self._vsep = 15.0
		self._hsep = 5.0
		self._vpad = (0.0, 0.0)
		self._hpad = (0.0, 0.0)
		self._arrowsize = 5.0
		
		self._invalidate_extents()
	
	def _invalidate_extents(self):
		self._grid = None
		self._layouted_extents = None
	
	def add_node(self, node_shape, slot_layouter = default_node_slot_layouter):
		self._invalidate_extents()
		n = node(node_shape, slot_layouter)
		self._nodes.append(n)
		node_shape.parent = self
		return n
	
	def add_edge(self, origin, target, label = None, origin_index = -1, target_index = -1):
		self._invalidate_extents()
		assert origin in self._nodes
		assert target in self._nodes
		if label is None: label = base.nullshape()
		e = edge(origin, target, label, origin_index = origin_index, target_index = target_index)
		self._edges.append(e)
		label.parent = self
		return e
	
	def _recompute_node_rank(self, n):
		"""(Re)computes rank of a single node.
		
		Returns True if the rank was changed."""
		rank = 0
		for e in n.incoming:
			if not e.rank_weight: continue
			rank = max(rank, e.origin.rank + 1)
		if rank != n.rank:
			n.rank = rank
			return True
		else:
			return False
	
	def _compute_ranks(self):
		"""(Re)computes the ranks of all nodes.
		
		Returns one plus the highest rank of any node."""
		count = len(self._nodes)
		for n in self._nodes:
			n.rank = 0
		repeat = True
		max_rank = 0
		while repeat:
			repeat = False
			for n in self._nodes:
				repeat = self._recompute_node_rank(n) or repeat
				max_rank = max(max_rank, n.rank + 1)
		assert max_rank <= count
		return max_rank
	
	def _add_node_to_grid(self, grid, node, done):
		w, h = node.minimum_extents
		rsv = grid.add(node.rank, node, w + self._hsep, h + self._vsep)
		node.grid_attach = rsv
		done.add(node)
	
	def _add_edge_to_grid(self, grid, edge, done):
		if edge in done:
			return
		top = edge.origin.rank
		bottom  = edge.target.rank
		backwards = top > bottom
		if top > bottom: top, bottom = bottom,top
		
		origin_attach = edge.origin.grid_attach
		
		pts = []
		edge.origin_x_min, edge.origin_x_max = edge.origin.output_slot_xminmax(edge.origin_index)
		ox = (edge.origin_x_min + edge.origin_x_max) * 0.5
		if not backwards: oy = edge.origin.minimum_extents[1]
		else: oy = 0
		pts.append((origin_attach, ox + self._hsep * 0.5, oy + self._vsep * 0.5))
		
		if backwards: r = range(bottom - 1, top, -1)
		else: r = range(top + 1, bottom)
		for rank in r:
			rsv = grid.add(rank, edge, self._hsep * 2, self._vsep)
			pts.append((rsv,  self._hsep,  self._vsep * 0.5))
		done.add(edge)
		
		if edge.target not in done:
			self._recurse_add_node_to_grid(grid, edge.target, done)
		
		target_attach = edge.target.grid_attach
		edge.target_x_min, edge.target_x_max = edge.target.input_slot_xminmax(edge.target_index)
		tx = (edge.target_x_min + edge.target_x_max) * 0.5
		if backwards: ty = edge.target.minimum_extents[1]
		else: ty = 0
		pts.append((target_attach, tx + self._hsep * 0.5, ty + self._vsep * 0.5))
		
		edge.pts = pts
		
		for n in range(len(pts) - 1):
			p1, x1, y1 = pts[n]
			p2, x2, y2 = pts[n + 1]
			grid.add_constraint(p1, p2, x1 - x2, y1 - y2)
	
	def _recurse_add_node_to_grid(self, grid, node, done):
		if node in done:
			return
		self._add_node_to_grid(grid, node, done)
		for edge in node.outgoing:
			self._add_edge_to_grid(grid, edge, done)
	
	def _create_rank_grid(self):
		for n in self._nodes:
			n.layout()
		for e in self._edges:
			e.layout()
		nranks = self._compute_ranks()
		grid = layout_grid(nranks)
		done = set()
		for node in self._nodes:
			if node.rank == 0:
				self._recurse_add_node_to_grid(grid, node, done)
		grid.compute_heights()
		return grid
	
	def _row_extents(self, rank):
		row_width = 0.0
		row_height = 0.0
		for item in rank:
			e = item.width, item.height
			row_width += e[0]# + self._hsep
			row_height = max(row_height, e[1])
		return row_width, row_height
	
	def _rank_grid_extents(self, rank_grid):
		total_width = 0
		total_height = 0
		for rank in rank_grid.rows:
			row_width, row_height = self._row_extents(rank)
			total_width = max(total_width, row_width)
			total_height += row_height
		return total_width, total_height
	
	def extents(self):
		if not self._layouted_extents:
			self.layout(0, 0)
			(w, h) = self._rank_grid_extents(self._grid)
			self._layouted_extents = (w + self._hpad[0] + self._hpad[1], h + self._vpad[0] + self._vpad[1])
		return self._layouted_extents
	
	def layout(self, w, h):
		if (w, h) == self._layouted_extents:
			return
		rank_grid = self._create_rank_grid()
		total_width, total_height = self._rank_grid_extents(rank_grid)
		
		y = 0.0
		for rank_index, rank in zip(range(len(rank_grid.rows)), rank_grid.rows):
			layout_row = []
			row_width, row_height = self._row_extents(rank)
			x = (total_width - row_width) / 2.0
			y = y + (row_height + self._vsep) / 2.0
			for item in rank:
				iw, ih = item.width, item.height
				x = x + iw + self._hsep
			y = y + (row_height + self._vsep) / 2.0
		
		max_width = max(w, rank_grid.max_width())
		for i in range(32):
			rank_grid.relax_iter(max_width)
		for e in self._edges:
			if len(e.pts) == 2: continue
			
			po, pox, poy = e.pts[0]
			xo, yo = po.x + pox, po.y + poy
			pm, pmx, pmy = e.pts[1]
			xm, ym = pm.x + pmx, pm.y + pmy
			pn, pnx, pny = e.pts[2]
			xn, yn = pn.x + pnx, pn.y + pny
			if xo < xm and xn < xm and xm <= po.x + e.origin_x_max:
				e.pts[0] = po, xm - po.x, poy
			
			pt, ptx, pty = e.pts[-1]
			xt, yt = pt.x + ptx, pt.y + pty
			pm, pmx, pmy = e.pts[-2]
			xm, ym = pm.x + pmx, pm.y + pmy
			pn, pnx, pny = e.pts[-3]
			xn, yn = pn.x + pnx, pn.y + pny
			if xt < xm and xn < xm and xm <= pt.x + e.target_x_max:
				e.pts[-1] = pt, xm - pt.x, pty
		
		self._grid = rank_grid
		self._layouted_extents = (w, h)
		
		x = self._hpad[0]
		y = self._vpad[0]
		for n in self._nodes:
			px, py = n.grid_attach.x + self._hsep * 0.5, n.grid_attach.y + self._vsep * 0.5
			n.visible_shape.x_in_parent = x + px
			n.visible_shape.y_in_parent = y + py
			#n.visible_shape.render(x + px, y + py, tgt)
		
		return rank_grid
	
	def _edge_path(self, x, y, e):
		top = e.origin.rank
		bottom  = e.target.rank
		backwards = top > bottom
		
		points = []
		for n in range(len(e.pts)):
			a, x_off, y_off = e.pts[n]
			if n == 0 or n == len(e.pts) - 1:
				points.append((a.x + x_off, a.y + y_off))
			else:
				h = self._grid.row_height(a.row) - self._vsep
				if backwards:
					points.append((a.x + x_off, a.y + y_off + h * 0.5))
					points.append((a.x + x_off, a.y + y_off - h * 0.5))
				else:
					points.append((a.x + x_off, a.y + y_off - h * 0.5))
					points.append((a.x + x_off, a.y + y_off + h * 0.5))
		
		return points
	
	def _render_edge(self, x, y, e, tgt):
		top = e.origin.rank
		bottom  = e.target.rank
		backwards = top > bottom
		
		points = []
		for n in range(len(e.pts)):
			a, x_off, y_off = e.pts[n]
			if n == 0 or n == len(e.pts) - 1:
				points.append((a.x + x_off, a.y + y_off))
			else:
				h = self._grid.row_height(a.row) - self._vsep
				if backwards:
					points.append((a.x + x_off, a.y + y_off + h * 0.5))
					points.append((a.x + x_off, a.y + y_off - h * 0.5))
				else:
					points.append((a.x + x_off, a.y + y_off - h * 0.5))
					points.append((a.x + x_off, a.y + y_off + h * 0.5))
				
		pts = 'm %f,%f' % (points[0][0] + x, points[0][1] + y)
		
		for n in range(1, len(points)):
			pts += ' %f,%f' % ((points[n][0]-points[n-1][0]),(points[n][1]-points[n-1][1]))
		
		tgt.write('<path style="stroke:#000000;stroke-width:1;fill:none" d="%s" />\n' % pts)
		dx, dy = points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]
		d = (dx*dx + dy*dy) ** 0.5
		dx, dy = dx / d * self._arrowsize, dy / d * self._arrowsize
		sin30, cos30 = 0.5, 0.75**0.5
		d1x, d1y = dx * cos30 + dy * sin30, dy * cos30 - dx * sin30
		d2x, d2y = dx * cos30 - dy * sin30, dy * cos30 + dx * sin30
		px, py = points[-1]
		tgt.write('<path style="stroke:#000000;stroke-width:1;fill:none" d="m %f,%f %f,%f %f,%f" />\n'
			% (px - d1x + x, py - d1y + y, d1x, d1y, -d2x, -d2y))
		
		backwards = e.origin.rank > e.target.rank
		
		w, h = e.label_shape.minimum_extents
		lx, ly = points[0]
		if backwards: ly -= h + 1
		else: ly += 1
		if points[1][0] > points[0][0]: lx -= w + 0.25
		else: lx += 0.25
		e.label_shape.render(lx + x, ly + y, tgt)
	
	def render(self, x, y, tgt):
		for n in self._nodes:
			n.visible_shape.render(n.visible_shape.x_in_parent + x, n.visible_shape.y_in_parent + y, tgt)
		x += self._hpad[0]
		y += self._vpad[0]
		for e in self._edges:
			self._render_edge(x, y, e, tgt)
	
	def render_pst(self, x, y, tgt):
		for n in self._nodes:
			n.visible_shape.render_pst(n.visible_shape.x_in_parent + x, n.visible_shape.y_in_parent + y, tgt)
		x += self._hpad[0]
		y += self._vpad[0]
		for e in self._edges:
			self._render_edge_pst(x, y, e, tgt)

def compute_fwd_edges(cfg):
	pending = set(cfg.entries)
	reached = set()
	fwd = set()
	
	while pending:
		n = pending.pop()
		reached.add(n)
		for e in n.outgoing:
			if e.target not in reached:
				fwd.add(e)
				pending.add(e.target)
	
	return fwd

def cfg_to_graph_layout(cfg):
	dg = digraph()
	done_nodes = {}
	done_edges = set()
	fwd_edges = compute_fwd_edges(cfg)
	
	def recurse_add_node(n):
		if n in done_nodes: return done_nodes[n]
		on = dg.add_node(base.make_text_box(str(n.stmt)))
		done_nodes[n] = on
		for e in n.outgoing:
			if e in done_edges: continue
			tn = recurse_add_node(e.target)
			ve = dg.add_edge(on, tn)
			if not e in fwd_edges: ve.rank_weight = False
		return on
	
	for entry in cfg.entries:
		recurse_add_node(entry)
	
	return dg
