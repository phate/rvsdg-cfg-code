import itertools

def union_min_extents(objs):
	w, h = 0
	for obj in objs:
		obj_w, obj_h = obj.min_extents
		w = max(obj_w, w)
		h = max(obj_h, h)
	return w, h

def union_bounds(objs):
	minx, miny, maxx, maxy = 1e+1000, 1e+1000, 0, 0
	for obj in objs:
		x, y, w, h = obj.bounds
		minx = min(minx, x)
		maxx = max(maxx, x + w)
		miny = min(miny, y)
		maxy = max(maxy, y + h)
	w = max(0.0, maxx - minx)
	h = max(0.0, maxy - miny)
	return minx, miny, w, h

class linestyle(object):
	__slots__ = ()
	def get_style(self): abstract

class solid_linestyle(object):
	__slots__ = ()
	def get_style(self): return ''
SOLID = solid_linestyle()
class invisible_linestyle(object):
	__slots__ = ()
	def get_style(self): return '[linestyle=none]'
INVISIBLE = invisible_linestyle()
class dashed_linestyle(linestyle):
	__slots__ = ()
	def get_style(self): return '[linestyle=dashed,dash=3pt 3pt]'
DASHED = dashed_linestyle()
class dotted_linestyle(linestyle):
	__slots__ = ()
	def get_style(self): return '[linestyle=dashed,dash=1pt 1pt]'
DOTTED = dotted_linestyle()
class thick_linestyle(linestyle):
	__slots__ = ()
	def get_style(self): return '[linewidth=1pt]'
THICK = thick_linestyle()
class thick_grayed(object):
	__slots__ = ()
	def get_style(self): return '[linewidth=1pt,fillstyle=solid,fillcolor=lightgray]'
THICK_GRAYED = thick_grayed()

class shape(object):
	__slots__ = (
		# dependency graph for minimum extents
		'_min_extent_superiors',
		'_min_extent_dependents',
		'_cached_min_extents',
		# dependency graph for layouting
		'_layout_superiors',
		'_layout_dependents',
		'_bounds',
		# canvas where all objects live
		'_canvas',
	)
	
	def __init__(self, canvas = None):
		self._min_extent_superiors = set()
		self._min_extent_dependents = set()
		self._cached_min_extents = None
		
		self._layout_superiors = set()
		self._layout_dependents = set()
		self._bounds = None
		
		self._canvas = canvas
		if canvas:
			canvas.register_object(self)
	
	def mark_min_extent_depends(self, other):
		self._min_extent_superiors.add(other)
		other._min_extent_dependents.add(self)
		self.invalidate_min_extents()
	def invalidate_min_extents(self):
		if self._cached_min_extents is None:
			return
		self._cached_min_extents = None
		self.invalidate_layout()
		for other in self._min_extent_dependents:
			other.invalidate_min_extents()
	def compute_min_extents(self): abstract
	def get_min_extents(self):
		if not self._cached_min_extents:
			self._cached_min_extents = self.compute_min_extents()
		return self._cached_min_extents
	min_extents = property(get_min_extents)
	
	def mark_layout_depends(self, other):
		self._layout_superiors.add(other)
		other._layout_dependents.add(self)
		self.invalidate_layout()
	def invalidate_layout(self):
		if self._bounds is None:
			return
		self._bounds = None
		for other in self._layout_dependents:
			other.invalidate_layout()
	def layout(self):
		if self._bounds: return
		for sup in self._layout_superiors: sup.layout()
		if self._bounds: return
		self.layout_self_default()
	def layout_self_default(self):
		w, h = self.min_extents
		self.apply_bounds(0.0, 0.0, w, h)
	def apply_bounds(self, x, y, w, h):
		self._bounds = (x, y, w, h)
		self.layout_bounds(x, y, w, h)
	def layout_bounds(self, x, y, w, h): pass
	def get_bounds(self):
		self.layout()
		return self._bounds
	bounds = property(get_bounds)
	
	def render_pst(self, tgt): abstract
	def render_svg(self, tgt): abstract
	
	# mandatory overrides:
	# - compute_min_extents
	# - render_pst
	# - render_svc
	# optional overrides:
	# - layout_bounds
	# - layout_self_default

class nullshape(shape):
	__slots__ = ()
	def compute_min_extents(self): return (0.0, 0.0)
	def render_svg(self, tgt): pass
	def render_pst(self, tgt): pass

class canvas(object):
	__slots__ = ('_objects',)
	def __init__(self):
		self._objects = []
	def contents(self):
		return tuple(self._objects)
	def register_object(self, obj):
		assert obj not in self._objects
		self._objects.append(obj)
	def layout(self):
		again = True
		while again:
			again = False
			for obj in self._objects:
				if obj._bounds is not None: continue
				again = again or (obj._bounds is None)
				obj.layout()
				assert obj._bounds
	def render_pst(self, tgt):
		self.layout()
		x, y, w, h = union_bounds(self._objects)
		tgt.write('\\begin{pspicture}(%f,%f)(%f,%f)\n' %
			(x, -y, (x + w), -(y + h)))
		for obj in reversed(self._objects): obj.render_pst(tgt)
		tgt.write('\\end{pspicture}\n')
	def render_svg(self, tgt):
		self.layout()
		tgt.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
		tgt.write('<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">\n')
		for obj in self._objects: obj.render_svg(tgt)
		tgt.write('</svg>\n')

class box(shape):
	__slots__ = (
		'_hpad',
		'_vpad',
		'_surrounds',
		'_contains',
		'_static_bounds',
		'_static_extents',
		'_style',
	)
	
	def __init__(self, canvas = None, pad = 0, hpad = 0, vpad = 0, surrounds = (), contains = None, static_bounds = None, static_extents = None, style = SOLID):
		assert not surrounds or not contains or not static_bounds or not static_extents
		assert surrounds or contains or static_bounds or static_extents
		shape.__init__(self, canvas)
		self._hpad = max(pad, hpad)
		self._vpad = max(pad, vpad)
		self._surrounds = surrounds
		self._static_bounds = tuple(static_bounds) if static_bounds else None
		self._static_extents = tuple(static_extents) if static_extents else None
		self._contains = contains
		self._style = style
		if contains:
			contains.mark_layout_depends(self)
			self.mark_min_extent_depends(contains)
		for child in surrounds:
			self.mark_layout_depends(child)
	
	def compute_min_extents(self):
		if self._static_bounds:
			return self._static_bounds[2:]
		elif self._static_extents:
			return self._static_extents
		elif self._contains:
			w, h = self._contains.min_extents
			return (w + 2 * self._hpad, h + 2 * self._vpad)
		else:
			return (0.0, 0.0)
	
	def layout_bounds(self, x, y, w, h):
		if self._contains:
			self._contains.apply_bounds(x + self._hpad, y + self._vpad, w - 2 * self._hpad, h - 2 * self._vpad)
	
	def layout_self_default(self):
		if self._static_bounds:
			self.apply_bounds(*self._static_bounds)
		elif self._static_extents:
			self.apply_bounds(0.0, 0.0, *self._static_extents)
		elif self._surrounds:
			x, y, w, h = union_bounds(self._surrounds)
			self.apply_bounds(x - self._hpad, y - self._vpad, w + 2 * self._hpad, h + 2 * self._vpad)
		else:
			shape.layout_self_default(self)

	def render_svg(self, tgt):
		x, y, w, h = self.bounds
		
		pts = '%f,%f %f,%f %f,%f %f,%f %f,%f' % (
			x, y,
			x + w, y,
			x + w, y + h,
			x, y + h,
			x, y)
		box = '<polygon points="%s" stroke="black" fill="none" />\n' % pts
		tgt.write(box)
	
	def render_pst(self, tgt):
		x, y, w, h = self.bounds
		style = self._style.get_style()
		x1, y1 = x, -(y+h)
		x2, y2 = x+w, -y
		tgt.write('\\pspolygon%s(%f,%f)(%f,%f)(%f,%f)(%f,%f)\n' %
			(style, x1, y1, x2, y1, x2, y2, x1, y2))

class label(shape):
	__slots__ = ('_text', '_fontsize')
	
	def __init__(self, text, fontsize = 10, canvas = None):
		shape.__init__(self, canvas)
		self._text = text
		self._fontsize = fontsize
	
	def compute_min_extents(self):
		w = len(self._text) * (0.0131 * self._fontsize)
		h = 0.0255 * self._fontsize
		return w, h
	
	def render_svg(self, tgt):
		text_w, text_h = self.compute_min_extents()
		x, y, w, h = self.bounds
		x, y = x + w / 2.0, y + h / 2.0 + text_h / 3
		tgt.write('<text x="%f" y="%f" font-family="Courier,monospace" font-size="%d" text-anchor="middle">%s</text>\n' % (x, y, self._fontsize, self._text))
	
	def render_pst(self, tgt):
		text_w, text_h = self.min_extents
		x, y, w, h = self.bounds
		x, y = x + w / 2.0, y + h / 2.0
		tgt.write('\\rput(%f,%f){\\scriptsize \\tt %s}\n' % (x, -y, self._text))

class anchored_label(shape):
	__slots__ = (
		'_text',
		'_fontsize',
		'_anchor',
		'_relx',
		'_rely',
		'_x',
		'_y',
		'_align',)
	
	def __init__(self, text, anchor, relx, rely, align = '', canvas = None):
		shape.__init__(self, canvas)
		self._text = text
		self._anchor = anchor
		self._relx = relx
		self._rely = rely
		self._fontsize = 10
		self._align = align
	
	def compute_min_extents(self):
		w = len(self._text) * (0.0131 * self._fontsize)
		h = 0.0255 * self._fontsize
		return w, h
	
	def render_svg(self, tgt):
		pass
	
	def layout_self_default(self):
		w, h = self.min_extents
		ax, ay, aw, ah = self._anchor.bounds
		
		self._x = ax + aw * self._relx
		self._y = ay + ah * self._rely
		
		self.apply_bounds(self._x, self._y, w, h)
	
	def render_svg(self, tgt): pass
	def render_pst(self, tgt):
		if self._align: align = '[%s]' % self._align
		else: align = ''
		tgt.write('\\rput%s(%f,%f){%s}\n' %
			(align, self._x, -self._y, self._text))

class hbox(shape):
	__slots__ = ('_children', '_vpad', '_hpad')
	
	def __init__(self, children = (), vpad = 0, hpad = 0, canvas = None):
		shape.__init__(self, canvas)
		self._children = list(children)
		for child in children:
			self.mark_min_extent_depends(child)
			child.mark_layout_depends(self)
		self._vpad = vpad
		self._hpad = hpad
	
	def compute_min_extents(self):
		w, h = 0, 0
		for child in self._children:
			cw, ch = child.min_extents
			w += cw
			h = max(h, ch)
		return w + len(self._children) * self._hpad, h + self._vpad
	
	def layout_bounds(self, x, y, w, h):
		if not self._children:
			return
		min_w, min_h = self.min_extents
		h = max(h, min_h)
		extra_w = (w - min_w) / len(self._children)
		for child in self._children:
			cw, ch = child.min_extents
			cw, ch = cw + extra_w + self._hpad, h
			child.apply_bounds(x + self._hpad * 0.5, y + self._vpad * 0.5, cw - self._hpad, ch - self._vpad)
			x += cw
	
	def render_svg(self, x, y, tgt): pass
	def render_pst(self, x, y, tgt): pass

class vbox(shape):
	__slots__ = ('_children', '_vpad', '_hpad')
	
	def __init__(self, children = (), vpad = 0, hpad = 0, canvas = None):
		shape.__init__(self, canvas)
		self._children = list(children)
		for child in children:
			self.mark_min_extent_depends(child)
			child.mark_layout_depends(self)
		self._vpad = vpad
		self._hpad = hpad
	
	def compute_min_extents(self):
		w, h = 0, 0
		for child in self._children:
			cw, ch = child.min_extents
			w = max(w, cw + self._vpad)
			h = h + ch + self._hpad
		return w, h
	
	def layout_bounds(self, x, y, w, h):
		min_w, min_h = self.min_extents
		w = max(w, min_w)
		extra_h = (h - min_h) / len(self._children) + self._vpad
		for child in self._children:
			cw, ch = child.min_extents
			cw, ch = w, ch + extra_h
			child.apply_bounds(x + self._hpad * 0.5, y + self._vpad * 0.5, cw - self._hpad, ch - self._vpad)
			y += ch
	
	def render_svg(self, tgt): pass
	def render_pst(self, tgt): pass

def distribute_cell_space(requests):
	ncells = 0
	for lo, hi, size in requests: ncells = max(hi, ncells)
	
	space = [0.0] * ncells
	for n in range(100):
		for lo, hi, size in requests:
			if hi - lo > n: continue
			avail = 0.0
			for idx in range(lo, hi): avail += space[idx]
			if avail > size: continue
			delta = (size - avail) / (hi - lo)
			for idx in range(lo, hi): space[idx] += delta
	
	return space

def spaces_to_stops(spaces, pad = 0.0):
	stops = [0.0]
	for space in spaces:
		stops.append(stops[-1] + space + pad)
	return stops

class tabular(shape):
	__slots__ = (
		'_children',
		'_hpad',
		'_vpad',
	)
	
	def __init__(self, canvas = None, children = (), hpad = 0.0, vpad = 0.0):
		shape.__init__(self, canvas)
		self._children = []
		self._hpad = hpad
		self._vpad = vpad
		for child in children: self.attach(*child)
	
	def compute_min_extents(self):
		col_widths = distribute_cell_space(
			[(cx, cx+cw, child.min_extents[0]) for cx, cy, cw, ch, child, options in self._children])
		row_heights = distribute_cell_space(
			[(cy, cy+ch, child.min_extents[1]) for cx, cy, cw, ch, child, options in self._children])
		col_stops = spaces_to_stops(col_widths, self._hpad)
		row_stops = spaces_to_stops(row_heights, self._vpad)
		return max(0, col_stops[-1] - self._hpad), max(0, row_stops[-1] - self._vpad)
		
	def layout_bounds(self, x, y, w, h):
		min_w, min_h = self.min_extents
		col_widths = distribute_cell_space(
			[(cx, cx+cw, child.min_extents[0]) for cx, cy, cw, ch, child, options in self._children])
		row_heights = distribute_cell_space(
			[(cy, cy+ch, child.min_extents[1]) for cx, cy, cw, ch, child, options in self._children])
		
		eff_hpad = (w - min_w) / max(1, (len(col_widths) - 1)) + self._hpad
		eff_vpad = (h - min_h) / max(1, (len(row_heights) - 1)) + self._vpad
		#assert eff_hpad >= self._hpad, (eff_hpad, self._hpad)
		#assert eff_vpad >= self._vpad
		eff_hpad = max(self._hpad, eff_hpad)
		eff_vpad = max(self._vpad, eff_vpad)
		
		col_stops = spaces_to_stops(col_widths, eff_hpad)
		row_stops = spaces_to_stops(row_heights, eff_vpad)
		
		for cx, cy, cw, ch, child, options in self._children:
			x0 = col_stops[cx]
			x1 = col_stops[cx + cw] - eff_hpad
			y0 = row_stops[cy]
			y1 = row_stops[cy + ch] - eff_vpad
			
			if options:
				child_w = x1 - x0
				child_h = y1 - y0
			else:
				child_w, child_h = child.min_extents
			child.apply_bounds(x + (x1 + x0 - child_w) * 0.5, y + (y1 + y0 - child_h) * 0.5, child_w, child_h)
	
	def render_svg(self, tgt): pass
	def render_pst(self, tgt): pass
	
	def attach(self, child, x, y, w = 1, h = 1, options = 0):
		self._children.append((x, y, w, h, child, options))
		self.mark_min_extent_depends(child)
		child.mark_layout_depends(self)

class socket(shape):
	__slots__ = (
		'_anchor',
		'_relx',
		'_rely',
		'_up',
		'_fill',
		'_radius',
		'_center_x',
		'_center_y',
	)
	
	def __init__(self, anchor, relx, rely, up, radius=0.08, fill=False, canvas = None):
		shape.__init__(self, canvas)
		self._anchor = anchor
		self._relx = relx
		self._rely = rely
		self._up = up
		self._radius = radius
		self._fill = fill
		self.mark_layout_depends(anchor)
	
	def compute_min_extents(self):
		return (2 * self.radius, self.radius)
	
	def layout_self_default(self):
		if not hasattr(self, '_center_x'):
			ax, ay, aw, ah = self._anchor.bounds
			self._center_x = ax + aw * self._relx
			self._center_y = ay + ah * self._rely
		if self._up: y = self._center_y - self._radius
		else: y = self._center_y
		x = self._center_x
		self.apply_bounds(x - self._radius, y, 2 * self._radius, self._radius)
	
	def render_svg(self, tgt): pass
	def render_pst(self, tgt):
		if self._up: begin, end = 0, 180
		else: begin, end = 180, 360
		if self._fill: style = '[fillstyle=solid,fillcolor=black]'
		else: style = ''
		tgt.write('\\psarc%s(%f,%f){%f}{%d}{%d}\n' %
			(style, self._center_x, - self._center_y, self._radius, begin, end))

class annotation_digit(shape):
	__slots__ = (
		'_digit',
		'_anchor',
		'_relx',
		'_rely',
		'_alignx',
		'_aligny',
		'_pad'
	)
	
	def __init__(self, digit, anchor, relx, rely, alignx, aligny, pad = 0.0, canvas = None):
		shape.__init__(self, canvas)
		self._digit = digit
		self._anchor = anchor
		self._relx = relx
		self._rely = rely
		self._alignx = alignx
		self._aligny = aligny
		self._pad = pad
		self.mark_layout_depends(anchor)
	
	def compute_min_extents(self):
		return (0.27 + self._pad, 0.27 + self._pad)
	
	def layout_self_default(self):
		w, h = self.min_extents
		ax, ay, aw, ah = self._anchor.bounds
		
		x = ax + aw * self._relx - w * 0.5
		y = ay + ah * self._rely - h * 0.5
		if self._alignx < 0 : x -= w * 0.5
		if self._alignx > 0 : x += w * 0.5
		if self._aligny < 0 : y -= h * 0.5
		if self._aligny > 0 : y += h * 0.5
		
		self.apply_bounds(x, y, w, h)
	
	def render_svg(self, tgt): pass
	def render_pst(self, tgt):
		x, y, w, h = self.bounds
		x = x + w * 0.5
		y = y + h * 0.5
		r = max(w - self._pad, h - self._pad) * 0.5
		tgt.write('\\pscircle(%f,%f){%f}\\rput(%f,%f){\\scriptsize %d}\n' % (x, -y, r, x, -y,  self._digit))

class connector_line(shape):
	__slots__ = (
		'_stops',
		'_style',
	)
	
	def __init__(self, stops = (), style = SOLID, canvas = None):
		shape.__init__(self, canvas)
		self._stops = []
		self._style = style
		assert style
		for stop in stops: self.add_stop(*stop)
	
	def layout_self_default(self):
		pts = []
		for anchor_shape, relx, rely in self._stops:
			x, y, w, h = anchor_shape.bounds
			x = x + w * relx
			y = y + h * rely
			pts.append((x, y))
		
		xmin = min(pt[0] for pt in pts)
		xmax = max(pt[0] for pt in pts)
		ymin = min(pt[1] for pt in pts)
		ymax = max(pt[1] for pt in pts)
		
		self.apply_bounds(xmin, ymin, xmax - xmin, ymax - ymin)
	def compute_min_extents(self): return 0.0, 0.0
	def render_pst(self, tgt):
		pts = []
		for anchor_shape, relx, rely in self._stops:
			x, y, w, h = anchor_shape.bounds
			x = x + w * relx
			y = y + h * rely
			pts.append((x, -y))
		style = self._style.get_style()
		tgt.write('\\psline%s%s\n' % (style, ''.join('(%f,%f)' % pt for pt in pts)))
		dx = pts[-1][0] - pts[-2][0]
		dy = pts[-1][1] - pts[-2][1]
		arrowsize = 0.1
		d = (dx*dx + dy*dy) ** 0.5
		dx, dy = dx / d * arrowsize, dy / d * arrowsize
		sin30, cos30 = 0.5, 0.75**0.5
		d1x, d1y = dx * cos30 + dy * sin30, dy * cos30 - dx * sin30
		d2x, d2y = dx * cos30 - dy * sin30, dy * cos30 + dx * sin30
		hx, hy = pts[-1]
		tgt.write('\\psline(%f,%f)(%f,%f)(%f,%f)\n' %
			(hx - d1x, hy - d1y, hx, hy, hx - d2x, hy - d2y))
	
	def add_stop(self, anchor_shape, relx = 0.5, rely = 0.5):
		self._stops.append((anchor_shape, relx, rely))
		self.mark_layout_depends(anchor_shape)

class attach_layout(shape):
	__slots__ = (
		'_child',
		'_anchor',
		'_relx',
		'_rely',
		'_alignx',
		'_aligny',
		'_pad',
	)
	
	def __init__(self, child, anchor, relx, rely, alignx, aligny, pad = 0.0, canvas = None):
		shape.__init__(self, canvas)
		self._child = child
		self._anchor = anchor
		self._relx = relx
		self._rely = rely
		self._alignx = alignx
		self._aligny = aligny
		self._pad = pad
		self.mark_layout_depends(anchor)
		self.mark_min_extent_depends(child)
		child.mark_layout_depends(self)
	
	def compute_min_extents(self):
		w, h = self._child.min_extents
		return (w + self._pad, h + self._pad)
	
	def layout_self_default(self):
		w, h = self.min_extents
		ax, ay, aw, ah = self._anchor.bounds
		
		x = ax + aw * self._relx - w * 0.5
		y = ay + ah * self._rely - h * 0.5
		if self._alignx < 0 : x -= w * 0.5
		if self._alignx > 0 : x += w * 0.5
		if self._aligny < 0 : y -= h * 0.5
		if self._aligny > 0 : y += h * 0.5
		
		self.apply_bounds(x, y, w, h)
	
	def layout_bounds(self, x, y, w, h):
		self._child.apply_bounds(x + self._pad * 0.5, y + self._pad * 0.5, w - self._pad, h - self._pad)
	
	def render_svg(self, tgt): pass
	def render_pst(self, tgt): pass

def make_text_box(text, canvas = None, style = SOLID):
	b = box(canvas = canvas, pad = 0.05, contains = label(text, canvas = canvas), style = style)
	return b
