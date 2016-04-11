# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from main import Wikipedia, Graph

WIKI_CODE = 'it'
DUMP_DATE = '20160203'


if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()

    wp = Wikipedia(WIKI_CODE, DUMP_DATE)
    # wp.get_id_dict()
    # wp.crawl()
    # wp.crawl(recrawl_damaged=True)
    # wp.get_resolved_redirects()
    import os
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '940000-950000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1180000-1190000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '280000-290000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1170000-1180000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1410000-1420000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1040000-1050000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '470000-480000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1720000-1730000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '590000-600000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1310000-1320000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1360000-1370000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '460000-470000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1560000-1570000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '540000-550000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '950000-960000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1240000-1250000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '990000-1000000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1010000-1020000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '70000-80000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '190000-200000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '110000-120000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '410000-420000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1320000-1330000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1130000-1140000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1790000-1800000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1860000-1870000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1760000-1770000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1270000-1280000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '300000-310000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1740000-1750000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '270000-280000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '680000-690000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1200000-1210000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '520000-530000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '560000-570000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '930000-940000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1380000-1390000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1590000-1600000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '310000-320000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '620000-630000.obj'))
    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '780000-790000.obj'))

    # wp.get_link_chunk_all(file_path=os.path.join('data', 'itwiki', 'html', '1120000-1130000.obj'))

    # wp.get_links(link_type='all', start=91, stop=108)
    # wp.get_links(link_type='all', start=108, stop=125)
    # wp.get_links(link_type='all', start=125, stop=142)
    # wp.get_links(link_type='all', start=142, stop=158)
    # wp.get_links(link_type='all', start=158, stop=174)
    # wp.get_links(link_type='all', start=174, stop=None)
    # wp.combine_link_chunks()
    # wp.get_links('divs_tables')
    # wp.correct_bug()
    # wp.cleanup()
    #
    for n_val in [
        1,
        # 'first_p',
        # 'lead',
        # 'infobox',
        # 'all',
    ]:
        print('---------------- N =', n_val, '----------------')
        g = Graph(wiki_code=WIKI_CODE, N=n_val)
        g.load_graph()
        # g.compute_stats()
        g.update_stats()
        # g.print_stats()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

