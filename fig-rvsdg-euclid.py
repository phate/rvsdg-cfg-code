import figure

import rvsdg_figure_tools ; from rvsdg_figure_tools import *
cv = figure.base.canvas()
rvsdg_figure_tools.cv = cv

region1 = rvsdg_region('xy', ['$r', 'x', 'y'])
mod = make_opnode('ii', 'mod', 'i')
make_edge(region1.args[0], mod.inputs[0])
make_edge(region1.args[1], mod.inputs[1])
region1.attach(mod.node, 1, 0)
n = figure.base.nullshape()
region1.attach(n, 0, 0)
copy = make_opnode('ii', 'copy', 'ii')
make_edge(region1.args[1], copy.inputs[0], intermediate_stops = [(n, 0, 0)])
make_edge(mod.outputs[0], copy.inputs[1])
region1.attach(copy.node, 1, 1)
pred = make_opnode('', '1', '$')
region1.attach(pred.node, 0, 1)
make_edge(pred.outputs[0], region1.ress[0])
make_edge(copy.outputs[0], region1.ress[1])
make_edge(copy.outputs[1], region1.ress[2])

region2 = rvsdg_region('xy', ['$r', 'x', 'y'])
pred = make_opnode('', '0', '$')
region2.attach(pred.node, 0, 1)
n1 = figure.base.nullshape()
n2 = figure.base.nullshape()
region2.attach(n1, 1, 1)
region2.attach(n2, 2, 1)
make_edge(pred.outputs[0], region2.ress[0])
make_edge(region2.args[0], region2.ress[1], intermediate_stops = [(n1, 0, 0)])
make_edge(region2.args[1], region2.ress[2], intermediate_stops = [(n2, 0, 0)])

region3 = rvsdg_region('xy', ['${\\normalsize$\\theta$}', 'x', 'y'])
const0 = make_opnode('', '0', 'i')
region3.attach(const0.node, 0, 0)
comp = make_opnode('ii', 'equals', '$')
region3.attach(comp.node, 0, 1)
make_edge(const0.outputs[0], comp.inputs[0])
make_edge(region3.args[1], comp.inputs[1])
gamma = make_gammanode('$xy', [region1, region2], ['$r', 'x', 'y'])
region3.attach(gamma.node, 0, 2, 3)
make_edge(comp.outputs[0], gamma.inputs[0])
make_edge(region3.args[0], gamma.inputs[1])
make_edge(region3.args[1], gamma.inputs[2])
make_edge(gamma.outputs[0], region3.ress[0])
make_edge(gamma.outputs[1], region3.ress[1])
make_edge(gamma.outputs[2], region3.ress[2])

region4 = rvsdg_region('xy', 'x')
theta = make_thetanode('xy', region3, 'x')
region4.attach(theta.node, 0, 0)
make_edge(region4.args[0], theta.inputs[0])
make_edge(region4.args[1], theta.inputs[1])
make_edge(theta.outputs[0], region4.ress[0])

region5 = rvsdg_region('xy', 'x')
copy = make_opnode('i', 'copy', 'i')
region5.attach(copy.node, 0, 1)
make_edge(region5.args[1], copy.inputs[0])
make_edge(copy.outputs[0], region5.ress[0])

region6 = rvsdg_region('xy', 'x', root = True)
const0 = make_opnode('', '0', 'i')
region6.attach(const0.node, 0, 0)
comp = make_opnode('ii', 'equals', '$')
region6.attach(comp.node, 0, 1)
make_edge(const0.outputs[0], comp.inputs[0])
make_edge(region6.args[0], comp.inputs[1])
gamma = make_gammanode('$xy', [region4, region5], 'x')
region6.attach(gamma.node, 0, 2, 3)
make_edge(comp.outputs[0], gamma.inputs[0])
make_edge(region6.args[0], gamma.inputs[1])
make_edge(region6.args[1], gamma.inputs[2])
make_edge(gamma.outputs[0], region6.ress[0])


#ll_region = rvsdg_region('xy', ['$p', 'x'])
#ll_pred = make_opnode('', 'false', '$')
#ll_region.attach(ll_pred.node, 0, 0)
#ll_op = make_opnode('ii', 'add', 'i')
#make_edge(ll_region.args[0], ll_op.inputs[0])
#make_edge(ll_region.args[1], ll_op.inputs[1])
#ll_region.attach(ll_op.node, 1, 0)
#make_edge(ll_pred.outputs[0], ll_region.ress[0])
#make_edge(ll_op.outputs[0], ll_region.ress[1])

#lr_region = rvsdg_region('xy', ['$p', 'x'])
#lr_pred = make_opnode('', 'true', '$')
#lr_region.attach(lr_pred.node, 0, 0)
#lr_op = make_opnode('ii', 'sub', 'i')
#make_edge(lr_region.args[0], lr_op.inputs[0])
#make_edge(lr_region.args[1], lr_op.inputs[1])
#lr_region.attach(lr_op.node, 1, 0)
#make_edge(lr_pred.outputs[0], lr_region.ress[0])
#make_edge(lr_op.outputs[0], lr_region.ress[1])

#l_region = rvsdg_region('xy', ['$p', 'x'])
#l_null = make_opnode('', '0', 'i')
#l_region.attach(l_null.node, 1, 0, 1)
#l_compare = make_opnode('ii', 'greater', '$')
#make_edge(l_region.args[0], l_compare.inputs[0])
#make_edge(l_null.outputs[0], l_compare.inputs[1])
#l_region.attach(l_compare.node, 0, 1, 1)
#l_gamma = make_gammanode('$xy',
	#[ll_region, lr_region],
	#['$p', 'x'])
#make_edge(l_compare.outputs[0], l_gamma.inputs[0])
#make_edge(l_region.args[0], l_gamma.inputs[1])
#make_edge(l_region.args[1], l_gamma.inputs[2])
#l_region.attach(l_gamma.node, 0, 2, 3)
#make_edge(l_gamma.outputs[0], l_region.ress[0])
#make_edge(l_gamma.outputs[1], l_region.ress[1])

#r_region = rvsdg_region('xy', ['$p', 'x'])
#r_n1 = figure.base.nullshape()
#r_region.attach(r_n1, 1, 0)
#r_pred = make_opnode('', 'true', '$')
#r_region.attach(r_pred.node, 0, 1)
#r_n2 = figure.base.nullshape()
#r_region.attach(r_n2, 1, 2)
#make_edge(r_pred.outputs[0], r_region.ress[0])
#make_edge(r_region.args[0], r_region.ress[1], intermediate_stops = [(r_n1, 0, 0), (r_n2, 0, 0)])

#l2_region = rvsdg_region('x', 'x')
#make_edge(l2_region.args[0], l2_region.ress[0])

#r2_region = rvsdg_region('x', 'x')
#r2_mul = make_opnode('ii', 'mul', 'i')
#make_edge(r2_region.args[0], r2_mul.inputs[0])
#make_edge(r2_region.args[0], r2_mul.inputs[1])
#r2_region.attach(r2_mul.node, 0, 1)
#make_edge(r2_mul.outputs[0], r2_region.ress[0])

#root = rvsdg_region('xy', 'x', root = True)
#root_null = make_opnode('', '0', 'i')
#root.attach(root_null.node, 0, 0, 1)
#root_pred = make_opnode('ii', 'greater', '$')
#make_edge(root.args[1], root_pred.inputs[0])
#make_edge(root_null.outputs[0], root_pred.inputs[1])
#root.attach(root_pred.node, 0, 1, 1)
#root_gamma1 = make_gammanode('$xy', [l_region, r_region], ['$p', 'x'])
#make_edge(root_pred.outputs[0], root_gamma1.inputs[0])
#make_edge(root.args[0], root_gamma1.inputs[1])
#make_edge(root.args[1], root_gamma1.inputs[2])
#root.attach(root_gamma1.node, 0, 2, 3)
#root_gamma2 = make_gammanode('$x', [l2_region, r2_region], 'x')
#make_edge(root_gamma1.outputs[0], root_gamma2.inputs[0])
#make_edge(root_gamma1.outputs[1], root_gamma2.inputs[1])
#root.attach(root_gamma2.node, 0, 3, 3)
#make_edge(root_gamma2.outputs[0], root.ress[0])

import sys
cv.render_pst(sys.stdout)