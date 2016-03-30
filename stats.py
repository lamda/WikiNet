# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals
import io
import os
import pdb

from main import Graph
from tools import read_pickle, write_pickle, url_unescape


def get_graph2cpsize():
    wikipedias = [
        'simple',

        'en',
        'de',
        'fr',
        'es',
        'ru',
        'it',
        'ja',
        'nl',
    ]
    n_vals = [
        'first_p',
        'lead',
        'all',
        'infobox',
    ]
    d = {wp: {n_val: 0 for n_val in n_vals} for wp in wikipedias}
    for wp in wikipedias:
        print(wp)
        for n_val in n_vals:
            print('   ', n_val)
            g = Graph(data_dir=os.path.join('data', wp + 'wiki'),
                      fname='links', use_sample=False, refresh=False,
                      N=n_val)
            g.load_graph(refresh=False)
            d[wp][n_val] = len([v for v in g.graph.vertices() if g.graph.vp['bowtie'][v] == 'SCC'])
    write_pickle(os.path.join('data', 'graph2cpsize.obj'), d)


def get_navigability_stats():
    wikipedias = [
        # 'simple',

        'en',
        'de',
        'fr',
        'es',
        'ru',
        'it',
        'ja',
        'nl',
        ]

    n_vals = [
        'first_p',
        'lead',
        'all'
    ]

    wikipedia2articles_edits = {
        'en': (812170986, 5072214),
        'de': (156204159, 1905450),
        'fr': (125368222, 1721902),
        'es': (94262365, 1232123),
        'ru': (88544149, 1287687),
        'it': (83993233, 1251650),
        'ja': (59504158, 1001180),
        'nl': (46955102, 1854708),
    }
    # get_graph2cpsize()
    graph2cpsize = read_pickle(os.path.join('data', 'graph2cpsize.obj'))
    fpath = os.path.join('plots', 'stats.txt')
    with io.open(fpath, 'a', encoding='utf-8') as outfile:
        for wp in wikipedias:
            a, e = wikipedia2articles_edits[wp]
            for n_val in n_vals:
                if n_val == n_vals[0]:
                    text = '%s & %d & %d & %s & ' % (wp, a, e, n_val.replace('_', '\\_'))
                else:
                    text = ' & & & %s & ' % (n_val.replace('_', '\\_'))
                scc_size = graph2cpsize[wp][n_val]
                text += '$%.5f$ & $%.5f$ \\\\' % (scc_size / a, scc_size / e)
                print(text)
                outfile.write(text + '\n')
            outfile.write('\\hline\n')


def get_view_count_stats():
    wikipedias = [
        # 'simple',
        'en',
        'de',
        'fr',
        'es',
        'ru',
        'it',
        'ja',
        'nl',
        ]
    for wp in wikipedias:
        print(wp)
        id2bowtie = read_pickle(os.path.join('data', 'pageviews', 'filtered',
                                'id2bowtie-' + wp + '.obj'))
        id2views = read_pickle(os.path.join('data', 'pageviews', 'filtered',
                               'id2views-' + wp + '.obj'))

        in_views, scc_views, out_views = 0, 0, 0
        in_len, scc_len, out_len = 0, 0, 0
        for node, cp in id2bowtie['first_p'].items():
            if cp == 'SCC':
                scc_views += id2views[node]
                scc_len += 1
            elif cp == 'IN':
                in_views += id2views[node]
                in_len += 1
            elif cp == 'OUT':
                out_views += id2views[node]
                out_len += 1
        fpath = os.path.join('plots', 'stats_views.txt')
        with io.open(fpath, 'a', encoding='utf-8') as outfile:
            text = wp + ' & $%.2f$ & $%.2f$ & $%.2f$\\\\\n' \
            % (in_views/in_len, scc_views/scc_len, out_views/out_len)
            print(text)
            outfile.write(text)


if __name__ == '__main__':
    get_navigability_stats()
    # get_view_count_stats()

