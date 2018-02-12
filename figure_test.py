import unittest

import figure.base
import figure.digraph
#import figure.rvsdg
import rvsdg_model

class mockbox(figure.base.nullshape):
	__slots__ = ('min_w', 'min_h')
	def __init__(self, min_w, min_h, canvas = None):
		figure.base.nullshape.__init__(self, canvas)
		self.min_w, self.min_h = min_w, min_h
	def compute_min_extents(self): return self.min_w, self.min_h

class strstream(object):
	__slots__ = (
		'_text',
	)
	
	def __init__(self):
		self._text = []
	
	def write(self, text):
		self._text.append(text)
	
	text = property(lambda self: ''.join(self._text))

theta_expect = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">
<polygon points="2.500000,15.000000 58.300000,15.000000 58.300000,29.000000 2.500000,29.000000 2.500000,15.000000" stroke="black" fill="none" />
<text x="30.400000" y="24.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">v1</text>
<polygon points="2.500000,29.000000 58.300000,29.000000 58.300000,135.000000 2.500000,135.000000 2.500000,29.000000" stroke="black" fill="none" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 30.400000,29.000000 0.000000,17.000000" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 17.450000,118.000000 12.950000,17.000000" />
<polygon points="4.500000,46.000000 56.300000,46.000000 56.300000,118.000000 4.500000,118.000000 4.500000,46.000000" stroke="black" fill="none" />
<polygon points="7.000000,61.000000 53.800000,61.000000 53.800000,75.000000 7.000000,75.000000 7.000000,61.000000" stroke="black" fill="none" />
<text x="30.400000" y="70.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">v1</text>
<polygon points="7.000000,75.000000 53.800000,75.000000 53.800000,89.000000 7.000000,89.000000 7.000000,75.000000" stroke="black" fill="none" />
<text x="30.400000" y="84.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">dec</text>
<polygon points="7.000000,89.000000 18.800000,89.000000 18.800000,103.000000 7.000000,103.000000 7.000000,89.000000" stroke="black" fill="none" />
<text x="12.900000" y="98.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">r</text>
<polygon points="18.800000,89.000000 53.800000,89.000000 53.800000,103.000000 18.800000,103.000000 18.800000,89.000000" stroke="black" fill="none" />
<text x="36.300000" y="98.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">$pred</text>
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 30.400000,46.000000 0.000000,15.000000" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 27.900000,56.669873 2.500000,4.330127 2.500000,-4.330127" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 18.700000,103.000000 -1.250000,15.000000" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 15.318233,113.477217 2.131767,4.522783 2.850962,-4.107556" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 42.100000,103.000000 1.250000,15.000000" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 40.499038,113.892444 2.850962,4.107556 2.131767,-4.522783" />
<polygon points="2.500000,135.000000 58.300000,135.000000 58.300000,149.000000 2.500000,149.000000 2.500000,135.000000" stroke="black" fill="none" />
<text x="30.400000" y="144.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">v1</text>
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 30.400000,0.000000 0.000000,15.000000" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 27.900000,10.669873 2.500000,4.330127 2.500000,-4.330127" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 30.400000,149.000000 0.000000,15.000000" />
<path style="stroke:#000000;stroke-width:1;fill:none" d="m 27.900000,159.669873 2.500000,4.330127 2.500000,-4.330127" />
</svg>
"""

class TestCfgLayout(unittest.TestCase):
	__slots__ = ()
	
	def test_box(self):
		cv = figure.base.canvas()
		l = figure.base.label('abc', canvas = cv)
		b = figure.base.box(canvas = cv, pad = 0.1, contains = l)
		e = b.min_extents
		b.layout()
		s = strstream()
		cv.render_svg(s)
		expected = \
			'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + \
			'<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">\n' + \
			'<text x="0.296500" y="0.312500" font-family="Courier,monospace" font-size="10" text-anchor="middle">abc</text>\n' + \
			'<polygon points="0.000000,0.000000 0.593000,0.000000 0.593000,0.455000 0.000000,0.455000 0.000000,0.000000" stroke="black" fill="none" />\n' + \
			'</svg>\n'
		#expected = \
			#'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + \
			#'<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">\n' + \
			#'<text x="0.393000" y="0.340000" font-family="Courier,monospace" font-size="10" text-anchor="middle">abc</text>\n' + \
			#'<polygon points="0.000000,0.000000 0.593000,0.000000 0.593000,0.455000 0.000000,0.455000 0.000000,0.000000" stroke="black" fill="none" />\n' + \
			#'</svg>\n'
		self.assertEqual(s.text, expected)

	def test_wrapping_box(self):
		l = figure.base.label(text = 'abc')
		b = figure.base.box(pad = 0.1, contains = l)
		
		e = b.min_extents
		self.assertAlmostEqual(e[0], 0.593)
		self.assertAlmostEqual(e[1], 0.455)
	
	def _disabled_test_graph(self):
		s1 = figure.base.make_text_box('abc')
		s2 = figure.base.make_text_box('def')
		s3 = figure.base.make_text_box('ghi')
		s4 = figure.base.make_text_box('jkl')
		
		g = figure.digraph.digraph()
		n1 = g.add_node(s1)
		n2 = g.add_node(s2)
		n3 = g.add_node(s3)
		n4 = g.add_node(s4)
		g.add_edge(n1, n2, figure.base.label('0', fontsize = 5))
		g.add_edge(n2, n4)
		g.add_edge(n1, n4, figure.base.label('1', fontsize = 5))
		g.add_edge(n1, n3, figure.base.label('2', fontsize = 5))
		g.add_edge(n3, n4)
		
		cv = figure.base.canvas()
		cv.add(g)
		
		g.layout(0, 0)
		s = strstream()
		cv.render(s)
		cv.render(file("/tmp/tmp.svg", "w"))
	
	def test_hbox(self):
		mb1 = mockbox(1, 2)
		mb2 = mockbox(2, 1)
		hb = figure.base.hbox([mb1, mb2])
		self.assertEqual(hb.min_extents, (3, 2))
		hb.apply_bounds(0, 0, 5, 2)
		self.assertEqual(mb1.bounds, (0, 0, 2, 2))
		self.assertEqual(mb2.bounds, (2, 0, 3, 2))
	
	def test_vbox(self):
		mb1 = mockbox(1, 2)
		mb2 = mockbox(2, 1)
		hb = figure.base.vbox([mb1, mb2])
		self.assertEqual(hb.min_extents, (2, 3))
		hb.apply_bounds(0, 0, 2, 5)
		self.assertEqual(mb1.bounds, (0, 0, 2, 3))
		self.assertEqual(mb2.bounds, (0, 3, 2, 2))
	
	def _to_svg(self, shape):
		shape.layout(*shape.minimum_extents)
		cv = figure.base.canvas()
		cv.add(shape)
		s = strstream()
		cv.render(s)
		return s.text
	
	def _disabled_test_rvdsg_opnode(self):
		r = rvsdg_model.rvsdg(('S',))
		n = r.add_opnode('read', ('S',), ('S', 'x'), ((None, 'S'),))
		
		svg = self._to_svg(figure.rvsdg.render_opnode(n))
		expected = \
			'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + \
			'<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">\n' + \
			'<polygon points="0.000000,0.000000 29.200000,0.000000 29.200000,14.000000 0.000000,14.000000 0.000000,0.000000" stroke="black" fill="none" />\n' + \
			'<text x="14.600000" y="9.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">S</text>\n' + \
			'<polygon points="0.000000,14.000000 29.200000,14.000000 29.200000,28.000000 0.000000,28.000000 0.000000,14.000000" stroke="black" fill="none" />\n' + \
			'<text x="14.600000" y="23.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">read</text>\n' + \
			'<polygon points="0.000000,28.000000 14.600000,28.000000 14.600000,42.000000 0.000000,42.000000 0.000000,28.000000" stroke="black" fill="none" />\n' + \
			'<text x="7.300000" y="37.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">S</text>\n' + \
			'<polygon points="14.600000,28.000000 29.200000,28.000000 29.200000,42.000000 14.600000,42.000000 14.600000,28.000000" stroke="black" fill="none" />\n' + \
			'<text x="21.900000" y="37.666667" font-family="Courier,monospace" font-size="10" text-anchor="middle">x</text>\n' + \
			'</svg>\n'
		self.assertEqual(expected, svg)
	
	def _disabled_test_simple_rvsdg(self):
		G = rvsdg_model.rvsdg(('v1', 'v2'))
		add = G.add_opnode('add', ('o1', 'o2'), ('sum',), ((None, 'v1'), (None, 'v2')))
		sub = G.add_opnode('sub', ('o1', 'o2'), ('dif',), ((None, 'v1'), (None, 'v2')))
		G.add_result('v1', (add, 'sum'))
		G.add_result('v2', (sub, 'dif'))
		
		svg = self._to_svg(figure.rvsdg.render_rvsdg_interior(G))
		expected = \
			'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + \
			'<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">\n' + \
			'<polygon points="2.500000,22.500000 20.100000,22.500000 20.100000,36.500000 2.500000,36.500000 2.500000,22.500000" stroke="black" fill="none" />\n' + \
			'<text x="11.300000" y="32.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">o1</text>\n' + \
			'<polygon points="20.100000,22.500000 37.700000,22.500000 37.700000,36.500000 20.100000,36.500000 20.100000,22.500000" stroke="black" fill="none" />\n' + \
			'<text x="28.900000" y="32.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">o2</text>\n' + \
			'<polygon points="2.500000,36.500000 37.700000,36.500000 37.700000,50.500000 2.500000,50.500000 2.500000,36.500000" stroke="black" fill="none" />\n' + \
			'<text x="20.100000" y="46.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">add</text>\n' + \
			'<polygon points="2.500000,50.500000 37.700000,50.500000 37.700000,64.500000 2.500000,64.500000 2.500000,50.500000" stroke="black" fill="none" />\n' + \
			'<text x="20.100000" y="60.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">sum</text>\n' + \
			'<polygon points="42.700000,22.500000 60.300000,22.500000 60.300000,36.500000 42.700000,36.500000 42.700000,22.500000" stroke="black" fill="none" />\n' + \
			'<text x="51.500000" y="32.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">o1</text>\n' + \
			'<polygon points="60.300000,22.500000 77.900000,22.500000 77.900000,36.500000 60.300000,36.500000 60.300000,22.500000" stroke="black" fill="none" />\n' + \
			'<text x="69.100000" y="32.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">o2</text>\n' + \
			'<polygon points="42.700000,36.500000 77.900000,36.500000 77.900000,50.500000 42.700000,50.500000 42.700000,36.500000" stroke="black" fill="none" />\n' + \
			'<text x="60.300000" y="46.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">sub</text>\n' + \
			'<polygon points="42.700000,50.500000 77.900000,50.500000 77.900000,64.500000 42.700000,64.500000 42.700000,50.500000" stroke="black" fill="none" />\n' + \
			'<text x="60.300000" y="60.166667" font-family="Courier,monospace" font-size="10" text-anchor="middle">dif</text>\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 31.400000,7.500000 -20.100000,15.000000" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 13.275096,17.906636 -1.975096,4.593364 4.965518,-0.586199" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 49.000000,7.500000 -20.100000,15.000000" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 30.875096,17.906636 -1.975096,4.593364 4.965518,-0.586199" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 31.400000,7.500000 20.100000,15.000000" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 46.534482,21.913801 4.965518,0.586199 -1.975096,-4.593364" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 49.000000,7.500000 20.100000,15.000000" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 64.134482,21.913801 4.965518,0.586199 -1.975096,-4.593364" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 20.100000,64.500000 -0.000000,15.000000" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 17.600000,75.169873 2.500000,4.330127 2.500000,-4.330127" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 60.300000,64.500000 -0.000000,15.000000" />\n' + \
			'<path style="stroke:#000000;stroke-width:1;fill:none" d="m 57.800000,75.169873 2.500000,4.330127 2.500000,-4.330127" />\n' + \
			'</svg>\n'
		
		#print svg
		#self.assertEqual(expected, svg)
	
	def _disabled_test_rvsdg_gamma(self):
		G = rvsdg_model.rvsdg(('v1', 'v2'))
		c = G.add_opnode('gt', ('v1', 'v2'), ('pred',), ((None, 'v1'), (None, 'v2')))
		
		a1 = rvsdg_model.rvsdg(('v1', 'v2'))
		add = a1.add_opnode('add', ('o1', 'o2'), ('r',), ((None, 'v1'), (None, 'v2')))
		a1.add_result('r', (add, 'r'))
		
		a2 = rvsdg_model.rvsdg(('v1', 'v2'))
		sub = a2.add_opnode('sub', ('o1', 'o2'), ('r',), ((None, 'v1'), (None, 'v2')))
		a2.add_result('r', (sub, 'r'))
		
		g = G.add_gamma((a1, a2), ((None, 'v1'), (None, 'v2')), (c, 'pred'))
		G.add_result('r', (g, 'r'))
		
		svg = self._to_svg(figure.rvsdg.render_rvsdg_interior(G))
		#print svg
	
	def _disabled_test_rvsdg_theta(self):
		G = rvsdg_model.rvsdg(('v1',))
		
		body = rvsdg_model.rvsdg(('v1',))
		dec = body.add_opnode('dec', ('v1',), ('r', '$pred'), ((None, 'v1'),))
		body.add_result('v1', (dec, 'r'))
		body.add_result('$repeat', (dec, '$pred'))
		theta = G.add_theta(body, ((None, 'v1'),))
		G.add_result('v1', (theta, 'v1'))
		
		svg = self._to_svg(figure.rvsdg.render_rvsdg_interior(G))
		#self.assertEqual(theta_expect, svg)

if __name__ == '__main__':
	unittest.main()
