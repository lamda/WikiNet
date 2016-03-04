# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import json
import io
import numpy as np
import operator
import os
import pandas as pd
import pdb
import random
import re
import urllib


DATA_DIR = 'enwiki'
WIKI_NAME = 'enwiki'
WIKI_CODE = 'en'
DUMP_DATE = '20150304'


def debug_iter(iterable, length=None):
    for index, element in enumerate(iterable):
        if (index % 1000) == 0:
            # print('\r', index, '/', length, end='')
            print('\r', index, end='')
        yield element


def convert_graph_file(fname):
    fpath_old = os.path.join('enwiki', fname)
    fpath_new = os.path.join('enwiki', ''.join(fname.split('_original')))
    node2nbs = collections.defaultdict(list)
    with io.open(fpath_old, encoding='utf-8') as infile:
        for lidx, line in enumerate(infile):
            if (lidx % 1000) == 0:
                print('\r', lidx, '/', 80482288, end='')
            if lidx == 0:
                continue
            node, nb = line.strip().split('\t')[:2]
            node2nbs[node].append(nb)

    with io.open(fpath_new, 'w', encoding='utf-8') as outfile:
        for node, nbs in node2nbs.items():
            outfile.write(node + '\t' + ';'.join(nbs) + '\n')


def read_pickle(fpath):
    with open(fpath, 'rb') as infile:
        obj = pickle.load(infile)
    return obj


def url_escape(title):
    # return title.replace("\\'", "%27")\
    #             .replace('\\"', '%22')\
    #             .replace('\\%', '%25')\
    #             .replace('\\\\', '%5C')\
    #             .replace(u'\u2013', '%E2%80%93')
    title = title.replace("\\'", "'")\
                    .replace('\\"', '"')\
                    .replace('\\_', '_')\
                    .replace('\\%', '%')\
                    .replace('\\\\', '\\')\
                    .replace(' ', '_')
    title = urllib.quote(title.encode('utf-8'))

    # unquote a few chars back because they appear in Wikipedia
    for quoted, unquoted in [
        ('%21', '!'),
        ('%22', '"'),
        # ('%23', '#'),
        ('%24', '$'),
        ('%25', '%'),
        ('%26', '&'),
        # ('%27', "'"),
        ('%28', '('),
        ('%29', ')'),
        ('%2A', '*'),
        # ('%2B', '+'),
        ('%2C', ','),
        ('%2D', '-'),
        ('%2E', '.'),
        ('%2F', '/'),
        ('%3A', ':'),
        ('%3B', ';'),
        ('%3C', '<'),
        ('%3D', '='),
        ('%3E', '>'),
        ('%3F', '?'),
        ('%40', '@'),
    ]:
        title = title.replace(quoted, unquoted)

    return title


def get_id_dict(data_dir, wiki_name, dump_date):
    id2title = {}
    fname = os.path.join(data_dir, wiki_name + '-' + dump_date + '-page.sql')
    with io.open(fname, encoding='utf-8') as infile:
        lidx = 1
        for line in infile:
            print('\r', lidx, end='')
            lidx += 1
            if not line.startswith('INSERT'):
                continue
            # matches = re.findall(r"\((\d+),(\d+),'([^\']+)", line)
            # matches = re.findall(r"\((\d+),(\d+),'(.*?)(?<!\\)'", line)
            matches = re.findall(r"\((\d+),(\d+),'(.*?)((?<!\\)|(?<=\\\\))'", line)
            for page_id, page_namespace, page_title, dummy in matches:
                if page_namespace != '0':
                    continue
                id2title[int(page_id)] = url_escape(page_title)
        with open(os.path.join(data_dir, 'id2title.obj'), 'wb') as outfile:
            pickle.dump(id2title, outfile, -1)


def check_files(data_dir):
    damaged = []
    id2title = read_pickle(os.path.join(data_dir, 'id2title.obj'))
    for pid in debug_iter(id2title.keys()):
        pid_u = unicode(pid)
        fpath = os.path.join(data_dir, 'html', pid_u + '.txt   ')
        with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
            try:
                data = json.load(infile)
            except ValueError:
                print('\n\t', pid)
                damaged.append(pid)

    with io.open(os.path.join(data_dir, 'damaged.txt'), 'w', encoding='utf-8')\
            as outfile:
        for d in sorted(damaged):
            outfile.write(unicode(d) + '\n')


def get_redirect_dict(data_dir, wiki_name, dump_date):
    id2redirect = {}
    fname = os.path.join(data_dir, wiki_name + '-' + dump_date + '-redirect.sql')
    with io.open(fname, encoding='utf-8') as infile:
        lidx = 1
        for line in infile:
            print(lidx, end='\r')
            lidx += 1
            if not line.startswith('INSERT'):
                continue
            # matches = re.findall(r"\((\d+),(\d+),'([^\']+)", line)
            # matches = re.findall(r"\((\d+),(\d+),'(.*?)(?<!\\)'", line)
            matches = re.findall(r"\((\d+),(\d+),'(.*?)((?<!\\)|(?<=\\\\))'", line)
            for page_id, page_namespace, page_title, dummy in matches:
                if page_namespace != '0':
                    continue
                id2redirect[int(page_id)] = url_escape(page_title)

        with open(os.path.join(data_dir, 'id2redirect.obj'), 'wb') as outfile:
            pickle.dump(id2redirect, outfile, -1)


def get_resolved_redirects(data_dir):
    # id2title = read_pickle(os.path.join(data_dir, 'id2title.obj'))
    # title2id = {v: k for k, v in id2title.iteritems()}
    # id2redirect = read_pickle(os.path.join(data_dir, 'id2redirect.obj'))
    #
    # title2redirect = {}
    # idx = 1
    # length = len(id2redirect)
    # for k, v in id2redirect.iteritems():
    #     print(idx, '/', length, end='\r')
    #     idx += 1
    #     try:
    #         title2redirect[id2title[k]] = title2id[v]
    #     except KeyError:
    #         pass
    # with open(os.path.join(data_dir, 'title2redirect.obj'), 'wb') as outfile:
    #     pickle.dump(title2redirect, outfile, -1)

    # damaged = []
    # title2redirect = {}
    # id2title = read_pickle(os.path.join(data_dir, 'id2title.obj'))
    # for pid in debug_iter(id2title):
    #     pid_u = unicode(pid)
    #     fpath = os.path.join(data_dir, 'html', pid_u + '.txt   ')
    #     with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
    #         try:
    #             data = json.load(infile)
    #             rd_from = data['query']['redirects'][0]['from']
    #             rd_to = data['query']['redirects'][0]['to']
    #             title2redirect[url_escape(rd_from)] = url_escape(rd_to)
    #         except KeyError:
    #             continue
    #         except ValueError:
    #             print(pid)
    #             damaged.append(pid)
    #
    # if damaged:
    #     for d in damaged:
    #         print(d)
    # else:
    #     with open(os.path.join(data_dir, 'title2redirect.obj'), 'wb') as outfile:
    #         pickle.dump(title2redirect, outfile, -1)

    title2redirect = {}
    file_names = [
        f
        for f in os.listdir(os.path.join(data_dir, 'html'))
        if f.endswith('.obj')
    ]
    for fidx, file_name in enumerate(file_names):
        print('\r', fidx, '/', len(file_names))
        df = pd.read_pickle(os.path.join(data_dir, 'html', file_name))
        df = df[~df['redirects_to'].isnull()]
        for k, v in zip(df['title'], df['redirects_to']):
            title2redirect[k] = v

    with open(os.path.join(data_dir, 'title2redirect.obj'), 'wb') as outfile:
         pickle.dump(title2redirect, outfile, -1)


class Graph(object):
    def __init__(self, data_dir, fname='', use_sample=False,
                 refresh=False, suffix='', N=None):
        print(fname, N, 'use_sample =', use_sample, 'refresh =', refresh)
        self.data_dir = data_dir
        self.stats_folder = os.path.join(self.data_dir, 'stats')
        if not os.path.exists(self.stats_folder):
            os.makedirs(self.stats_folder)
        self.use_sample = use_sample
        self.graph_name = fname if not use_sample else fname + '_sample'
        self.graph_file_path = os.path.join(self.data_dir,
                                            self.graph_name + '.tsv')
        self.N = N
        self.gt_file_path = os.path.join(
            self.data_dir,
            self.graph_name + '_' + str(self.N) + suffix + '.gt'
        )
        self.stats_file_path = os.path.join(
            self.stats_folder,
            self.graph_name + '_' + str(self.N) + suffix + '.obj'
        )
        self.graph = gt.Graph(directed=True)
        self.names = self.graph.new_vertex_property('string')
        lbd_add = lambda: self.graph.add_vertex()
        self.name2node = collections.defaultdict(lbd_add)

    def load_graph(self, refresh=False):
        if refresh:
            self.load_graph_from_adjacency_list()
            self.save()
            print('graph loaded from adjacency list')
        else:
            try:  # load the .gt file
                self.graph = gt.load_graph(self.gt_file_path, fmt='gt')
                print('graph loaded from .gt file')
            except IOError:  # fall back to text file
                self.load_graph_from_adjacency_list()
                self.save()
                print('graph loaded from adjacency list')

    def load_graph_from_adjacency_list(self):
        print('\ngetting all nodes...')
        nodes = set()
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for line in debug_iter(infile):
                parts = line.strip().split('\t')
                node = parts[0]
                nodes.add(node)
                if len(parts) > 1:
                    nbs = parts[1].split(';')[:self.N]
                    nodes.update(nbs)

        print('\nadding nodes to graph...')
        for node in debug_iter(nodes, len(nodes)):
            v = self.name2node[node]
            self.names[v] = node
        self.graph.vp['name'] = self.names

        print('\nloading edges...')
        edges = []
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for line in debug_iter(infile):
                parts = line.strip().split('\t')
                if len(parts) > 1:
                    v = self.graph.vertex_index[self.name2node[parts[0]]]
                    nbs = parts[1].split(';')[:self.N]
                    edges += [(v, self.graph.vertex_index[self.name2node[n]])
                              for n in nbs]
        self.graph.add_edge_list(edges)

        print('loading titles...')
        # load id2title dict
        with open(os.path.join(self.data_dir, 'id2title.obj'), 'rb') as infile:
            id2title = pickle.load(infile)

        # assign titles as a vertex property
        vp_title = self.graph.new_vertex_property('string')
        for vertex in self.graph.vertices():
            vp_title[self.graph.vertex(vertex)] = id2title[int(self.graph.vp['name'][vertex])]
        self.graph.vp['title'] = vp_title
        self.save()

    def save(self):
        self.graph.save(self.gt_file_path, fmt='gt')

    def compute_stats(self):
        print('computing stats...')
        stats = {}
        data = self.basic_stats()
        stats['graph_size'], stats['recommenders'], stats['outdegree_av'] = data
        # stats['cc'] = self.clustering_coefficient()
        stats['cp_size'], stats['cp_count'] = self.largest_component()
        if self.N == 1:
            stats['singles'], stats['comp_stats'] = self.cycle_components()
        # stats['bow_tie'] = self.bow_tie()
        # stats['lc_ecc'] = self.eccentricity()

        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(stats, outfile, -1)
        print()

    def update_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            stats = pickle.load(infile)

        data = self.basic_stats()
        stats['graph_size'], stats['recommenders'], stats['outdegree_av'] = data

        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(stats, outfile, -1)
        print()

    def print_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            stats = pickle.load(infile)
        for k, v in stats.items():
            if k in {'comp_stats', 'singles'}:
                continue
            print(k, v)
        print('found', stats['singles'], 'single components')

        cstats = stats['comp_stats']
        print('top 10 cycles by cycle length')
        for comp_stat in cstats[:10]:
            print('len=%d, incomp_len=%d' %
                  (comp_stat['len'], comp_stat['incomp_size']))
            print('    ' + ', '.join(comp_stat['names']))

        print('\ntop 10 cycles by incomponent length')
        no_articles = sum(comp_stat['incomp_size'] for comp_stat in cstats)
        cstats.sort(key=operator.itemgetter('incomp_size'), reverse=True)
        cover = sum(comp_stat['incomp_size']
                    for comp_stat in cstats[:10]) / no_articles
        print('    covering %.2f%% of articles' % (100 * cover))
        for comp_stat in cstats[:10]:
            print('len=%d, incomp_len=%d, incomp_perc=%.2f' %
                  (comp_stat['len'], comp_stat['incomp_size'], 100 * comp_stat['incomp_size'] / no_articles))
            print('    ' + ', '.join(comp_stat['names']))

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

    def get_recommenders_from_adjacency_list(self):
        recommenders = set()
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for index, line in enumerate(infile):
                recommenders.add(line.strip().split('\t')[0])
        return recommenders

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

    def largest_component(self):
        print('largest_component()')
        component, histogram = gt.label_components(self.graph)
        return [
            100 * max(histogram) / self.graph.num_vertices(),  # size of SCC
            len(histogram),  # number of strongly connected components
        ]

    def cycle_components(self):
        print('cycle_components()')
        component, histogram = gt.label_components(self.graph)
        print('    get number of vertices per component')
        comp2verts = {i: list() for i in range(len(histogram))}
        for node, comp in enumerate(component.a):
            comp2verts[comp].append(node)
        comp2verts = {k: v for k, v in comp2verts.items() if len(v) > 1}
        singles = self.graph.num_vertices() -\
            sum(len(i) for i in comp2verts.items())

        print('    get all components with at least two vertices')
        comps = []
        for comp, verts in comp2verts.items():
            comps.append(verts)
        comps.sort(key=len)

        print('    get the sizes of the incomponents')
        incomps = []
        graph_reversed = gt.GraphView(self.graph, reversed=True, directed=True)
        for comp in comps:
            comp_node = random.sample(comp, 1)[0]
            incomps.append(
                np.count_nonzero(
                    gt.label_out_component(graph_reversed, comp_node).a
                )
            )

        print('    get the names of nodes in the components')
        comp_names = []
        for cidx, comp in enumerate(comps):
            # print('\r       ', cidx, '/', len(comps), end='')
            names = []
            node = random.sample(comp, 1)[0]
            name_start = self.graph.vp['title'][node]
            name = ''
            while name != name_start:
                node = self.graph.vertex(node).out_neighbours().next()
                name = self.graph.vp['title'][node]
                # print(node, name)
                # pdb.set_trace()
                names.append(name)
            comp_names.append(names)
        print()

        comp_stats = []
        for comp, incomp_size, comp_name in zip(comps, incomps, comp_names):
            comp_stats.append(
                {
                    'vertices': comp,
                    'names': comp_name,
                    'len': len(comp),
                    'incomp_size': incomp_size
                }
            )
        comp_stats.sort(key=operator.itemgetter('len'), reverse=True)

        return singles, comp_stats

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
        graph_reversed = gt.GraphView(self.graph, reversed=True, directed=True)

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


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # convert_graph_file('recommender_network_top20links_original.tsv')
    # get_id_dict()

    # g = Graph(data_dir=DATA_DIR, fname='recommender_network_top20links',
    #           use_sample=False, refresh=False, N=1)
    # g.load_graph(refresh=False)
    # g.compute_stats()
    # g.print_stats()
    # # g.update_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))





