# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import io
import numpy as np
import os
import pdb
import random
import re


def article_generator():
    # get list of files
    fpath = os.path.join('w4s', 'articles.txt')
    with io.open(fpath, encoding='utf-8') as infile:
        files = infile.read()

    # extract first link that is not in italics or in parentheses
    for file in files.splitlines():
        fpath = os.path.join('w4s', file[0].lower(), file + '.htm')
        with io.open(fpath, encoding='utf-8') as infile:
            data = infile.read()
            yield file, data

class Parser(object):
    def __init__(self):
        self.parentheses = 0

    def parse(self, data):
        self.parentheses = 0
        do_print = True
        for pos in range(len(data)):
            if data[pos] == '|':
                do_print = True
            if do_print:
                print(data[pos])
            if data[pos] == '(':
                self.parentheses += 1
                print('    adding to par')
            elif data[pos] == ')':
                self.parentheses -= 1
                print('    subtracting from par')
            elif data[pos] == '<' and self.parentheses == 0:
                lookahead = data[pos:pos+70]
                if lookahead.startswith('<a href="../../wp/') or\
                        lookahead.startswith('<a class="mw-redirect" href="href="../../wp/'):
                    return pos
        return -1


link_regex = re.compile(r'(?:<a (?:class="mw-redirect" )?'
                        'href="../../wp/[^/]+/(.+?)\.htm" title="[^"]+">'
                        '.+?</a>)', re.DOTALL)
parser = Parser()


def get_first_link(html):
    # get rid of everything in () until the first link
    # get rid of links in italics?
    first_link = parser.parse(html)
    if first_link != -1:
        html = html[first_link:]
    links = link_regex.findall(html)
    print(links[0])
    pdb.set_trace()


    # links = link_regex.findall(html)
    #
    # html = 'Test (not a link: <a href="../../wp/p/Parisp1.htm" title="Paris">Paris</a>), blabla (also not a link: <a href="../../wp/p/Parisp2.htm" title="Paris">Paris</a>), but here comes a link: <a href="../../wp/p/link1.htm" title="Paris">Paris</a> and again (<a href="../../wp/p/link1.htm" title="link2p">Paris</a>) and again some text, and finally: <a href="../../wp/p/link1.htm" title="lastlink">Paris</a>'
    # html = 'Test (not a link: <a href1>), blabla (also not a link: <a href2>), but here comes a link: <a href3> and again (<a href4>) and again some text, and finally: <a href5>'
    # re_link = '(?:<a (?:class="mw-redirect" )?href="../../wp/[^/]+/(.+?)\\.htm" title="[^"]+">.+?</a>)'
    # re_link = '(<a (class="mw-redirect" )?href="../../wp/[^/]+/(.+?)\\.htm" title="[^"]+">.+?</a>)'
    # re.findall(r'(?:.*?(?:\(.*?\))?)*' + re_link + r'(?:.*?' + re_link + ')*', html)
    #
    # # http://stackoverflow.com/questions/12999419/python-re-findall-is-not-working-as-expected
    # # I want to match all occurrences of the letter a, except for the first one if it is in parentheses
    # e.g., 'b a b a c de a' --> ['a', 'a', 'a']
    # e.g., 'b (a) b a c de a' --> ['a', 'a']


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    for idx, (title, html) in enumerate(article_generator()):
        print(title)
        link = get_first_link(html)

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
