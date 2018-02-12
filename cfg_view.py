import os
import pygraphviz

def handle_node(node, gvg, structured):
	nsucc = len([s for s in node.succ])
	label = str(node.stmt)
	shape = 'rect'
	return gvg.add_node("n%d" % id(node), label=label, shape=shape, fontsize=10, fontname='Courier', width=0.01, height=0.01)

def handle_edge(edge, gvg):
	label = "%d" % edge.index
	gvg.add_edge("n%d" % id(edge.origin), "n%d" % id(edge.target), label=label, fontsize=5, fontname='Courier', arrowsize=0.25)

def make_gvg(cfg, structured, clusters = ()):
	gvg = pygraphviz.AGraph(directed=True, strict=True, ranksep=0.05, nodesep=0.25, splines='ortho')
	done_nodes = set()
	idx = 0
	for c in clusters:
		gr = gvg.add_subgraph(name='cluster%d' % idx)
		idx += 1
		for node in c:
			handle_node(node, gr, structured)
		done_nodes.add(node)
	for node in cfg.nodes:
		if node not in done_nodes:
			handle_node(node, gvg, structured)
	for edge in cfg.edges.values():
		handle_edge(edge, gvg)
	gvg.layout('dot')
	return gvg

def save(cfg, name, structured = True, clusters = ()):
	gvg = make_gvg(cfg, structured, clusters)
	gvg.draw(name)

def show(cfg, structured = True, clusters = ()):
	gvg = make_gvg(cfg, structured, clusters)
	gvg.draw('/tmp/tmp.png')
	os.system('display /tmp/tmp.png')
