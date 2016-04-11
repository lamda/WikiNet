# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from main import Wikipedia, Graph

WIKI_CODE = 'es'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    wp = Wikipedia(WIKI_CODE, DUMP_DATE)
    # wp.get_id_dict()
    # wp.crawl()
    # wp.crawl(recrawl_damaged=True)
    # wp.get_resolved_redirects()
    # wp.get_links(link_type='all', start=None, stop=72)
    # wp.get_links(link_type='all', start=72, stop=144)
    # wp.get_links(link_type='all', start=144, stop=216)
    # wp.get_links(link_type='all', start=216, stop=None)

    # wp.get_links(link_type='all', start=None, stop=36)
    # wp.get_links(link_type='all', start=36, stop=72)
    # wp.get_links(link_type='all', start=72, stop=108)
    # wp.get_links(link_type='all', start=108, stop=144)
    # wp.get_links(link_type='all', start=144, stop=180)
    # wp.get_links(link_type='all', start=180, stop=216)
    # wp.get_links(link_type='all', start=216, stop=252)
    # wp.get_links(link_type='all', start=252, stop=None)
    # wp.get_links('divs_tables')
    # wp.combine_link_chunks()
    # wp.correct_bug()
    # wp.cleanup()
    # import pdb; pdb.set_trace()

    for n_val in [
        1,
        # 'first_p',
        # 'lead',
        # 'infobox',
        # 'all',
    ]:
        print('---------------- N =', n_val, '----------------')
        g = Graph(wiki_code=WIKI_CODE, N=n_val)
        g.load_graph()
        # g.compute_stats()
        g.update_stats()
        # g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

