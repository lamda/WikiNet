# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import io
import json
import numpy as np
import os
import pandas as pd
import pdb
import random
import requests
import shutil
import time
from twisted.internet import reactor, defer, task
from twisted.python import log
from twisted.web import client

from main import debug_iter, url_escape

# set a few options
pd.options.mode.chained_assignment = None
pd.set_option('display.width', 1000)


class Crawler(object):
    def __init__(self, label, wiki_code, data_dir, dump_date, pids=None,
                 limit=None, chunksize=10000, recrawl_damaged=False):
        self.wiki_code = wiki_code
        self.dump_date = dump_date
        self.label = label
        self.data_dir = data_dir
        self.html_dir = os.path.join(self.data_dir, 'html')
        self.html_temp_dir = os.path.join(self.data_dir, 'html', 'temp')
        if not os.path.exists(self.html_temp_dir):
            os.makedirs(self.html_temp_dir)
        self.titles = set()
        self.no_crawlers = 100
        self.chunks = range(0, len(pids), chunksize) + [len(pids)]

        self.file_names = set(f[:-4] for f in os.listdir(self.html_dir)
                              if '.obj' in f)
        self.pids = sorted(set(map(unicode, pids)))
        self.pids = random.sample(self.pids, limit) if limit else self.pids
        print(len(pids), 'pids total')
        self.pids = map(unicode, self.pids)

        if recrawl_damaged:
            reactor.callWhenRunning(self.crawl_missing)
        else:
            reactor.callWhenRunning(self.get_next_chunk)
        reactor.run()

    def parallel(self, iterable, count, callable, *args, **kwargs):
        coop = task.Cooperator()
        work = (callable(elem, *args, **kwargs) for elem in iterable)
        return defer.DeferredList(
            [coop.coiterate(work) for i in xrange(count)]
        )

    def download(self, pid):
        url = 'https://' + self.wiki_code + '.wikipedia.org/' +\
              'w/api.php?format=json'\
              '&rvstart=' + self.dump_date + '235959' +\
              '&prop=revisions|categories&continue' \
              '&pageids=%s&action=query&rvprop=content&rvparse' \
              '&cllimit=500&clshow=!hidden&redirects=True'
        # print(url % pid)
        path = os.path.join(self.html_temp_dir, pid + '.txt')
        return client.downloadPage(str(url % pid), path)

    def get_next_chunk(self, stuff=None):
        start, stop = self.chunks[:2]
        self.chunks = self.chunks[1:]
        if unicode(start) + '-' + unicode(stop) in self.file_names:
            print('    skipping chunk %d - %d...' % (start, stop))
            self.get_next_chunk()
        else:
            print('    crawling chunk %d - %d...' % (start, stop))
            finished = self.parallel(self.pids[start:stop], self.no_crawlers, self.download)
            finished.addErrback(self.handle_error)
            finished.addCallback(self.compress_files, start, stop)
            finished.addCallback(self.get_next_chunk)
            if len(self.chunks) == 1:
                finished.addCallback(lambda ign: reactor.stop())

    def handle_error(self, stuff=None):
        print('Error!')
        pdb.set_trace()

    def compress_files(self, stuff, start, stop):
        file_names = os.listdir(self.html_temp_dir)
        pids, titles, contents, categories, redirect_tos = [], [], [], [], []
        # for file_name in debug_iter(file_names):
        for file_name in file_names:
            # print(file_name)
            fpath = os.path.join(self.html_temp_dir, file_name)
            pid_u = file_name.split('.')[0]
            with io.open(fpath, encoding='utf-8', errors='ignore') as infile:
                try:
                    data = json.load(infile)['query']
                    if 'redirects' in data:
                        title = url_escape(data['redirects'][0]['from'])
                        content = np.NaN
                        category = np.NaN
                        redirects_to = url_escape(data['redirects'][0]['to'])
                    elif 'missing' in data['pages'][pid_u]:
                        continue
                    else:
                        title = url_escape(data['pages'][pid_u]['title'])
                        content = data['pages'][pid_u]['revisions'][0]['*']
                        if 'categories' in data['pages'][pid_u]:
                            category = [
                                c['title'].split(':', 1)[1]
                                for c in data['pages'][pid_u]['categories']
                            ]
                        else:
                            category = np.NaN
                        redirects_to = np.NaN
                    pids.append(int(pid_u))
                    titles.append(title)
                    contents.append(content)
                    categories.append(category)
                    redirect_tos.append(redirects_to)
                except KeyError, e:
                    print('\nKeyError', e)
                    pdb.set_trace()
                except ValueError, e:
                    print('\nValueError', e)
                    pdb.set_trace()
        df = pd.DataFrame(
            data=zip(pids, titles, contents, categories, redirect_tos),
            columns=['pid', 'title', 'content', 'categories', 'redirects_to']
        )
        df.sort_values(by='pid', inplace=True)
        if start is None and stop is None:
            fname = os.path.join(self.html_dir, unicode(self.chunks[-2]) +
                                 '-' + unicode(self.chunks[-1]) + '.obj')
            df_last = pd.read_pickle(fname)
            df_new = pd.concat([df_last, df])
            df_new.to_pickle(fname)
        else:
            fname = unicode(start) + '-' + unicode(stop) + '.obj'
            df.to_pickle(os.path.join(self.html_dir, fname))

        # delete and recreate temp folder
        shutil.rmtree(self.html_temp_dir)
        time.sleep(2)
        os.makedirs(self.html_temp_dir)

    def get_missing_pids(self):
        pids = set()
        for file_name in self.file_names:
            start, stop = file_name.split('.')[0].split('-')
            target_ids = set(self.pids[int(start):int(stop)])
            df = pd.read_pickle(os.path.join(self.html_dir, file_name + '.obj'))
            pids |= (target_ids - {unicode(p) for p in df['pid']})
        return pids

    def crawl_missing(self):
        pids = self.get_missing_pids()
        finished = self.parallel(pids, self.no_crawlers, self.download)
        finished.addErrback(self.handle_error)
        finished.addCallback(self.compress_files, start=None, stop=None)
        finished.addCallback(lambda ign: reactor.stop())


class Logger(object):
    def __init__(self, counter=0):
        self.counter = counter

    def write(self, text):
        if 'Starting factory' in text:
            pass
        elif 'Stopping factory' in text:
            self.counter += 1
            if (self.counter % 100) == 0:
                print(self.counter, end='\r')
        else:
            print(text)

    def flush(self):
        pass

