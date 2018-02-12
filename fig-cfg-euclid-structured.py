import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

a = make_node('p := 0=x')
tab.attach(a, 0, 0, 4)
b = make_node('branch p')
tab.attach(b, 0, 1, 4)
c = make_node('p := 0=y')
tab.attach(c, 1, 2, 2)
d = make_node('branch p')
tab.attach(d, 1, 3, 2)
e = make_node('r := 0')
tab.attach(e, 2, 6, 1)
f = make_node('z := x mod y')
tab.attach(f, 1, 4, 1)
g = make_node('x, y := y, z')
tab.attach(g, 1, 5, 1)
h = make_node('r := 1')
tab.attach(h, 1, 6, 1)
i = make_node('branch r')
tab.attach(i, 1, 7, 2)
j = make_node('x := y')
tab.attach(j, 3, 7, 1)
k = make_node('return x')
tab.attach(k, 0, 8, 4)

n0 = figure.base.nullshape()
n1 = figure.base.nullshape()
tab.attach(n0, 0, 2, 1)
tab.attach(n1, 0, 7, 1)
n2 = figure.base.nullshape()
tab.attach(n2, 3, 2, 1)
n3 = figure.base.nullshape()
tab.attach(n3, 2, 4, 1)

make_edge(a, b)
make_edge(b, c, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
make_edge(b, j, origin_rel = 0.7, origin_label='1', origin_label_orient = -1, intermediate_stops=[(n2, 0, 0)])
make_edge(c, d)
make_edge(d, f, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
make_edge(d, e, origin_rel = 0.7, origin_label='1', origin_label_orient = -1, intermediate_stops=[(n3, 0, 0)])
make_edge(f, g)
make_edge(g, h)
make_edge(h, i)
make_edge(e, i, target_rel = 0.7)
make_edge(i, k, origin_label='0', target_rel = 0.3)
make_edge(i, c, origin_label='1', origin_label_orient = -1, origin_y = 0.5, origin_rel = 0, target_y = 0.5, target_rel = 0, intermediate_stops=[(n1, 0, 0), (n0, 0, 0)])
make_edge(j, k, target_rel = 0.7)

import sys
cv.render_pst(sys.stdout)
