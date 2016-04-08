# -*- coding: utf-8 -*-

from __future__ import division, print_function
import collections
try:
    import graph_tool.all as gt
except ImportError:
    pass
import numpy as np
import operator
import os
import pdb
import random

from main import Graph
from tools import read_pickle, write_pickle, url_unescape


class OutOfLinksException(Exception):
    pass


class BaseRecommender(object):
    def __init__(self):
        self.scc, self.inc = set(), set()
        self.scc_vs, self.inc_vs = set(), set()
        self.node2out_component = {}

    def find_nodes(self, start_node, inc, scc, do_debug=False, limit=None):
        # via networkx.algorithms.simple_paths.all_simple_paths
        if do_debug:
            debug = lambda *text: print(' '.join(str(t) for t in text))
        else:
            debug = lambda *text: None

        debug('\nstarting from', int(start_node), '---------------')
        self.node2out_component[int(start_node)] = {int(start_node)}
        visited = [start_node]
        reached = set()
        stack = [(int(start_node), start_node.out_neighbours())]
        while stack:
            if limit and len(stack) > limit:
                del self.node2out_component[int(start_node)]
                return False
            node, nb_generator = stack[-1]
            nb = next(nb_generator, None)
            debug('node =', node, 'nb =', int(nb) if nb else 'None')
            if nb is None:
                if any(v in scc for v in visited):
                    self.node2out_component[int(start_node)] |= set(map(int, visited)) - scc
                debug('    NB is None, setting node2out_component to', self.node2out_component[int(start_node)])
                stack.pop()
                visited.pop()
                continue
            if nb in reached:
                debug('    NB already reached')
                continue
            else:
                reached.add(nb)
            if nb in scc:
                debug('    nb in SCC')
                visited.append(nb)
                continue
            if nb not in inc:
                debug('    nb not in INC or SCC, skipping')
                continue
            if nb in visited:
                debug('    nb in visited')
                continue
            try:  # nb already computed?
                self.node2out_component[int(start_node)] |= self.node2out_component[int(nb)]
                debug('    NODE already computed as', self.node2out_component[int(nb)])
                continue
            except KeyError:
                pass
            # else nb is not in visited
            debug('    nb not yet visited')
            visited.append(nb)
            stack.append((int(nb), nb.out_neighbours()))

            # debug('node2out_component: ++++++++')
            # for k, v in self.node2out_component.items():
            #     debug('   ', k, v)
            # debug('--------------------------------')
            # if do_debug:
            #     pdb.set_trace()
        return True


class Recommender(BaseRecommender):
    def __init__(self, wiki_code, small_n='first_p', large_n='lead',
                 n_recs=100, verbose=False):
        BaseRecommender.__init__(self)
        self.wiki_code = wiki_code
        self.wiki_name = wiki_code + 'wiki'
        self.verbose = verbose
        print(self.wiki_name, n_recs, '<--------')
        self.small_n, self.large_n = small_n, large_n
        self.g_small, self.g_large = None, None
        self.n_recs = n_recs
        self.scc_sizes, self.inc_sum_vcs, self.scc_sum_vcs = [], [], []

        print('loading graphs...')
        self.load_graphs()

        print('loading id2views...')
        fpath = os.path.join('data', 'pageviews', 'filtered')
        fname = 'id2views-' + self.wiki_code + '.obj'
        self.id2views = read_pickle(os.path.join(fpath, fname))
        self.wid2node_small = {self.g_small.graph.vp['name'][v]: v
                               for v in self.g_small.graph.vertices()}
        self.wid2node_large = {self.g_large.graph.vp['name'][v]: v
                               for v in self.g_large.graph.vertices()}
        self.graph_reversed = gt.GraphView(self.g_small.graph, reversed=True,
                                           directed=True)

        self.scc_sum_vc, self.inc_sum_vc = 0, 0
        self.c_inc2c_scc = collections.defaultdict(set)
        self.added_edges = []

    def get_stats(self):
        # get SCC and IN
        component, histogram = gt.label_components(self.g_small.graph)
        scc_size = max(histogram)
        largest_component = (component.a == np.argmax(histogram))
        self.scc = set(np.nonzero(largest_component)[0])
        self.inc = gt.label_out_component(
            self.graph_reversed,
            random.sample(self.scc, 1)[0]
        ).a
        self.inc = set(np.nonzero(self.inc)[0]) - self.scc

        # convert sets to WP ids
        self.inc_vs = self.inc
        self.scc_vs = self.scc
        self.inc = set([self.g_small.graph.vp['name'][n] for n in self.inc])
        self.scc = set([self.g_small.graph.vp['name'][n] for n in self.scc])

        # get view counts
        self.scc_sum_vc = sum(self.id2views[v] for v in self.scc)
        self.inc_sum_vc = sum(self.id2views[v] for v in self.inc)

        return scc_size, self.inc_sum_vc, self.scc_sum_vc

    def load_graphs(self, skip_large=False):
        self.g_small = Graph(wiki_code=self.wiki_code, N=self.small_n)
        self.g_small.load_graph()
        if not skip_large:
            self.g_large = Graph(wiki_code=self.wiki_code, N=self.large_n)
            self.g_large.load_graph()

    def reset(self):
        print('loading graph...')
        self.load_graphs(skip_large=True)
        print('getting stats...')
        self.scc_sizes, self.inc_sum_vcs, self.scc_sum_vcs = [], [], []
        self.scc_sum_vc, self.inc_sum_vc = 0, 0
        scc_size, inc_sum_vc, scc_sum_vc = self.get_stats()
        self.scc_sizes = [scc_size]
        self.inc_sum_vcs = [inc_sum_vc]
        self.scc_sum_vcs = [scc_sum_vc]
        self.c_inc2c_scc = collections.defaultdict(set)
        self.added_edges = []

    def get_reach(self, inc=None, scc=None):
        fpath = os.path.join('data', self.wiki_name, 'reach.obj')
        try:
            self.node2out_component = read_pickle(fpath)
            print('reach loaded from disk')
        except IOError:
            print('getting reach...')
            if inc is None:
                inc = self.inc_vs
            if scc is None:
                scc = self.scc_vs

            print('got a total of', len(self.inc_vs), 'nodes to compute')
            print('\ntrying with 4...')
            skipped_nodes = []
            # via http://stackoverflow.com/questions/25027122
            for nidx, node in enumerate(self.inc_vs):
                print('\r   ', nidx+1, '/', len(self.inc_vs),
                      len(self.node2out_component), end='')
                result = self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False,
                    limit=4
                )
                if not result:
                    skipped_nodes.append(node)

            print('\nretrying with 8...')
            skipped_nodes2 = []
            for nidx, node in enumerate(skipped_nodes):
                print('\r   ', nidx+1, '/', len(skipped_nodes),
                      len(self.node2out_component), end='')
                result = self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False,
                    limit=8
                )
                if not result:
                    skipped_nodes2.append(node)

            print('\nretrying with 16...')
            skipped_nodes3 = []
            for nidx, node in enumerate(skipped_nodes2):
                print('\r   ', nidx+1, '/', len(skipped_nodes2),
                      len(self.node2out_component), end='')
                result = self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False,
                    limit=16
                )
                if not result:
                    skipped_nodes3.append(node)

            print('\retrying with unlimited...')
            for nidx, node in enumerate(skipped_nodes3):
                print('\r   ', nidx + 1, '/', len(skipped_nodes3),
                      len(self.node2out_component), end='')
                self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False,
                    limit=None
                )

            print('\nconverting to Wikipedia IDs...')
            d = {}
            for nidx, (node, reach) in enumerate(self.node2out_component.iteritems()):
                print('\r   ', nidx+1, '/', len(self.node2out_component), end='')
                d[self.g_small.graph.vp['name'][node]] = set(
                    self.g_small.graph.vp['name'][r] for r in reach
                )
            self.node2out_component = d

            print('\nwriting to disk...')
            write_pickle(fpath, self.node2out_component)

    def print_example(self, wpid):
        self.reset()
        self.get_reach()
        self.get_recommendation_candidates()
        scc_node = wpid
        inc_nodes = set()
        for idx, (c_inc, c_scc) in enumerate(self.c_inc2c_scc.iteritems()):
            print('\r', idx + 1, '/', len(self.c_inc2c_scc), end='')
            if scc_node in c_scc:
                inc_nodes.add(c_inc)
        print()

        scc_graph_node = self.wid2node_small[scc_node]
        scc_title = self.g_small.graph.vp['title'][scc_graph_node]
        print('%s (%d)' % (scc_title, scc_node))
        for inc_node in inc_nodes:
            inc_graph_node = self.wid2node_small[inc_node]
            inc_title = self.g_small.graph.vp['title'][inc_graph_node]
            print('    %s (%d)' % (inc_title, inc_node))
        pdb.set_trace()

    def print_examples(self):
        self.reset()
        self.get_reach()
        self.get_recommendation_candidates()
        print('GETTING EXAMPLES...')
        c_scc2c_inc = collections.defaultdict(set)
        for idx, (c_inc, c_scc) in enumerate(self.c_inc2c_scc.iteritems()):
            print('\r', idx+1, '/', len(self.c_inc2c_scc), end='')
            for scc_node in c_scc:
                c_scc2c_inc[scc_node].add(c_inc)

        config = [
            # (self.get_next_recommendation_scc_based, 'scc_based', 'SCC-based'),
            (self.get_next_recommendation_vc_based, 'vc_based', 'VC-based'),
        ]

        for idx, (func, rec_type, label) in enumerate(config):
            if idx > 0:
                self.reset()
                self.get_reach()
                self.get_recommendation_candidates()
            print(label, 'recommendations')
            for i in range(10):
                inc_node, scc_nodes = func(example=True)
                for scc_node in scc_nodes:
                    scc_graph_node = self.wid2node_small[scc_node]
                    scc_title = self.g_small.graph.vp['title'][scc_graph_node]
                    print('%s (%d)' % (scc_title, scc_node))
                    for inc_node in c_scc2c_inc[scc_node]:
                        inc_graph_node = self.wid2node_small[inc_node]
                        inc_title = self.g_small.graph.vp['title'][inc_graph_node]
                        print('    %s (%d)' % (inc_title, inc_node))
                self.add_recommendation(rec_type=rec_type)

    def get_next_recommendation_scc_based(self, example=False):
        c_inc_max, val_max = -1, -1
        for c_inc in self.c_inc2c_scc:
            reach = len(self.node2out_component[c_inc])
            if reach > val_max:
                c_inc_max = c_inc
                val_max = reach
        if self.verbose:
            inc_graph_node = self.wid2node_small[c_inc_max]
            print('%s (%d)' % (self.g_small.graph.vp['title'][inc_graph_node], c_inc_max))
            for scc_node in self.c_inc2c_scc[c_inc_max]:
                scc_graph_node = self.wid2node_small[scc_node]
                print('    %s (%d)' % (self.g_small.graph.vp['title'][scc_graph_node], scc_node))
        if c_inc_max == -1 or val_max == -1:
            raise OutOfLinksException
        if example:
            return c_inc_max, self.c_inc2c_scc[c_inc_max]
        return c_inc_max, random.sample(self.c_inc2c_scc[c_inc_max], 1)[0]

    def get_next_recommendation_vc_based(self, example=False):
        c_inc_max, val_max = -1, -1
        for c_inc in self.c_inc2c_scc:
            val = sum(
                self.id2views[n] for n in self.node2out_component[c_inc])
            if val > val_max:
                c_inc_max = c_inc
                val_max = val
        if self.verbose:
            inc_graph_node = self.wid2node_small[c_inc_max]
            print('        %s (%d)' % (
                self.g_small.graph.vp['title'][inc_graph_node], c_inc_max)
            )
            for scc_node in self.c_inc2c_scc[c_inc_max]:
                scc_graph_node = self.wid2node_small[scc_node]
                print('            %s (%d)' % (
                    self.g_small.graph.vp['title'][scc_graph_node], scc_node)
                )
        if c_inc_max == -1 or val_max == -1:
            raise OutOfLinksException
        if example:
            return c_inc_max, self.c_inc2c_scc[c_inc_max]
        return c_inc_max, random.sample(self.c_inc2c_scc[c_inc_max], 1)[0]

    def get_recommendation_candidates(self):
        fpath = os.path.join('data', self.wiki_name, 'candidates.obj')
        try:
            self.c_inc2c_scc = read_pickle(fpath)
            print('recommendation candidates loaded from disk')
        except IOError:
            print('getting recommendation candidates...')
            for idx, wpid in enumerate(self.scc):
                print('\r   ', idx + 1, '/', len(self.scc), end='')
                node_small = self.wid2node_small[wpid]
                node_large = self.wid2node_large[wpid]
                nbs_small = [nb for nb in node_small.out_neighbours()]
                nbs_small = set(self.g_small.graph.vp['name'][n] for n in nbs_small)
                nbs_large = [nb for nb in node_large.out_neighbours()]
                nbs_large = set(self.g_large.graph.vp['name'][n] for n in nbs_large)
                candidates = nbs_large - nbs_small
                candidates = set(c for c in candidates if c in self.inc)
                for cand in candidates:
                    self.c_inc2c_scc[cand].add(wpid)
            print()

            print('\nwriting to disk...')
            write_pickle(fpath, self.c_inc2c_scc)

    def add_recommendation(self, rec_type):
        # add the recommendation
        if rec_type == 'scc_based':
            inc_node, scc_node = self.get_next_recommendation_scc_based()
        elif rec_type == 'vc_based':
            inc_node, scc_node = self.get_next_recommendation_vc_based()
        else:
            print('NOT SUPPORTED')
            pdb.set_trace()
        scc_graph_node = self.wid2node_small[scc_node]
        inc_graph_node = self.wid2node_small[inc_node]
        self.g_small.graph.add_edge(scc_graph_node, inc_graph_node)
        self.added_edges.append((
                self.g_small.graph.vp['title'][scc_graph_node], scc_node,
                self.g_small.graph.vp['title'][inc_graph_node], inc_node
            ))

        added_nodes = self.node2out_component[inc_node]

        # compute the effects of adding it
        self.scc |= added_nodes
        self.inc -= added_nodes
        vc_change = sum(self.id2views[n] for n in added_nodes)
        self.scc_sizes.append(self.scc_sizes[-1] + len(added_nodes))
        self.scc_sum_vc += vc_change
        self.inc_sum_vc -= vc_change
        self.inc_sum_vcs.append(self.inc_sum_vc)
        self.scc_sum_vcs.append(self.scc_sum_vc)

        # update c_inc2c_scc
        for node in added_nodes:
            try:
                del self.c_inc2c_scc[node]
            except KeyError:
                pass

        # update node2out_component
        for node in added_nodes:
            del self.node2out_component[node]
        for node, reach in self.node2out_component.items():
                self.node2out_component[node] -= added_nodes

    def recommend(self, rec_type):
        self.reset()
        self.get_reach()
        self.get_recommendation_candidates()
        print('adding recommendations based on %s...' % rec_type)
        for i in range(self.n_recs):
            if self.verbose:
                print('   ', i+1, '/', self.n_recs)
            else:
                print('\r   ', i+1, '/', self.n_recs, end='')
            try:
                self.add_recommendation(rec_type=rec_type)
            except OutOfLinksException:
                print('\nout of links at %d - breaking' % (i+1))
                break
        print()

        self.g_small.load_stats()
        self.g_small.stats['recs_' + rec_type + '_vc_inc'] = self.inc_sum_vcs
        self.g_small.stats['recs_' + rec_type + '_vc_scc'] = self.scc_sum_vcs
        self.g_small.stats['recs_' + rec_type + '_scc_size'] = self.scc_sizes
        self.g_small.stats['recs_' + rec_type + '_edges'] = self.added_edges
        self.g_small.save_stats()


class TestRecommender(BaseRecommender):
    def __init__(self):
        BaseRecommender.__init__(self)

    def get_reach_test(self, graph, nodes, inc=None, scc=None, do_debug=False):
        self.node2out_component = {}
        if inc is None:
            inc = self.inc_vs
        if scc is None:
            scc = self.scc_vs
        for nidx, node in enumerate(nodes):
            # print('\r', nidx+1, '/', len(nodes), end='')
            self.find_nodes(graph.vertex(node), inc, scc, do_debug=do_debug)
        print()
        self.node2out_component = {
            k: v for k, v in self.node2out_component.items() if k in inc
        }

    def test_node2reach(self):
        g = gt.Graph(directed=True)
        v0 = g.add_vertex()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        v6 = g.add_vertex()
        g.add_edge_list([
            (v1, v0),
            (v2, v6),
            (v2, v0),
            (v2, v1),
            (v3, v1),
            (v3, v2),
            (v3, v4),
            (v4, v5),
        ])
        self.get_reach_test(graph=g, nodes=[v1, v2, v3],
                       inc={v1, v2, v3}, scc={v0, v6})
        for node, out_component in self.node2out_component.items():
            if out_component:
                print(node, map(int, out_component))
            else:
                print(node, out_component)

        assert self.node2out_component == {
            1: {1},
            2: {1, 2},
            3: {1, 2, 3},
        }

    def test_node2reach2(self):
        g = gt.Graph(directed=True)
        v0 = g.add_vertex()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        g.add_edge_list([
            (v1, v0),
            (v1, v2),
            (v1, v3),
            (v2, v0),
            (v2, v1),
            (v2, v3),
            (v3, v1),
            (v3, v2),
            (v3, v4),
            (v4, v5),
        ])
        self.get_reach_test(graph=g, nodes=[v1, v2, v3],
                       inc={v1, v2, v3}, scc={v0})

        for node, out_component in self.node2out_component.items():
            if out_component:
                print(node, map(int, out_component))
            else:
                print(node, out_component)
        assert self.node2out_component == {
            1: {1, 2, 3},
            2: {1, 2, 3},
            3: {1, 2, 3},
        }

    def test_node2reach3(self):
        g = gt.Graph(directed=True)
        v0 = g.add_vertex()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        v6 = g.add_vertex()
        v7 = g.add_vertex()
        g.add_edge_list([
            (v1, v0),
            (v1, v2),
            (v2, v0),
            (v2, v5),
            (v3, v2),
            (v4, v1),
            (v5, v6),
            (v6, v3),
            (v7, v5),
            (v7, v4),
        ])
        self.get_reach_test(graph=g, nodes=[v1, v2, v3, v4, v5, v6, v7],
                       inc={v1, v2, v3, v4, v5, v6, v7}, scc={v0},
                       do_debug=False)

        for node, out_component in self.node2out_component.items():
            if out_component:
                print(node, map(int, out_component))
            else:
                print(node, out_component)
        assert self.node2out_component == {
            1: {1, 2, 3, 5, 6},
            2: {2, 3, 5, 6},
            3: {2, 3, 5, 6},
            4: {1, 2, 3, 4, 5, 6},
            5: {2, 3, 5, 6},
            6: {2, 3, 5, 6},
            7: {1, 2, 3, 4, 5, 6, 7},
        }

    def test_node2reach4(self):
        g = gt.Graph(directed=True)
        v0 = g.add_vertex()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        v6 = g.add_vertex()
        v7 = g.add_vertex()
        v8 = g.add_vertex()
        v9 = g.add_vertex()
        v10 = g.add_vertex()
        v11 = g.add_vertex()
        g.add_edge_list([
            (v1, v0),
            (v1, v2),
            (v2, v0),
            (v2, v5),
            (v3, v2),
            (v4, v1),
            (v5, v6),
            (v6, v3),
            (v7, v5),
            (v7, v4),
            (v7, v8),
            (v5, v9),
            (v8, v5),
            (v9, v10),
            (v10, v11),
            (v11, v8),
        ])
        self.get_reach_test(graph=g, nodes=[v1, v2, v3, v4, v5, v6, v7],
                       inc={v1, v2, v3, v4, v5, v6, v7}, scc={v0},
                       do_debug=False)

        for node, out_component in self.node2out_component.items():
            if out_component:
                print(node, map(int, out_component))
            else:
                print(node, out_component)
        assert self.node2out_component == {
            1: {1, 2, 3, 5, 6},
            2: {2, 3, 5, 6},
            3: {2, 3, 5, 6},
            4: {1, 2, 3, 4, 5, 6},
            5: {2, 3, 5, 6},
            6: {2, 3, 5, 6},
            7: {1, 2, 3, 4, 5, 6, 7},
        }

    def test_node2reach5(self):
        g = gt.Graph(directed=True)
        v0 = g.add_vertex()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        v6 = g.add_vertex()
        v7 = g.add_vertex()
        g.add_edge_list([
            (v1, v2),
            (v1, v6),
            (v2, v6),
            (v3, v4),
            (v4, v0),
            (v4, v6),
            (v5, v4),
            (v6, v3),
            (v6, v7),
        ])

        self.get_reach_test(graph=g, nodes=[v1, v2, v3, v4, v5, v6],
                            inc={v1, v2, v3, v4, v5, v6}, scc={v0, v7},
                            do_debug=False)

        for node, out_component in self.node2out_component.items():
            if out_component:
                print(node, map(int, out_component))
            else:
                print(node, out_component)
        assert self.node2out_component == {
            1: {1, 2, 3, 4, 6},
            2: {2, 3, 4, 6},
            3: {3, 4, 6},
            4: {3, 4, 6},
            5: {3, 4, 5, 6},
            6: {3, 4, 6},
        }

    def test_node2reach6(self):
        g = gt.Graph(directed=True)
        v0 = g.add_vertex()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        v6 = g.add_vertex()
        v7 = g.add_vertex()
        v8 = g.add_vertex()
        v9 = g.add_vertex()
        v10 = g.add_vertex()
        v11 = g.add_vertex()
        g.add_edge_list([
            (v1, v3),
            (v2, v7),
            (v2, v11),
            (v3, v7),
            (v3, v11),
            (v4, v0),
            (v4, v6),
            (v5, v9),
            (v5, v10),
            (v6, v0),
            (v7, v3),
            (v7, v4),
            (v8, v10),
            (v9, v10),
        ])

        self.get_reach_test(graph=g, nodes=[v1, v2, v3, v4, v5, v6, v7, v8, v9],
                            inc={v1, v2, v3, v4, v5, v6, v7, v8, v9}, scc={v0, v10, v11},
                            do_debug=False)

        for node, out_component in self.node2out_component.items():
            if out_component:
                print(node, map(int, out_component))
            else:
                print(node, out_component)
        assert self.node2out_component == {
            1: {1, 3, 4, 6, 7},
            2: {2, 3, 4, 6, 7},
            3: {3, 4, 6, 7},
            4: {4, 6},
            5: {5, 9},
            6: {6},
            7: {3, 4, 6, 7},
            8: {8},
            9: {9},
        }


if __name__ == '__main__':
    for wp in [
        # 'simple',
        # 'en',
        # 'de',
        # 'fr',
        # 'es',
        'it',
    ]:
        r = Recommender(wp, n_recs=1000, verbose=False)
        # r.print_example()
        # r.print_examples()
        # r.recommend(rec_type='scc_based')
        r.recommend(rec_type='vc_based')

    # st = TestRecommender()
    # st.test_node2reach()
    # st.test_node2reach2()
    # st.test_node2reach3()
    # st.test_node2reach4()
    # st.test_node2reach5()
    # st.test_node2reach6()

    # wikipedias = [
    #     'simple',
    #
    #     # 'en',
    #     # 'de',
    #     # 'fr',
    #     # 'es',
    #     # 'ru',
    #     # 'it',
    #     # 'ja',
    #     # 'nl',
    # ]
    #
    # pageview_dir_filtered = os.path.join('data', 'pageviews', 'filtered')
    #
    # for wp in wikipedias:
    #     print(wp)
    #     wp_small = 'first_p'
    #     wp_large = 'lead'
    #     print('   ', wp_small, wp_large)
    #     g_small = Graph(data_dir=os.path.join('data', wp + 'wiki'),
    #                     fname='links', use_sample=False, refresh=False,
    #                     N=wp_small)
    #     g_small.load_graph(refresh=False)
    #     g_large = Graph(data_dir=os.path.join('data', wp + 'wiki'),
    #                     fname='links', use_sample=False, refresh=False,
    #                     N=wp_large)
    #     g_large.load_graph(refresh=False)
    #
    #     print('       loading dicts...')
    #     id2views = read_pickle(os.path.join(pageview_dir_filtered,
    #                                         'id2views-' + wp + '.obj'))
    #     wid2node_small = {g_small.graph.vp['name'][v]: v
    #                       for v in g_small.graph.vertices()}
    #     wid2node_large = {g_large.graph.vp['name'][v]: v
    #                       for v in g_large.graph.vertices()}
    #     wpid2title_small = {
    #         g_small.graph.vp['name'][v]: g_small.graph.vp['title'][v]
    #         for v in g_small.graph.vertices()
    #     }
    #
    #     inc = [g_small.graph.vp['name'][v] for v in g_small.graph.vertices()
    #            if g_small.graph.vp['bowtie'][v] == 'IN']
    #     outc = [g_small.graph.vp['name'][v] for v in g_small.graph.vertices()
    #             if g_small.graph.vp['bowtie'][v] == 'OUT']
    #
    #     # print('       find articles in IN with highest view count')
    #     # result_inc = get_top_n(inc, id2views, 10)
    #     #
    #     # print('       find articles in OUT with highest view count')
    #     # result_outc = get_top_n(outc, id2views, 10)
    #     #
    #     # text = unicode(wp)
    #     # for (node_in, views_in), (node_out, views_out) in zip(result_inc, result_outc):
    #     #     text += u' & %s & %d & %s & %d\\\\\n' \
    #     #             % (url_unescape(wpid2title_small[node_in]), views_in,
    #     #                url_unescape(wpid2title_small[node_out]), views_out)
    #     # text += u'\\hline\n'
    #     # fpath = os.path.join('plots', 'recommendations_views.txt')
    #     # with io.open(fpath, 'a', encoding='utf-8') as outfile:
    #     #     outfile.write(text)
    #     #
    #     # print(text)
    #
    #     # # look at candidates and find articles in IN with highest view count
    #     # for node in inc:
    #     #     node_small = wid2node_small[g_large.graph.vp['name'][node]]
    #     #     candidates = set(node.out_neighbours()) -\
    #     #                  set(node_small.out_neighbours())
    #
    #     # find articles in IN with largest OUT component towards SCC
    #     id2reach_inc = get_reach(g_small.graph, inc)
    #     id2reach_out = get_reach(g_small.graph, outc)


