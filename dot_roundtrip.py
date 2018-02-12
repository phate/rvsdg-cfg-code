import signal
import sys
import time

import dotparse
import cfg2cfg
import cfg2rvsdg
import cfg_algorithm
import cfg_model
import rvsdg2cfg
import rvsdg_model
import stmts

import cfg_view
import rvsdg_view

sys.setrecursionlimit(100000)

cfg = dotparse.parse_dot_to_cfg(sys.stdin.readlines())

#signal.alarm(10)

cfg_orig = cfg.copy()
orig_cfg_nodes = len(cfg_orig.nodes)

#cfg_view.show(cfg_orig)

start_fwd = time.time()
rvsdg = cfg2rvsdg.convert(cfg)
rvsdg.normalize()
end_fwd = time.time()
#rvsdg_view.show(rvsdg)

start_rev = time.time()
cfg_post = rvsdg2cfg.convert(rvsdg)
end_rev = time.time()
#cfg_view.show(cfg_post)

nbranches = len([n for n in cfg_orig.nodes if isinstance(n.stmt, stmts.branch_stmt)])

structured_cfg_nodes = orig_cfg_nodes +  \
	cfg2cfg.artificial_branches + cfg2rvsdg.artificial_loop_entry_mux + \
	cfg2rvsdg.artificial_loop_exit_mux + cfg2rvsdg.artificial_loop_repeat + \
	cfg2rvsdg.artificial_loop_letqs + \
	cfg2rvsdg.artificial_loop_letqrs + \
	cfg2rvsdg.artificial_loop_letrs + \
	cfg2cfg.artificial_branchjoin_nulls + \
	cfg2cfg.artificial_branch_letps

structured_cfg_branches = nbranches + \
	cfg2cfg.artificial_branches + cfg2rvsdg.artificial_loop_entry_mux + \
	cfg2rvsdg.artificial_loop_exit_mux + cfg2rvsdg.artificial_loop_repeat

print orig_cfg_nodes, nbranches, rvsdg.node_count(), rvsdg.gamma_count(), \
	rvsdg.theta_count(), rvsdg.maximum_depth(), cfg2cfg.artificial_branches, cfg2rvsdg.artificial_loop_entry_mux, \
	cfg2rvsdg.artificial_loop_exit_mux, cfg2rvsdg.artificial_loop_repeat, \
	cfg2rvsdg.artificial_loop_letqs, \
	cfg2rvsdg.artificial_loop_letqrs, \
	cfg2rvsdg.artificial_loop_letrs, \
	cfg2cfg.artificial_branchjoin_nulls, \
	cfg2cfg.artificial_branch_letps, \
	structured_cfg_nodes, structured_cfg_branches, \
	end_fwd - start_fwd, end_rev - start_rev

d = cfg_algorithm.search_difference(cfg_orig, cfg_post)

if isinstance(d, tuple):
	print "FAILED", str(d[0]), str(d[1])
	sys.exit(1)
else:
	sys.exit(0)
