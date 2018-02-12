import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

a = make_node('P, a := A(P)')
branch_a = make_node('branch a')
b = make_node('P := B(P)')
bp = make_node('b := B''(P)')
branch_b = make_node('branch b')
c = make_node('P := C(P)')
cp = make_node('c := C''(P)')
branch_c = make_node('branch c')
d = make_node('P := D(P)')
e = make_node('P := E(P)')
stop = make_node('return')

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

tab.attach(a, 0, 0, 4)
tab.attach(branch_a, 0, 1, 4)
tab.attach(b, 0, 3, 2)
tab.attach(bp, 0, 4)
tab.attach(branch_b, 0, 5, 2)
tab.attach(d, 0, 7, 2)
tab.attach(c, 2, 3, 2)
tab.attach(cp, 3, 4)
tab.attach(branch_c, 2, 5, 2)
tab.attach(e, 2, 7, 2)
tab.attach(stop, 0, 8, 4)

make_edge(a, branch_a)
aE0 = make_edge(branch_a, b, origin_rel=0.3, origin_label='0', origin_label_orient = +1)
aE1 = make_edge(branch_a, c, origin_rel=0.7, origin_label='1', origin_label_orient = -1)

make_edge(b, bp, origin_rel = 0.3)
make_edge(bp, branch_b, target_rel = 0.3)
aX0 = make_edge(branch_b, d, origin_label='0', origin_label_orient = +1)
aR0 = make_edge(branch_b, c, origin_rel = 0.7, origin_y = 0, target_rel = 0.3, target_y = 1, origin_label='1', origin_label_orient = -1)

make_edge(c, cp, origin_rel = 0.7)
make_edge(cp, branch_c, target_rel = 0.7)
aX1 = make_edge(branch_c, e, origin_label='0', origin_label_orient = -1)
aR1 = make_edge(branch_c, b, origin_rel = 0.3, origin_y = 0, target_rel = 0.7, target_y = 1, origin_label='1', origin_label_orient = +1)

figure.base.anchored_label('$v^E_0$', b, 0, -0.2, 'bl', canvas = cv)
figure.base.anchored_label('$v^E_1$', c, 1, -0.2, 'br', canvas = cv)

figure.base.anchored_label('$v^X_0$', d, 0, 1.1, 'tl', canvas = cv)
figure.base.anchored_label('$v^X_1$', e, 1, 1.1, 'tr', canvas = cv)

figure.base.anchored_label('$a^E_0$', aE0, 0.5, 0.5, 'br', canvas = cv)
figure.base.anchored_label('$a^E_1$', aE1, 0.5, 0.5, 'bl', canvas = cv)

figure.base.anchored_label('$a^X_0$', aX0, 0.5, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$a^X_1$', aX1, 0.5, 0.5, 'l', canvas = cv)

figure.base.anchored_label('$a^R_0$', aR0, 0.2, 0.7, 'tl', canvas = cv)
figure.base.anchored_label('$a^R_1$', aR1, 0.7, 0.7, 'tr', canvas = cv)

make_edge(d, stop, target_rel = 0.3)
make_edge(e, stop, target_rel = 0.7)

box_head = figure.base.box(surrounds = (b, bp, branch_b, c, cp, branch_c), canvas = cv, pad = 0.1, style = figure.base.DASHED)

import sys
cv.render_pst(sys.stdout)
