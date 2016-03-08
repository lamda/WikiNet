# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import gzip
import os
import pandas as pd
import pdb
import re


if __name__ == '__main__':
    files = [f for f in os.listdir('.') if f.endswith('_stats.sql.gz')]
    regex = r'INSERT INTO `site_stats` VALUES \(\d+,\d+,(\d+),(\d+)'
    labels, edits, articles = [], [], []
    for filename in files:
        with gzip.open(filename, 'rb') as infile:
            data = infile.read()
        match = re.search(regex, data, re.DOTALL)
        labels.append(filename[:filename.index('wiki')])
        edits.append(int(match.group(1)))
        articles.append(int(match.group(2)))
    df = pd.DataFrame(data=zip(labels, edits, articles),
                      columns=['label', 'edits', 'articles'])
    print('EDITS')
    print(df.sort_values(by='edits', ascending=False))
    print()
    print('ARTICLES')
    print(df.sort_values(by='articles', ascending=False))
    pdb.set_trace()
