# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import cPickle as pickle
import json
import io
import numpy as np
import os
import pdb
import urllib2

from parsers import WikipediaHTMLParser

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)

base_url = url = 'https://%s.wikipedia.org/w/api.php?format=json&rvstart=20160203235959&prop=revisions|categories&continue&pageids=%s&action=query&rvprop=content&rvparse&cllimit=500&clshow=!hidden&redirects=True'

if __name__ == '__main__':

    solutions = {
        # ('es', '1173'): ['Wikipedia:Etimolog%C3%ADas', 'Idioma_franc%C3%A9s', 'Estado_miembro_de_la_Uni%C3%B3n_Europea'],
        # ('es', '972'): ['Estado', 'Estado', 'Estado_miembro_de_la_Uni%C3%B3n_Europea'],
        # ('es', '10'): ['Estado_naci%C3%B3n', 'Estado_naci%C3%B3n', 'Archivo:Flag_of_Argentina.svg'],
        # ('es', '7722'): ['Anexo:Pa%C3%ADses_por_poblaci%C3%B3n', 'Hindi', 'Archivo:Flag_of_India.svg'],
        # ('es', '36522'): ['Lat%C3%ADn', 'Lat%C3%ADn', ''],
        # ('de', '1497705'): ['Medium:De-Deutschland.ogg', 'Medium:De-Deutschland.ogg', 'Datei:Flag_of_Germany.svg'],
        # ('de', '21362'): ['Monarchie', 'Monarchie', ''],  # IB not detected, should be 'Datei:Wappen_Deutsches_Reich_-_K%C3%B6nigreich_Preussen_(Grosses).png'
        # ('fr', '170932'): ['Fichier:Drum_vibration_mode22.gif', 'Fichier:Drum_vibration_mode22.gif', ''],
        # ('fr', '2681'): ['Rome', 'Rome', ''],
        # ('ru', '68'): ['%D0%9E%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%BC', '%D0%93%D1%80%D0%B5%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA', ''],
        # ('it', '481124'): ['Musica', 'Musica', ''],
        ('nl', '1491'): ['Media:Nl-Roemeni%C3%AB.ogg', 'Media:Nl-Roemeni%C3%AB.ogg', 'Bestand:Flag_of_Romania.svg'],
        # ('de', ''): ['', '', ''],
        # ('de', ''): ['', '', ''],
        # ('de', ''): ['', '', ''],
    }

    test_cases = solutions.keys()
    for wiki_code, pid in test_cases:
        print(wiki_code, pid)
        fpath = os.path.join('test', wiki_code + '-' + pid + '.json')
        if not os.path.isfile(fpath):
            response = urllib2.urlopen(url % (wiki_code, pid))
            data = response.read().decode('utf-8')
            with io.open(fpath, 'w', encoding='utf-8') as outfile:
                outfile.write(data)
        with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
            data_original = json.load(infile)
        data = data_original['query']['pages'][pid]['revisions'][0]['*']

        parser = WikipediaHTMLParser(label=wiki_code + 'wiki')
        parser.feed(data)
        first_links, first_p_links, lead_links, ib_links, all_links = parser.get_data()
        solution = solutions[(wiki_code, pid)]

        pdb.set_trace()
        try:
            assert first_links[0] == solution[0]
            assert lead_links[0] == solution[1]
            if solution[2]:
                assert ib_links and ib_links[0] == solution[2]
            else:
                assert ib_links == []
            print('    PASSED')
        except AssertionError:
            print('    FAILED')
            pdb.set_trace()
        # parser.feed(data, debug='links')

    # pid = '1173'
    # wiki = 'es'
    #
    # # import urllib2
    # # url = 'https://' + wiki + '.wikipedia.org/w/api.php?format=json&rvstart=20160203235959&prop=revisions|categories&continue&pageids=%s&action=query&rvprop=content&rvparse&cllimit=500&clshow=!hidden&redirects=True'
    # # print(url % pid)
    # # response = urllib2.urlopen(url % pid)
    # # data = response.read().decode('utf-8')
    # # with io.open('test2.txt', 'w', encoding='utf-8') as outfile:
    # #     outfile.write(data)
    #
    # with io.open('test2.txt', encoding='utf-8', errors='ignore') as infile:
    #     data_original = json.load(infile)
    # data = data_original['query']['pages'][pid]['revisions'][0]['*']
    #
    # parser = WikipediaHTMLParser(label=wiki + 'wiki')
    # parser.feed(data)
    #
    # print('\nhttp://' + wiki +
    #       '.wikipedia.org?curid=%s' % pid)
    # first_links, first_p_links, lead_links, ib_links, all_links = parser.get_data()
    # # fix double % encoding
    # first_links = [l.replace('%25', '%') for l in first_links]
    # first_p_links = [l.replace('%25', '%') for l in first_p_links]
    # lead_links = [l.replace('%25', '%') for l in lead_links]
    # ib_links = [l.replace('%25', '%') for l in ib_links]
    # all_links = [l.replace('%25', '%') for l in all_links]
    # print('----FIRST LINKS:')
    # for l in first_links:
    #     print('   ', l)
    # print('----IB LINKS:')
    # for l in ib_links[:10]:
    #     print('   ', l)
    # print('----LEAD LINKS:')
    # for l in lead_links[:10]:
    #     print('   ', l)
    # pdb.set_trace()
    # parser.feed(data, debug='links')
