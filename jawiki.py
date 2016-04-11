# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import pdb

from main import Wikipedia, Graph

WIKI_CODE = 'ja'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    wp = Wikipedia(WIKI_CODE, DUMP_DATE)
    # wp.get_id_dict()
    # wp.crawl()
    # wp.crawl(recrawl_damaged=True)
    # wp.get_resolved_redirects()
    # wp.get_links('all')
    # wp.get_links('divs_tables')
    # wp.correct_bug()
    # wp.cleanup()

    def get_node(title):
        node = name2node[title]
        nbs = []
        for nb in node.in_neighbours():
            nbs.append((nb.in_degree(), g.graph.vp['name'][nb]))
        for nb in sorted(nbs, reverse=True)[:15]:
            print(nb)

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
        # name2node = {g.graph.vp['title'][i]: i for i in g.graph.vertices()}
        # pdb.set_trace()  # 人間 (%E4%BA%BA%E9%96%93), 人間関係 (%E4%BA%BA%E9%96%93%E9%96%A2%E4%BF%82)
        # g.compute_stats()
        g.update_stats()
        # g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

