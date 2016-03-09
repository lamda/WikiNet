# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals
import os

from main import get_id_dict, crawl, get_resolved_redirects,\
    get_top_n_links_chunks, combine_chunks, Graph

from crawler import Crawler


DATA_DIR = os.path.join('data', 'simplewiki')
WIKI_NAME = 'simplewiki'
WIKI_CODE = 'simple'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)

    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, recrawl_damaged=True)

    # get_resolved_redirects(DATA_DIR)

    # get_top_n_links_chunks(DATA_DIR)

    # combine_chunks(DATA_DIR)

    for n_val in [
        1,
        # 'first_p',
        # 'lead',
        # 'infobox',
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

