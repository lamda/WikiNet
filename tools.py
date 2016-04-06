# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import cPickle as pickle
import os
import pdb
import urllib


def debug_iter(iterable, length=None):
    for index, element in enumerate(iterable):
        if (index % 1000) == 0:
            # print('\r', index, '/', length, end='')
            print('\r', index, end='')
        yield element


def read_pickle(fpath):
    with open(fpath, 'rb') as infile:
        obj = pickle.load(infile)
    return obj


def write_pickle(fpath, obj):
    with open(fpath, 'wb') as outfile:
        pickle.dump(obj, outfile, -1)


def url_escape(title):
    # return title.replace("\\'", "%27")\
    #             .replace('\\"', '%22')\
    #             .replace('\\%', '%25')\
    #             .replace('\\\\', '%5C')\
    #             .replace(u'\u2013', '%E2%80%93')
    title = title.replace("\\'", "'")\
                    .replace('\\"', '"')\
                    .replace('\\_', '_')\
                    .replace('\\%', '%')\
                    .replace('\\\\', '\\')\
                    .replace(' ', '_')
    title = urllib.quote(title.encode('utf-8'))

    # unquote a few chars back because they appear in Wikipedia
    for quoted, unquoted in [
        ('%21', '!'),
        ('%22', '"'),
        # ('%23', '#'),
        ('%24', '$'),
        ('%25', '%'),
        ('%26', '&'),
        # ('%27', "'"),
        ('%28', '('),
        ('%29', ')'),
        ('%2A', '*'),
        # ('%2B', '+'),
        ('%2C', ','),
        ('%2D', '-'),
        ('%2E', '.'),
        ('%2F', '/'),
        ('%3A', ':'),
        ('%3B', ';'),
        ('%3C', '<'),
        ('%3D', '='),
        ('%3E', '>'),
        ('%3F', '?'),
        ('%40', '@'),
    ]:
        title = title.replace(quoted, unquoted)

    return title


def url_unescape(title):
    title = urllib.unquote(title.encode('utf-8')).decode('utf-8')
    return title


def export_bowtie_dicts():
    from main import Graph
    bt_labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
    wikipedias = [
        # 'simple',

        # 'it',
        # 'de',
        # 'fr',
        # 'es',
        # 'ja',
        # 'nl',
        # 'ru',
        'en',
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
            g = Graph(wiki_code=wp, N=n_val)
            g.load_graph(refresh=False)
            d[n_val] = {g.graph.vp['name'][v]: g.graph.vp['bowtie'][v]
                        for v in g.graph.vertices()}
            d_tmp = {l: 0 for l in bt_labels}
            for v in g.graph.vertices():
                d_tmp[g.graph.vp['bowtie'][v]] += 1
            for l in bt_labels:
                print('       ', l, d_tmp[l])
        fname = 'id2bowtie-' + wp + '.obj'
        write_pickle(os.path.join(pageview_dir_filtered, fname), d)


if __name__ == '__main__':
    export_bowtie_dicts()
