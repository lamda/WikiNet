# -*- coding: utf-8 -*-

from __future__ import division, print_function
try:
    import graph_tool.all as gt
except ImportError:
    pass
import io
import os
import pdb

from main import Graph
from tools import read_pickle, write_pickle, url_unescape


def get_top_n(nodes, node2val, topn):
    topviews =[0 for i in xrange(topn)]
    topnodes =[0 for i in xrange(topn)]
    minviews = 0
    minnodes = 0
    for v in nodes:
        if node2val[int(v)] > minviews:
            topviews[minnodes] = node2val[v]
            topnodes[minnodes] = v
            minviews = min(topviews)
            minnodes = topviews.index(minviews)
    return sorted([(a, b) for a, b in zip(topnodes, topviews)],
                  key=lambda x: x[1], reverse=True)


def debug(*text):
    """wrapper for the print function that can be turned on and off"""
    if True:
        print(' '.join(str(t) for t in text))


def find_nodes(start_node, to_find):
    # via networkx.algorithms.simple_paths.all_simple_paths
    reached_nodes = set()
    visited = [start_node]
    stack = [start_node.out_neighbours()]
    while stack:
        node = stack[-1]
        nb = next(node, None)
        if nb is None:
            stack.pop()
            visited.pop()
        elif nb in to_find:
            reached_nodes |= set(visited)
        elif nb not in visited:
            visited.append(nb)
            stack.append(nb.out_neighbours())
    return reached_nodes


def get_reach(graph, nodes, to_find):
    node2reach = {}
    for nidx, node in enumerate(nodes):
        print('\r', nidx+1, '/', len(nodes), end='')
        # print(nidx+1, '/', len(nodes))
        reach = find_nodes(graph.vertex(node), to_find)
        node2reach[node] = len(reach)
        # node2reach[node] = reach
    print()
    return node2reach


def test_node2reach():
    g = gt.Graph(directed=True)
    v0 = g.add_vertex()
    v1 = g.add_vertex()
    v2 = g.add_vertex()
    v3 = g.add_vertex()
    v4 = g.add_vertex()
    v5 = g.add_vertex()
    v00 = g.add_vertex()
    g.add_edge_list([
        (v1, v0),
        (v2, v00),
        (v2, v0),
        (v2, v1),
        (v3, v1),
        (v3, v2),
        (v3, v4),
        (v4, v5),
    ])
    node2reach = get_reach(g, [v1, v2, v3, v4, v5], set([v0]))
    # node2reach = get_reach(g, [v3], set([v0]))
    result = []
    for n, r in node2reach.items():
        print(n, r)
        result.append((int(n), r))
    assert result == [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 0),
        (5, 0),
    ]


def add_recommendations(label):
    wp_small = 'first_p'
    wp_large = 'lead'
    g = Graph(data_dir=os.path.join('data', label + 'wiki'),
              fname='links', use_sample=False, refresh=False, N=wp_small)
    g.load_graph(refresh=False)
    scc_size, vc_ratio = g.get_recommendation_stats()


if __name__ == '__main__':

    # test_node2reach()

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


