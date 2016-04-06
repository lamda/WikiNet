# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from main import Wikipedia, Graph

WIKI_CODE = 'en'
DUMP_DATE = '20160204'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    wp = Wikipedia(WIKI_CODE, DUMP_DATE)
    # wp.get_id_dict()
    # wp.crawl()
    # wp.crawl(recrawl_damaged=True)
    # wp.get_resolved_redirects()
    # wp.get_links(link_type='all', start=0, stop=225)
    # wp.get_links(link_type='all', start=222, stop=400)
    # wp.get_links(link_type='all', start=400, stop=600)
    # wp.get_links(link_type='all', start=600, stop=700)
    # wp.get_links(link_type='all', start=700, stop=800)
    # wp.get_links(link_type='all', start=800, stop=900)
    # wp.get_links(link_type='all', start=900, stop=1000)
    # wp.get_links(link_type='all', start=1000, stop=1050)
    wp.get_links(link_type='all', start=1050, stop=1100)
    # ---

    # wp.get_links('divs_tables')
    # wp.correct_bug()
    # wp.cleanup()
    #
    # for n_val in [
    #     1,
    #     'first_p',
    #     'lead',
    #     'infobox',
    #     'all',
    # ]:
    #     print('---------------- N =', n_val, '----------------')
    #     g = Graph(wiki_code=WIKI_CODE, N=n_val)
    #     g.load_graph()
    #     g.compute_stats()
    #     # g.update_stats()
    #     g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

