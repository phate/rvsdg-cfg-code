import re
import sys

import cfg_model
import stmts

_vertex_re = re.compile('^([0-9]+)\\[shape = box, label = "([^"]*)"\\];$')
_edge_re = re.compile('^([0-9]+) -> ([0-9]+)\\[label = "([^"]*)"\\];$')

class dot_graph(object):
	__slots__ = (
		'vertex_labels',
		'vertex_outgoing',
	)
	
	def __init__(self):
		self.vertex_labels = {}
		self.vertex_outgoing = {}

def _get_enter_vertex(dg):
	for vertex, label in dg.vertex_labels.items():
		if label == 'ENTER': return vertex
	return None

def _get_exit_vertex(dg):
	for vertex, label in dg.vertex_labels.items():
		if label == 'EXIT': return vertex
	return None

def _get_reachable(dg, origin):
	pending = set((origin,))
	reachable = set()
	while pending:
		vertex = pending.pop()
		reachable.add(vertex)
		for succ, label in dg.vertex_outgoing.get(vertex, []):
			if succ not in reachable: pending.add(succ)
	return reachable

def _prune_unreachable(dg, reachable):
	for vertex in dg.vertex_labels.keys():
		if vertex not in reachable:
			del dg.vertex_labels[vertex]
			del dg.vertex_outgoing[vertex]
def _parse_line(line, dg):
	m = _vertex_re.match(line)
	if m:
		vertex = m.group(1)
		label = m.group(2)
		dg.vertex_labels[vertex] = label
		return
	m = _edge_re.match(line)
	if m:
		origin = m.group(1)
		target = m.group(2)
		label = m.group(3)
		dg.vertex_outgoing[origin] = dg.vertex_outgoing.get(origin, []) + [(target, label)]

def _convert_to_cfg(dg):
	cfg = cfg_model.cfg()
	cfg_tgt_map = {}
	cfg_org_map = {}
	
	entry = cfg.make_node(stmts.null_stmt())
	exit = cfg.make_node(stmts.null_stmt())
	
	for vertex, label in dg.vertex_labels.items():
		if label == 'ENTER':
			cfg_org_map[vertex] = entry
			continue
		elif label == 'EXIT':
			cfg_tgt_map[vertex] = exit
			continue
		succs = dg.vertex_outgoing.get(vertex, [])
		is_branch = len(succs) > 1
		
		if is_branch:
			n1 = cfg.make_node('let P, p%s := f%s(P)' % (vertex, vertex))
			n2 = cfg.make_node('branch p%s' % vertex)
			cfg.make_edge(n1, n2)
			cfg_tgt_map[vertex] = n1
			cfg_org_map[vertex] = n2
		else:
			n = cfg.make_node('let P := f%s(P)' % vertex)
			cfg_tgt_map[vertex] = n
			cfg_org_map[vertex] = n
	
	for origin, tgts in dg.vertex_outgoing.items():
		for target, label in tgts:
			n1 = cfg_org_map[origin]
			n2 = cfg_tgt_map[target]
			if (n1, n2) in cfg.edges:
				dummy = cfg.make_node('let P := dummy(P)')
				cfg.make_edge(dummy, n2, 0)
				n2 = dummy
			cfg.make_edge(n1, n2, int(label))
	
	return cfg

def parse_dot_to_cfg(lines):
	dg = dot_graph()
	for line in lines:
		_parse_line(line[:-1], dg)
	
	reachable = _get_reachable(dg, _get_enter_vertex(dg))
	_prune_unreachable(dg, reachable)
	
	cfg = _convert_to_cfg(dg)
	
	return cfg
