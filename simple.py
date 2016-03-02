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

from main import debug_iter, get_id_dict, get_redirect_dict,\
    get_resolved_redirects, read_pickle
from crawler import Crawler

DATA_DIR = 'simplewiki'
WIKI_NAME = 'simplewiki'
WIKI_CODE = 'simple'
DUMP_DATE = '20160203'


def crawl(data_dir, wiki_name, wiki_code, dump_date, pids=None, replace=False):
    if not pids:
        with open(os.path.join(data_dir, 'id2title.obj'), 'rb') as infile:
            id2title = pickle.load(infile)
        pids = sorted(id2title)
    Crawler(wiki_name, wiki_code, data_dir, dump_date, pids=pids, replace=replace)


class WikipediaHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, top_n, debug=False):
        HTMLParser.HTMLParser.__init__(self)
        self.top_n = top_n
        self.found_links = 0
        self.fed = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.first_p_found = False
        self.tracking_div = 0
        self.div_counter = 0
        self.table_counter = 0
        self.tracking_table = 0
        self.debug = debug
        self.debug_found = False

        self.skip_divs = [
            'thumb',
            'thumb tright',
            'thumb tleft',
            'boilerplate metadata'
        ]

        self.file_prefixes = {
            # https://en.wikipedia.org/wiki/Help:Files
            'User',
            'Wikipedia',
            'File',
            'MediaWiki',
            'Template',
            'Help',
            'Category',
            'Portal',
            'Book',
            'Draft',
            'Education_Program',
            'TimedText',
            'Module',
            'Gadget',
            'Gadget_definition',
            'Topic',
            'Special',
            'Media'
        }

    def reset(self):
        self.found_links = 0
        self.fed = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.first_p_found = False
        self.tracking_div = 0
        self.div_counter = 0
        self.table_counter = 0
        self.tracking_table = 0
        self.debug_found = False
        HTMLParser.HTMLParser.reset(self)

    def feed(self, data):
        self.reset()
        end_strings = [
            '<h2><span class="mw-headline" id="References">',
            '<h2><span class="mw-headline" id="Notes">',
            '<h2><span class="mw-headline" id="Footnotes">',
        ]
        for end_string in end_strings:
            data = data.split(end_string)[0]
        for line in data.splitlines():
            HTMLParser.HTMLParser.feed(self, line)
            if self.found_links >= self.top_n:
                break

    def handle_starttag(self, tag, attrs):
        # if self.debug and tag == 'a' and\
        #     'Extraso' in ' '.join([a[1] for a in attrs]):
        #     print('    -->', self.parentheses_counter)
        #     print('    -->', self.tracking_table, self.table_counter,
        #           self.tracking_div, self.div_counter)
        #     pdb.set_trace()

        if (tag == 'a' and self.div_counter == 0 and self.table_counter == 0)\
                and (self.parentheses_counter == 0 or self.first_link_found)\
                and self.first_p_found:
            if self.debug:
                print('a, 0', tag, attrs)
            href = [a[1] for a in attrs if a[0] == 'href']
            if href and href[0].startswith('/wiki/'):
                a_init = href[0].split('/', 2)[-1].split(':')[0]
                if a_init not in self.file_prefixes:
                    self.fed.append(
                        href[0].split('/', 2)[-1].split('#')[0]
                    )
                    self.tracking_link = True
                    self.first_link_found = True
                    self.found_links += 1

        elif tag == 'div':
            if self.debug:
                print('div OPEN', tag, attrs)
            aclass = [a[1] for a in attrs if a[0] == 'class']
            if aclass and aclass[0] in self.skip_divs:
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

        elif tag == 'p':
            self.first_p_found = True

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


def article_generator(data_dir, id2title, title2id, title2redirect,
                      start=None, stop=None):
    # get file ids
    pids = sorted(set(id2title.keys()) - set(title2id[t] for t in title2redirect))

    pids = pids[start:stop]
    for pid in pids:
        pid_u = unicode(pid)
        fpath = os.path.join(data_dir, 'html', pid_u + '.txt   ')
        with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
            data = json.load(infile)
            try:
                json_data = data['query']['pages'][pid_u]['revisions'][0]['*']
                yield id2title[pid], pid_u, json_data
            except KeyError:
                pdb.set_trace()
                print('yielding None')
                # yield None, None, None


def resolve_redirects(links, title2id, title2redirect):
    result = []
    for link in links:
        try:
            result.append(title2redirect[link])
        except KeyError:
            try:
                result.append(title2id[link])
            except KeyError:
                # a link to an article that didn't exist at DUMP_DATE, but
                # unfortunately is linked in the old revision retrieved via API
                print('       ', link, 'not found ----')
                pass
    return result


def get_top_n_links(n, start, stop):
    # extract the first n links
    id2title = read_pickle(os.path.join(DATA_DIR, 'id2title.obj'))
    title2id = {v: k for k, v in id2title.items()}
    title2redirect = read_pickle(os.path.join(DATA_DIR, 'title2redirect.obj'))
    title2links = {}
    parser = WikipediaHTMLParser(top_n=n, debug=False)
    # parser = WikipediaHTMLParser(debug=True)
    for idx, (title, pid, html) in enumerate(
            article_generator(
                DATA_DIR, id2title, title2id, title2redirect,
                start=start,
                stop=stop
            )
    ):
        print(idx, pid, title, 'http://simple.wikipedia.org/wiki/' + title)
        parser.feed(html)
        # links = parser.get_data()[:20]
        links = parser.get_data()
        links = [l.replace('%25', '%') for l in links]  # fix double % encoding
        # for l in links[:10]:
        # for l in links[:10]:
        #     print('   ', l)
        # print('.........')
        # for l in links[-10:]:
        #     print('   ', l)
        title2links[pid] = resolve_redirects(links, title2id, title2redirect)[:n]
        # pdb.set_trace()

    with io.open(
            os.path.join(
                DATA_DIR, 'top20links_' +
                unicode(start) + '_' + unicode(stop) + '.tsv'
            ), 'w', encoding='utf-8'
    ) as outfile:
        for k in sorted(title2links):
            u_links = [unicode(l) for l in title2links[k]]
            outfile.write(unicode(k) + '\t' + ';'.join(u_links) + '\n')


if __name__ == '__main__':
    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)
    # get_redirect_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)
    # get_resolved_redirects(DATA_DIR)

    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    damaged = [297167, 35932, 359158]
    # TODO: 29709 has problems
    crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, pids=damaged, replace=True)

    # start = 0
    # stop = 1000
    #
    # get_top_n_links(20, start, stop)
    #
