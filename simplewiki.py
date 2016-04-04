# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from main import Wikipedia, Graph

WIKI_NAME = 'simple'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    wp = Wikipedia(WIKI_NAME, DUMP_DATE)
    # wp.get_id_dict()
    # wp.crawl()
    # wp.crawl(recrawl_damaged=True)
    # wp.get_resolved_redirects()
    # wp.get_links('all')
    # wp.combine_link_chunks()
    # wp.get_links('divs_tables')
    # wp.cleanup()

    for n_val in [
        # 1,
        # 'first_p',
        # 'lead',
        # 'infobox',
        'all',
    ]:
        print('---------------- N =', n_val, '----------------')
        g = Graph(wiki_name=WIKI_NAME, N=n_val)
        g.load_graph()
        g.compute_stats()
        # g.update_stats()
        g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

