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
import signal

from main import Graph
from tools import read_pickle, write_pickle, url_unescape


class TimeoutException(Exception):   # Custom exception class
    pass


def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException


# via http://stackoverflow.com/questions/25027122
# Change the behavior of SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)


class BaseRecommender(object):
    def __init__(self):
        self.scc, self.inc = set(), set()
        self.scc_vs, self.inc_vs = set(), set()
        self.node2out_component = {}

    def find_nodes(self, start_node, inc, scc, do_debug=False):
        # via networkx.algorithms.simple_paths.all_simple_paths
        if do_debug:
            debug = lambda *text: print(' '.join(str(t) for t in text))
        else:
            debug = lambda *text: None

        debug('\nstarting from', int(start_node), '---------------')
        self.node2out_component[int(start_node)] = set([int(start_node)])
        visited = [start_node]
        stack = [(int(start_node), start_node.out_neighbours())]
        while stack:
            node, nb_generator = stack[-1]
            nb = next(nb_generator, None)
            debug('node =', node, 'nb =', int(nb) if nb else 'None')
            if nb in visited:
                debug('    nb in visited')
            elif nb is None:
                if set(visited) & scc:
                    self.node2out_component[int(start_node)] |= set(
                        map(int, visited)) - scc
                debug('    NB is None, setting node2out_component to',
                      self.node2out_component[int(start_node)])
                stack.pop()
                visited.pop()
            elif int(nb) in self.node2out_component:
                debug('    NODE already computed as',
                      self.node2out_component[int(nb)])
                self.node2out_component[int(start_node)] |= self.node2out_component[int(nb)]
            elif nb in scc:
                debug('    nb in SCC')
                visited.append(nb)
            elif nb not in inc:
                debug('    nb not in INC or SCC, skipping')
                pass
            elif nb not in visited:
                debug('    nb not yet visited')
                visited.append(nb)
                stack.append((int(nb), nb.out_neighbours()))
            debug('node2out_component: ++++++++')
            for k, v in self.node2out_component.items():
                debug('   ', k, v)
            debug('--------------------------------')
            if do_debug:
                pdb.set_trace()


class Recommender(BaseRecommender):
    def __init__(self, wiki_code, small_n='first_p', large_n='lead',
                 n_recs=100):
        BaseRecommender.__init__(self)
        self.wiki_code = wiki_code
        self.wiki_name = wiki_code + 'wiki'
        print(self.wiki_name)
        self.small_n, self.large_n = small_n, large_n
        self.g_small, self.g_large = None, None
        self.n_recs = n_recs
        self.vc_ratios, self.scc_sizes = [], []

        self.load_graphs()
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
        scc_size, vc_ratio = self.get_stats()
        self.scc_sizes = [scc_size]
        self.vc_ratios = [vc_ratio]

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

        # get view count ratio
        self.scc_sum_vc = sum(self.id2views[v] for v in self.scc)
        self.inc_sum_vc = sum(self.id2views[v] for v in self.inc)
        vc_ratio = (self.scc_sum_vc / len(self.scc)) /\
                   (self.inc_sum_vc / len(self.inc))

        return scc_size, vc_ratio

    def load_graphs(self):
        print('loading graphs...')
        self.g_small = Graph(wiki_code=self.wiki_code, N=self.small_n)
        self.g_small.load_graph()
        self.g_large = Graph(wiki_code=self.wiki_code, N=self.large_n)
        self.g_large.load_graph()

    def get_reach(self, inc=None, scc=None):
        fpath = os.path.join('data', self.wiki_name, 'reach.obj')
        try:
            self.node2out_component = read_pickle(fpath)
            print('reach loaded!')
        except IOError:
            pass
        print('getting reach...')
        if inc is None:
            inc = self.inc_vs
        if scc is None:
            scc = self.scc_vs

        print('\ntrying with 2 seconds...')
        skipped_nodes = []
        # via http://stackoverflow.com/questions/25027122
        for nidx, node in enumerate(self.inc_vs):
            print('\r   ', nidx+1, '/', len(self.inc_vs), end='')
            signal.alarm(2)
            try:
                self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False)
            except TimeoutException:
                skipped_nodes.append(node)
            else:
                signal.alarm(0)

        print('\nretrying with 4 seconds...')
        skipped_nodes2 = []
        for nidx, node in enumerate(skipped_nodes):
            print('\r   ', nidx+1, '/', len(skipped_nodes), end='')
            signal.alarm(4)
            try:
                self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False)
            except TimeoutException:
                skipped_nodes2.append(node)
            else:
                signal.alarm(0)

        print('\nretrying with 8 seconds...')
        skipped_nodes3 = []
        for nidx, node in enumerate(skipped_nodes2):
            print('\r   ', nidx+1, '/', len(skipped_nodes2), end='')
            signal.alarm(4)
            try:
                self.find_nodes(
                    start_node=self.g_small.graph.vertex(node),
                    inc=inc, scc=scc,
                    do_debug=False)
            except TimeoutException:
                skipped_nodes3.append(node)
            else:
                signal.alarm(0)

        print('\retrying with unlimited time...')
        for nidx, node in enumerate(skipped_nodes3):
            print('\r   ', nidx + 1, '/', len(skipped_nodes3), end='')
            self.find_nodes(
                start_node=self.g_small.graph.vertex(node),
                inc=inc, scc=scc,
                do_debug=False)

        print('\nwriting to disk...')
        write_pickle(fpath, self.node2out_component)


class ViewCountRecommender(Recommender):
    def __init__(self, wiki_code, small_n='first_p', large_n='lead', n_recs=100):
        Recommender.__init__(self, wiki_code, small_n, large_n, n_recs)
        self.scc_inc_vc = []

    def get_recommendation_candidates(self):
        print('getting recommendation candidates...')
        for idx, wpid in enumerate(self.scc):
            print('\r   ', idx+1, '/', len(self.scc), end='')
            node_small = self.wid2node_small[wpid]
            node_large = self.wid2node_large[wpid]
            nbs_small = [nb for nb in node_small.out_neighbours()]
            nbs_small = set(self.g_small.graph.vp['name'][n] for n in nbs_small)
            nbs_large = [nb for nb in node_large.out_neighbours()]
            nbs_large = set(self.g_large.graph.vp['name'][n] for n in nbs_large)
            candidates = nbs_large - nbs_small
            candidates = set(c for c in candidates if c in self.inc)
            for cand in candidates:
                self.scc_inc_vc.append((wpid, cand, self.id2views[cand]))
        print()
        self.scc_inc_vc.sort(key=operator.itemgetter(2))

    def add_recommendation(self):
        # add the recommendation
        scc_node, inc_node, vc = -1, random.sample(self.scc, 1)[0], -1
        while inc_node in self.scc:
            scc_node, inc_node, vc = self.scc_inc_vc.pop()
        self.g_small.graph.add_edge(self.wid2node_small[scc_node],
                                    self.wid2node_small[inc_node])

        # compute the effects of adding it
        vc_change = 0
        scc_change = 0
        # TODO: scc_node and inc_node are wpids, self.node2out_component saves graph vertex ids
        pdb.set_trace()
        for node in self.node2out_component[inc_node]:
            if node not in self.scc:
                self.scc.add(node)
                self.inc.remove(node)
                vc_change += self.id2views[node]
                scc_change += 1
        self.scc_sizes.append(self.scc_sizes[-1] + scc_change)
        self.scc_sum_vc += vc_change
        self.inc_sum_vc -= vc_change
        vc_ratio = (self.scc_sum_vc / len(self.scc)) /\
                   (self.inc_sum_vc / len(self.inc))
        self.vc_ratios.append(vc_ratio)

    def recommend(self):
        self.get_reach()
        self.get_recommendation_candidates()
        print('adding recommendations...')
        for i in range(self.n_recs):
            print('\r   ', i+1, '/', self.n_recs, end='')
            self.add_recommendation()
        print()

        self.g_small.stats['recs_vc_based_vc_ratio'] = self.vc_ratios
        self.g_small.stats['recs_vc_based_scc_size'] = self.scc_sizes
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


if __name__ == '__main__':
    vc_recommender = ViewCountRecommender('simple', n_recs=10)
    vc_recommender.recommend()

    # vc_recommender = ViewCountRecommender('it', n_recs=10)
    # vc_recommender.recommend()


    # st = TestRecommender()
    # st.test_node2reach()
    # st.test_node2reach2()
    # st.test_node2reach3()
    # st.test_node2reach4()

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


