# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from bs4 import BeautifulSoup

import HTMLParser
import pdb


class WikipediaHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, label, debug=False):
        HTMLParser.HTMLParser.__init__(self)
        self.label = label
        self.first_links = []
        self.lead_links = []
        self.infobox_links = []
        self.links = []
        self.parentheses_counter = 0
        self.first_links_found = False
        self.first_link_tracking = False
        self.first_p_or_section_found = False
        self.first_p_ended = False
        self.lead_ended = False
        self.first_p_len = 0
        self.tracking_div = 0
        self.div_counter_any = 0
        self.table_counter = 0
        self.table_counter_any = 0
        self.tracking_table = 0
        self.debug = debug
        self.debug_links = False
        self.debug_found = False

        self.japars_open = [
            u'\uff08',
            u'\u0028',
            u'\ufe59',
            u'\u2768',
            u'\u276a',
            u'\u207d',
            u'\u208d',
            u'\u005b',
            u'\uff3b',
            u'\u007b',
            u'\uff5b',
            u'\ufe5b',
            u'\u2774',

            u'\u2985',
            u'\uFF5F',
            u'\u300C',
            u'\uFF62',
            u'\u300E',
            u'\u301A',
            u'\u27E6',
        ]

        self.japars_closed = [
            u'\uff09',
            u'\u0029',
            u'\ufe5a',
            u'\u2769',
            u'\u276b',
            u'\u207e',
            u'\u208e',
            u'\u005d',
            u'\uff3d',
            u'\u007d',
            u'\uff5d',
            u'\ufe5c',
            u'\u2775',

            u'\u2986',
            u'\uFF60',
            u'\u300D',
            u'\uFF63',
            u'\u300F',
            u'\u301B',
            u'\u27E7',
        ]

        if label == 'enwiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'dewiki':
            self.infobox_classes = [
                'infobox',
                'toptextcells',
                'float-right',
            ]

        elif label == 'frwiki':
            self.infobox_classes = [
                'infobox',
                'infobox_v2',
                'taxobox_classification',
            ]

        elif label == 'eswiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'itwiki':
            self.infobox_classes = [
                'sinottico',
                'sinottico_annidata',
            ]

        elif label == 'jawiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'nlwiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'ruwiki':
            self.infobox_classes = [
                'infobox',
            ]

        elif label == 'simplewiki':
            self.infobox_classes = [
                'infobox',
            ]

        else:
            print('WikipediaParser: label (%s) not supported' % label)
            pdb.set_trace()

    def reset(self):
        self.first_links = []
        self.lead_links = []
        self.infobox_links = []
        self.links = []
        self.parentheses_counter = 0
        self.first_links_found = False
        self.first_link_tracking = False
        self.first_p_or_section_found = False
        self.first_p_len = 0
        self.first_p_ended = False
        self.lead_ended = False
        self.tracking_div = 0
        self.tracking_table = 0
        self.div_counter_any = 0
        self.table_counter = 0
        self.table_counter_any = 0
        self.debug_found = False
        HTMLParser.HTMLParser.reset(self)

    def feed(self, data, debug=False):
        self.reset()
        if debug:
            self.debug = True
            if debug == 'links':
                self.debug_links = True

        repl_strings = [
            '<p>\n</p>',
            '<p> </p>',
            '<p></p>',
        ]
        for repl_string in repl_strings:
            data = data.replace(repl_string, '')

        for line in data.splitlines():
            if '<h2><span class="mw-headline"' in line:
                if not self.lead_ended:
                    self.lead_ended = True
                    if self.debug:
                        print('++++ LEAD ENDED ++++')
                if not self.first_p_or_section_found:
                    self.first_p_or_section_found = True
                    if self.debug:
                        print(
                            '++++ FIRST P, UL OR SECTION FOUND ++++ (mw-headline)')
            HTMLParser.HTMLParser.feed(self, line)

        if self.first_links == [] or self.lead_links == []:
            if self.debug:
                print('FIRST OR LEAD LINKS EMPTY - TRYING WITH BS4')
            self.reset()
            try:
                soup = BeautifulSoup(data, 'html5lib')
                pretty_data = soup.prettify()
                for line in pretty_data.splitlines():
                    if '<h2><span class="mw-headline"' in line:
                        if not self.lead_ended:
                            self.lead_ended = True
                            if self.debug:
                                print('++++ LEAD ENDED ++++')
                        if not self.first_p_or_section_found:
                            self.first_p_or_section_found = True
                            if self.debug:
                                print('++++ FIRST P, UL OR SECTION FOUND ++++ (mw-headline)')
                    HTMLParser.HTMLParser.feed(self, line)
            except (IndexError, AttributeError) as e:
                if self.debug:
                    print(e)
                    print('ERROR - falling back to standard parsing')
                self.reset()
                for line in data.splitlines():
                    if '<h2><span class="mw-headline"' in line:
                        if not self.lead_ended:
                            self.lead_ended = True
                            if self.debug:
                                print('++++ LEAD ENDED ++++')
                        if not self.first_p_or_section_found:
                            self.first_p_or_section_found = True
                            if self.debug:
                                print('++++ FIRST P, UL OR SECTION FOUND ++++ (mw-headline)')
                    HTMLParser.HTMLParser.feed(self, line)

        if debug:
            self.debug = False
            if debug == 'links':
                self.debug_links = False

    def handle_starttag(self, tag, attrs):
        if tag == 'p' or tag == 'ul':
            if self.div_counter_any < 1 and self.table_counter_any < 1 and \
                    not self.first_p_or_section_found:
                if self.debug:
                    print('++++ FIRST P, UL OR SECTION FOUND ++++ (tag == p)')
                self.first_p_or_section_found = True
            self.parentheses_counter = 0

        elif tag == 'a':
            href = [a[1] for a in attrs if a[0] == 'href']
            if href and href[0].startswith('/wiki/'):
                self.links.append(href[0].split('/', 2)[-1].split('#')[0])
                if self.debug:
                    if self.debug_links:
                        print('   ', self.links[-1], end='')
                if (not self.lead_ended and
                        self.div_counter_any == 0 and
                        self.table_counter_any == 0 and
                        self.first_p_or_section_found):
                    self.lead_links.append(self.links[-1])
                    if self.debug_links:
                        print(' (LEAD)', end='')
                if (not self.first_links_found and
                        self.first_p_or_section_found and
                        self.div_counter_any == 0 and
                        self.table_counter_any == 0 and
                        self.parentheses_counter == 0):
                    self.first_links.append(self.links[-1])
                    self.first_link_tracking = True
                    if len(self.first_links) >= 5:
                        self.first_links_found = True
                    if self.debug_links:
                        print('(FIRST LINK)', end='')

                if self.tracking_table:
                    self.infobox_links.append(self.links[-1])
                    if self.debug_links:
                        print('(INFOBOX)', end='')
                if self.debug_links:
                    print()

        elif tag == 'div':
            self.div_counter_any += 1
            if self.debug:
                print('div OPEN', tag, attrs)

        elif tag == 'table' or tag == 'dl':
            if self.debug:
                print('table OPEN', tag, attrs)
            self.table_counter_any += 1
            aclass = [a[1] for a in attrs if a[0] == 'class' or a[0] == 'id']
            if aclass:
                acl = aclass[0].lower()
                if any(s in acl for s in self.infobox_classes):
                    self.tracking_table += 1
                    if self.debug:
                        print('---- start tracking table ---')
            if self.tracking_table:
                self.table_counter += 1

    def handle_endtag(self, tag):
        if tag == 'div':
            self.div_counter_any -= 1
            if self.div_counter_any < 0:
                self.div_counter_any = 0
            if self.debug:
                print('div CLOSE', self.div_counter_any)

        elif tag == 'table' or tag == 'dl':
            self.table_counter_any -= 1
            if self.debug:
                print('table CLOSE', self.table_counter_any)
            if self.table_counter_any < 0:
                self.table_counter_any = 0
            if self.tracking_table > 0:
                self.table_counter -= 1
                if self.table_counter < 0:
                    self.table_counter = 0
                if self.table_counter == 0:
                    self.tracking_table -= 1
                    if self.tracking_table < 0:
                        self.tracking_table = 0
                if self.debug and self.tracking_table == 0:
                    print('---- stop tracking table ----')

        elif (tag == 'p' or tag == 'ul') and\
                not self.first_p_ended and self.first_p_or_section_found:
            self.first_p_ended = True
            self.first_p_len = len(self.lead_links)

    def handle_data(self, d):
        if self.first_link_tracking:
            prefix = d.strip()
            if prefix:
                prefix = prefix[0]
                if (prefix in '([{' or
                        (self.label == 'jawiki' and prefix in self.japars_open)):
                    self.first_links.pop()
                    if len(self.first_links) < 5:
                        self.first_links_found = False
            self.first_link_tracking = False

        if self.tracking_div or self.tracking_table or self.first_links_found:
            return
        par_diff = d.count('(') + d.count('[') + d.count('{') -\
                   d.count(')') - d.count(']') - d.count('}')
        if self.label == 'jawiki':
            par_plus = sum(d.count(po) for po in self.japars_open)
            par_minus = sum(d.count(pc) for pc in self.japars_closed)
            par_diff = par_plus - par_minus
        self.parentheses_counter += par_diff

    def get_data(self):
        return self.first_links, self.lead_links[:self.first_p_len],\
            self.lead_links, self.infobox_links, self.links


class WikipediaDivTableParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.divclass2id = {}
        self.tableclass2id = {}
        self.pid = None

    def reset(self):
        self.divclass2id = {}
        self.tableclass2id = {}
        self.pid = None

    def feed(self, data, pid):
        HTMLParser.HTMLParser.reset(self)
        self.reset()
        self.pid = pid
        end_strings = [
            '<h2><span class="mw-headline"',  # split at first section heading
        ]
        for end_string in end_strings:
            data = data.split(end_string)[0]

        for line in data.splitlines():
            HTMLParser.HTMLParser.feed(self, line)

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            aclass = [a[1] for a in attrs if a[0] == 'class']
            for aa in aclass:
                # for a in aa.split(' '):
                #     self.class2id[a] = self.pid
                self.tableclass2id[frozenset(aa.split(' '))] = self.pid

        elif tag == 'div':
            aclass = [a[1] for a in attrs if a[0] == 'class']
            for aa in aclass:
                # for a in aa.split(' '):
                #     self.class2id[a] = self.pid
                self.divclass2id[frozenset(aa.split(' '))] = self.pid

    def get_data(self):
        return self.divclass2id, self.tableclass2id
