import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

a = make_node('P, a := A(P)')
b = make_node('P:= B(P)')
branch_a = make_node('branch a')
c = make_node('P, c := C(P)')
branch_c = make_node('branch c')
p0 = make_node('p := 0')
p1 = make_node('p := 1', style = figure.base.THICK_GRAYED)
exit = make_node('null')

tab = figure.base.tabular(hpad=0.4, vpad=0.5, canvas = cv)

tab.attach(a, 0, 0, 3)
tab.attach(branch_a, 0, 1, 3)
tab.attach(b, 2, 3, 1)
tab.attach(c, 0, 3, 2)
tab.attach(branch_c, 0, 4, 2)
tab.attach(p1, 0, 5, 1)
tab.attach(p0, 2, 6, 1)
tab.attach(exit, 0, 7, 3)

make_edge(a, branch_a)
aF0 = make_edge(branch_a, c, origin_rel=0.3, origin_label='0', origin_label_orient=+1)
aF1 = make_edge(branch_a, b, origin_rel=0.7, origin_label='1', origin_label_orient=-1, target_rel=0.7)
make_edge(b, p0)
make_edge(c, branch_c)
make_edge(branch_c, p1, origin_label='0', origin_label_orient=+1)
make_edge(branch_c, p0, origin_rel=0.8, origin_label='1', target_rel=0.3)
make_edge(p1, exit, target_rel=0.3)
make_edge(p0, exit, target_rel=0.7)

figure.base.anchored_label('$a^F_0$', aF0, 0.5, 0.4, 'r', canvas = cv)
figure.base.anchored_label('$a^F_1$', aF1, 0.5, 0.4, 'l', canvas = cv)

box_b1b = figure.base.box(surrounds = (c, branch_c, p1), canvas = cv, pad = 0.15, style = figure.base.DOTTED)
box_b2b = figure.base.box(surrounds = (b,), canvas = cv, pad = 0.15, style = figure.base.DOTTED)

box_head = figure.base.box(surrounds = (a, branch_a), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_b1 = figure.base.box(surrounds = (c, branch_c), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_b2 = figure.base.box(surrounds = (b,), canvas = cv, pad = 0.1, style = figure.base.DASHED)
box_tail = figure.base.box(surrounds = (p0, p1, exit), canvas = cv, pad = 0.15, style = figure.base.DASHED)
box_tailb = figure.base.box(surrounds = (p0, exit), canvas = cv, pad = 0.1, style = figure.base.DOTTED)

figure.base.anchored_label('$\\CfgH$', box_head, 0, 0, 'tr', canvas = cv)
figure.base.anchored_label('$\\CfgB_0$', box_b1b, 0, 0, 'bl', canvas = cv)
figure.base.anchored_label('$\\CfgB_1$', box_b2b, 1, 0, 'br', canvas = cv)
figure.base.anchored_label('$\\CfgT$', box_tailb, 1, 1, 'br', canvas = cv)

import sys
cv.render_pst(sys.stdout)
