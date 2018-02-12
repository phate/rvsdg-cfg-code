import cfg_model
import figure
import stmts
#import cfg_layout

G = cfg_model.cfg()
entry = G.make_node(stmts.null_stmt())
exit = G.make_node(stmts.null_stmt())
n_if = G.make_node('branch p1')
G.make_edge(entry, n_if)
n_then = G.make_node('branch p2')
G.make_edge(n_if, n_then, index = 0)
n_else = G.make_node('let a := 1')
G.make_edge(n_if, n_else, index = 1)
n_thenthen = G.make_node('let a := 2')
G.make_edge(n_then, n_thenthen, index = 0)
n_thenelse = G.make_node('let a := 3')
G.make_edge(n_then, n_thenelse, index = 1)
n_close1 = G.make_node('let b := a')
G.make_edge(n_else, n_close1)
G.make_edge(n_thenelse, n_close1)
n_close2 = G.make_node('let b := a')
G.make_edge(n_close1, n_close2)
G.make_edge(n_thenthen, n_close2)
G.make_edge(n_close2, exit)

cv = figure.base.canvas()
l = figure.digraph.cfg_to_graph_layout(G)
cv.add(l)
l.layout(0, 0)

import sys
cv.render(sys.stdout)
