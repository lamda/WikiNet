# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals
import io
import matplotlib
matplotlib.rc('pdf', fonttype=42)
import matplotlib.pyplot as plt
import os
import pdb
from scipy.stats import pearsonr, spearmanr

from main import Graph
from tools import read_pickle, write_pickle, url_unescape


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
        'infobox',
        'all'
    ]

    wikipedia2edits_articles_depths = {
        'en': (812170986, 5072214, 924.41),
        'de': (156204159, 1905450, 102.5),
        'fr': (125368222, 1721902, 208.46),
        'es': (94262365, 1232123, 197.3),
        'ru': (88544149, 1287687, 134.32),
        'it': (83993233, 1251650, 118.43),
        'ja': (59504158, 1001180, 73.38),
        'nl': (46955102, 1854708, 11.55),
    }
    # fpath = os.path.join('plots', 'stats.txt')
    # with io.open(fpath, 'a', encoding='utf-8') as outfile:
    #     for wp in wikipedias:
    #         a, e = wikipedia2articles_edits[wp]
    #         for n_val in n_vals:
    #             if n_val == n_vals[0]:
    #                 text = '%s & %d & %d & %s & ' % (wp, a, e, n_val.replace('_', '\\_'))
    #             else:
    #                 text = ' & & & %s & ' % (n_val.replace('_', '\\_'))
    #             scc_size = graph2cpsize[wp][n_val]
    #             text += '$%.5f$ & $%.5f$ \\\\' % (scc_size / a, scc_size / e)
    #             print(text)
    #             outfile.write(text + '\n')
    #         outfile.write('\\hline\n')

    for n_val in n_vals:
        print(n_val.replace('_', '\\_') + ' & ', end='')
        for feature, xlabel in [
            ('edits', '# edits'),
            ('articles', '# articles'),
            ('edits_per_article', 'edits per article'),
            # ('depth', 'depth'),
            # ('outdegree_av', 'outdegree (average)'),
            ('outdegree_md', 'outdegree (median)'),
        ]:
            fig, ax = plt.subplots(1, figsize=(6, 3))
            xs, ys = [], []
            for wp in wikipedias:
                stats_file_path = os.path.join('data', wp + 'wiki', 'stats')
                fpath = os.path.join(stats_file_path, 'links_' + n_val + '.obj')
                stats = read_pickle(fpath)
                scc_size = stats['bow_tie'][1]
                edits, articles, depth = wikipedia2edits_articles_depths[wp]
                if feature == 'edits':
                    x_vals = [edits]
                elif feature == 'articles':
                    x_vals = [articles]
                elif feature == 'edits_per_article':
                    x_vals = [edits/articles]
                elif feature == 'depth':
                    x_vals = [depth]
                elif feature == 'outdegree_av':
                    x_vals = [stats['outdegree_av']]
                elif feature == 'outdegree_md':
                    x_vals = [stats['outdegree_median']]
                ax.plot(x_vals, [scc_size], label=wp, ms=5, marker='o')
                ax.annotate('%s' % (wp), xy=(x_vals[0], scc_size), textcoords='data')
                xs.append(x_vals[0])
                ys.append(scc_size)
            # pdb.set_trace()
            # corr = pearsonr(xs, ys)
            corr = spearmanr(xs, ys)
            # print('    pearson corr=%.3f, p=%.3f' % (pn[0], pn[1]))
            # print('    spearman corr=%.3f, p=%.3f' % (sm[0], sm[1]))
            if corr[1] <= 0.05:
                print('$%.2f$' % corr[0], end='')
            else:
                print('-', end='')
            if feature != 'outdegree_md':
                print(' & ', end='')
            else:
                print('\\\\')
            ax.set_ylabel('SCC size')
            ax.set_xlabel(xlabel)
            # plt.legend()
            plt.tight_layout()
            fpath = os.path.join('plots', 'navigability_' + n_val + '_' + feature)
            for ftype in ['.png']:
                plt.savefig(fpath + ftype)
            plt.close()


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


def plot_recommendation_results():
    wikipedia_color = [
        # 'simple',

        # ('en', (0.4, 0.7607843137254902, 0.6470588235294118)),
        # ('de', (0.9882352941176471, 0.5529411764705883, 0.3843137254901961)),
        ('en', 'red'),
        ('de', 'blue'),
        # 'fr',
        # 'es',
        # 'ru',
        # 'it',
        # 'ja',
        # 'nl',
    ]
    wp2vc_sum = {
        'it': 282703316,
        'de': 684947734,
        'fr': 490725667,
        'es': 507420831,
        'ja': 579254856,
        'nl': 113945934,
        'ru': 710613125,
        'en': 4804651317,
    }
    for metric, label in [
        ('scc_size', 'SCC Size in %'),
        ('vc_scc', 'Sum of View Counts in %')
    ]:
        fig, ax = plt.subplots(1, figsize=(6, 3))
        for wp, color in wikipedia_color:
            stats_file_path = os.path.join('data', wp + 'wiki', 'stats')
            fpath = os.path.join(stats_file_path, 'links_' + 'first_p' + '.obj')
            stats = read_pickle(fpath)
            if metric == 'scc_size':
                d = stats['graph_size']
            elif metric == 'vc_scc':
                d = wp2vc_sum[wp]
            vals_scc_based = [100*v/d for v in stats['recs_scc_based_' + metric]]
            vals_vc_based = [100*v/d for v in stats['recs_vc_based_' + metric]]
            x_vals = range(len(vals_scc_based))
            ax.plot(x_vals, vals_scc_based, label=wp + ' (SCC-based)', color=color, ls='solid', lw=2)
            ax.plot(x_vals, vals_vc_based, label=wp + ' (VC-based)', color=color, ls='dashed', lw=2)

        ylabel = label
        ax.set_xlabel('# recommendations added')
        ax.set_ylabel(ylabel)
        # ax.set_ylim(0, 101)
        # plt.legend()

        plt.tight_layout()
        fpath = os.path.join('plots', 'recs_' + metric)
        for ftype in ['.pdf']:
            plt.savefig(fpath + ftype)
        plt.close()


def plot_legend():
    color2label = {
        # (0.4, 0.7607843137254902, 0.6470588235294118): 'English',
        # (0.9882352941176471, 0.5529411764705883, 0.3843137254901961): 'German'
        'red': 'English',
        'blue': 'German',
    }
    linestyle2label = {
        'solid': 'SCC-based',
        'dashed': 'VC-based',
    }

    figData = plt.figure()
    ax = figData.add_subplot(111)
    for c in color2label:
        for ls in linestyle2label:
            label = color2label[c] + ' (' + linestyle2label[ls] + ')'
            plt.plot([0, 1], [2, 3], color=c, linestyle=ls, label=label)
    figlegend = plt.figure(figsize=(11.85, 0.55))
    figlegend.legend(*ax.get_legend_handles_labels(), loc='upper left', ncol=4)
    figlegend.show()
    figlegend.savefig(os.path.join('plots', 'recs_legend.pdf'))


if __name__ == '__main__':
    # get_navigability_stats()
    # get_view_count_stats()
    # plot_recommendation_results()
    plot_legend()

