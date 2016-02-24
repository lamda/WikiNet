# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import io
import numpy as np
import os
import pdb
import random


class Graph(object):
    graph_folder = 'graphs'
    matrix_folder = 'matrix'
    stats_folder = os.path.join(graph_folder, 'stats')

    def __init__(self, fname='', N=None, use_sample=False, refresh=False,
                 suffix=''):
        print(fname, N, 'use_sample =', use_sample, 'refresh =', refresh)
        if not os.path.exists(Graph.stats_folder):
            os.makedirs(Graph.stats_folder)
        self.use_sample = use_sample
        self.graph_name = fname if not use_sample else fname + '_sample'
        self.graph_file_path = os.path.join(Graph.graph_folder,
                                            self.graph_name + '.tsv')
        self.N = N
        self.gt_file_path = os.path.join(
            Graph.graph_folder,
            self.graph_name + '_' + str(self.N) + suffix + '.gt'
        )
        self.stats_file_path = os.path.join(
            Graph.stats_folder,
            self.graph_name + '_' + str(self.N) + suffix + '.obj'
        )
        self.graph = gt.Graph(directed=True)
        self.names = self.graph.new_vertex_property('string')
        lbd_add = lambda: self.graph.add_vertex()
        self.name2node = collections.defaultdict(lbd_add)

    def load_graph(self, graph=None, refresh=False):
        if graph is not None:
            self.graph = graph
            print('graph set directly')
        elif refresh:
            self.load_from_adjacency_list()
            self.save()
            print('graph loaded from adjacency list')
        else:
            try:
                self.load_from_file()
                print('graph loaded from .gt file')
            except IOError:
                self.load_from_adjacency_list()
                self.save()
                print('graph loaded from adjacency list')

    def load_from_file(self):
        self.graph = gt.load_graph(self.gt_file_path, fmt='gt')

    def get_all_nodes_from_adjacency_list(self):
        print('getting all nodes...')
        nodes = set()
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for index, line in enumerate(infile):
                print('\r', index, '/', 15791883, end='')
                node, nbs = line.strip().split('\t')[:2]
                nbs = nbs.split(';')[:self.N]
                nodes.add(node)
                nodes.update(nbs)
        return nodes

    def get_recommenders_from_adjacency_list(self):
        recommenders = set()
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for index, line in enumerate(infile):
                recommenders.add(line.strip().split('\t')[0])
        return recommenders

    def load_nodes_from_adjacency_list(self):
        nodes = self.get_all_nodes_from_adjacency_list()
        for node in nodes:
            v = self.name2node[node]
            self.names[v] = node
        self.graph.vp['name'] = self.names

    def load_from_adjacency_list(self):
        self.load_nodes_from_adjacency_list()
        print('loading edges...')
        edges = []
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for index, line in enumerate(infile):
                print('\r', index, '/', 15791883, end='')
                node, nbs = line.strip().split('\t')
                nbs = nbs.split(';')[:self.N]
                v = self.graph.vertex_index[self.name2node[node]]
                edges += [(v, self.graph.vertex_index[self.name2node[n]])
                          for n in nbs]
        self.graph.add_edge_list(edges)

    def save(self):
        self.graph.save(self.gt_file_path, fmt='gt')

    def compute_stats(self):
        print('computing stats...')
        stats = {}
        data = self.basic_stats()
        stats['graph_size'], stats['recommenders'], stats['outdegree_av'] = data
        stats['cc'] = self.clustering_coefficient()
        stats['cp_size'], stats['cp_count'] = self.largest_component()
        stats['bow_tie'] = self.bow_tie()
        stats['lc_ecc'] = self.eccentricity()

        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(stats, outfile, -1)
        print()

    def update_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            stats = pickle.load(infile)

        # data = self.basic_stats()
        # stats['graph_size'], stats['recommenders'], stats['outdegree_av'] = data
        # print(stats['cp_size'], stats['cp_size'] * stats['graph_size'] / 100,
        #       0.01 * stats['cp_size'] * stats['graph_size'] / 100)
        # print(100 * stats['recommenders'] / stats['graph_size'])
        # stats['cp_size'], stats['cp_count'] = self.largest_component()
        # stats['lc_ecc'] = self.eccentricity()
        stats['cp_size'], stats['cp_count'] = self.largest_component()
        # print('SCC size:', stats['cp_size'] * self.graph.num_vertices())
        # stats['bow_tie'] = self.bow_tie()

        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(stats, outfile, -1)
        print()

    def aggregate_ecc(self, dirname):
        fnames = os.listdir(dirname)
        ecc = collections.defaultdict(int)
        for fname in fnames:
            with io.open(dirname + '/' + fname, encoding='utf-8') as infile:
                for line in infile:
                    data = int(line.strip())
                    ecc[data] += 1
        ecc = [ecc[i] for i in range(max(ecc.keys()) + 2)]
        ecc = [100 * v / sum(ecc) for v in ecc]
        return ecc

    def basic_stats(self):
        print('basic_stats():')
        graph_size = self.graph.num_vertices()
        recommenders = len(self.get_recommenders_from_adjacency_list())
        pm = self.graph.degree_property_map('out')
        outdegree_av = float(np.mean(pm.a[pm.a != 0]))
        print('    ', graph_size, 'nodes in graph')
        print('    ', recommenders, 'recommenders in graph')
        print('     %.2f average out-degree' % outdegree_av)
        return graph_size, recommenders, outdegree_av

    def clustering_coefficient(self, minimal_neighbors=2):
        print('clustering_coefficient()')
        clustering_coefficient = 0
        neighbors = {int(node): set([int(n) for n in node.out_neighbours()])
                     for node in self.graph.vertices()}
        for idx, node in enumerate(self.graph.vertices()):
            node = int(node)
            if len(neighbors[node]) < minimal_neighbors:
                continue
            edges = sum(len(neighbors[int(n)] & neighbors[node])
                        for n in neighbors[node])
            cc = edges / (len(neighbors[node]) * (len(neighbors[node]) - 1))
            clustering_coefficient += cc
        return clustering_coefficient / self.graph.num_vertices()

    def largest_component(self):
        print('largest_component()')
        component, histogram = gt.label_components(self.graph)
        return [
            100 * max(histogram) / self.graph.num_vertices(),
            len(histogram),
        ]

    def bow_tie(self):
        print('bow tie')

        component, histogram = gt.label_components(self.graph)
        label_of_largest_component = np.argmax(histogram)
        largest_component = (component.a == label_of_largest_component)
        lcp = gt.GraphView(self.graph, vfilt=largest_component)

        # Core, In and Out
        all_nodes = set(int(n) for n in self.graph.vertices())
        scc = set([int(n) for n in lcp.vertices()])
        scc_node = random.sample(scc, 1)[0]
        graph_reversed = gt.GraphView(self.graph, reversed=True)

        outc = np.nonzero(gt.label_out_component(self.graph, scc_node).a)[0]
        inc = np.nonzero(gt.label_out_component(graph_reversed, scc_node).a)[0]
        outc = set(outc) - scc
        inc = set(inc) - scc

        # Tubes, Tendrils and Other
        wcc = gt.label_largest_component(self.graph, directed=False).a
        wcc = set(np.nonzero(wcc)[0])
        tube = set()
        out_tendril = set()
        in_tendril = set()
        other = all_nodes - wcc
        remainder = wcc - inc - outc - scc

        for idx, r in enumerate(remainder):
            print(idx+1, '/', len(remainder), end='\r')
            predecessors = set(np.nonzero(gt.label_out_component(graph_reversed, r).a)[0])
            successors = set(np.nonzero(gt.label_out_component(self.graph, r).a)[0])
            if any(p in inc for p in predecessors):
                if any(s in outc for s in successors):
                    tube.add(r)
                else:
                    in_tendril.add(r)
            elif any(s in outc for s in successors):
                out_tendril.add(r)
            else:
                other.add(r)

        vp_bowtie = self.graph.new_vertex_property('string')
        for component, label in [
            (inc, 'IN'),
            (scc, 'SCC'),
            (outc, 'OUT'),
            (in_tendril, 'TL_IN'),
            (out_tendril, 'TL_OUT'),
            (tube, 'TUBE'),
            (other, 'OTHER')
        ]:
            for node in component:
                vp_bowtie[self.graph.vertex(node)] = label
        self.graph.vp['bowtie'] = vp_bowtie
        self.save()

        bow_tie = [inc, scc, outc, in_tendril, out_tendril, tube, other]
        bow_tie = [100 * len(x)/self.graph.num_vertices() for x in bow_tie]
        return bow_tie

    def eccentricity(self):
        component, histogram = gt.label_components(self.graph)
        label_of_largest_component = np.argmax(histogram)
        largest_component = (component.a == label_of_largest_component)
        graph_copy = self.graph.copy()
        lcp = gt.GraphView(graph_copy, vfilt=largest_component)
        lcp.purge_vertices()
        lcp.clear_filters()

        print('eccentricity() for lcp of', lcp.num_vertices(), 'vertices')
        ecc = collections.defaultdict(int)
        vertices = [int(v) for v in lcp.vertices()]
        sample_size = int(0.15 * lcp.num_vertices())
        if sample_size == 0:
            sample_size = lcp.num_vertices()
        sample = random.sample(vertices, sample_size)
        for idx, node in enumerate(sample):
            print(idx+1, '/', len(sample), end='\r')
            dist = gt.shortest_distance(lcp, source=node).a
            ecc[max(dist)] += 1
        ecc = [ecc[i] for i in range(max(ecc.keys()) + 2)]
        lc_ecc = [100 * v / sum(ecc) for v in ecc]
        return lc_ecc


def convert_graph_file(fname):
    fpath_old = os.path.join('graphs', fname)
    fpath_new = os.path.join('graphs', ''.join(fname.split('_original')))
    with io.open(fpath_old, encoding='utf-8') as infile,\
        io.open(fpath_new, 'w', encoding='utf-8') as outfile:
        cur_node, cur_nbs = None, []
        for lidx, line in enumerate(infile):
            if (lidx % 1000) == 0:
                print('\r', lidx, '/', 80482288, end='')
            if lidx == 0:
                continue
            node, nb = line.strip().split('\t')[:2]
            if cur_node is not None and node != cur_node:
                outfile.write(cur_node + '\t' + ';'.join(cur_nbs) + '\n')
                cur_nbs = []
            cur_nbs.append(nb)
            cur_node = node
        outfile.write(cur_node + '\t' + ';'.join(cur_nbs) + '\n')


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # convert_graph_file('recommender_network_top20links_original.tsv')
    
    g = Graph(fname='recommender_network_top20links', N=1,
              use_sample=False, refresh=False)
    g.load_graph(refresh=False)
    g.compute_stats()
    g.update_stats()
    
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))





