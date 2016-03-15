# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import os

from main import*

from crawler import Crawler

DATA_DIR = os.path.join('data', 'ruwiki')
WIKI_NAME = 'ruwiki'
WIKI_CODE = 'ru'
DUMP_DATE = '20160203'

if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # get_id_dict(DATA_DIR, WIKI_NAME, DUMP_DATE)

    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE)
    # crawl(DATA_DIR, WIKI_NAME, WIKI_CODE, DUMP_DATE, recrawl_damaged=True)
    #
    # get_resolved_redirects(DATA_DIR)

    # get_id2title_no_redirect(DATA_DIR)

    # get_divtable_classes_chunks(DATA_DIR)

    # combine_divtable_chunks(DATA_DIR)

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

        # from tools import url_escape
        # (569543, '%D0%90%D0%B1%D0%B1%D1%80%D0%B5%D0%B2%D0%B8%D0%B0%D1%82%D1%83%D1%80%D0%B0')
        # (247372, '%D0%90%D0%BA%D1%80%D0%BE%D0%BD%D0%B8%D0%BC')
        # # hugo = [v for v in g.graph.vertices() if g.graph.vp['title'][v] == '%D0%90%D0%B1%D0%B1%D1%80%D0%B5%D0%B2%D0%B8%D0%B0%D1%82%D1%83%D1%80%D0%B0']
        # v = g.graph.vertex(569543)
        # pdb.set_trace()
        # g.compute_stats()
        g.update_stats()
        # g.print_stats()

    # end_time = datetime.now()
    # print('Duration: {}'.format(end_time - start_time))
