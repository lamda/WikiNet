# -*- coding: utf-8 -*-

from __future__ import division, print_function

try:
    import graph_tool.all as gt
except ImportError:
    pass
import os
import pdb

from main import Graph
from tools import write_pickle


if __name__ == '__main__':
    wikipedias = [
        # 'simple',

        'it',
        'en',
        'de',
        'fr',
        'es',
        'ru',
        'ja',
        'nl',
    ]

    n_vals = [
        '1',
        'first_p',
        'lead',
        'all',
        'infobox',
    ]
    pageview_dir_filtered = os.path.join('data', 'pageviews', 'filtered')

    for wp in wikipedias:
        print(wp)
        d = {}
        for n_val in n_vals:
            print('   ', n_val)
            g = Graph(data_dir=os.path.join('data', wp + 'wiki'), fname='links',
                      use_sample=False, refresh=False, N=n_val)
            g.load_graph(refresh=False)
            d[n_val] = {g.graph.vp['name'][v]: g.graph.vp['bowtie'][v]
                        for v in g.graph.vertices()}
        fname = 'id2bowtie-' + wp + '.obj'
        write_pickle(os.path.join(pageview_dir_filtered, fname), d)







