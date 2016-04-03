# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from main import Wikipedia

if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    wp = Wikipedia('fr', '20160203')

    wp.get_id_dict()

    wp.crawl()

    wp.crawl(recrawl_damaged=True)

    wp.get_resolved_redirects()

    wp.get_links('all_lead')

    wp.get_links('divs_tables')

    wp.cleanup()

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
