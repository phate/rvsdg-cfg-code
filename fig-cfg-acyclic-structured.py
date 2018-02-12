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
cb = figure.base.nullshape()
ct = figure.base.nullshape()
cl = make_node('p := 1')
d = make_node('x := x + y')
e = make_node('x := x - y')
dl = make_node('p := 0')
el = make_node('p := 1')
join1 = make_node('null')
rebranch = make_node('branch p')
f = make_node('x := x * x')
stop = make_node('return x')



tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

tab.attach(a, 0, 0, 3)
tab.attach(branch1, 0, 1, 3)
tab.attach(b, 0, 3, 2)
tab.attach(ct, 2, 3)
tab.attach(cl, 2, 5)
tab.attach(cb, 2, 7)
tab.attach(branch2, 0, 4, 2)
tab.attach(d, 0, 5)
tab.attach(e, 1, 5)
tab.attach(dl, 0, 6)
tab.attach(el, 1, 6)
tab.attach(join1, 0, 7, 2)
tab.attach(rebranch, 0, 8, 3)
tab.attach(f, 1, 9, 2)
tab.attach(stop, 0, 10, 3)

box_head = figure.base.box(surrounds = (a, branch1), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_b1 = figure.base.box(surrounds = (b, branch2, d, e, dl, el, join1), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_b2 = figure.base.box(surrounds = (cb, cl, ct), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_tail = figure.base.box(surrounds = (f, stop, rebranch), canvas = cv, pad = 0.1, style = figure.base.DASHED)

figure.base.anchored_label('$\\CfgH^*$', box_head, 0, 0, 'tr', canvas = cv)
figure.base.anchored_label('$\\CfgB^*_0$', box_b1, 0, 0, 'bl', canvas = cv)
figure.base.anchored_label('$\\CfgB^*_1$', box_b2, 1, 0, 'br', canvas = cv)
figure.base.anchored_label('$\\CfgT^*$', box_tail, 0, 1, 'br', canvas = cv)

figure.base.anchored_label('$v^{T*}$', rebranch, 1.1, 0.5, 'l', canvas = cv)

make_edge(a, branch1)
aF0 = make_edge(branch1, b, origin_rel=0.3, origin_label='0', origin_label_orient = +1)
aF1 = make_edge(branch1, cl, origin_rel=0.7, origin_label='1', origin_label_orient = -1, intermediate_stops = [(ct, 0, 0)])
make_edge(b, branch2)
make_edge(branch2, d, origin_rel=0.3, origin_label='0', origin_label_orient = +1)
make_edge(branch2, e, origin_rel=0.7, origin_label='1', origin_label_orient = -1)
make_edge(e, el)
make_edge(d, dl)
make_edge(dl, join1, target_rel=0.3)
make_edge(el, join1, target_rel=0.7)
make_edge(cl, rebranch, target_rel=0.7, intermediate_stops = [(cb, 0, 0)])
make_edge(join1, rebranch, target_rel=0.3)
make_edge(rebranch, f, origin_rel=0.7, origin_label='1', origin_label_orient = -1)
make_edge(rebranch, stop, origin_rel=0.3, target_rel=0.3, origin_label='0', origin_label_orient = +1)
make_edge(f, stop, target_rel=0.7)

figure.base.anchored_label('$a^F_0$', aF0, 0.5, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$a^F_1$', aF1, 0.5, 0.15, 'l', canvas = cv)

figure.base.anchored_label('$v^T_0$', stop, 1, 0.5, 'l', canvas = cv)
figure.base.anchored_label('$v^T_1$', f, 1, 0, 'rb', canvas = cv)

#tab.layout(0, 0)

import sys
cv.render_pst(sys.stdout)
