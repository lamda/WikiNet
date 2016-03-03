# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import io
import json
import os
import pdb
import random
import requests
import sys
from twisted.internet import reactor, defer, task
from twisted.python import log
from twisted.web import client


class Crawler(object):
    def __init__(self, label, wiki_code, data_dir, dump_date, pids=None,
                 limit=None, recrawl_damaged=False):
        self.wiki_code = wiki_code
        self.dump_date = dump_date
        self.label = label
        self.data_dir = data_dir
        self.html_dir = os.path.join(self.data_dir, 'html')
        if not os.path.exists(self.html_dir):
            os.makedirs(self.html_dir)
        if recrawl_damaged:
            self.pids = []
            with io.open(os.path.join(self.data_dir, 'damaged.txt'),
                         encoding='utf-8') as infile:
                for line in infile:
                    self.pids.append(line.strip())
        else:
            file_ids = set(f[:-4] for f in os.listdir(self.html_dir))
            self.pids = sorted(set(map(unicode, pids)) - file_ids)
            self.pids = random.sample(self.pids, limit) if limit else self.pids
            print(len(pids), 'pids total')
        self.pids = map(unicode, self.pids)
        self.titles = set()
        print(len(self.pids), 'files to download')
        self.no_crawlers = 50
        self.crawl_twisted_ids()

    def crawl_twisted_ids(self):

        def parallel(iterable, count, callable, *args, **kwargs):
            coop = task.Cooperator()
            work = (callable(elem, *args, **kwargs) for elem in iterable)
            return defer.DeferredList(
                [coop.coiterate(work) for i in xrange(count)]
            )

        def download(pid):
            url = 'https://' + self.wiki_code + '.wikipedia.org/' +\
                  'w/api.php?format=json'\
                  '&rvstart=' + self.dump_date + '235959' +\
                  '&prop=revisions|categories&continue' \
                  '&pageids=%s&action=query&rvprop=content&rvparse' \
                  '&cllimit=500&clshow=!hidden&redirects=True'
            print(url % pid)
            path = os.path.join(self.html_dir, pid + '.txt')
            return client.downloadPage(str(url % pid), path)

        print('downloading', len(self.pids), 'files...')
        log.startLogging(Logger(), setStdout=0)
        finished = parallel(self.pids, self.no_crawlers, download)
        finished.addErrback(log.err)
        finished.addCallback(lambda ign: reactor.stop())
        reactor.run()


class Logger(object):
    def __init__(self, counter=0):
        self.counter = counter

    def write(self, text):
        if 'Starting factory' in text:
            pass
        elif 'Stopping factory' in text:
            self.counter += 1
            print(self.counter, end='\r')
        else:
            print(text)

    def flush(self):
        pass
