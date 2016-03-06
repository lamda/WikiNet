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
import pandas as pd
import pdb
import re

from main import debug_iter, get_id_dict, get_redirect_dict,\
    get_resolved_redirects, Graph, read_pickle, check_files

from crawler import Crawler


DATA_DIR = os.path.join('data', 'simplewiki')
WIKI_NAME = 'simplewiki'
WIKI_CODE = 'simple'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)

    crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, recrawl_damaged=True)

    # get_resolved_redirects(DATA_DIR)

    # get_top_n_links_chunks(DATA_DIR)

    # combine_chunks(DATA_DIR)

    # for n_val in [
    #     1,
    #     5,
    #     10,
    #     20
    # ]:
    #     print('---------------- N = %d ----------------' % n_val)
    #     g = Graph(data_dir=DATA_DIR, fname='top20links',
    #               use_sample=False, refresh=False, N=n_val)
    #     g.load_graph(refresh=False)
    #     g.compute_stats()
    #     g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

