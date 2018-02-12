import cfg_model
import figure
import stmts

cv = figure.base.canvas()

def make_node(label):
	return figure.base.make_text_box(label, canvas = cv)

def make_edge(origin, target, origin_rel = 0.5, target_rel = 0.5):
	e = figure.base.connector_line([(origin, origin_rel, 1), (target, target_rel, 0)], canvas = cv)

a = make_node('let P, a := A(P)')
branch1 = make_node('branch a')
b = make_node('let P, b := B(P)')
branch2 = make_node('branch b')
c = make_node('let P := C(P)')
d = make_node('let P := D(P)')
e = make_node('let P := E(P)')
f = make_node('let P := F(P)')
stop = make_node('stop')

tab = figure.base.tabular(hpad=0.3, vpad=0.5, canvas = cv)

tab.attach(a, 0, 0, 3)
tab.attach(branch1, 0, 1, 3)
tab.attach(b, 0, 2, 2)
tab.attach(c, 2, 2)
tab.attach(branch2, 0, 3, 2)
tab.attach(d, 0, 4)
tab.attach(e, 1, 4)
tab.attach(f, 1, 5, 2)
tab.attach(stop, 0, 6, 3)

box_head = figure.base.box(surrounds = (a, branch1), canvas = cv, pad = 0.1, style = figure.base.dashed)
box_b1 = figure.base.box(surrounds = (b, branch2, d, e), canvas = cv, pad = 0.1, style = figure.base.dashed)
box_b2 = figure.base.box(surrounds = (c,), canvas = cv, pad = 0.1, style = figure.base.dashed)
box_tail = figure.base.box(surrounds = (f, stop), canvas = cv, pad = 0.1, style = figure.base.dashed)

figure.base.annotation_digit(1, anchor = box_head, relx = 0.0, rely = 0.0, alignx = -1, aligny = +1, pad = 0.1, canvas = cv)
figure.base.annotation_digit(2, anchor = box_b1, relx = 0.0, rely = 0.0, alignx = +1, aligny = -1, pad = 0.1, canvas = cv)
figure.base.annotation_digit(3, anchor = box_b2, relx = 1.0, rely = 0.0, alignx = -1, aligny = -1, pad = 0.1, canvas = cv)
figure.base.annotation_digit(4, anchor = box_tail, relx = 0.0, rely = 0.0, alignx = -1, aligny = +1, pad = 0.1, canvas = cv)

make_edge(a, branch1)
make_edge(branch1, b, origin_rel=0.3)
make_edge(branch1, c, origin_rel=0.7)
make_edge(b, branch2)
make_edge(branch2, d, origin_rel=0.3)
make_edge(branch2, e, origin_rel=0.7)
make_edge(c, f, target_rel=0.7)
make_edge(e, f, target_rel=0.3)
make_edge(d, stop, target_rel=0.3)
make_edge(f, stop, target_rel=0.7)

#tab.layout(0, 0)

import sys
cv.render_pst(sys.stdout)
