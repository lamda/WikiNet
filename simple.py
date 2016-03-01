# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import HTMLParser
import io
import json
import os
import pdb
import re

from main import debug_iter, get_id_dict
from crawler import Crawler

DATA_DIR = 'simplewiki'
WIKI_NAME = 'simplewiki'
WIKI_CODE = 'simple'
DUMP_DATE = '20160203'


def read_pickle(fpath):
    with open(fpath, 'rb') as infile:
        obj = pickle.load(infile)
    return obj


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
            matches = re.findall(r"\((\d+),(\d+),'([^\']+)", line)
            for page_id, page_namespace, page_title in matches:
                if page_namespace != '0':
                    continue
                id2redirect[int(page_id)] = page_title

        with open(os.path.join(data_dir, 'id2redirect.obj'), 'wb') as outfile:
            pickle.dump(id2redirect, outfile, -1)


def resolve_redirects(data_dir):
    id2title = read_pickle(os.path.join(data_dir, 'id2title.obj'))
    title2id = {v: k for k, v in id2title.iteritems()}
    id2redirect = read_pickle(os.path.join(data_dir, 'id2redirect.obj'))

    title2redirect = {}
    idx = 1
    length = len(id2redirect)
    for k, v in id2redirect.iteritems():
        print(idx, '/', length, end='\r')
        idx += 1
        try:
            title2redirect[id2title[k]] = title2id[v]
        except KeyError:
            pass

    with open(os.path.join(data_dir, 'title2redirect.obj'), 'wb') as outfile:
        pickle.dump(title2redirect, outfile, -1)


def crawl(data_dir, wiki_name, wiki_code, dump_date):
    with open(os.path.join(data_dir, 'id2title.obj'), 'rb') as infile:
        id2title = pickle.load(infile)
    pids = sorted(id2title)
    Crawler(wiki_name, wiki_code, data_dir, dump_date, pids)


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
                    href[0].split('/')[-1].split('#')[0].rsplit('.', 1)[0]
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


def article_generator(data_dir, offset=0, start=None, limit=None):
    # get file ids
    with open(os.path.join(data_dir, 'id2title.obj'), 'rb') as infile:
        id2title = pickle.load(infile)
    pids = sorted(id2title)

    # extract first link that is not in italics or in parentheses
    counter = 0
    for pid in pids:
        if pid == start:
            start = None
        if counter < offset or start is not None:
            counter += 1
            continue
        if limit and counter > limit:
            break
        pid_u = unicode(pid)
        fpath = os.path.join(data_dir, 'html', pid_u + '.txt   ')
        with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
            data = json.load(infile)
            try:
                json_data = data['query']['pages'][pid_u]['revisions'][0]['*']
                yield id2title[pid], pid_u, json_data
            except KeyError:
                print('yielding None')
                yield None, None, None


if __name__ == '__main__':
    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)
    # get_redirect_dict()
    # resolve_redirects()

    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)

    # extract the first 20 links
    title2links = {}
    parser = WikipediaHTMLParser(debug=False)
    # parser = WikipediaHTMLParser(debug=True)
    for idx, (title, pid, html) in enumerate(article_generator(DATA_DIR)):
        print(title)
        parser.feed(html)
        links = parser.get_data()[:20]
        links = [l.replace('%25', '%') for l in links]  # fix double % encoding
        pdb.set_trace()

    with io.open(os.path.join(DATA_DIR, 'top20links.tsv'), 'w',
                 encoding='utf-8') as outfile:
        for k in sorted(title2links):
            u_links = [unicode(l) for l in title2links[k]]
            outfile.write(unicode(k) + '\t' + ';'.join(u_links) + '\n')
