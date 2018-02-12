import cfg_model
import figure
import stmts

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

gr = make_node('g := x > y')
tab.attach(gr, 0, 0, 2)
branch_g = make_node('branch g')
tab.attach(branch_g, 0, 1, 2)
sub1 = make_node('z := y - x')
tab.attach(sub1, 0, 2, 1)
sub2 = make_node('z := x - y')
tab.attach(sub2, 1, 2, 1)
exit = make_node('return z')
tab.attach(exit, 0, 3, 2)

make_edge(gr, branch_g)
make_edge(branch_g, sub1, origin_rel = 0.3, origin_label='0', origin_label_orient = +1)
make_edge(branch_g, sub2, origin_rel = 0.7, origin_label='1', origin_label_orient = -1)
make_edge(sub1, exit, target_rel = 0.3)
make_edge(sub2, exit, target_rel = 0.7)

import sys
cv.render_pst(sys.stdout)
