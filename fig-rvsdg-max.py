import figure

import rvsdg_figure_tools ; from rvsdg_figure_tools import *
cv = figure.base.canvas()
rvsdg_figure_tools.cv = cv

root = rvsdg_region('xy', 'z', root = True)

l_region = rvsdg_region('xy', 'z')
l_op = make_opnode('ii', 'sub', 'i')
l_region.attach(l_op.node, 0, 0)
make_edge(l_region.args[0], l_op.inputs[0])
make_edge(l_region.args[1], l_op.inputs[1])
make_edge(l_op.outputs[0], l_region.ress[0])

r_region = rvsdg_region('xy', 'z')
r_op = make_opnode('ii', 'sub', 'i')
r_region.attach(r_op.node, 0, 0)
make_edge(r_region.args[0], r_op.inputs[1])
make_edge(r_region.args[1], r_op.inputs[0])
make_edge(r_op.outputs[0], r_region.ress[0])

root_compare = make_opnode('ii', 'greater', '$')
make_edge(root.args[0], root_compare.inputs[0])
make_edge(root.args[1], root_compare.inputs[1])
root.attach(root_compare.node, 0, 1, 1)
p1 = figure.base.nullshape()
root.attach(p1, 1, 0, 1)
p2 = figure.base.nullshape()
root.attach(p2, 1, 1, 1)
root_gamma1 = make_gammanode('$xy', [r_region, l_region], 'z')
make_edge(root_compare.outputs[0], root_gamma1.inputs[0])
make_edge(root.args[0], root_gamma1.inputs[1], intermediate_stops=[(p1,0,0), (p2,0,0)])
make_edge(root.args[1], root_gamma1.inputs[2])
root.attach(root_gamma1.node, 0, 2, 3)
make_edge(root_gamma1.outputs[0], root.ress[0])

import sys
cv.render_pst(sys.stdout)
