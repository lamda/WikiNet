# -*- coding: utf-8 -*-

from __future__ import division, print_function
import os

from main import Graph
from tools import read_pickle, write_pickle


if __name__ == '__main__':
    wikipedias = [
        # 'simple',

        'it',
        # 'en',
        # 'de',
        # 'fr',
        # 'es',
        # 'ru',
        # 'ja',
        # 'nl',
    ]

    n_vals = [
        ('first_p', 'lead'),
        # ('lead', 'all'),
    ]
    pageview_dir_filtered = os.path.join('data', 'pageviews', 'filtered')

    for wp in wikipedias:
        print(wp)
        for wp_small, wp_large in n_vals:
            print('   ', wp_small, wp_large)
            g_small = Graph(data_dir=os.path.join('data', wp + 'wiki'),
                            fname='links', use_sample=False, refresh=False,
                            N=wp_small)
            g_large = Graph(data_dir=os.path.join('data', wp + 'wiki'),
                            fname='links', use_sample=False, refresh=False,
                            N=wp_large)
            g_small.load_graph(refresh=False)
            g_large.load_graph(refresh=False)
            id2views = read_pickle(os.path.join(pageview_dir_filtered,
                                                'id2views-' + wp + '.obj'))
            id2bowtie = read_pickle(os.path.join(pageview_dir_filtered,
                                                 'id2bowtie-' + wp + '.obj'))
            id2bowtie_small = id2bowtie[wp_small]
            id2bowtie_large = id2bowtie[wp_large]

            # find articles in OUT with highest view count
            outc = [v for v in g_large.graph.vertices()
                    if g_large.graph.vp['bowtie'] == 'OUT']
            # find top 10 efficiently...



            # find articles in IN with highest view count

            # look at candidates and find articles in IN with highest view count

            # find articles in IN with largest OUT component towards SCC




