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
import os
import pdb
import re
import urllib2

import numpy as np
import pandas as pd

from main import debug_iter, get_id_dict

DATA_DIR = 'simplewiki'
WIKI_NAME = 'simplewiki'
WIKI_CODE = 'simple'
DUMP_DATE = '20160203'

# set a few options
pd.options.mode.chained_assignment = None
pd.set_option('display.width', 1000)
url_opener = urllib2.build_opener()


def get_redirect_dict():
    id2redirect = {}
    fname = os.path.join(DATA_DIR, WIKI_NAME + '-' + DUMP_DATE + '-redirect.sql')
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

        with open(os.path.join(DATA_DIR, 'id2redirect.obj'), 'wb') as outfile:
            pickle.dump(id2redirect, outfile, -1)


def resolve_redirects():
    id2title = pd.read_pickle(os.path.join(DATA_DIR, 'id2title.obj'))
    title2id = {v: k for k, v in id2title.iteritems()}
    id2redirect = pd.read_pickle(os.path.join(DATA_DIR, 'id2redirect.obj'))

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

    with open(os.path.join(DATA_DIR, 'title2redirect.obj'), 'wb') as outfile:
        pickle.dump(title2redirect, outfile, -1)


def get_wiki_pages(titles):
    for i, title in enumerate(titles):
        print(i+1, '/', len(titles))
        path = os.path.join('wp', title[0].lower())
        if not os.path.exists(path):
                os.makedirs(path)
        if os.path.isfile(os.path.join(path, title + '.htm')):
            print('present')
            continue
        url = 'http://' + WIKI_CODE + '.wikipedia.org/wiki/' + title
        data = ''
        try:
            request = urllib2.Request(url)
            data = url_opener.open(request).read()
            data = data.decode('utf-8', 'ignore')
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print('!+!+!+!+!+!+!+!+ URLLIB ERROR !+!+!+!+!+!+!+!+')
            print('URLError', e, title)
            continue
        with io.open(os.path.join(path, title + '.htm'), 'w', encoding='utf-8') \
                as outfile:
            outfile.write(data)


def compute_link_positions(titles):
    print('computing link positions...')

    class MLStripper(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.reset()
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return ''.join(self.fed)

        def reset(self):
            self.fed = []
            HTMLParser.HTMLParser.reset(self)

    parser = MLStripper()
    link_regex = re.compile(('(<a href="/wiki/(.+?)" title="[^"]+?[^>]+?">.+?</a>)'))
    folder = 'wp'
    link2pos_first, link2pos_last, pos2link, pos2linklength = {}, {}, {}, {}
    length, ib_length, lead_length = {}, {}, {}
    for i, a in enumerate(titles):
        print(unicode(i+1), '/', unicode(len(titles)), end='\r')
        lpos_first, lpos_last, posl, posll = {}, {}, {}, {}
        fname = os.path.join(folder, a[0].lower(), a + '.htm')
        try:
            with io.open(fname, encoding='utf-8') as infile:
                data = infile.read()
        except UnicodeDecodeError:
            # there exist decoding errors for a few irrelevant pages
            print(fname)
            continue
        data = data.split('<div id="mw-content-text" lang="en" dir="ltr" class="mw-content-ltr">')[1]
        data = data.split('<div id="mw-navigation">')[0]
        regex_results = link_regex.findall(data)
        regex_results = [(r[0], r[1]) for r in regex_results]
        for link in regex_results:
            link = [l for l in link if l]
            data = data.replace(link[0], ' [['+link[1]+']] ')

        # find infobox
        # if '<table' in data[:500]:
        #     idx = data.find('</table>')
        #     data = data[:idx] + ' [[[ENDIB]]] ' + data[idx:]
        # else:
        #     data = ' [[[ENDIB]]] ' + data

        # find lead
        idx = data.find('<span class="mw-headline"')
        if idx == -1:
            data += ' [[[ENDLEAD]]] '
        else:
            data = data[:idx] + ' [[[ENDLEAD]]] ' + data[idx:]

        data = [d.strip() for d in data.splitlines()]
        data = [d for d in data if d]
        text = []
        for d in data:
            parser.reset()
            parser.feed(parser.unescape(d))
            stripped_d = parser.get_data()
            if stripped_d:
                text.append(stripped_d)
        text = ' '.join(text)
        text = text.replace(']][[', ']] [[')
        words = (re.split(': |\. |, |\? |! |\n | |\(|\)', text))
        words = [wo for wo in words if wo]

        idx = words.index('[[[ENDLEAD]]]')
        lead_length[a] = idx
        del words[idx]

        # idx = words.index('[[[ENDIB]]]')
        # ib_length[a] = idx
        # del words[idx]

        # for wi, word in enumerate(reversed(words)):
        #     if word.startswith('[['):
        #         try:
        #             aid = title2id[word[2:-2].replace('%25', '%')]
        #             lpos_first[aid] = len(words) - wi - 1
        #         except KeyError:
        #           pass

        for wi, word in enumerate(words):
            if word.startswith('[['):
                try:
                    aid = title2id[word[2:-2].replace('%25', '%')]
                    posl[wi] = aid
                except KeyError:
                    try:
                        aid = title2id[title2redirect[word[2:-2].replace('%25', '%')]]
                        posl[wi] = aid
                    except KeyError:
                        pass
        pos2link[a] = posl
        length[a] = len(words)
        # for k in sorted(pos2link[a]):
        #     print(k, id2title[pos2link[a][k]])
        # pdb.set_trace()
    path = os.path.join('link_positions.obj')
    with open(path, 'wb') as outfile:
        pickle.dump([pos2link, lead_length], outfile, -1)


def get_local_titles():
    folders = os.listdir('wp')
    titles = []
    for folder in folders:
        path = os.path.join('wp', folder)
        titles += [f.split('.htm')[0] for f in os.listdir(path)]
    return titles


if __name__ == '__main__':
    # get_id_dict()
    # get_redirect_dict()
    # resolve_redirects()

    id2title = pd.read_pickle(os.path.join(DATA_DIR, 'id2title.obj'))
    title2id = {v: k for k, v in id2title.iteritems()}
    id2redirect = pd.read_pickle(os.path.join(DATA_DIR, 'id2redirect.obj'))
    title2redirect = pd.read_pickle(os.path.join(DATA_DIR, 'title2redirect.obj'))
    pdb.set_trace()

    # with io.open('titles.txt', encoding='utf-8') as infile:
    #     titles = infile.read()
    #
    # titles = titles.splitlines()
    # titles = [t for t in titles if '%' not in t]

    # get_wiki_pages(titles)
    # titles = get_titles()
    # titles = [t for t in titles if '%' not in t]
    # titles = [t for t in titles if '__' not in t]
    # # compute_link_positions(titles)
    #
    # # analyze_clicks(titles, split_type='first')
    #
    # results = pd.read_pickle('results_first.obj')
    # # pdb.set_trace()
    # data = []
    # for lead, rest in results.values():
    #     total = lead + rest
    #     if total:
    #         data.append(lead / total)
    #
    # print(np.mean(data), np.median(data))







