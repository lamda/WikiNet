# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import io
import matplotlib
matplotlib.rc('pdf', fonttype=42)
import matplotlib.pyplot as plt
import numpy as np
import operator
import os
import pdb
import cPickle as pickle

from tools import url_unescape


class Plotter(object):
    def __init__(self, label, to_plot):
        self.label = label
        self.stats_folder = os.path.join('data', self.label, 'stats')
        self.colors = ['#FFA500', '#FF0000', '#0000FF', '#05FF05', '#000000']
        self.colors_set2 = [
            (0.4, 0.7607843137254902, 0.6470588235294118),
            (0.9882352941176471, 0.5529411764705883, 0.3843137254901961),
            (0.5529411764705883, 0.6274509803921569, 0.796078431372549),
            (0.9058823529411765, 0.5411764705882353, 0.7647058823529411),
            (0.6509803921568628, 0.8470588235294118, 0.32941176470588235),
            (1.0, 0.8509803921568627, 0.1843137254901961),
            (0.8980392156862745, 0.7686274509803922, 0.5803921568627451),
            (0.7019607843137254, 0.7019607843137254, 0.7019607843137254)
        ]
        self.label2language = {
            'simple': 'Simple English',
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'ru': 'Russian',
            'nl': 'Dutch',
            'it': 'Italian',
            'ja': 'Japanese',
        }
        # self.hatches = ['', 'xxx', '///', '---']
        self.hatches = ['----', '/', 'xxx', '', '///', '---']
        self.linestyles = ['-', '--', ':', '-.']
        # self.graph_order = ['1', 'first_p', 'lead', 'infobox']
        self.graph_order = n_vals
        self.graph_data = {}
        self.bowtie_changes = {}
        self.plot_folder = 'plots'
        if not os.path.exists(self.plot_folder):
            os.makedirs(self.plot_folder)
        self.load_graph_data()
        self.plot_file_types = [
            '.png',
            '.pdf',
        ]

        if 'cycles' in to_plot:
            self.print_cycles()
        if 'link_counts' in to_plot:
            self.print_link_counts()
        if 'cp_size' in to_plot:
            self.plot('cp_size')
        if 'cp_count' in to_plot:
            self.plot('cp_count')
        if 'outdegree_av' in to_plot:
            self.plot('outdegree_av')
        if 'cc' in to_plot:
            self.plot('cc')
        if 'recommendations' in to_plot:
            self.plot_recommendations_scc_size()
            self.plot_recommendations_vc()
        if 'ecc' in to_plot:
            self.plot_ecc()
        if 'pls' in to_plot:
            self.plot_pls()
        if 'bow_tie' in to_plot:
            self.plot_bow_tie()
        if 'bow_tie_alluvial' in to_plot:
            self.plot_alluvial()
        if 'bow_tie_stats' in to_plot:
            self.bow_tie_stats()

    def load_graph_data(self):
        for graph_type in self.graph_order:
            graph_fname = 'links_' + graph_type
            fpath = os.path.join(self.stats_folder, graph_fname + '.obj')
            with open(fpath, 'rb') as infile:
                graph_data = pickle.load(infile)
            self.graph_data[graph_type] = graph_data

    def print_cycles(self):
        def translate(word):
            d = {
                # de
                'Philosophie': 'Philosophy',
                'Welt': 'World',
                'Totalität': 'Totality',
                'Liste japanischer Inseln': 'List of islands of Japan',
                'Kommunikationsmittel': 'Means of communication',
                'Medium (Kommunikation)': 'Media (Communication)',
                'Druckerzeugnis': 'Printed matter',
                'Zeitschrift': 'Magazine',

                # fr
                'Connaissance': 'Knowledge',
                'Notion': 'Notion (philosophy)',
                'Grec ancien': 'Ancient Greek',
                'Grec': 'Greek language',
                'Langues helléniques': 'Hellenic languages',
                'Isoglosse centum-satem': 'Centum and satem languages',
                'Isoglosse': 'Isogloss',
                'Trait (linguistique)': 'Feature (linguistics)',
                'Linguistique': 'Linguistics',
                'Discipline (spécialité)': ' Discipline (academia)',
                'Savoir': 'Knowledge',
                'Âme': 'Soul',
                'Principe (philosophie)': 'Principle',
                'Liaison (mécanique)': 'Linkage (mechanical)',
                'Assemblage mécanique': 'Assembly',
                'Mécanisme': 'Mechanism (engineering)',

                # es
                'Psicología': 'Psychology',
                'Profesión': 'Profession',
                'Especialización': 'Specialization',
                'Actividad': 'Activity',
                'Norma social': 'Norm (social)',
                'Norma jurídica': 'Precept',
                'Información': 'Information',
                'Dato': 'Data',
                'Código (comunicación)': 'Code',
                'Comunicación': 'Communication',

                # it
                'Conoscenza': 'Knowledge',
                'Consapevolezza': 'Awareness',
                'Psicologia': 'Psychology',
                'Psiche': 'Psyche (psychology)',
                'Cervello': 'Brain',
                'Sistema nervoso centrale': 'Central nervous system',
                'Sistema nervoso': 'Nervous system',
                'Tessuto (biologia)': ' Tissue (biology)',
                'Biologia': 'Biology',
                'Scienza': 'Science',
                'Matita': 'Pencil',
                'Disegno': 'Drawing',
                'Norma giuridica': 'Precept',
                'Ordinamento giuridico': 'Legal system',
                'Diritto': 'Law',

                # nl
                'Kennis': 'Knowledge',
                'Weten': 'Know-how',
                'Leven': 'Life',
                'Organisme': 'Organism',
                'Continentaal plat': 'Continental shelf',

                # ru
                'Философия': 'Philosophy',
                'Познание': 'Cognition',
                'Метод': 'Method (philosophy)',
                'Систематизация': 'Systematization',
                'Теория множеств': 'Set theory',
                'Математика': 'Mathematics',
                'Наука': 'Science',
                'Объективность': 'Objectivity (philosophy)',
                'Объект (философия)': 'Object (philosophy)',

                'Аббревиатура': 'Abbreviation',
                'Акроним': 'Acronym',

                'Земля': 'Earth',
                'Солнце': 'Sun',
                'Звезда': 'Star',

                # ja
                'インド・ヨーロッパ語族': 'Indo-European Languages',
                'ヨーロッパ': 'Europe',
                '地球': 'Earth',
                '人類': 'Humanity',
                '人間': 'Person',
                '英語': 'English language',

                '動物': 'Animal',
                '生物': 'Organism',
                '植物': 'Plant',
                '草本': 'Gras',

                '28年': '28',
                '西暦': 'Anno Domini',
                'イエス・キリスト': 'Jesus',
                'ゲルマン語派': 'Germanic languages',
                '人間関係': 'Interpersonal relationship',
                'アメリカ合衆国': 'United States',
                'イン・ゴッド・ウィー・トラスト': 'In God we trust',
                'メソポタミア': 'Mesopotamia',
                'チグリス川': 'Tigris',
                'トルコ': 'Turkey',
                '西アジア': 'Western Asia',
                'アジア': 'Asia',
                'アッシリア': 'Assyria',

                'トルコ語': 'Turkish language',
                'アゼルバイジャン語': 'Azerbaijani language',

            }

            try:
                return d[word]
            except KeyError:
                return word

        fpath = os.path.join('plots', 'cycles.txt')
        cstats = self.graph_data['1']['comp_stats']
        no_articles = self.graph_data['1']['graph_size']

        cstats.sort(key=operator.itemgetter('incomp_size'), reverse=True)
        with io.open(fpath, 'a', encoding='utf-8') as outfile:
            text = self.label2language[self.label[:-4]]
            # print(text)
            outfile.write(text)
            for cidx, cstat in enumerate(cstats[:1]):
                text = ''
                cover = 100 * cstat['incomp_size'] / no_articles
                if cidx == 0:
                    top_cycle = self.graph_data['1']['top_cyle']
                    top_cycle.sort(reverse=True)
                    names = [tn[1].replace('_', ' ') for tn in top_cycle]
                else:
                    names = [n.replace('_', ' ') for n in cstat['names']]
                names = map(url_unescape, names)
                names_translated = ', '.join(map(translate, names))
                if cidx == 0:
                    n0 = '\\textbf{' + translate(names[0]) + ' (%.1f\\%%)}' % (100*top_cycle[0][0] / no_articles)
                    names_translated = [n0] + map(translate, names[1:])
                    names_translated = ', '.join(names_translated)
                names = ', '.join(names)
                if self.label == 'jawiki':
                    names = '\\begin{CJK}{UTF8}{min} ' + names + '\\end{CJK}'
                elif self.label == 'ruwiki':
                    names = '\\foreignlanguage{russian}{' + names + '}'
                text += ' & %.1f\\%% & %s & %s \\\\\n' %\
                        (cover, names_translated, names)
                # print(text, end='')
                outfile.write(text)
            text = '\\hline\n'
            # print(text, end='')
            outfile.write(text)

    def print_link_counts(self):
          with io.open(os.path.join('plots', 'outdegrees.txt'), 'a',
                       encoding='utf-8') as outfile:
            text = self.label[:-4]
            print(self.label2language[text] + ' & ' + text + ' & ', end='')
            outfile.write(text)
            data = ['%.2f' % (self.graph_data[graph_name]['outdegree_av'])
                    for graph_name in self.graph_order[1:]]
            text = ' & '.join(data) + '\\\\'
            print(text)
            outfile.write(text + '\n')

    def plot(self, prop):
        fig, ax = plt.subplots(1, figsize=(6, 3))
        bar_vals = [self.graph_data[graph_name][prop]
                    for graph_name in self.graph_order]
        x_vals = range(len(self.graph_order))
        bars = ax.bar(x_vals, bar_vals, align='center')

        # Beautification
        for bidx, bar in enumerate(bars):
            bar.set_fill(False)
            bar.set_hatch(self.hatches[bidx])
            bar.set_edgecolor(self.colors[bidx])

        ax.set_xlim(-0.5, len(self.graph_order) - 0.5)
        ax.set_xticks([x - 0.25 for x in x_vals])
        for tic in ax.xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
        labels = [g for g in self.graph_order]
        ax.set_xticklabels(labels, rotation='-50', ha='left')

        if prop == 'cc':
            ylabel = 'Clustering Coefficient'
            ax.set_ylim(0, 0.5)
        elif prop == 'cp_count':
            ylabel = '# of components'
        else:
            ylabel = 'Share of Nodes (%)'
            ax.set_ylim(0, 110)
        ax.set_ylabel(ylabel)

        plt.tight_layout()
        fpath = os.path.join(self.plot_folder, self.label + '_' + prop)
        for ftype in self.plot_file_types:
            plt.savefig(fpath + ftype)
        plt.close()

    def plot_ecc(self):
        # # plot_ecc_legend
        fig = plt.figure()
        figlegend = plt.figure(figsize=(3, 2))
        ax = fig.add_subplot(111)
        objects = [
            matplotlib.patches.Patch(color='black', hatch='---'),
            matplotlib.patches.Patch(color='black', hatch='//'),
            matplotlib.patches.Patch(color='black', hatch='xxx'),
        ]
        labels = ['First Lead Paragraph', 'Entire Lead', 'Infobox']
        for pidx, patch in enumerate(objects):
            patch.set_fill(False)

        figlegend.legend(objects, labels, ncol=3)
        figlegend.savefig('plots/legend_ecc_full.pdf', bbox_inches='tight')
        cmd = 'pdfcrop --margins 5 ' +\
              'plots/legend_ecc_full.pdf plots/legend_ecc.pdf'
        os.system(cmd)
        print(cmd)

        fig, ax = plt.subplots(1, figsize=(6.25, 2.5))
        vals = [self.graph_data[graph_name]['lc_ecc']
                for graph_name in self.graph_order[1:]]
        for vidx, val, in enumerate(vals):
            val = [100 * v / sum(val) for v in val]
            bars = ax.bar(range(len(val)), val, color=self.colors[vidx], lw=1)

            # Beautification
            for bidx, bar in enumerate(bars):
                bar.set_fill(False)
                bar.set_hatch(self.hatches[vidx])
                bar.set_edgecolor(self.colors[vidx])
        ax.set_xlim(0, 200)
        ax.set_ylim(0, 100)
        ax.set_xlabel('Eccentricity')
        ax.set_ylabel('% of Nodes')
        # plt.title(self.rec_type2label[graph_type])
        plt.tight_layout()
        fpath = os.path.join(self.plot_folder, self.label + '_ecc')
        for ftype in self.plot_file_types:
            plt.savefig(fpath + ftype)
        plt.close()

    def plot_pls(self):
        # # # plot_pls_legend
        # fig = plt.figure()
        # figlegend = plt.figure(figsize=(3, 2))
        # ax = fig.add_subplot(111)
        # objects = [
        #     matplotlib.patches.Patch(color='black', hatch='---'),
        #     matplotlib.patches.Patch(color='black', hatch='//'),
        #     matplotlib.patches.Patch(color='black', hatch='xxx'),
        #     matplotlib.patches.Patch(color='black', hatch=''),
        # ]
        # labels = ['First Links', 'First Lead Paragraph', 'Entire Lead',
        #           'Infobox']
        # for pidx, patch in enumerate(objects):
        #     patch.set_fill(False)
        #
        # figlegend.legend(objects, labels, ncol=3)
        # figlegend.savefig('plots/legend_pls_full.pdf', bbox_inches='tight')
        # cmd = 'pdfcrop --margins 5 ' +\
        #       'plots/legend_pls_full.pdf plots/legend_pls.pdf'
        # os.system(cmd)
        # print(cmd)

        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(6.25, 2.5))
        vals = [self.graph_data[graph_name]['pls']
                for graph_name in self.graph_order[1:]]
        vals_max = [self.graph_data[graph_name]['pls_max']
                    for graph_name in self.graph_order[1:]]
        for vidx, val, in enumerate(vals):
            val = [100 * v / sum(val) for v in val]
            bars = ax.bar(range(len(val)), val, color=self.colors[vidx], lw=1)
            bars2 = ax2.bar([2147483647+vidx], vals_max[vidx],
                            color=self.colors[vidx], lw=1)

            # Beautification
            for bidx, bar in enumerate(bars):
                bar.set_fill(False)
                bar.set_hatch(self.hatches[vidx])
                bar.set_edgecolor(self.colors[vidx])
            for bidx, bar in enumerate(bars2):
                bar.set_fill(False)
                bar.set_hatch(self.hatches[vidx])
                bar.set_edgecolor(self.colors[vidx])

        ax.set_xlim(0, 200)
        ax.set_ylim(0, 100)
        ax.set_xlabel('Path Lengths')
        ax.set_ylabel('% of Nodes')

        ax2.set_xlim(2147483647-10, 2147483647+10)
        ax2.set_ylim(0, 100)

        ax.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        # ax.yaxis.set_visible(False)
        ax2.yaxis.set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax2.xaxis.set_ticks_position('none')
        ax2.xaxis.set_ticks_position('none')
        ax2.set_xticklabels([])
        ax2.set_xlabel('disconnected')

        # via http://matplotlib.org/examples/pylab_examples/broken_axis.html
        # This looks pretty good, and was fairly painless, but you can get that
        # cut-out diagonal lines look with just a bit more work. The important
        # thing to know here is that in axes coordinates, which are always
        # between 0-1, spine endpoints are at these locations (0,0), (0,1),
        # (1,0), and (1,1).  Thus, we just need to put the diagonals in the
        # appropriate corners of each of our axes, and so long as we use the
        # right transform and disable clipping.

        d = .025  # how big to make the diagonal lines in axes coordinates
        # arguments to pass plot, just so we don't keep repeating them
        kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
        ax.plot((1-d, 1+d), (-d, +d), **kwargs)        # right-top diagonal
        ax.plot((1-d, 1+d), (1 - d, 1 + d), **kwargs)  # right-bottom diagonal

        kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
        ax2.plot((-d, +d), (-d, +d), **kwargs)        # left-top diagonal
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # left-bottom diagonal

        # What's cool about this is that now if we vary the distance between
        # ax and ax2 via f.subplots_adjust(hspace=...) or plt.subplot_tool(),
        # the diagonal lines will move accordingly, and stay right at the tips
        # of the spines they are 'breaking'

        plt.tight_layout()
        plt.subplots_adjust(wspace=0.025)
        plt.show()

        fpath = os.path.join(self.plot_folder, self.label + '_pls')
        for ftype in self.plot_file_types:
            plt.savefig(fpath + ftype)
        plt.close()

    def plot_bow_tie(self):
        # TODO FIXME legend plotting doesn't work
        # plot the legend in a separate plot
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # patches = [ax.bar([0], [0]) for i in range(7)]
        # for pidx, p in enumerate(patches):
        #     p[0].set_color(self.colors_set2[pidx])
        #     p[0].set_edgecolor('white')
        #     p[0].set_hatch(self.hatches[pidx % 4])
        # figlegend = plt.figure(figsize=(10.05, 0.475))
        # legend_labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
        # pdb.set_trace()
        # leg = figlegend.legend(patches, legend_labels, ncol=7)
        # leg.get_frame().set_linewidth(0.0)
        # fig.subplots_adjust(left=0.19, bottom=0.06, right=0.91, top=0.92,
        #                     wspace=0.34, hspace=0.32)
        # for ftype in self.plot_file_types:
        #     figlegend.savefig(os.path.join('plots', 'bowtie_legend' + ftype))

        fig, ax = plt.subplots(1, figsize=(6, 3))
        x_vals = [1, 2, 4, 5, 7, 8, 10, 11]
        bar_x = [x - 0.25 for x in x_vals]
        bar_vals = []
        for graph_type in self.graph_order:
            bar_vals += [self.graph_data[graph_type]['bow_tie']]
        bars = []
        labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
        bottom = np.zeros(2 * len(self.graph_order))
        for idx, label in enumerate(labels):
            vals = [v[idx] for v in bar_vals]
            pdb.set_trace()
            p = plt.bar(bar_x, vals, bottom=bottom,
                        edgecolor='white', color=self.colors_set2[idx],
                        align='center')
            bottom += vals
            bars.append(p)
            for bidx, bar in enumerate(p):
                bar.set_hatch(self.hatches[idx % 4])

        # Beautification
        ax.set_ylabel('Component Membership')
        ax.set_xlim(0.25, 3 * len(self.graph_order))
        ax.set_xticks(bar_x)
        labels = [g for k in self.graph_order for g in self.graph_labels[k]]
        ax.set_xticklabels(labels, rotation='-50', ha='left')

        ax.set_ylim(0, 105)

        # plt.legend((p[0] for p in bars), labels, loc='center left',
        #            bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        # fig.subplots_adjust(right=0.73)
        # plt.show()
        fpath = os.path.join(self.plot_folder, self.label + '_' + 'bowtie')
        for ftype in self.plot_file_types:
            plt.savefig(fpath + ftype)
        plt.close()

    def plot_alluvial(self):
        """ produce an alluvial diagram (sort of like a flow chart) for the
        bowtie membership changes over N"""

        np.set_printoptions(precision=3)
        np.set_printoptions(suppress=True)
        graph_order = ['all', 'lead', 'first_p', '1', 'infobox']
        indices = [0, 4, 9, 14, 19]
        ind = u'    '
        labels = ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
        with io.open('plots/alluvial/alluvial.html', encoding='utf-8')\
                as infile:
            template = infile.read().split('"data.js"')
        data_raw = [self.graph_data[g]['bow_tie'] for g in graph_order]
        data = [[] for i in range(20)]
        for i, d in zip(indices, data_raw):
            data[i] = d
        changes = [self.graph_data[g]['bow_tie_changes'] for g in graph_order]
        # pdb.set_trace()
        # changes = [[]] + [c.T for c in changes if c else None]
        changes = [c if c is not None else None for c in changes][:-2] +\
            [[], []]

        # DEBUG
        print(self.label)
        print()
        print(labels)
        for d, c in zip(data_raw, changes):
            print('-----------------------------------------------------------')
            for dd in d:
                print('%.4f, ' % dd, end='')
            print()
            print(c)
            print()
        # /DEBUG

        fname = 'data_' + self.label + '.js'
        with io.open('plots/alluvial/' + fname, 'w', encoding='utf-8')\
                as outfile:
            outfile.write(u'var data = {\n')
            outfile.write(ind + u'"times": [\n')
            for iden, idx in enumerate(indices):
                t = data[idx]
                outfile.write(ind * 2 + u'[\n')
                for jdx, n in enumerate(t):
                    outfile.write(ind * 3 + u'{\n')
                    outfile.write(ind * 4 + u'"nodeName": "Node ' +
                                  unicode(jdx) + u'",\n')
                    nid = unicode(iden * len(labels) + jdx)
                    outfile.write(ind * 4 + u'"id": ' + nid +
                                  u',\n')
                    outfile.write(ind * 4 + u'"nodeValue": ' +
                                  # unicode(int(n * 10000)) + u',\n')
                                  unicode(int(n * 100000)) + u',\n')
                    outfile.write(ind * 4 + u'"nodeLabel": "' +
                                  labels[jdx] + u'"\n')
                    outfile.write(ind * 3 + u'}')
                    if jdx != (len(t) - 1):
                        outfile.write(u',')
                    outfile.write(u'\n')
                outfile.write(ind * 2 + u']')
                if idx != (len(data) - 1):
                    outfile.write(u',')
                outfile.write(u'\n')
            outfile.write(ind + u'],\n')
            outfile.write(ind + u'"links": [\n')

            for cidx, ci in enumerate(changes):
                for mindex, val in np.ndenumerate(ci):
                    outfile.write(ind * 2 + u'{\n')
                    # pdb.set_trace()
                    s = unicode((cidx) * len(labels) + mindex[0])
                    t = unicode((cidx+1) * len(labels) + mindex[1])
                    outfile.write(ind * 3 + u'"source": ' + s +',\n')
                    outfile.write(ind * 3 + u'"target": ' + t + ',\n')
                    outfile.write(ind * 3 + u'"value": ' +
                                  # unicode(val * 500000) + '\n')
                                  unicode(val * 5000000) + '\n')
                    outfile.write(ind * 2 + u'}')
                    if mindex != (len(ci) - 1):
                        outfile.write(u',')
                    outfile.write(u'\n')
            outfile.write(ind + u']\n')
            outfile.write(u'}')
        hfname = 'plots/alluvial/alluvial_' + self.label + '.html'
        with io.open(hfname, 'w', encoding='utf-8') as outfile:
            outfile.write(template[0] + '"' + fname + '"' + template[1])

    def bow_tie_stats(self):
        # ['IN', 'SCC', 'OUT', 'TL_IN', 'TL_OUT', 'TUBE', 'OTHER']
        # for graph_type in self.graph_order:
            # scc_size = self.graph_data[graph_type]['bow_tie'][1]
            # print('       ', graph_type, 'SCC size is %.2f%%' % scc_size)
        val = 100 * self.graph_data['infobox']['recommenders'] / self.graph_data['all']['graph_size']
        print('        Infoboxes present for %.2f%%' % val)

if __name__ == '__main__':
    n_vals = [
        '1',
        # 'first_p',
        # 'lead',
        # 'all',
        # 'infobox',
    ]
    to_plot = [
        'cycles',
        # 'outdegree_av',
        # 'link_counts',
        # 'cp_count',
        # 'cp_size',
        # 'cc',
        # 'recommendations',
        # 'ecc',
        # 'pls',
        # 'bow_tie',
        # 'bow_tie_alluvial',
        'bow_tie_stats',
    ]
    if 'cycles' in to_plot:
        try:
            os.remove(os.path.join('plots', 'cycles.txt'))
        except OSError:
            pass

    for wp in [
        # 'simple',

        'en',
        'de',
        'fr',
        'es',
        'ru',
        'it',
        'ja',
        'nl',
    ]:
        print(wp)
        p = Plotter(wp + 'wiki', to_plot=to_plot)
