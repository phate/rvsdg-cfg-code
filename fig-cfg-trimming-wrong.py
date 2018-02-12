import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

a = make_node('P, a := A(P)')
b = make_node('P := B(P)')
branch_a = make_node('branch a')
c = make_node('P, c := C(P)')
branch_c = make_node('branch c')
branch_demux = make_node('branch p')
p0 = make_node('p := 0')
p1 = make_node('p := 1', style = figure.base.THICK_GRAYED)
exit = make_node('null')

lp0 = make_node('p := 0')
lp1 = make_node('p := 1')
rp1 = make_node('p := 1')
lnull = make_node('null')
tab = figure.base.tabular(hpad=0.4, vpad=0.5, canvas = cv)

tab.attach(a, 0, 0, 3)
tab.attach(branch_a, 0, 1, 3)
tab.attach(b, 2, 2)
tab.attach(c, 0, 2, 2)
tab.attach(branch_c, 0, 3, 2)
tab.attach(p1, 0, 4, 1)
tab.attach(lp0, 0, 5, 1)
tab.attach(lp1, 1, 5, 1)
tab.attach(rp1, 2, 5, 1)
tab.attach(lnull, 0, 6, 2)
tab.attach(branch_demux, 0, 7, 3)
tab.attach(p0, 2, 8, 1)
tab.attach(exit, 0, 9, 3)

make_edge(a, branch_a)
make_edge(branch_a, c, origin_rel=0.3, origin_label='0', origin_label_orient=+1)
make_edge(branch_a, b, origin_rel=0.7, origin_label='1', origin_label_orient=-1, target_rel=0.7)
make_edge(b, rp1)
make_edge(c, branch_c)
make_edge(branch_c, p1, origin_rel=0.2, origin_label='0', origin_label_orient=+1)
make_edge(branch_c, lp1, origin_rel=0.8, origin_label='1', origin_label_orient=-1)
make_edge(p0, exit, target_rel=0.7)
make_edge(p1, lp0)
make_edge(lp0, lnull, target_rel=0.3)
make_edge(lp1, lnull, target_rel=0.7)
make_edge(lnull, branch_demux, target_rel=0.3)
make_edge(rp1, branch_demux, target_rel=0.7)
make_edge(branch_demux, p0, origin_rel=0.7, origin_label='1')
make_edge(branch_demux, exit, origin_label='0', origin_label_orient=-1)

box_head = figure.base.box(surrounds = (a, branch_a), canvas = cv, pad = 0.1, style = figure.base.DOTTED)
box_b1 = figure.base.box(surrounds = (c, branch_c, p1, lp0, lp1, lnull), canvas = cv, pad = 0.1, style = figure.base.DOTTED)
box_b2 = figure.base.box(surrounds = (b,rp1), canvas = cv, pad = 0.1, style = figure.base.DOTTED)
box_tail = figure.base.box(surrounds = (branch_demux, p0, exit), canvas = cv, pad = 0.1, style = figure.base.DOTTED)

figure.base.anchored_label('$\\CfgH^*$', box_head, 0, 0, 'tr', canvas = cv)
figure.base.anchored_label('$\\CfgB_0^*$', box_b1, 0, 0, 'bl', canvas = cv)
figure.base.anchored_label('$\\CfgB_1^*$', box_b2, 1, 0, 'br', canvas = cv)
figure.base.anchored_label('$\\CfgT^*$', box_tail, 1, 1, 'br', canvas = cv)

import sys
cv.render_pst(sys.stdout)
