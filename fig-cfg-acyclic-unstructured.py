import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

a = make_node('a := greater(y, 0)')
branch1 = make_node('branch a')
b = make_node('b := greater(x, 0)')
branch2 = make_node('branch b')
ct = figure.base.nullshape()
cb = figure.base.nullshape()
d = make_node('x := x + y')
e = make_node('x := x - y')
f = make_node('x := x * x')
stop = make_node('return x')

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

tab.attach(a, 0, 0, 3)
tab.attach(branch1, 0, 1, 3)
tab.attach(b, 0, 3, 2)
tab.attach(ct, 2, 3)
tab.attach(cb, 2, 5)
tab.attach(branch2, 0, 4, 2)
tab.attach(d, 0, 5)
tab.attach(e, 1, 5)
tab.attach(f, 1, 6, 2)
tab.attach(stop, 0, 7, 3)

box_head = figure.base.box(surrounds = (a, branch1), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_b1 = figure.base.box(surrounds = (b, branch2, d, e), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_b2 = figure.base.box(surrounds = (cb, ct,), canvas = cv, pad = 0.3, style = figure.base.DASHED)
box_tail = figure.base.box(surrounds = (f, stop), canvas = cv, pad = 0.1, style = figure.base.DASHED)

figure.base.anchored_label('$\\CfgH$', box_head, 0, 0, 'tr', canvas = cv)
figure.base.anchored_label('$\\CfgB_0$', box_b1, 0, 0, 'bl', canvas = cv)
figure.base.anchored_label('$\\CfgB_1$', box_b2, 1, 0, 'br', canvas = cv)
figure.base.anchored_label('$\\CfgT$', box_tail, 0, 1, 'br', canvas = cv)

make_edge(a, branch1)
aF0 = make_edge(branch1, b, origin_rel=0.3, origin_label='0', origin_label_orient = +1)
aF1 = make_edge(branch1, f, origin_rel=0.7, origin_label='1', origin_label_orient = -1, intermediate_stops = [(ct, 0, 0), (cb, 0, 0)])
make_edge(b, branch2)
make_edge(branch2, d, origin_rel=0.3, origin_label='0', origin_label_orient = +1)
make_edge(branch2, e, origin_rel=0.7, origin_label='1', origin_label_orient = -1)
make_edge(e, f, target_rel=0.3)
make_edge(d, stop, target_rel=0.3)
make_edge(f, stop, target_rel=0.7)

figure.base.anchored_label('$a^F_0$', aF0, 0.5, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$a^F_1$', aF1, 0.5, 0.11, 'l', canvas = cv)

figure.base.anchored_label('$v^T_0$', stop, 1, 0.5, 'l', canvas = cv)
figure.base.anchored_label('$v^T_1$', f, 0, 0.5, 'r', canvas = cv)

#tab.layout(0, 0)

import sys
cv.render_pst(sys.stdout)
