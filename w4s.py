# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import HTMLParser
import io
import itertools
import numpy as np
import os
import pdb
import random
import re


DATA_DIR = 'w4s'


def get_title2id():
    fpath = os.path.join('w4s', 'articles.txt')
    with io.open(fpath, encoding='utf-8') as infile:
        data = infile.read()

    d = {f: i for i, f in enumerate(data.splitlines())}
    return d


def article_generator(offset=0, start=None):
    # get list of files
    fpath = os.path.join('w4s', 'articles.txt')
    with io.open(fpath, encoding='utf-8') as infile:
        files = infile.read()

    # extract first link that is not in italics or in parentheses
    counter = 0
    for f in files.splitlines():
        if f == start:
            start = None
        if counter < offset or start is not None:
            counter += 1
            continue
        fpath = os.path.join('w4s', f[0].lower(), f + '.htm')
        with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
            data = infile.read()
            yield f, data


class WikipediaHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, debug=False):
        HTMLParser.HTMLParser.__init__(self)
        self.fed = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.tracking_div = 0
        self.div_counter = 0
        self.table_counter = 0
        self.tracking_table = 0
        self.debug = debug
        self.debug_found = False

    def reset(self):
        self.fed = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.tracking_div = 0
        self.div_counter = 0
        self.table_counter = 0
        self.tracking_table = 0
        self.debug_found = False
        HTMLParser.HTMLParser.reset(self)

    def feed(self, data):
        self.reset()
        data = data.split('<!-- start content -->')[1]
        data = data.split('<!-- end content -->')[0]
        HTMLParser.HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attrs):
        # if self.debug and tag == 'a' and\
        #     'Extraso' in ' '.join([a[1] for a in attrs]):
        #     print('    -->', self.parentheses_counter)
        #     print('    -->', self.tracking_table, self.table_counter,
        #           self.tracking_div, self.div_counter)
        #     pdb.set_trace()

        if (tag == 'a' and self.div_counter == 0 and self.table_counter == 0)\
                and (self.parentheses_counter == 0 or self.first_link_found):
            if self.debug:
                print('a, 0', tag, attrs)
            href = [a[1] for a in attrs if a[0] == 'href']
            # if href and href[0].startswith('/wiki/'):
            if href and href[0].startswith('../../wp/'):
                self.fed.append(
                    href[0].split('/')[-1].split('#')[0].rsplit('.')[0]
                )
                self.tracking_link = True
                self.first_link_found = True

        elif tag == 'div':
            if self.debug:
                print('div OPEN', tag, attrs)
            aclass = [a[1] for a in attrs if a[0] == 'class']
            if aclass and 'thumb tright' in aclass[0]:
                self.tracking_div += 1
            if self.tracking_div:
                self.div_counter += 1

        elif tag == 'table':
            if self.debug:
                print('table OPEN', tag, attrs)
            # aclass = [a[1] for a in attrs if a[0] == 'class']
            # if aclass and 'infobox' in aclass[0]:
            #     self.tracking_table += 1
            self.tracking_table += 1
            if self.tracking_table:
                self.table_counter += 1

    def handle_endtag(self, tag):
        if tag == 'a' and self.tracking_link:
            self.tracking_link = False
        elif tag == 'div':
            if self.debug:
                print('div CLOSE')
            if self.tracking_div > 0:
                self.div_counter -= 1
                if self.div_counter == 0:
                    self.tracking_div = min(0, self.tracking_div-1)
        elif tag == 'table':
            if self.debug:
                print('table CLOSE')
            if self.tracking_table > 0:
                self.table_counter -= 1
                if self.table_counter == 0:
                    self.tracking_table = min(0, self.tracking_table-1)

    def handle_data(self, d):
        # if not self.tracking_link:
        #     d = d.strip('\t\x0b\x0c\r ')
        #     if d:
        #         self.fed.append(d + ' ')
        # d = d.strip('\t\x0b\x0c\r \n')
        # if not d:
        #     return
        # print(d)
        # pdb.set_trace()
        if self.tracking_div or self.tracking_table:
            return
        par_diff = d.count('(') - d.count(')')
        self.parentheses_counter += par_diff
        # if self.parentheses_counter > 0:
        #     print(self.parentheses_counter, d)
        # if 'Notable' in d:
        #     self.debug_found = True
        # if self.debug_found:
        #     print(self.parentheses_counter, d)
        # print(self.parentheses_counter, d)

    def get_data(self):
        return self.fed


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    title2id = get_title2id()
    title2links = {}
    parser = WikipediaHTMLParser(debug=False)
    # parser = WikipediaHTMLParser(debug=True)
    for idx, (title, html) in enumerate(article_generator()):
        print(title)
        parser.feed(html)
        links = parser.get_data()[:20]
        pdb.set_trace()
        # TODO: problem is 'D%25C3%25A1l_Riata' (usage in articles) vs 'D%C3%A1l_Riata' (usage in article list)
        title2links[title2id[title]] = [title2id[l] for l in links]

    with io.open(os.path.join(DATA_DIR, 'top1links.tsv'), 'w',
                 encoding='utf-8') as outfile:
        for k in sorted(title2links):
            outfile.write(k + '\t' + ';'.join(title2links[k]) + '\n')

    # from main import Graph
    # g = Graph(fname='top20links.tsv', use_sample=False, refresh=False, N=1)
    # g.load_graph(refresh=False)

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
