import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

a = make_node('P, a := A(P)')
branch_a = make_node('branch a')
prologue_b = make_node('q := 0')
prologue_c = make_node('q := 1')
entry = make_node('branch q')
b = make_node('P := B(P)')
bp = make_node('b := B''(P)')
branch_b = make_node('branch b')
c = make_node('P := C(P)')
cp = make_node('c := C''(P)')
branch_c = make_node('branch c')

b_break = make_node('q,r:=0,0')
b_cont = make_node('q,r:=1,1')

c_break = make_node('q,r:=1,0')
c_cont = make_node('q,r:=0,1')

rep = make_node('branch r')

epilogue = make_node('branch q')

d = make_node('P := D(P)')
e = make_node('P := E(P)')
stop = make_node('return')

n1 = figure.base.nullshape()
n2 = figure.base.nullshape()

tab = figure.base.tabular(hpad=0.15, vpad=0.3, canvas = cv)

tab.attach(a, 0, 0, 4)
tab.attach(branch_a, 0, 1, 4)
tab.attach(prologue_b, 0, 2, 2)
tab.attach(prologue_c, 2, 2, 2)
tab.attach(entry, 0, 3, 4)
tab.attach(n1, 4, 3, 1)
tab.attach(b, 0, 4, 2)
tab.attach(bp, 0, 5, 2)
tab.attach(branch_b, 0, 6, 2)
tab.attach(b_break, 0, 7, 1)
tab.attach(b_cont, 1, 7, 1)
tab.attach(c, 2, 4, 2)
tab.attach(cp, 2, 5, 2)
tab.attach(branch_c, 2, 6, 2)
tab.attach(c_break, 2, 7, 1)
tab.attach(c_cont, 3, 7, 1)
tab.attach(rep, 0, 8, 4)
tab.attach(n2, 4, 8, 1)
tab.attach(epilogue, 0, 9, 4)

tab.attach(d, 0, 11, 2)
tab.attach(e, 2, 11, 2)
tab.attach(stop, 0, 12, 4)

make_edge(a, branch_a)
aE0 = make_edge(branch_a, prologue_b, origin_rel=0.3, origin_label='0', origin_label_orient = +1)
aE1 = make_edge(branch_a, prologue_c, origin_rel=0.7, origin_label='1', origin_label_orient = -1)

make_edge(prologue_b, entry, target_rel = 0.3)
make_edge(prologue_c, entry, target_rel = 0.7)

make_edge(entry, b, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
make_edge(entry, c, origin_rel = 0.7, origin_label='1', origin_label_orient = -1)

make_edge(b, bp, origin_rel = 0.3)
make_edge(bp, branch_b, target_rel = 0.3)
make_edge(branch_b, b_break, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
make_edge(branch_b, b_cont, origin_rel = 0.7, origin_label='1', origin_label_orient = -1)

make_edge(c, cp, origin_rel = 0.7)
make_edge(cp, branch_c, target_rel = 0.7)
make_edge(branch_c, c_break, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
make_edge(branch_c, c_cont, origin_rel = 0.7, origin_label='1', origin_label_orient = -1)

make_edge(b_break, rep, target_rel = 0.2)
make_edge(b_cont, rep, target_rel = 0.4)
make_edge(c_break, rep, target_rel = 0.6)
make_edge(c_cont, rep, target_rel = 0.8)

make_edge(rep, epilogue, origin_label = '0', origin_label_orient = -1)
make_edge(rep, entry, origin_label = '1', origin_label_orient = +1, origin_rel = 1, origin_y = 0.5, target_rel = 1, target_y = 0.5, style = figure.base.DOTTED, intermediate_stops = [(n2, 0, 0), (n1, 0, 0)])

aX0 = make_edge(epilogue, d, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
aX1 = make_edge(epilogue, e, origin_rel = 0.7, origin_label='1', origin_label_orient = -1)

make_edge(d, stop, target_rel = 0.3)
make_edge(e, stop, target_rel = 0.7)

box_head = figure.base.box(surrounds = (entry, b, bp, branch_b, c, cp, branch_c, rep, n1, n2, b_break, b_cont, c_break, c_cont), canvas = cv, pad = 0.1, style = figure.base.DASHED)

figure.base.anchored_label('$v^{E*}$', entry, 0, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$v^{T*}$', rep, 0, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$v^{X*}$', epilogue, 0, 0.5, 'r', canvas = cv)

figure.base.anchored_label('$v^E_0$', b, 0, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$v^E_1$', c, 1, 0.5, 'l', canvas = cv)

figure.base.anchored_label('$v^X_0$', d, 0, 0.5, 'r', canvas = cv)
figure.base.anchored_label('$v^X_1$', e, 1, 0.5, 'l', canvas = cv)

figure.base.anchored_label('$a^E_0$', aE0, 0.5, 0.5, 'br', canvas = cv)
figure.base.anchored_label('$a^E_1$', aE1, 0.5, 0.5, 'bl', canvas = cv)

figure.base.anchored_label('$a^X_0$', aX0, 0.3, 0.7, 'rb', canvas = cv)
figure.base.anchored_label('$a^X_1$', aX1, 0.7, 0.7, 'lb', canvas = cv)

#figure.base.anchored_label('$a^R_0$', aR0, 0.2, 0.7, 'tl', canvas = cv)
#figure.base.anchored_label('$a^R_1$', aR1, 0.7, 0.7, 'tr', canvas = cv)


import sys
cv.render_pst(sys.stdout)
