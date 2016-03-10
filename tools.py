# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import cPickle as pickle
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

