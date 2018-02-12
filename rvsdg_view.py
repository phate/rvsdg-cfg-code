import os
import pygraphviz

def make_edge(rvsdg, gvg, origin, target):
	opts = {}
	if origin[0] is None:
		origin_node = "a%d%s" % (id(rvsdg), origin[1])
	elif isinstance(origin[0], rvsdg.thetanode) or isinstance(origin[0], rvsdg.gammanode):
		origin_node = "no%d" % id(origin[0])
		opts["tailport"] = "o%s" % origin[1]
	else:
		origin_node = "n%d" % id(origin[0])
		opts["tailport"] = "o%s" % origin[1]
	
	if target[0] is None:
		target_node = "r%d%s" % (id(rvsdg), target[1])
	elif isinstance(target[0], rvsdg.thetanode) or isinstance(target[0], rvsdg.gammanode):
		target_node = "ni%d" % id(target[0])
		opts["headport"] = "i%s" % target[1]
	else:
		target_node = "n%d" % id(target[0])
		opts["headport"] = "i%s" % target[1]
	gvg.add_edge(origin_node, target_node, **opts)

def handle_opnode(rvsdg, gvg, n):
	name = "n%d" % id(n)
	top = "|".join("<i%s> %s" % (i,i) for i in n.input_names)
	bot = "|".join("<o%s> %s" % (o,o) for o in n.output_names)
	label="{{%s}|%s|{%s}}" % (top, n.operator, bot)
	gvg.add_node(name, shape="record", label=label)
	
	for i, v in zip(n.input_names, n.operands):
		tgt = "%s:i%s" % (name, i)
		make_edge(rvsdg, gvg, v, (n, i))

def handle_litnode(rvsdg, gvg, n):
	name = "n%d" % id(n)
	top = "|".join("<i%s> %s" % (i,i) for i in n.input_names)
	bot = "|".join("<o%s> %s" % (o,o) for o in n.output_names)
	label="{{%s}|%s|{%s}}" % (top, str(n.values), bot)
	gvg.add_node(name, shape="record", label=label)
	
	for i, v in zip(n.input_names, n.operands):
		tgt = "%s:i%s" % (name, i)
		make_edge(rvsdg, gvg, v, (n, i))

def handle_thetanode(rvsdg, gvg, n):
	ng = gvg.add_subgraph(name = "cluster_n%d" % id(n))
	
	igrp = "ni%d" % id(n)
	ng.add_node(igrp, shape="record", label = "|".join("<i%s> %s" % (i,i) for i in n.input_names))
	for i, v in zip(n.input_names, n.operands):
		make_edge(rvsdg, gvg, v, (n, i))
	
	bg = ng.add_subgraph(name = "cluster_g%d" % id(n.body))
	handle_region(n.body, bg)
	
	ogrp = "no%d" % id(n)
	ng.add_node(ogrp, shape="record", label = "|".join("<o%s> %s" % (o,o) for o in n.output_names))
	
	for i in n.input_names:
		ng.add_edge(igrp, "a%d%s" % (id(n.body), i), tailport="i%s" % i)
	
	for o in n.output_names:
		ng.add_edge("r%d%s" % (id(n.body), o), ogrp, headport="o%s" % o)

def handle_gammanode(rvsdg, gvg, n):
	ng = gvg.add_subgraph(name = "cluster_n%d" % id(n))
	
	igrp = "ni%d" % id(n)
	ng.add_node(igrp, shape="record", label = "|".join("<i%s> %s" % (i,i) for i in n.input_names))
	for i, v in zip(n.input_names, n.operands):
		make_edge(rvsdg, gvg, v, (n, i))
	
	ogrp = "no%d" % id(n)
	ng.add_node(ogrp, shape="record", label = "|".join("<o%s> %s" % (o,o) for o in n.output_names))
	
	index = 0
	for a in n.alternatives:
		bg = ng.add_subgraph(name = "cluster_g%d" % id(a), label="%d" % index)
		index += 1
		handle_region(a, bg)
		for i in a.arguments:
			ng.add_edge(igrp, "a%d%s" % (id(a), i), tailport="i%s" % i)
		for o in a.results:
			ng.add_edge("r%d%s" % (id(a), o), ogrp, headport="o%s" % o)
	
	
def handle_region(rvsdg, gvg):
	for arg in rvsdg.arguments:
		n = gvg.add_node("a%d%s" % (id(rvsdg), arg), label=arg)
	for n in rvsdg.nodes:
		if isinstance(n, rvsdg.opnode):
			handle_opnode(rvsdg, gvg, n)
		elif isinstance(n, rvsdg.litnode):
			handle_litnode(rvsdg, gvg, n)
		elif isinstance(n, rvsdg.thetanode):
			handle_thetanode(rvsdg, gvg, n)
		elif isinstance(n, rvsdg.gammanode):
			handle_gammanode(rvsdg, gvg, n)
	
	for res, resval in zip(rvsdg.results, rvsdg.result_values):
		resnode = "r%d%s" % (id(rvsdg), res)
		n = gvg.add_node(resnode, label=res)
		make_edge(rvsdg, gvg, resval, (None, res))

def make_gvg(rvsdg):
	gvg = pygraphviz.AGraph(directed=True, strict=False)
	handle_region(rvsdg, gvg)
	gvg.layout('dot')
	return gvg

def show(rvsdg):
	gvg = make_gvg(rvsdg)
	gvg.draw('/tmp/tmp.png')
	os.system('display /tmp/tmp.png')
