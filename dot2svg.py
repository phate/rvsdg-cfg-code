import sys

import dotparse
import figure

cfg = dotparse.parse_dot_to_cfg(sys.stdin.readlines())

cv = figure.base.canvas()
l = figure.digraph.cfg_to_graph_layout(cfg)
cv.add(l)
l.layout(0, 0)

cv.render(sys.stdout)
