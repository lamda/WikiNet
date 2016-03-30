# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import os
import pdb
import shutil

if __name__ == '__main__':
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    files.remove('alluvial.html')
    files = [
        (f, f.rsplit('.', 1)[0] + '_full.pdf', f.rsplit('.', 1)[0] + '.pdf')
        for f in files
    ]
    # files = files[:1]

    print('converting to pdf...')
    for f in files:
        cmd = '"C:\\Program Files\\wkhtmltopdf\\bin\wkhtmltopdf.exe" ' +\
              f[0] + ' ' + f[1]
        os.system(cmd)

    print('cropping pdf...')
    for f in files:
        cmd = 'pdfcrop --margins 15 ' + f[1] + ' ' + f[2]
        os.system(cmd)

    print('copying pdfs...')
    for f in files:
        # shutil.copy(f[2], 'D:\\Dropbox\\paper_wikinet\\figures')
        shutil.copy(f[2], 'D:\\PhD\\Dropbox\\paper_wikinet\\figures')

    print('done')
