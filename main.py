# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import json
import HTMLParser
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
from tools import debug_iter, read_pickle, write_pickle, url_escape


DATA_DIR = 'enwiki'
WIKI_NAME = 'enwiki'
WIKI_CODE = 'en'
DUMP_DATE = '20150304'


np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)


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
                id2redirect[int(page_id)] = url_escape(page_title)

        with open(os.path.join(data_dir, 'id2redirect.obj'), 'wb') as outfile:
            pickle.dump(id2redirect, outfile, -1)


def get_resolved_redirects(data_dir):
    print('getting resolved redirects...')
    title2redirect = {}
    file_names = [
        f
        for f in os.listdir(os.path.join(data_dir, 'html'))
        if f.endswith('.obj')
    ]
    for fidx, file_name in enumerate(file_names):
        print('\r', fidx+1, '/', len(file_names), end='')
        df = pd.read_pickle(os.path.join(data_dir, 'html', file_name))
        df = df[~df['redirects_to'].isnull()]
        for k, v in zip(df['title'], df['redirects_to']):
            title2redirect[k] = v
    print()

    with open(os.path.join(data_dir, 'title2redirect.obj'), 'wb') as outfile:
        pickle.dump(title2redirect, outfile, -1)


def crawl(data_dir, wiki_name, wiki_code, dump_date, recrawl_damaged=False):
    with open(os.path.join(data_dir, 'id2title.obj'), 'rb') as infile:
        id2title = pickle.load(infile)
    pids = sorted(id2title)
    Crawler(wiki_name, wiki_code, data_dir, dump_date, pids=pids,
            recrawl_damaged=recrawl_damaged)


class WikipediaHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, label, debug=False):
        HTMLParser.HTMLParser.__init__(self)
        self.found_links = 0
        self.lead_links = []
        self.infobox_links = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.first_p_found = False
        self.first_p_ended = False
        self.first_p_len = 0
        self.tracking_div = 0
        self.div_counter_any = 0
        self.div_counter = 0
        self.table_counter = 0
        self.table_counter_any = 0
        self.tracking_table = 0
        self.debug = debug
        self.debug_found = False

        self.skip_divs = [
            'magnify',
            'metadata',
            'noprint',
            'rellink',
            'thumb',
            'thumbcaption',
            'thumbimage',
            'thumbinner',
            'toc',

            # de
            'navcontent',
            'navhead',
            'navframe',
            'coordinates',
            'sisterproject',
            'gallerytext',
        ]

        if label == 'enwiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'dewiki':
            self.infobox_classes = [
                'infobox',
                'toptextcells',
                'float-right',
            ]

        elif label == 'frwiki':
            self.infobox_classes = [
                'infobox',
                'infobox_v2',
                'taxobox_classification',
            ]

        elif label == 'eswiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'itwiki':
            self.infobox_classes = [
                'sinottico',
                'sinottico_annidata',
            ]
        elif label == 'nlwiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'simplewiki':
            self.infobox_classes = [
                'infobox',
            ]

        else:
            print('WikipediaParser: label (%s) not supported' % label)
            pdb.set_trace()

        # self.file_prefixes = {
        #     # https://en.wikipedia.org/wiki/Help:Files
        #     'User',
        #     'Wikipedia',
        #     'File',
        #     'MediaWiki',
        #     'Template',
        #     'Help',
        #     'Category',
        #     'Portal',
        #     'Book',
        #     'Draft',
        #     'Education_Program',
        #     'TimedText',
        #     'Module',
        #     'Gadget',
        #     'Gadget_definition',
        #     'Topic',
        #     'Special',
        #     'Media'
        # }
        # file_prefixes_talk = {fp + '_talk' for fp in self.file_prefixes}
        # self.file_prefixes = self.file_prefixes | file_prefixes_talk

    def reset(self):
        self.found_links = 0
        self.lead_links = []
        self.infobox_links = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.first_p_found = False
        self.first_p_len = 0
        self.first_p_ended = False
        self.tracking_div = 0
        self.tracking_table = 0
        self.div_counter_any = 0
        self.div_counter = 0
        self.table_counter = 0
        self.table_counter_any = 0
        self.debug_found = False
        HTMLParser.HTMLParser.reset(self)

    def feed(self, data):
        self.reset()
        # end_strings = [
        #     '<h2><span class="mw-headline" id="References">',
        #     '<h2><span class="mw-headline" id="Notes">',
        #     '<h2><span class="mw-headline" id="Footnotes">',
        # ]
        end_strings = [
            '<h2><span class="mw-headline"',  # split at first section heading
        ]
        for end_string in end_strings:
            data = data.split(end_string)[0]

        for line in data.splitlines():
            HTMLParser.HTMLParser.feed(self, line)

    def handle_starttag(self, tag, attrs):
        # if self.debug and tag == 'a' and not self.tracking_div and not self.tracking_table:
        #     # print('    -->', self.parentheses_counter)
        #     # print('    -->', self.tracking_table, self.table_counter,
        #     #       self.tracking_div, self.div_counter)
        #     print(tag, attrs)
        #     pdb.set_trace()

        if (tag == 'a' and self.div_counter == 0 and self.table_counter == 0)\
                and (self.parentheses_counter == 0 or self.first_link_found)\
                and self.first_p_found:
            if self.debug:
                print('a, 0', tag, attrs)
            href = [a[1] for a in attrs if a[0] == 'href']
            if href and href[0].startswith('/wiki/'):
                # a_init = href[0].split('/', 2)[-1].split(':')[0]
                # if a_init not in self.file_prefixes:
                self.lead_links.append(
                    href[0].split('/', 2)[-1].split('#')[0]
                )
                self.tracking_link = True
                self.first_link_found = True
                self.found_links += 1

        elif tag == 'a' and self.tracking_table:
            if self.debug:
                print('a, 1hg', tag, attrs)
            href = [a[1] for a in attrs if a[0] == 'href']
            if href and href[0].startswith('/wiki/'):
                # a_init = href[0].split('/', 2)[-1].split(':')[0]
                # if a_init not in self.file_prefixes:
                self.infobox_links.append(
                    href[0].split('/', 2)[-1].split('#')[0]
                )

        elif tag == 'div':
        #     pass
            # if self.debug:
            #     print('div OPEN', tag, attrs)
            self.div_counter_any += 1
            # aclass = [a[1] for a in attrs if a[0] == 'class']
            # if aclass and aclass[0] in self.skip_divs:
            #     self.tracking_div += 1
            # if self.tracking_div:
            #     self.div_counter += 1

        elif tag == 'table':
            if self.debug:
                print('table OPEN', tag, attrs)
            self.table_counter_any += 1
            aclass = [a[1] for a in attrs if a[0] == 'class']
            # if aclass and 'infobox' in aclass[0]:
            if aclass:
                acl = aclass[0].lower()
                if any(s in acl for s in self.infobox_classes):
                    self.tracking_table += 1
            if self.tracking_table:
                self.table_counter += 1

        elif tag == 'p' and self.div_counter_any < 1 and self.table_counter_any < 1:
        # elif tag == 'p':
        #     print(self.div_counter_any, self.table_counter_any)
            self.first_p_found = True
            self.parentheses_counter = 0

    def handle_endtag(self, tag):
        if tag == 'a' and self.tracking_link:
            self.tracking_link = False
        elif tag == 'div':
        #     pass
            # if self.debug:
            #     print('div CLOSE')
            self.div_counter_any -= 1
            # if self.tracking_div > 0:
            #     self.div_counter -= 1
            #     if self.div_counter == 0:
            #         self.tracking_div = min(0, self.tracking_div-1)
        elif tag == 'table':
            if self.debug:
                print('table CLOSE')
            self.table_counter_any -= 1
            if self.tracking_table > 0:
                self.table_counter -= 1
                if self.table_counter == 0:
                    self.tracking_table = min(0, self.tracking_table-1)
        elif tag == 'p' and not self.first_p_ended and self.first_p_found:
            self.first_p_ended = True
            self.first_p_len = len(self.lead_links)

    def handle_data(self, d):
        # if not self.tracking_link:
        #     d = d.strip('\t\x0b\x0c\r ')
        #     if d:
        #         self.fed.append(d + ' ')
        # d = d.strip('\t\x0b\x0c\r \n')
        # if not d:
        #     return

        if self.tracking_div or self.tracking_table:
            return
        par_diff = d.count('(') + d.count('[') + d.count('{') -\
                   d.count(')') - d.count(']') - d.count('}')
        self.parentheses_counter += par_diff

    def get_data(self):
        return self.infobox_links, self.lead_links, self.first_p_len


class WikipediaDivTableParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.divclass2id = {}
        self.tableclass2id = {}
        self.pid = None

    def reset(self):
        self.divclass2id = {}
        self.tableclass2id = {}
        self.pid = None

    def feed(self, data, pid):
        HTMLParser.HTMLParser.reset(self)
        self.reset()
        self.pid = pid
        end_strings = [
            '<h2><span class="mw-headline"',  # split at first section heading
        ]
        for end_string in end_strings:
            data = data.split(end_string)[0]

        for line in data.splitlines():
            HTMLParser.HTMLParser.feed(self, line)

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            aclass = [a[1] for a in attrs if a[0] == 'class']
            for aa in aclass:
                # for a in aa.split(' '):
                #     self.class2id[a] = self.pid
                self.tableclass2id[frozenset(aa.split(' '))] = self.pid

        elif tag == 'div':
            aclass = [a[1] for a in attrs if a[0] == 'class']
            for aa in aclass:
                # for a in aa.split(' '):
                #     self.class2id[a] = self.pid
                self.divclass2id[frozenset(aa.split(' '))] = self.pid

    def get_data(self):
        return self.divclass2id, self.tableclass2id


def resolve_redirects(links, title2id, title2redirect):
    result = []
    for link in links:
        try:
            result.append(title2id[title2redirect[link]])
        except KeyError:
            try:
                result.append(title2id[link])
            except KeyError:
                # a link to an article that didn't exist at DUMP_DATE, but
                # unfortunately is linked in the old revision retrieved via API
                # print('       ', link, 'not found ----')
                pass
    return result


def get_top_n_links_chunks(data_dir, start=None, stop=None, file_list=None):
    print('getting top n links...')
    label = data_dir.split(os.path.sep)[1]
    id2title = read_pickle(os.path.join(data_dir, 'id2title.obj'))
    title2id = {v: k for k, v in id2title.items()}
    title2redirect = read_pickle(os.path.join(data_dir, 'title2redirect.obj'))
    if file_list:
        file_names = file_list
    else:
        file_names = [
            f
            for f in os.listdir(os.path.join(data_dir, 'html'))
            if f.endswith('.obj')
        ][start:stop]
    for fidx, file_name in enumerate(file_names):
        print('\r', fidx+1, '/', len(file_names), end='')
        file_path = os.path.join(data_dir, 'html', file_name)
        get_top_n_links(title2id, title2redirect, file_path, label)
    print()


def get_top_n_links(title2id, title2redirect, file_path, label):
    # extract the first n links
    parser = WikipediaHTMLParser(label=label, debug=False)
    # parser = WikipediaHTMLParser(label=label, debug=True)
    df = pd.read_pickle(file_path)

    parsed_ib_links, parsed_lead_links, first_p_lens = [], [], []
    for idx, row in df.iterrows():
        # print(idx, row['pid'], row['title'],
        #       'http://es.wikipedia.org/wiki/' + row['title'])
        # if (idx % 1000) == 0:
        #     print('\r', idx, end='')
        if pd.isnull(row['redirects_to']):
            parser.feed(row['content'])
            # links = parser.get_data()[:20]
            ib_links, lead_links, first_p_len = parser.get_data()
            # fix double % encoding
            ib_links = [l.replace('%25', '%') for l in ib_links]
            lead_links = [l.replace('%25', '%') for l in lead_links]

            # for l in ib_links[:10]:
            #     print('   ', l)
            # print('.........')
            # for l in lead_links[:10]:
            #     print('   ', l)
            # pdb.set_trace()
            ib_li = resolve_redirects(ib_links, title2id, title2redirect)
            lead_li = resolve_redirects(lead_links, title2id, title2redirect)
            parsed_ib_links.append([unicode(l) for l in ib_li])
            parsed_lead_links.append([unicode(l) for l in lead_li])
            first_p_lens.append(first_p_len)
        else:
            parsed_ib_links.append([])
            parsed_lead_links.append([])
            first_p_lens.append(0)

    df['ib_links'] = parsed_ib_links
    df['lead_links'] = parsed_lead_links
    df['first_p_len'] = first_p_lens
    pd.to_pickle(df, file_path)


def combine_chunks(data_dir):
    print('combining chunks...')
    file_names = [
        f
        for f in os.listdir(os.path.join(data_dir, 'html'))
        if f.endswith('.obj')
    ]
    with io.open(os.path.join(data_dir, 'links.tsv'), 'w',
                 encoding='utf-8') as outfile:
        for fidx, file_name in enumerate(sorted(file_names)):
            # print('\r', fidx+1, '/', len(file_names), end='')
            print('\r', fidx+1, '/', len(file_names), file_name, end='')
            df = pd.read_pickle(os.path.join(data_dir, 'html', file_name))

            for idx, row in df.iterrows():
                if pd.isnull(row['redirects_to']):
                    outfile.write(
                        unicode(row['pid']) + '\t' + ';'.join(row['ib_links']) +
                        '\t' + ';'.join(row['lead_links']) + '\t' +
                        unicode(row['first_p_len']) + '\n'
                    )
        print()


def get_divtable_classes_chunks(data_dir, start=None, stop=None, file_list=None):
    print('getting div and table classes...')
    if file_list:
        file_names = file_list
    else:
        file_names = [
            f
            for f in os.listdir(os.path.join(data_dir, 'html'))
            if f.endswith('.obj')
        ][start:stop]
    for fidx, file_name in enumerate(file_names):
        print('\r', fidx+1, '/', len(file_names), end='')
        get_divtable_classes(data_dir, file_name)
    print()


def get_divtable_classes(data_dir, file_name):
    # extract the table classes
    parser = WikipediaDivTableParser()
    file_path = os.path.join(data_dir, 'html', file_name)
    df = pd.read_pickle(file_path)
    divclass2id = collections.defaultdict(list)
    tableclass2id = collections.defaultdict(list)

    for idx, row in df.iterrows():
        # print(idx, row['pid'], row['title'],
        #       'http://simple.wikipedia.org/wiki/' + row['title'])
        # if (idx % 1000) == 0:
        #     print('\r', idx, end='')
        if pd.isnull(row['redirects_to']):
            parser.feed(row['content'], row['pid'])
            divs, tables = parser.get_data()

            for k, v in divs.items():
                divclass2id[k].append(v)
            for k, v in tables.items():
                tableclass2id[k].append(v)
    file_dir = os.path.join(data_dir, 'html', 'divtables')
    if not os.path.exists(file_dir):
            os.makedirs(file_dir)
    write_pickle(os.path.join(file_dir, file_name), [divclass2id, tableclass2id])


def combine_divtable_chunks(data_dir):
    print('combining chunks...')
    file_names = [
        f
        for f in os.listdir(os.path.join(data_dir, 'html', 'divtables'))
        if f.endswith('.obj')
    ]
    divclass2id = collections.defaultdict(list)
    tableclass2id = collections.defaultdict(list)
    for fidx, file_name in enumerate(sorted(file_names)):
        print('\r', fidx+1, '/', len(file_names), file_name, end='')
        fpath = os.path.join(data_dir, 'html', 'divtables', file_name)
        divs, tables = read_pickle(fpath)
        for k, v in divs.items():
            divclass2id[k] += v
        for k, v in tables.items():
            tableclass2id[k] += v

    with io.open(os.path.join(data_dir, 'tables.tsv'), 'w',
                 encoding='utf-8') as outfile:
        for k in sorted(tableclass2id, key=lambda k: len(tableclass2id[k]),
                        reverse=True):
            outfile.write(unicode(len(tableclass2id[k])) + '\t' +
                          ' '.join(sorted(k)) + '\t' +
                          ';'.join(map(unicode, tableclass2id[k][:20])) + '\n')

    with io.open(os.path.join(data_dir, 'divs.tsv'), 'w',
                 encoding='utf-8') as outfile:
        for k in sorted(divclass2id, key=lambda k: len(divclass2id[k]),
                        reverse=True):
            outfile.write(unicode(len(divclass2id[k])) + '\t' +
                          ' '.join(sorted(k)) + '\t' +
                          ';'.join(map(unicode, divclass2id[k][:20])) + '\n')


def cleanup(data_dir):
    files = [f for f in os.listdir(data_dir) if f.endswith('.gt')]
    for f in files:
        os.remove(os.path.join(data_dir, f))


def get_id2title_no_redirect(data_dir):
    print('get_id2title_no_redirect...')
    file_names = [
        f
        for f in os.listdir(os.path.join(data_dir, 'html'))
        if f.endswith('.obj')
    ]
    id2title = {}
    for fidx, file_name in enumerate(sorted(file_names)):
        print('\r', fidx+1, '/', len(file_names), file_name, end='')
        df = pd.read_pickle(os.path.join(data_dir, 'html', file_name))
        for ridx, row in df[pd.isnull(df['redirects_to'])][['pid', 'title']].iterrows():
            id2title[row['pid']] = row['title']
    print()
    fpath = os.path.join('id2title', data_dir.split(os.path.sep)[1] + '.obj')
    write_pickle(fpath, id2title)


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
        self.names = self.graph.new_vertex_property('int32_t')
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
                node, ib_nbs, lead_nbs, first_p_len = line.strip().split('\t')
                nodes.add(node)
                if self.N == 'infobox' and ib_nbs:
                    nodes |= set(ib_nbs.split(';'))
                elif lead_nbs:
                    lead_nbs = lead_nbs.split(';')
                    if self.N == 1:
                        nodes.add(lead_nbs[0])
                    elif self.N == 'first_p':
                        nodes |= set(lead_nbs[:int(first_p_len)])
                    else:
                        nodes |= set(lead_nbs)

        print('\nadding nodes to graph...')
        for node in debug_iter(nodes, len(nodes)):
            v = self.name2node[node]
            self.names[v] = int(float(node))
        self.graph.vp['name'] = self.names

        print('\nloading edges...')
        edges = []
        with io.open(self.graph_file_path, encoding='utf-8') as infile:
            for line in debug_iter(infile):
                node, ib_nbs, lead_nbs, first_p_len = line.strip().split('\t')
                nbs = []
                if self.N == 'infobox' and ib_nbs:
                    nbs = set(ib_nbs.split(';'))
                elif lead_nbs:
                    lead_nbs = lead_nbs.split(';')
                    if self.N == 1:
                        nbs = lead_nbs[:1]
                    elif self.N == 'first_p':
                        nbs = lead_nbs[:int(first_p_len)]
                    else:
                        nbs = lead_nbs
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
            vp_title[self.graph.vertex(vertex)] = id2title[
                int(self.graph.vp['name'][vertex])]
        self.graph.vp['title'] = vp_title
        self.save()

    def save(self):
        self.graph.save(self.gt_file_path, fmt='gt')

    def compute_stats(self):
        print('computing stats...')
        stats = {}
        stats['graph_size'], stats['recommenders'], stats['outdegree_av'],\
            stats['outdegree_median'] = self.basic_stats()
        # # stats['cc'] = self.clustering_coefficient()
        stats['cp_size'], stats['cp_count'] = self.largest_component()
        # stats['pls'], stats['pls_max'] = self.path_lengths()
        if self.N == 1:
            stats['singles'], stats['comp_stats'] = self.cycle_components()
        # stats['bow_tie'] = self.bow_tie()
        # stats['bow_tie_changes'] = self.compute_bowtie_changes()
        # stats['lc_ecc'] = self.eccentricity()

        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(stats, outfile, -1)
        print()

    def update_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            stats = pickle.load(infile)

        # stats['graph_size'], stats['recommenders'], stats['outdegree_av'],\
        #     stats['outdegree_median'] = self.basic_stats()
        stats['pls'], stats['pls_max'] = self.path_lengths()
        # stats['lc_ecc'] = self.eccentricity()
        # stats['bow_tie'] = self.bow_tie()
        # stats['bow_tie_changes'] = self.compute_bowtie_changes()

        print('saving...')
        with open(self.stats_file_path, 'wb') as outfile:
            pickle.dump(stats, outfile, -1)
        print()

    def print_stats(self):
        with open(self.stats_file_path, 'rb') as infile:
            stats = pickle.load(infile)
        for k, v in stats.items():
            if k in {'comp_stats', 'singles', 'bow_tie'}:
                continue
            print(k, v)

        if 'comp_stats' in stats:
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
        comp_stats.sort(key=operator.itemgetter('incomp_size'), reverse=True)
        return singles, comp_stats

    def bow_tie(self):
        print('bow tie')

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

    def compute_bowtie_changes(self):
        labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
        comp2num = {l: i for l, i in zip(labels, range(len(labels)))}
        if self.N == 1 or self.N == 'infobox':
            return None
        elif self.N == 'first_p':
            prev_N = 1
        elif self.N == 'lead':
            prev_N = 'first_p'
        prev_gt_file_path = self.gt_file_path.split('_')[0] +\
            '_' + unicode(prev_N) + '.gt'
        prev_graph = gt.load_graph(prev_gt_file_path, fmt='gt')

        changes = np.zeros((len(labels), len(labels)))
        for node in self.graph.vertices():
            c1 = comp2num[self.graph.vp['bowtie'][node]]
            try:
                c2 = comp2num[prev_graph.vp['bowtie'][node]]
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
    from datetime import datetime
    start_time = datetime.now()

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

    data = io.open('test.txt', encoding='utf-8').read()
    url = 'https://fr.wikipedia.org/w/api.php?format=json&rvstart=20160203235959&prop=revisions|categories&continue&pageids=%s&action=query&rvprop=content&rvparse&cllimit=500&clshow=!hidden&redirects=True'
    print(url % 'Theatre')
    parser = WikipediaHTMLParser('frwiki', debug=True)
    parser.feed(data)

    ib_links, lead_links, first_p_len = parser.get_data()
    # fix double % encoding
    ib_links = [l.replace('%25', '%') for l in ib_links]
    lead_links = [l.replace('%25', '%') for l in lead_links]

    print('INFOBOX:')
    for l in ib_links[:10]:
        print('   ', l)
    print('\nLEAD:')
    for l in lead_links[:10]:
        print('   ', l)
    pdb.set_trace()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))





