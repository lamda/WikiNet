# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals
import os
import pdb
import sys

from tools import read_pickle, write_pickle
import HTMLParser
import pandas as pd
import io

from main import *

# from crawler import Crawler


DATA_DIR = os.path.join('data', 'enwiki')
WIKI_NAME = 'enwiki'
WIKI_CODE = 'en'
DUMP_DATE = '20160204'


def resolve_redirects2(links, title2id, title2redirect):
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


class WikipediaHTMLAllParser2(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.links = []

    def reset(self):
        self.links = []
        HTMLParser.HTMLParser.reset(self)

    def feed(self, data):
        self.reset()

        for line in data.splitlines():
            HTMLParser.HTMLParser.feed(self, line)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = [a[1] for a in attrs if a[0] == 'href']
            if href and href[0].startswith('/wiki/'):
                self.links.append(
                    href[0].split('/', 2)[-1].split('#')[0]
                )

    def get_data(self):
        return self.links


def get_all_links_chunks2(data_dir, start=None, stop=None, file_list=None):
    print('getting all links...')
    id2title = read_pickle(os.path.join(data_dir, 'id2title.obj'))
    title2id = {v: k for k, v in id2title.items()}
    title2redirect = read_pickle(os.path.join(data_dir, 'title2redirect.obj'))
    file_dir = os.path.join(data_dir, 'html', 'alllinks')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    present_files = set(os.listdir(file_dir))

    if file_list:
        file_names = file_list
    else:
        file_names = [
            f
            for f in os.listdir(os.path.join(data_dir, 'html'))
            if f.endswith('.obj')
        ][start:stop]
    file_names = sorted(file_names)

    for fidx, file_name in enumerate(file_names):
        print(fidx+1, '/', len(file_names), file_name)
        if file_name in present_files:
            print('    present')
            continue
        get_all_links(title2id, title2redirect, data_dir, file_name)
    print()


def get_all_links2(title2id, title2redirect, data_dir, file_name):
    parser = WikipediaHTMLAllParser()
    file_path = os.path.join(data_dir, 'html', file_name)
    df = pd.read_pickle(file_path)
    pid2links = {}
    file_dir = os.path.join(data_dir, 'html', 'alllinks')
    for idx, row in df.iterrows():
        if pd.isnull(row['redirects_to']):
            parser.feed(row['content'])
            links = parser.get_data()
            pid2links[row['pid']] = map(
                unicode,
                resolve_redirects(links, title2id, title2redirect)
            )

    write_pickle(os.path.join(file_dir, file_name), pid2links)


def combine_all_chunks2(data_dir):
    print('combining all chunks...')
    file_names = [
        f
        for f in os.listdir(os.path.join(data_dir, 'html', 'alllinks'))
        if f.endswith('.obj')
    ]
    with io.open(os.path.join(data_dir, 'alllinks.tsv'), 'w',
                 encoding='utf-8') as outfile:
        for fidx, file_name in enumerate(sorted(file_names)):
            print('\r', fidx+1, '/', len(file_names), file_name, end='')
            fpath = os.path.join(data_dir, 'html', 'alllinks', file_name)
            pid2links = read_pickle(fpath)

            for pid, links in pid2links.items():
                outfile.write(unicode(pid) + u'\t' + u';'.join(links) + '\n')


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)

    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, recrawl_damaged=True)

    # get_resolved_redirects(DATA_DIR)

    # get_divtable_classes_chunks(DATA_DIR)
    #
    # combine_divtable_chunks(DATA_DIR)

    # get_id2title_no_redirect(DATA_DIR)

    # if len(sys.argv) == 3:
    #     print('restricting to', sys.argv[1], ':', sys.argv[2])
    #     get_top_n_links_chunks(DATA_DIR, int(sys.argv[1]), int(sys.argv[2]))
    # else:
    #     get_top_n_links_chunks(DATA_DIR)
    # get_top_n_links_chunks(DATA_DIR)
    #
    # combine_chunks(DATA_DIR)

    # get_all_links_chunks(DATA_DIR)
    #
    # combine_all_chunks(DATA_DIR)

    # cleanup(DATA_DIR)

    for n_val in [
        1,
        'first_p',
        'lead',
        'infobox',
        'all',
    ]:
        print('---------------- N =', n_val, '----------------')
        g = Graph(data_dir=DATA_DIR, fname='links',
                  use_sample=False, refresh=False, N=n_val)
        g.load_graph(refresh=False)
        # g.compute_stats()
        g.update_stats()
        # g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
