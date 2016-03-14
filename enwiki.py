# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals
import os
import pdb
import sys

from main import *


from crawler import Crawler


DATA_DIR = os.path.join('data', 'enwiki')
WIKI_NAME = 'enwiki'
WIKI_CODE = 'en'
DUMP_DATE = '20160204'


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

    get_all_links_chunks(DATA_DIR)

    combine_all_chunks(DATA_DIR)

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
        g.compute_stats()
        # g.update_stats()
        g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
