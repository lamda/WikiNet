# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import os

from main import get_id_dict, crawl, get_resolved_redirects,\
    get_top_n_links_chunks, combine_chunks, Graph

from main import crawl, debug_iter, get_id_dict, get_redirect_dict,\
    get_resolved_redirects, get_top_n_links_chunks, read_pickle, check_files
from crawler import Crawler

DATA_DIR = os.path.join('data', 'eswiki')
WIKI_NAME = 'eswiki'
WIKI_CODE = 'es'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)

    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, recrawl_damaged=True)
    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, recrawl_damaged=True)

    get_resolved_redirects(DATA_DIR)

    get_top_n_links_chunks()
    get_top_n_links_chunks(DATA_DIR)

    combine_chunks(DATA_DIR)

    # from main import Graph
    # g = Graph(data_dir=DATA_DIR, fname='top20links',
    #           use_sample=False, refresh=False, N=1)
    # g.load_graph(refresh=False)
    # # g.compute_stats()
    # g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
