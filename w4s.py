# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import cPickle as pickle
try:
    import graph_tool.all as gt
except ImportError:
    pass
import HTMLParser
import io
import itertools
import numpy as np
import os
import pdb
import random
import re


def article_generator(offset=0):
    # get list of files
    fpath = os.path.join('w4s', 'articles.txt')
    with io.open(fpath, encoding='utf-8') as infile:
        files = infile.read()

    # extract first link that is not in italics or in parentheses
    counter = 0
    for file in files.splitlines():
        fpath = os.path.join('w4s', file[0].lower(), file + '.htm')
        with io.open(fpath, encoding='utf-8') as infile:
            data = infile.read()
            if counter >= offset:
                yield file, data
            counter += 1


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


def get_first_link_alt(html):
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


def link_generator(html):
    html = html.split('<!-- start content -->')[1].replace('\n', '')
    html = html.split('<!-- end content -->')[0]
    pdb.set_trace()
    html = re.sub('<div.*?</div>', '', html)
    pdb.set_trace()

    # via http://stackoverflow.com/questions/35689153
    without_paren = r'<a href="(?P<WITHOUT_PAREN>[^"]+)">'
    with_paren = r'\(.*?<a href="(?P<WITH_PAREN>[^"]+)">.*?\)'
    master_pattern = with_paren + '|' + without_paren  # try with_paren first
    it = re.finditer(master_pattern, html)
    # Drop matches in `it` until we hit the first without_paren match
    # and yield every match from there onwards
    for mo in itertools.dropwhile(lambda x: x.lastgroup == 'WITH_PAREN', it):
        yield mo.group(mo.lastgroup)


class WikipediaHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, debug=False):
        HTMLParser.HTMLParser.__init__(self)
        self.fed = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.tracking_div = 0
        self.div_counter = 0
        self.table_counter = 0
        self.tracking_table = 0
        self.debug = debug
        self.debug_found = False

    def reset(self):
        self.fed = []
        self.tracking_link = False
        self.parentheses_counter = 0
        self.first_link_found = False
        self.tracking_div = 0
        self.div_counter = 0
        self.table_counter = 0
        self.tracking_table = 0
        self.debug_found = False
        HTMLParser.HTMLParser.reset(self)

    def feed(self, data):
        self.reset()
        data = data.split('<!-- start content -->')[1]
        data = data.split('<!-- end content -->')[0]
        HTMLParser.HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attrs):
        # if tag == 'a' and 'Rabbit' in ' '.join([a[1] for a in attrs]):
        #     pdb.set_trace()


        if (tag == 'a' and self.div_counter == 0 and self.table_counter == 0)\
                and (self.parentheses_counter == 0 or self.first_link_found):
            if self.debug:
                print('a, 0', tag, attrs)
            href = [a[1] for a in attrs if a[0] == 'href']
            # if href and href[0].startswith('/wiki/'):
            if href and href[0].startswith('../../wp/'):
                self.fed.append(href[0].split('/')[-1].split('#')[0].rsplit('.')[0])
                self.tracking_link = True
                self.first_link_found = True

        elif tag == 'div':
            if self.debug:
                print('div OPEN', tag, attrs)
            aclass = [a[1] for a in attrs if a[0] == 'class']
            if aclass and 'thumb tright' in aclass[0]:
                self.tracking_div += 1
            if self.tracking_div:
                self.div_counter += 1

        elif tag == 'table':
            if self.debug:
                print('table OPEN', tag, attrs)
            # aclass = [a[1] for a in attrs if a[0] == 'class']
            # if aclass and 'infobox' in aclass[0]:
            #     self.tracking_table += 1
            self.tracking_table += 1
            if self.tracking_table:
                self.table_counter += 1

    def handle_endtag(self, tag):
        if tag == 'a' and self.tracking_link:
            self.tracking_link = False
        elif tag == 'div':
            if self.debug:
                print('div CLOSE')
            if self.tracking_div > 0:
                self.div_counter -= 1
                if self.div_counter == 0:
                    self.tracking_div = min(0, self.tracking_div-1)
        elif tag == 'table':
            if self.debug:
                print('table CLOSE')
            if self.tracking_table > 0:
                self.table_counter -= 1
                if self.table_counter == 0:
                    self.tracking_table = min(0, self.tracking_table-1)
            # pdb.set_trace(); print(self.tracking_table, self.table_counter, self.tracking_div, self.div_counter)

    def handle_data(self, d):
        # if not self.tracking_link:
        #     d = d.strip('\t\x0b\x0c\r ')
        #     if d:
        #         self.fed.append(d + ' ')
        # d = d.strip('\t\x0b\x0c\r \n')
        # if not d:
        #     return
        # print(d)
        # pdb.set_trace()
        if self.tracking_div or self.tracking_table:
            return
        par_diff = d.count('(') - d.count(')')
        self.parentheses_counter += par_diff
        # if self.parentheses_counter > 0:
        #     print(self.parentheses_counter, d)
        if 'rufus' in d:
            self.debug_found = True
        if self.debug_found:
            print(self.parentheses_counter, d)

    def get_data(self):
        return self.fed


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    # parser = WikipediaHTMLParser(debug=False)
    parser = WikipediaHTMLParser(debug=True)
    for idx, (title, html) in enumerate(article_generator()):
        print(title)
        parser.feed(html)
        links = parser.get_data()
        if len(links) < 2:
            pdb.set_trace()
        # for link in links[:10]:
        #     print('   ', link)
        # pdb.set_trace()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
