import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

a = make_node('branch 0=x')
tab.attach(a, 0, 0, 4)
c = make_node('branch 0=y')
tab.attach(c, 1, 2, 2)
e = make_node('null')
tab.attach(e, 2, 6, 1)
f = make_node('z := x mod y')
tab.attach(f, 1, 4, 1)
g = make_node('x, y := y, z')
tab.attach(g, 1, 5, 1)
h = make_node('null')
tab.attach(h, 1, 6, 1)
j = make_node('x := y')
tab.attach(j, 3, 7, 1)
k = make_node('return x')
tab.attach(k, 0, 8, 4)

n0 = figure.base.nullshape()
n1 = figure.base.nullshape()
tab.attach(n0, 0, 2, 1)
tab.attach(n1, 0, 6, 1)
n2 = figure.base.nullshape()
tab.attach(n2, 3, 2, 1)
n3 = figure.base.nullshape()
tab.attach(n3, 2, 4, 1)

make_edge(a, c, origin_rel = 0.3, origin_label='0', origin_label_orient = +1, style = figure.base.DOTTED)
make_edge(a, j, origin_rel = 0.7, origin_label='1', origin_label_orient = -1, intermediate_stops=[(n2, 0, 0)], style = figure.base.DOTTED)
make_edge(c, f, origin_rel = 0.3, origin_label='0', origin_label_orient = +1, style = figure.base.DOTTED)
make_edge(c, e, origin_rel = 0.9, origin_label='1', origin_label_orient = -1, style = figure.base.DOTTED, intermediate_stops=[(n3, 0, 0)])
make_edge(f, g)
make_edge(g, h)
make_edge(e, k, style = figure.base.DOTTED)
make_edge(h, c, origin_y = 0.5, origin_rel = 0, target_y = 0.5, target_rel = 0, intermediate_stops=[(n1, 0, 0), (n0, 0, 0)], style = figure.base.DOTTED)
make_edge(j, k, target_rel = 0.7)

import sys
cv.render_pst(sys.stdout)
