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

from crawler import Crawler
from parsers import WikipediaHTMLParser, WikipediaDivTableParser
from tools import debug_iter, read_pickle, write_pickle, url_escape


DATA_DIR = 'enwiki'
WIKI_NAME = 'enwiki'
WIKI_CODE = 'en'
DUMP_DATE = '20150304'


np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)


class Wikipedia(object):
    def __init__(self, label, dump_date):
        self.wiki_code = label
        self.wiki_name = label + 'wiki'
        self.data_dir = os.path.join('data', self.wiki_name)
        self.dump_date = dump_date
        self._id2title, self._title2id, self._title2redirect = None, None, None
        self._parsers = {}

    @property
    def id2title(self):
        if self._id2title is None:
            print('loading id2title...')
            fpath = os.path.join(self.data_dir, 'id2title.obj')
            self._id2title = read_pickle(fpath)
        return self._id2title

    @property
    def title2id(self):
        if self._id2title is None:
            print('loading id2title...')
            fpath = os.path.join(self.data_dir, 'id2title.obj')
            self._id2title = read_pickle(fpath)
        if self._title2id is None:
            self._title2id = {v: k for k, v in self._id2title.items()}
        return self._title2id

    @property
    def title2redirect(self):
        if self._title2redirect is None:
            print('loading title2redirect...')
            fpath = os.path.join(self.data_dir, 'title2redirect.obj')
            self._title2redirect = read_pickle(fpath)
        return self._title2redirect

    def get_parser(self, link_type):
        try:
            return self._parsers[link_type]
        except KeyError:
            if link_type == 'all':
                parser = WikipediaHTMLParser(self.wiki_name)
            elif link_type == 'divs_tables':
                parser = WikipediaDivTableParser()
            else:
                print('Parser type not supported')
                pdb.set_trace()
            self._parsers[link_type] = parser
            return self._parsers[link_type]

    def get_id_dict(self):
        id2title = {}
        fname = os.path.join(self.data_dir, self.wiki_name + '-' +
                             self.dump_date + '-page.sql')
        with io.open(fname, encoding='utf-8') as infile:
            lidx = 1
            for line in infile:
                print('\r', lidx, end='')
                lidx += 1
                if not line.startswith('INSERT'):
                    continue
                # matches = re.findall(r"\((\d+),(\d+),'([^\']+)", line)
                # matches = re.findall(r"\((\d+),(\d+),'(.*?)(?<!\\)'", line)
                matches = re.findall(
                    r"\((\d+),(\d+),'(.*?)((?<!\\)|(?<=\\\\))'",
                    line
                )
                for page_id, page_namespace, page_title, dummy in matches:
                    if page_namespace != '0':
                        continue
                    id2title[int(page_id)] = url_escape(page_title)
            with open(os.path.join(self.data_dir, 'id2title.obj'), 'wb')\
                    as outfile:
                pickle.dump(id2title, outfile, -1)

    def crawl(self, recrawl_damaged=False):
        pids = sorted(self.id2title)
        Crawler(self.wiki_name, self.wiki_code, self.data_dir, self.dump_date,
                pids=pids, recrawl_damaged=recrawl_damaged)

    def get_resolved_redirects(self):
        print('getting resolved redirects...')
        title2redirect = {}
        file_names = [
            f
            for f in os.listdir(os.path.join(self.data_dir, 'html'))
            if f.endswith('.obj')
        ]
        for fidx, file_name in enumerate(file_names):
            print('\r', fidx+1, '/', len(file_names), end='')
            df = pd.read_pickle(os.path.join(self.data_dir, 'html', file_name))
            df = df[~df['redirects_to'].isnull()]
            for k, v in zip(df['title'], df['redirects_to']):
                title2redirect[k] = v
        print()

        with open(os.path.join(self.data_dir, 'title2redirect.obj'), 'wb')\
                as outfile:
            pickle.dump(title2redirect, outfile, -1)

    def get_links(self, link_type, start=None, stop=None):
        print('getting links for type', link_type)

        html_dir = os.path.join(self.data_dir, 'html')
        file_names = [
            f
            for f in os.listdir(html_dir)
            if f.endswith('.obj')
        ][start:stop]

        file_dir = os.path.join(self.data_dir, 'html', 'divs_tables')
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        for fidx, file_name in enumerate(file_names):
            print('\r', fidx+1, '/', len(file_names), end='')
            fpath = os.path.join(html_dir, file_name)
            if link_type == 'all':
                self.get_link_chunk_all(fpath)
            elif link_type == 'divs_tables':
                self.get_link_chunk_divs_tables(fpath)
            ## df = pd.read_pickle(fpath)
            ## df.rename(columns={'first_lead_links': 'first_p_links'}, inplace=True)
            ## pd.to_pickle(df, fpath)

        print()

        if link_type == 'all':
            self.combine_link_chunks()
        elif link_type == 'divs_tables':
            self.combine_divs_tables_chunks()

    def get_link_chunk_all(self, file_path):
        parser = self.get_parser('all')
        df = pd.read_pickle(file_path)

        parsed_first_links, parsed_first_p_links, parsed_lead_links = [], [], []
        parsed_ib_links, parsed_all_links = [], []
        dbg_pid_found = False
        for idx, row in df.iterrows():
            # if row['pid'] == 955:
            #     dbg_pid_found = True
            # if not dbg_pid_found:
            #     continue
            if pd.isnull(row['redirects_to']):
                dbg = False
                # dbg_pid = 0
                # if row['pid'] == dbg_pid:
                #     dbg = True
                parser.feed(row['content'], debug=dbg)
                first_link, first_p_links, lead_links, ib_links,\
                    all_links = parser.get_data()

                # fix double % encoding
                first_link = [l.replace('%25', '%') for l in first_link]
                first_p_links = [l.replace('%25', '%') for l in first_p_links]
                lead_links = [l.replace('%25', '%') for l in lead_links]
                ib_links = [l.replace('%25', '%') for l in ib_links]
                all_links = [l.replace('%25', '%') for l in all_links]

                # if row['pid'] == dbg_pid:
                # print('Debug ID')
                # print('\nhttp://' + self.wiki_name +
                #       '.wikipedia.org?curid=%d' % row['pid'], row['title'])
                # print('----FIRST LINK:', first_link)
                # print('----IB LINKS:')
                # for l in ib_links[:10]:
                #     print('   ', l)
                # print('----LEAD LINKS:')
                # for l in lead_links[:10]:
                #     print('   ', l)
                # pdb.set_trace()
                # parser.feed(row['content'], debug=True)

                first_link = self.resolve_redirects(first_link)
                first_p_links = self.resolve_redirects(first_p_links)
                lead_links = self.resolve_redirects(lead_links)
                ib_links = self.resolve_redirects(ib_links)
                all_links = self.resolve_redirects(all_links)

                if first_link:
                    parsed_first_links.append(first_link)
                else:
                    parsed_first_links.append([np.nan])
                parsed_first_p_links.append(first_p_links)
                parsed_lead_links.append(lead_links)
                parsed_ib_links.append(ib_links)
                parsed_all_links.append(all_links)
            else:
                parsed_first_links.append([np.nan])
                parsed_first_p_links.append([])
                parsed_lead_links.append([])
                parsed_ib_links.append([])
                parsed_all_links.append([])

        df['first_link'] = parsed_first_links
        df['first_p_links'] = parsed_first_p_links
        df['lead_links'] = parsed_lead_links
        df['ib_links'] = parsed_ib_links
        df['all_links'] = parsed_all_links
        pd.to_pickle(df, file_path)

    def get_link_chunk_divs_tables(self, file_path):
        parser = self.get_parser('divs_tables')
        df = pd.read_pickle(file_path)
        divclass2id = collections.defaultdict(list)
        tableclass2id = collections.defaultdict(list)

        for idx, row in df.iterrows():
            if pd.isnull(row['redirects_to']):
                parser.feed(row['content'], row['pid'])
                divs, tables = parser.get_data()

                for k, v in divs.items():
                    divclass2id[k].append(v)
                for k, v in tables.items():
                    tableclass2id[k].append(v)

        file_dir = os.path.join(self.data_dir, 'html', 'divs_tables')
        file_name = file_path.split(os.path.sep)[-1]
        write_pickle(os.path.join(file_dir, file_name),
                     [divclass2id, tableclass2id])

    def combine_link_chunks(self):
        print('combining link chunks...')
        file_names = [
            f
            for f in os.listdir(os.path.join(self.data_dir, 'html'))
            if f.endswith('.obj')
        ]
        with io.open(os.path.join(self.data_dir, 'alllinks.tsv'), 'w',
                     encoding='utf-8') as outfile_all, \
            io.open(os.path.join(self.data_dir, 'links.tsv'), 'w',
                    encoding='utf-8') as outfile_lead:
            for fidx, file_name in enumerate(sorted(file_names)):
                print('\r', fidx + 1, '/', len(file_names), file_name, end='')
                fpath = os.path.join(self.data_dir, 'html', file_name)
                df = pd.read_pickle(fpath)
                for idx, row in df.iterrows():
                    if pd.isnull(row['redirects_to']):
                        outfile_all.write(
                            unicode(row['pid']) + '\t' +
                            ';'.join(row['all_links']) + '\n'
                        )
                        outfile_lead.write(
                            unicode(row['pid']) + '\t' +
                            unicode(row['first_link'][0]) + '\t' +
                            ';'.join(row['first_p_links']) + '\t' +
                            ';'.join(row['lead_links']) + '\t' +
                            ';'.join(row['ib_links']) + '\n'
                        )
            print()

    def combine_divs_tables_chunks(self):
        print('combining divs and tables chunks...')
        fpath = os.path.join(self.data_dir, 'html', 'divs_tables')
        file_names = [f for f in os.listdir(fpath) if f.endswith('.obj')]
        divclass2id = collections.defaultdict(list)
        tableclass2id = collections.defaultdict(list)
        for fidx, file_name in enumerate(sorted(file_names)):
            print('\r', fidx + 1, '/', len(file_names), file_name, end='')
            fpath = os.path.join(self.data_dir, 'html', 'divs_tables', file_name)
            divs, tables = read_pickle(fpath)
            for k, v in divs.items():
                divclass2id[k] += v
            for k, v in tables.items():
                tableclass2id[k] += v

        with io.open(os.path.join(self.data_dir, 'tables.tsv'), 'w',
                     encoding='utf-8') as outfile:
            for k in sorted(tableclass2id, key=lambda k: len(tableclass2id[k]),
                            reverse=True):
                outfile.write(unicode(len(tableclass2id[k])) + '\t' +
                              ' '.join(sorted(k)) + '\t' +
                              ';'.join(
                                  map(unicode, tableclass2id[k][:20])) + '\n')

        with io.open(os.path.join(self.data_dir, 'divs.tsv'), 'w',
                     encoding='utf-8') as outfile:
            for k in sorted(divclass2id, key=lambda k: len(divclass2id[k]),
                            reverse=True):
                outfile.write(unicode(len(divclass2id[k])) + '\t' +
                              ' '.join(sorted(k)) + '\t' +
                              ';'.join(
                                  map(unicode, divclass2id[k][:20])) + '\n')

    def resolve_redirects(self, links):
        result = []
        for link in links:
            try:
                result.append(self.title2id[self.title2redirect[link]])
            except KeyError:
                try:
                    result.append(self.title2id[link])
                except KeyError:
                    # a link to an article that didn't exist at DUMP_DATE, but
                    # unfortunately is linked in the old revision retrieved via API
                    # print('       ', link, 'not found ----')
                    pass
        return [unicode(l) for l in result]

    def cleanup(self):
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.gt')]
        for f in files:
            os.remove(os.path.join(self.data_dir, f))

    def to_file(self, data, file_name):
        with io.open(file_name, 'w', encoding='utf-8') as outfile:
            outfile.write(data)


class Graph(object):
    def __init__(self, wiki_code, refresh=False, N=None, verbose=False):
        self.verbose = verbose
        if self.verbose:
            print(N, 'refresh =', refresh)
        self.wiki_code = wiki_code
        self.wiki_name = wiki_code + 'wiki'
        self.N = N
        self.data_dir = os.path.join('data', self.wiki_name)
        self.stats_folder = os.path.join(self.data_dir, 'stats')
        if not os.path.exists(self.stats_folder):
            os.makedirs(self.stats_folder)
        self.graph_name = 'links'
        self.graph_file_path = os.path.join(
            self.data_dir,
            ('all' if self.N == 'all' else '') + self.graph_name + '.tsv'
        )
        self.gt_file_path = os.path.join(
            self.data_dir,
            self.graph_name + '_' + str(self.N) + '.gt'
        )
        self.stats_file_path = os.path.join(
            self.stats_folder,
            self.graph_name + '_' + str(self.N) + '.obj'
        )
        self.graph = gt.Graph(directed=True)
        self.names = self.graph.new_vertex_property('int32_t')
        lbd_add = lambda: self.graph.add_vertex()
        self.name2node = collections.defaultdict(lbd_add)
        self.stats = {}

    def load_graph(self, refresh=False):
        if refresh:
            self.load_graph_from_adjacency_list()
            self.save()
            if self.verbose:
                print('graph loaded from adjacency list')
        else:
            try:  # load the .gt file
                self.graph = gt.load_graph(self.gt_file_path, fmt='gt')
                if self.verbose:
                    print('graph loaded from .gt file')
            except IOError:  # fall back to text file
                self.load_graph_from_adjacency_list()
                self.save()
                if self.verbose:
                    print('graph loaded from adjacency list')

    def load_graph_from_adjacency_list(self):
        print('\ngetting all nodes...')
        nodes = set()
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for line in debug_iter(infile):
                if self.N == 'all':
                    node, nbs = line.split('\t')
                    nodes.add(node)
                    nbs = nbs.strip().split(';')
                    if nbs != [u'']:
                        nodes |= set(nbs)
                else:
                    data = line.split('\t')
                    node, first_link, first_p_links, lead_links, ib_links = data
                    node, first_link = node.strip(), first_link.strip()
                    first_p_links = first_p_links.strip()
                    lead_links, ib_links = lead_links.strip(), ib_links.strip()
                    nodes.add(node)
                    if self.N == 1 and first_link != 'nan':
                        nodes.add(first_link)
                    elif self.N == 'first_p' and first_p_links:
                        nodes |= set(first_p_links.split(';'))
                    elif self.N == 'lead' and lead_links:
                        nodes |= set(lead_links.split(';'))
                    elif self.N == 'infobox' and ib_links:
                        nodes |= set(ib_links.split(';'))

        print('\nadding nodes to graph...')
        for node in debug_iter(nodes, len(nodes)):
            v = self.name2node[node]
            self.names[v] = int(float(node))
        self.graph.vp['name'] = self.names

        print('\nloading edges...')
        edges = []
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for line in debug_iter(infile):
                if self.N == 'all':
                    node, nbs = line.split('\t')
                    nbs = nbs.strip().split(';')
                    if nbs == [u'']:
                        nbs = []
                else:
                    data = line.split('\t')
                    node, first_link, first_p_links, lead_links, ib_links = data
                    node, first_link = node.strip(), first_link.strip()
                    first_p_links = first_p_links.strip()
                    lead_links, ib_links = lead_links.strip(), ib_links.strip()
                    nbs = []
                    if self.N == 1 and first_link != 'nan':
                        nbs = [first_link]
                    elif self.N == 'first_p' and first_p_links:
                        nbs = first_p_links.split(';')
                    elif self.N == 'lead' and lead_links:
                        nbs = lead_links.split(';')
                    elif self.N == 'infobox' and ib_links:
                        nbs = ib_links.split(';')
                if nbs:
                    v = self.graph.vertex_index[self.name2node[node]]
                    edges += [(v, self.graph.vertex_index[self.name2node[n]])
                              for n in nbs]
        self.graph.add_edge_list(edges)

        print('\nloading titles...')
        # load id2title dict
        with open(os.path.join(self.data_dir, 'id2title.obj'), 'rb') as infile:
            id2title = pickle.load(infile)

        # assign titles as a vertex property
        vp_title = self.graph.new_vertex_property('string')
        for vertex in debug_iter(self.graph.vertices()):
            title = id2title[int(self.graph.vp['name'][vertex])]
            vp_title[self.graph.vertex(vertex)] = title
        self.graph.vp['title'] = vp_title
        self.save()

    def save(self):
        self.graph.save(self.gt_file_path, fmt='gt')

    def load_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            self.stats = pickle.load(infile)

    def save_stats(self):
        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(self.stats, outfile, -1)
        print()

    def compute_stats(self):
        print('computing stats...')
        self.stats['graph_size'], self.stats['recommenders'],\
            self.stats['outdegree_av'],\
            self.stats['outdegree_median'] = self.basic_stats()
        # # self.stats['cc'] = self.clustering_coefficient()
        self.stats['cp_size'], self.stats['cp_count'] = self.largest_component()
        # self.stats['pls'], self.stats['pls_max'] = self.path_lengths()
        if self.N == 1:
            self.stats['comp_stats'] = self.cycle_components()
        self.stats['bow_tie'] = self.bow_tie()
        self.stats['bow_tie_changes'] = self.compute_bowtie_changes()
        # self.stats['lc_ecc'] = self.eccentricity()
        self.save_stats()

    def update_stats(self):
        print('updating stats...')
        self.load_stats()
        if self.N == 1:
            self.stats['comp_stats'] = self.cycle_components()
        self.stats['bow_tie'] = self.bow_tie()
        self.stats['bow_tie_changes'] = self.compute_bowtie_changes()
        self.save_stats()

    def print_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            stats = pickle.load(infile)
        for k, v in stats.items():
            if k in {'comp_stats', 'singles', 'bow_tie'}:
                continue
            print(k, v)

        if 'comp_stats' in stats:
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
                      (comp_stat['len'], comp_stat['incomp_size'],
                       100 * comp_stat['incomp_size'] / no_articles))
                print('    ' + ', '.join(comp_stat['names']))

        if 'bow_tie' in stats:
            labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
            for val, label in zip(stats['bow_tie'], labels):
                print('    %.3f %s' % (val, label))

    def basic_stats(self):
        print('basic_stats():')
        graph_size = self.graph.num_vertices()
        recommenders = len(self.get_recommenders_from_adjacency_list())
        pm = self.graph.degree_property_map('out')
        # outdegree_av = float(np.mean(pm.a[pm.a != 0]))
        outdegree_av = float(np.mean(pm.a))
        outdegree_median = int(np.median(pm.a))
        print('    ', graph_size, 'nodes in graph')
        print('    ', recommenders, 'recommenders in graph')
        print('     %.2f average out-degree' % outdegree_av)
        print('     %d median out-degree' % outdegree_median)
        return graph_size, recommenders, outdegree_av, outdegree_median

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

    def largest_component(self):
        print('largest_component()')
        component, histogram = gt.label_components(self.graph)
        return [
            100 * max(histogram) / self.graph.num_vertices(),  # size of SCC
            len(histogram),  # number of strongly connected components
        ]

    def cycle_components(self):
        print('cycle_components()')

        print('    get number of vertices per component')
        component, histogram = gt.label_components(self.graph)
        comp2verts = {i: list() for i in range(len(histogram))}
        for node, comp in enumerate(component.a):
            comp2verts[comp].append(node)
        comps = []
        for cidx, (comp, verts) in enumerate(comp2verts.items()):
            if cidx + 1 % 1000 == 0:
                print('\r       ', cidx + 1, '/', len(comps), end='')
            # skip singleton component that are not endpoints
            if len(verts) == 1 and self.graph.vertex(verts[0]).out_degree() > 0:
                continue
            comps.append(verts)

        print('    get the sizes of the incomponents')
        incomps = []
        graph_reversed = gt.GraphView(self.graph, reversed=True, directed=True)
        for cidx, comp in enumerate(comps):
            if cidx+1 % 1000 == 0:
                print('\r       ', cidx+1, '/', len(comps), end='')
            inc = np.count_nonzero(
                gt.label_out_component(graph_reversed, comp[0]).a
            )
            incomps.append(inc)

        print('    get the names of nodes in the components')
        comp_names = [
            [self.graph.vp['title'][node] for node in comp]
            for comp in comps
        ]

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
        comp_stats.sort(key=operator.itemgetter('incomp_size'), reverse=True)

        return comp_stats

    def bow_tie_old(self):
        print('bow tie (old and slow version)')

        all_nodes = set(int(n) for n in self.graph.vertices())
        component, histogram = gt.label_components(self.graph)

        # Core, In and Out
        label_of_largest_component = np.argmax(histogram)
        largest_component = (component.a == label_of_largest_component)
        lcp = gt.GraphView(self.graph, vfilt=largest_component)
        scc = set([int(n) for n in lcp.vertices()])
        scc_node = random.sample(scc, 1)[0]
        graph_reversed = gt.GraphView(self.graph, reversed=True, directed=True)
        graph_undirected = gt.GraphView(self.graph, directed=False)

        outc = np.nonzero(gt.label_out_component(self.graph, scc_node).a)[0]
        inc = np.nonzero(gt.label_out_component(graph_reversed, scc_node).a)[0]
        outc = set(outc) - scc
        inc = set(inc) - scc

        # Tubes, Tendrils and Other
        wcc = set(
            np.nonzero(gt.label_out_component(graph_undirected, scc_node).a)[0]
        )
        tube = set()
        out_tendril = set()
        in_tendril = set()
        other = all_nodes - wcc
        remainder = wcc - inc - outc - scc
        for idx, r in enumerate(remainder):
            if (idx % 100) == 0:
                print('\r', '   ', idx+1, '/', len(remainder), end='')
            predecessors = set(
                np.nonzero(gt.label_out_component(graph_reversed, r).a)[0]
            )
            successors = set(
                np.nonzero(gt.label_out_component(self.graph, r).a)[0]
            )
            if any(p in inc for p in predecessors):
                if any(s in outc for s in successors):
                    tube.add(r)
                else:
                    in_tendril.add(r)
            elif any(s in outc for s in successors):
                out_tendril.add(r)
            else:
                other.add(r)
        print()

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

    def bow_tie(self):
        print('bow tie')

        all_nodes = set(int(n) for n in self.graph.vertices())
        component, histogram = gt.label_components(self.graph)

        # Core, In and Out
        if self.N == 1:
            # choose SCC with largest incomponent
            comp_stats = self.stats['comp_stats']
            comp_stats.sort(key=operator.itemgetter('incomp_size'), reverse=True)
            label_of_largest_component = component[comp_stats[0]['vertices'][0]]
        else:
            label_of_largest_component = np.argmax(histogram)

        largest_component = (component.a == label_of_largest_component)
        lcp = gt.GraphView(self.graph, vfilt=largest_component)
        scc = set([int(n) for n in lcp.vertices()])
        scc_node = random.sample(scc, 1)[0]
        graph_reversed = gt.GraphView(self.graph, reversed=True, directed=True)
        graph_undirected = gt.GraphView(self.graph, directed=False)

        outc = np.nonzero(gt.label_out_component(self.graph, scc_node).a)[0]
        inc = np.nonzero(gt.label_out_component(graph_reversed, scc_node).a)[0]
        outc = set(outc) - scc
        inc = set(inc) - scc

        # Tubes, Tendrils and Other
        wcc = set(
            np.nonzero(gt.label_out_component(graph_undirected, scc_node).a)[0]
        )
        tube = set()
        out_tendril = set()
        in_tendril = set()
        other = all_nodes - wcc
        remainder = wcc - inc - outc - scc
        num_remainder = len(remainder)

        def find_path(node, to_find, to_find_idx, visited, path, debug=False):
            if debug:
                print('find_path at', node)
            if int(node) in to_find:
                if debug:
                    print('    found to_find, returning', path)
                return True
            visited.add(node)
            for nb in node.out_neighbours():
                if nb in visited:
                    continue
                try:
                    reach = node2reach[int(nb)][to_find_idx]
                    if reach == False:
                        if debug:
                            print('    found previously visited node (%d, False)' % nb)
                        continue
                    if reach == True:
                        if debug:
                            print('    found previously visited node (%d, True)' % nb)
                        return path
                except KeyError:
                    pass
                if find_path(nb, to_find, to_find_idx, visited, path):
                    if debug:
                        print('    find path successful at node', int(nb))
                    path.append(int(nb))
                    return path
            if debug:
                print('    nothing found')
            return False

        node2reach = {node: [None, None] for node in remainder}  # (inc, outc)
        for nidx, node in enumerate(remainder):
            print('\r', nidx+1, '/', num_remainder, end='')
            predecessors = find_path(graph_reversed.vertex(node), inc, 0, set(), list())
            if predecessors != False:
                node2reach[node][0] = True
                if predecessors and predecessors[0] not in inc:
                    node2reach[predecessors[0]][0] = True
                for p in predecessors[1:]:
                    node2reach[p][0] = True

            successors = find_path(self.graph.vertex(node), outc, 1, set(), list())
            if successors != False:
                node2reach[node][1] = True
                if successors and successors[0] not in outc:
                    node2reach[successors[0]][1] = True
                for s in successors[1:]:
                    node2reach[s][1] = True
            # print(predecessors)
            # print(successors)
            # print(self.graph.vp['bowtie'][node])
            # pdb.set_trace()
        print()

        for nidx, (node, [inc_reach, outc_reach]) in enumerate(node2reach.items()):
            print('\r', nidx+1, '/', len(node2reach), end='')
            if inc_reach:
                if outc_reach:
                    tube.add(node)
                else:
                    in_tendril.add(node)
            elif outc_reach:
                out_tendril.add(node)
            else:
                other.add(node)
        print()

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

        # for nidx, node in enumerate(self.graph.vertices()):
        #     if self.graph.vp['bowtie'][node] != self.graph.vp['bowtie2'][node]:
        #         print(node, self.graph.vp['bowtie'][node], self.graph.vp['bowtie2'][node])
        #         pdb.set_trace()
        self.save()

        bow_tie = [inc, scc, outc, in_tendril, out_tendril, tube, other]
        bow_tie = [100 * len(x)/self.graph.num_vertices() for x in bow_tie]
        return bow_tie

    def compute_bowtie_changes(self):
        labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
        comp2num = {l: i for l, i in zip(labels, range(len(labels)))}
        if self.N == 1 or self.N == 'infobox':
            return None
        elif self.N == 'first_p':
            prev_N = 1
        elif self.N == 'lead':
            prev_N = 'first_p'
        elif self.N == 'all':
            prev_N = 'lead'
        prev_gt_file_path = self.gt_file_path.split('_')[0] +\
            '_' + unicode(prev_N) + '.gt'
        prev_graph = gt.load_graph(prev_gt_file_path, fmt='gt')

        changes = np.zeros((len(labels), len(labels)))
        wpid2node_c2 = {prev_graph.vp['name'][v]: v for v in prev_graph.vertices()}
        for node in self.graph.vertices():
            c1 = comp2num[self.graph.vp['bowtie'][node]]
            try:
                c2 = comp2num[prev_graph.vp['bowtie'][wpid2node_c2[self.graph.vp['name'][node]]]]
            except KeyError:
                c2 = comp2num['OTHER']
            changes[c1, c2] += 1
        changes /= prev_graph.num_vertices()
        return changes

    def eccentricity(self, sample_frac=0.01):
        if self.N == 1:
            return
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
        sample_size = int(sample_frac * lcp.num_vertices())
        if sample_frac == 0 or sample_frac == 100:
            sample_size = lcp.num_vertices()
        sample = random.sample(vertices, sample_size)
        for idx, node in enumerate(sample):
            print('\r', idx+1, '/', len(sample), end='')
            dist = gt.shortest_distance(lcp, source=node).a
            ecc[max(dist)] += 1
        print()
        ecc = [ecc[i] for i in range(max(ecc.keys()) + 2)]
        lc_ecc = [100 * v / sum(ecc) for v in ecc]
        return lc_ecc

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

    def path_lengths(self, sample_frac=0.01):
        print('path_lengths() ...')
        pls = collections.defaultdict(int)
        pls_max = 0
        sample_size = int(sample_frac * self.graph.num_vertices())
        if sample_frac == 0 or sample_frac == 100:
            print('sample size undefined')
            pdb.set_trace()
        sample1 = random.sample(xrange(self.graph.num_vertices()), sample_size)
        sample2 = random.sample(xrange(self.graph.num_vertices()), sample_size)
        pairs = zip(sample1, sample2)

        for idx, (node1, node2) in enumerate(pairs):
            print('\r', idx+1, '/', len(pairs), end='')
            dist = gt.shortest_distance(self.graph, source=node1, target=node2)
            if dist > 1000000:  # graph tool encodes disconnected as a large int
                pls_max += 1
            else:
                pls[dist] += 1
        print()
        sum_pls = sum(pls.values()) + pls_max
        if pls:
            pls = [pls[i] for i in range(max(pls.keys()) + 2)]
        else:
            pls = []
        pls = [100 * v / sum_pls for v in pls]
        return pls, 100 * pls_max / sum_pls


if __name__ == '__main__':
    wikipedias = [
        'simple',

        # 'en',
        # 'de',
        # 'fr',
        # 'es',
        # 'ru',
        # 'it',
        # 'ja',
        # 'nl',
    ]

    # data = io.open('test.txt', encoding='utf-8').read()

    # pid = '1698838'
    # wiki = 'ja'
    #
    # import urllib2
    # url = 'https://' + wiki + '.wikipedia.org/w/api.php?format=json&rvstart=20160203235959&prop=revisions|categories&continue&pageids=%s&action=query&rvprop=content&rvparse&cllimit=500&clshow=!hidden&redirects=True'
    # print(url % pid)
    # response = urllib2.urlopen(url % pid)
    # data = response.read().decode('utf-8')
    # with io.open('test2.txt', 'w', encoding='utf-8') as outfile:
    #     outfile.write(data)
    #
    # import json
    # with io.open('test2.txt', encoding='utf-8', errors='ignore') as infile:
    #     data_original = json.load(infile)
    # data = data_original['query']['pages'][pid]['revisions'][0]['*']
    #
    # parser = WikipediaHTMLAllParser()
    # parser.feed(data)
    #
    # ib_links, lead_links, first_p_len = parser.get_data()
    # # fix double % encoding
    # ib_links = [l.replace('%25', '%') for l in ib_links]
    # lead_links = [l.replace('%25', '%') for l in lead_links]
    #
    # print('INFOBOX:')
    # for l in ib_links[:10]:
    #     print('   ', l)
    # print('\nLEAD:')
    # for l in lead_links[:10]:
    #     print('   ', l)
    # pdb.set_trace()
