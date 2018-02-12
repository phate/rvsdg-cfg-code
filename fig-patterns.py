import cfg_model
import figure

import cfg_figure_tools ; from cfg_figure_tools import *
cv = figure.base.canvas()
cfg_figure_tools.cv = cv

#linear
lv1 = figure.base.nullshape()
lv2 = make_node('Vertex1')
lv3 = make_node('Vertex2')
lv4 = figure.base.nullshape()
make_edge(lv1, lv2)
make_edge(lv2, lv3)
make_edge(lv3, lv4)

#if then
itv1 = figure.base.nullshape()
itv2 = make_node('Vertex1')
itv3 = make_node('Vertex2')
itv4 = figure.base.nullshape()
make_edge(itv1, itv2)
make_edge(itv2, itv3, origin_rel = 0.3, origin_label = '1', origin_label_orient = +1)
make_edge(itv2, itv4, origin_rel = 0.5, target_rel = 0.7, origin_label = '0', origin_label_orient = +1)
make_edge(itv3, itv4)

#if then else
itev1 = figure.base.nullshape()
itev2 = make_node('Vertex1')
itev3 = make_node('Vertex2')
itev4 = make_node('Vertex3')
itev5 = figure.base.nullshape()
make_edge(itev1, itev2)
make_edge(itev2, itev3, origin_rel = 0.1, origin_label = '1', origin_label_orient = +1)
make_edge(itev2, itev4, origin_rel = 0.9, origin_label = '0', origin_label_orient = -1)
make_edge(itev3, itev5)
make_edge(itev4, itev5)

#self
sv1 = figure.base.nullshape()
sv2 = make_node('Vertex1')
sn1 = figure.base.nullshape()
sn2 = figure.base.nullshape()
sn3 = figure.base.nullshape()
sn4 = figure.base.nullshape()
sv3 = figure.base.nullshape()
make_edge(sv1, sv2, target_rel = 0.7)
make_edge(sv2, sv2, origin_label = '1', origin_label_orient = +1, origin_rel = 0.3,
	target_rel = 0.3, style = figure.base.DASHED,
	intermediate_stops = [(sn1, 0, 0), (sn2, 0, 0), (sn3, 0, 0), (sn4, 0, 0)])
make_edge(sv2, sv3, origin_label = '0', origin_rel = 0.7, origin_label_orient = -1)

#while
#wv1 = figure.base.nullshape()
#wv2 = make_node('Vertex1')
#wv3 = make_node('Vertex2')
#wv4 = figure.base.nullshape()
#wn1 = figure.base.nullshape()
#wn2 = figure.base.nullshape()
#wn3 = figure.base.nullshape()
#wn4 = figure.base.nullshape()
#make_edge(wv1, wv2, target_rel = 0.7)
#make_edge(wv2, wv3, origin_label = '1', origin_rel = 0.3, origin_label_orient = +1)
#make_edge(wv3, wv2, target_rel = 0.3, origin_rel = 0.3, style = figure.base.DASHED,
#	intermediate_stops = [(wn1, 0, 0), (wn2, 0, 0), (wn3, 0, 0), (wn4, 0, 0)])
#make_edge(wv2, wv4, origin_label = '0', origin_rel = 0.7, origin_label_orient = -1)

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

#linear
tab.attach(lv1, 0, 0, 3)
tab.attach(lv2, 0, 1, 3)
tab.attach(lv3, 0, 2, 3)
tab.attach(lv4, 0, 3, 3)

#if then
tab.attach(itv1, 4, 0, 3)
tab.attach(itv2, 4, 1, 3)
tab.attach(itv3, 3, 2, 3)
tab.attach(itv4, 4, 3, 3)

#if then else
tab.attach(itev1, 7, 0, 3)
tab.attach(itev2, 7, 1, 3)
tab.attach(itev3, 6, 2, 3)
tab.attach(itev4, 8, 2, 3)
tab.attach(itev5, 7, 3, 3)

#self
tab.attach(sv1, 13, 1, 3)
tab.attach(sv2, 12, 2, 3)
tab.attach(sv3, 13, 3, 3)
tab.attach(sn1, 11, 3, 3)
tab.attach(sn2, 10, 3, 3)
tab.attach(sn3, 10, 1, 3)
tab.attach(sn4, 11, 1, 3)

#while
#tab.attach(wv1, 26, 0, 3)
#tab.attach(wv2, 25, 1, 3)
#tab.attach(wv3, 24, 2, 3)
#tab.attach(wv4, 26, 2, 3)
#tab.attach(wn1, 23, 3, 3)
#tab.attach(wn2, 22, 3, 3)
#tab.attach(wn3, 22, 0, 3)
#tab.attach(wn4, 24, 0, 3)

import sys
cv.render_pst(sys.stdout)
