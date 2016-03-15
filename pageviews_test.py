import requests
import threading
import time
import os
import simplejson as json
import logging
import cPickle as pickle
import pdb
__author__ = 'dimitrovdr'

# see: https://en.wikipedia.org/api/rest_v1/?doc
MEDIAWIKI_API_ENDPOINT = 'https://wikimedia.org/api/rest_v1/' \
                         'metrics/pageviews/per-article/'
EMAIL = 'daniel.lamprecht@gmx.at'

# setup logging
LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
#logging.basicConfig(filename='/tmp/en_wiki_pageviews.log',
#  level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
logging.basicConfig(filename='id2title/pageviews.log',
                    level=logging.ERROR, format=LOGGING_FORMAT, filemode='w')


def read_pickle(fpath):
    with open(fpath, 'rb') as infile:
        obj = pickle.load(infile)
    return obj


def write_pickle(fpath, obj):
    with open(fpath, 'wb') as outfile:
        pickle.dump(obj, outfile, -1)


# Limit the number of threads.
pool = threading.BoundedSemaphore(50)  # can be higher


def worker(u, title, views):
    headers = {'user-agent': EMAIL}
    # Request passed URL.
    r = requests.get(u, headers=headers, stream=True)
    if r.status_code == 200:
        handle_response(r, title, views)
    else:
        logging.error('FAIL: '+title)
        #print title
    pool.release()


def req():
    # files = [f for f in os.listdir('id2title') if f.endswith('.obj')]
    files = [
        # 'jawiki.obj',
        'ruwiki.obj',
        # 'dewiki.obj',
        # 'eswiki.obj',
    ]
    for fname in files:
        if fname.endswith('.obj') and not fname.startswith('pageviews'):
            views = dict()
            print 'working on ' + fname
            logging.error('Working on: ' + fname)
            language = fname[:2]
            id2titles = read_pickle('id2title/' + fname)
            articles= id2titles.values()
            start = time.clock()
            start_time_iteration = start
            l = len(articles)
            for i, article in enumerate(articles):
                # if i > 10:
                #     break
                # print some progress
                if (i % 1000) == 0:
                    print i
                if i % 10000 == 0:
                    #print time for the iteration
                    seconds = time.clock() - start_time_iteration
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    print "Number of crawled articles: %d (%s)." \
                          " Total time for last iteration of 10000 articles:" \
                          " %d:%02d:%02d" % (i, fname, h, m, s)
                    start_time_iteration = time.clock()

                # Thread pool.
                # Blocks other threads (more than the set limit).
                pool.acquire(blocking=True)
                # Create a new thread.
                # Pass each URL (i.e. u parameter) to the worker function.
                t = threading.Thread(
                    target=worker,
                    args=(
                        MEDIAWIKI_API_ENDPOINT + language +
                        '.wikipedia/desktop/user/' + article +
                        '/daily/20160101/20160131',
                        article,
                        views)
                )
                #print "Iteration number: %d of %d" % (i, l)
                # Start the newly create thread.
                t.start()
                t.join()
            pdb.set_trace()
            seconds = time.clock() - start
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)

            write_pickle('id2title/pageviews_' + fname, views)
    print "Total time: %d:%02d:%02d" % (h, m, s)


def handle_response(r, title, views):
    resp =  json.loads(r.text)
    #print resp['items']
    v = 0
    for item in resp['items']:
        v+=item['views']
    views[title]=v
    #print views[title]


if __name__ == '__main__':
    req()

