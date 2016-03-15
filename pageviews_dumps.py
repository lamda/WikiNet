# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import collections
import cPickle as pickle
import gzip
import hashlib
import os
import pdb
import re
import sys
import urllib2


file_names_raw = """
pagecounts-20160101-000000.gz, size 66M
pagecounts-20160101-010000.gz, size 77M
pagecounts-20160101-020000.gz, size 72M
pagecounts-20160101-030000.gz, size 71M
pagecounts-20160101-040000.gz, size 69M
pagecounts-20160101-050000.gz, size 68M
pagecounts-20160101-060000.gz, size 69M
pagecounts-20160101-070000.gz, size 71M
pagecounts-20160101-080000.gz, size 73M
pagecounts-20160101-090000.gz, size 77M
pagecounts-20160101-100000.gz, size 83M
pagecounts-20160101-110000.gz, size 85M
pagecounts-20160101-120000.gz, size 85M
pagecounts-20160101-130000.gz, size 86M
pagecounts-20160101-140000.gz, size 84M
pagecounts-20160101-150000.gz, size 86M
pagecounts-20160101-160000.gz, size 89M
pagecounts-20160101-170000.gz, size 89M
pagecounts-20160101-180000.gz, size 93M
pagecounts-20160101-190000.gz, size 95M
pagecounts-20160101-200000.gz, size 92M
pagecounts-20160101-210000.gz, size 91M
pagecounts-20160101-220000.gz, size 92M
pagecounts-20160101-230000.gz, size 83M
pagecounts-20160102-000000.gz, size 81M
pagecounts-20160102-010000.gz, size 83M
pagecounts-20160102-020000.gz, size 76M
pagecounts-20160102-030000.gz, size 76M
pagecounts-20160102-040000.gz, size 75M
pagecounts-20160102-050000.gz, size 73M
pagecounts-20160102-060000.gz, size 72M
pagecounts-20160102-070000.gz, size 71M
pagecounts-20160102-080000.gz, size 75M
pagecounts-20160102-090000.gz, size 79M
pagecounts-20160102-100000.gz, size 84M
pagecounts-20160102-110000.gz, size 90M
pagecounts-20160102-120000.gz, size 90M
pagecounts-20160102-130000.gz, size 92M
pagecounts-20160102-140000.gz, size 95M
pagecounts-20160102-150000.gz, size 93M
pagecounts-20160102-160000.gz, size 94M
pagecounts-20160102-170000.gz, size 96M
pagecounts-20160102-180000.gz, size 95M
pagecounts-20160102-190000.gz, size 92M
pagecounts-20160102-200000.gz, size 92M
pagecounts-20160102-210000.gz, size 89M
pagecounts-20160102-220000.gz, size 87M
pagecounts-20160102-230000.gz, size 86M
pagecounts-20160103-000000.gz, size 82M
pagecounts-20160103-010000.gz, size 85M
pagecounts-20160103-020000.gz, size 80M
pagecounts-20160103-030000.gz, size 76M
pagecounts-20160103-040000.gz, size 75M
pagecounts-20160103-050000.gz, size 75M
pagecounts-20160103-060000.gz, size 77M
pagecounts-20160103-070000.gz, size 76M
pagecounts-20160103-080000.gz, size 80M
pagecounts-20160103-090000.gz, size 82M
pagecounts-20160103-100000.gz, size 88M
pagecounts-20160103-110000.gz, size 90M
pagecounts-20160103-120000.gz, size 92M
pagecounts-20160103-130000.gz, size 94M
pagecounts-20160103-140000.gz, size 94M
pagecounts-20160103-150000.gz, size 95M
pagecounts-20160103-160000.gz, size 93M
pagecounts-20160103-170000.gz, size 93M
pagecounts-20160103-180000.gz, size 94M
pagecounts-20160103-190000.gz, size 92M
pagecounts-20160103-200000.gz, size 91M
pagecounts-20160103-210000.gz, size 90M
pagecounts-20160103-220000.gz, size 90M
pagecounts-20160103-230000.gz, size 86M
pagecounts-20160104-000000.gz, size 80M
pagecounts-20160104-010000.gz, size 83M
pagecounts-20160104-020000.gz, size 83M
pagecounts-20160104-030000.gz, size 81M
pagecounts-20160104-040000.gz, size 79M
pagecounts-20160104-050000.gz, size 79M
pagecounts-20160104-060000.gz, size 79M
pagecounts-20160104-070000.gz, size 81M
pagecounts-20160104-080000.gz, size 84M
pagecounts-20160104-090000.gz, size 89M
pagecounts-20160104-100000.gz, size 94M
pagecounts-20160104-110000.gz, size 96M
pagecounts-20160104-120000.gz, size 92M
pagecounts-20160104-130000.gz, size 93M
pagecounts-20160104-140000.gz, size 98M
pagecounts-20160104-150000.gz, size 101M
pagecounts-20160104-160000.gz, size 102M
pagecounts-20160104-170000.gz, size 98M
pagecounts-20160104-180000.gz, size 98M
pagecounts-20160104-190000.gz, size 98M
pagecounts-20160104-200000.gz, size 96M
pagecounts-20160104-210000.gz, size 96M
pagecounts-20160104-220000.gz, size 96M
pagecounts-20160104-230000.gz, size 93M
pagecounts-20160105-000000.gz, size 88M
pagecounts-20160105-010000.gz, size 90M
pagecounts-20160105-020000.gz, size 84M
pagecounts-20160105-030000.gz, size 81M
pagecounts-20160105-040000.gz, size 81M
pagecounts-20160105-050000.gz, size 82M
pagecounts-20160105-060000.gz, size 85M
pagecounts-20160105-070000.gz, size 85M
pagecounts-20160105-080000.gz, size 90M
pagecounts-20160105-090000.gz, size 100M
pagecounts-20160105-100000.gz, size 103M
pagecounts-20160105-110000.gz, size 105M
pagecounts-20160105-120000.gz, size 105M
pagecounts-20160105-130000.gz, size 104M
pagecounts-20160105-140000.gz, size 106M
pagecounts-20160105-150000.gz, size 107M
pagecounts-20160105-160000.gz, size 106M
pagecounts-20160105-170000.gz, size 106M
pagecounts-20160105-180000.gz, size 105M
pagecounts-20160105-190000.gz, size 110M
pagecounts-20160105-200000.gz, size 112M
pagecounts-20160105-210000.gz, size 107M
pagecounts-20160105-220000.gz, size 110M
pagecounts-20160105-230000.gz, size 112M
pagecounts-20160106-000000.gz, size 102M
pagecounts-20160106-010000.gz, size 102M
pagecounts-20160106-020000.gz, size 93M
pagecounts-20160106-030000.gz, size 88M
pagecounts-20160106-040000.gz, size 87M
pagecounts-20160106-050000.gz, size 84M
pagecounts-20160106-060000.gz, size 90M
pagecounts-20160106-070000.gz, size 94M
pagecounts-20160106-080000.gz, size 99M
pagecounts-20160106-090000.gz, size 102M
pagecounts-20160106-100000.gz, size 104M
pagecounts-20160106-110000.gz, size 105M
pagecounts-20160106-120000.gz, size 104M
pagecounts-20160106-130000.gz, size 101M
pagecounts-20160106-140000.gz, size 104M
pagecounts-20160106-150000.gz, size 104M
pagecounts-20160106-160000.gz, size 103M
pagecounts-20160106-170000.gz, size 101M
pagecounts-20160106-180000.gz, size 101M
pagecounts-20160106-190000.gz, size 107M
pagecounts-20160106-200000.gz, size 105M
pagecounts-20160106-210000.gz, size 101M
pagecounts-20160106-220000.gz, size 103M
pagecounts-20160106-230000.gz, size 101M
pagecounts-20160107-000000.gz, size 92M
pagecounts-20160107-010000.gz, size 92M
pagecounts-20160107-020000.gz, size 90M
pagecounts-20160107-030000.gz, size 86M
pagecounts-20160107-040000.gz, size 85M
pagecounts-20160107-050000.gz, size 83M
pagecounts-20160107-060000.gz, size 83M
pagecounts-20160107-070000.gz, size 83M
pagecounts-20160107-080000.gz, size 90M
pagecounts-20160107-090000.gz, size 96M
pagecounts-20160107-100000.gz, size 99M
pagecounts-20160107-110000.gz, size 104M
pagecounts-20160107-120000.gz, size 103M
pagecounts-20160107-130000.gz, size 103M
pagecounts-20160107-140000.gz, size 104M
pagecounts-20160107-150000.gz, size 105M
pagecounts-20160107-160000.gz, size 108M
pagecounts-20160107-170000.gz, size 107M
pagecounts-20160107-180000.gz, size 106M
pagecounts-20160107-190000.gz, size 108M
pagecounts-20160107-200000.gz, size 106M
pagecounts-20160107-210000.gz, size 101M
pagecounts-20160107-220000.gz, size 104M
pagecounts-20160107-230000.gz, size 97M
pagecounts-20160108-000000.gz, size 91M
pagecounts-20160108-010000.gz, size 96M
pagecounts-20160108-020000.gz, size 90M
pagecounts-20160108-030000.gz, size 86M
pagecounts-20160108-040000.gz, size 86M
pagecounts-20160108-050000.gz, size 85M
pagecounts-20160108-060000.gz, size 89M
pagecounts-20160108-070000.gz, size 89M
pagecounts-20160108-080000.gz, size 96M
pagecounts-20160108-090000.gz, size 99M
pagecounts-20160108-100000.gz, size 100M
pagecounts-20160108-110000.gz, size 98M
pagecounts-20160108-120000.gz, size 97M
pagecounts-20160108-130000.gz, size 96M
pagecounts-20160108-140000.gz, size 100M
pagecounts-20160108-150000.gz, size 104M
pagecounts-20160108-160000.gz, size 103M
pagecounts-20160108-170000.gz, size 106M
pagecounts-20160108-180000.gz, size 103M
pagecounts-20160108-190000.gz, size 103M
pagecounts-20160108-200000.gz, size 102M
pagecounts-20160108-210000.gz, size 97M
pagecounts-20160108-220000.gz, size 95M
pagecounts-20160108-230000.gz, size 96M
pagecounts-20160109-000000.gz, size 89M
pagecounts-20160109-010000.gz, size 92M
pagecounts-20160109-020000.gz, size 86M
pagecounts-20160109-030000.gz, size 79M
pagecounts-20160109-040000.gz, size 75M
pagecounts-20160109-050000.gz, size 77M
pagecounts-20160109-060000.gz, size 75M
pagecounts-20160109-070000.gz, size 77M
pagecounts-20160109-080000.gz, size 79M
pagecounts-20160109-090000.gz, size 86M
pagecounts-20160109-100000.gz, size 92M
pagecounts-20160109-110000.gz, size 96M
pagecounts-20160109-120000.gz, size 98M
pagecounts-20160109-130000.gz, size 94M
pagecounts-20160109-140000.gz, size 96M
pagecounts-20160109-150000.gz, size 96M
pagecounts-20160109-160000.gz, size 98M
pagecounts-20160109-170000.gz, size 98M
pagecounts-20160109-180000.gz, size 99M
pagecounts-20160109-190000.gz, size 98M
pagecounts-20160109-200000.gz, size 98M
pagecounts-20160109-210000.gz, size 95M
pagecounts-20160109-220000.gz, size 93M
pagecounts-20160109-230000.gz, size 91M
pagecounts-20160110-000000.gz, size 87M
pagecounts-20160110-010000.gz, size 86M
pagecounts-20160110-020000.gz, size 84M
pagecounts-20160110-030000.gz, size 79M
pagecounts-20160110-040000.gz, size 78M
pagecounts-20160110-050000.gz, size 78M
pagecounts-20160110-060000.gz, size 76M
pagecounts-20160110-070000.gz, size 81M
pagecounts-20160110-080000.gz, size 82M
pagecounts-20160110-090000.gz, size 85M
pagecounts-20160110-100000.gz, size 91M
pagecounts-20160110-110000.gz, size 93M
pagecounts-20160110-120000.gz, size 93M
pagecounts-20160110-130000.gz, size 92M
pagecounts-20160110-140000.gz, size 93M
pagecounts-20160110-150000.gz, size 96M
pagecounts-20160110-160000.gz, size 98M
pagecounts-20160110-170000.gz, size 97M
pagecounts-20160110-180000.gz, size 97M
pagecounts-20160110-190000.gz, size 99M
pagecounts-20160110-200000.gz, size 99M
pagecounts-20160110-210000.gz, size 93M
pagecounts-20160110-220000.gz, size 91M
pagecounts-20160110-230000.gz, size 90M
pagecounts-20160111-000000.gz, size 82M
pagecounts-20160111-010000.gz, size 83M
pagecounts-20160111-020000.gz, size 79M
pagecounts-20160111-030000.gz, size 80M
pagecounts-20160111-040000.gz, size 82M
pagecounts-20160111-050000.gz, size 83M
pagecounts-20160111-060000.gz, size 82M
pagecounts-20160111-070000.gz, size 86M
pagecounts-20160111-080000.gz, size 90M
pagecounts-20160111-090000.gz, size 95M
pagecounts-20160111-100000.gz, size 102M
pagecounts-20160111-110000.gz, size 96M
pagecounts-20160111-120000.gz, size 100M
pagecounts-20160111-130000.gz, size 98M
pagecounts-20160111-140000.gz, size 101M
pagecounts-20160111-150000.gz, size 102M
pagecounts-20160111-160000.gz, size 102M
pagecounts-20160111-170000.gz, size 101M
pagecounts-20160111-180000.gz, size 99M
pagecounts-20160111-190000.gz, size 99M
pagecounts-20160111-200000.gz, size 98M
pagecounts-20160111-210000.gz, size 99M
pagecounts-20160111-220000.gz, size 95M
pagecounts-20160111-230000.gz, size 91M
pagecounts-20160112-000000.gz, size 91M
pagecounts-20160112-010000.gz, size 91M
pagecounts-20160112-020000.gz, size 84M
pagecounts-20160112-030000.gz, size 80M
pagecounts-20160112-040000.gz, size 81M
pagecounts-20160112-050000.gz, size 82M
pagecounts-20160112-060000.gz, size 81M
pagecounts-20160112-070000.gz, size 83M
pagecounts-20160112-080000.gz, size 90M
pagecounts-20160112-090000.gz, size 93M
pagecounts-20160112-100000.gz, size 96M
pagecounts-20160112-110000.gz, size 99M
pagecounts-20160112-120000.gz, size 97M
pagecounts-20160112-130000.gz, size 95M
pagecounts-20160112-140000.gz, size 96M
pagecounts-20160112-150000.gz, size 101M
pagecounts-20160112-160000.gz, size 99M
pagecounts-20160112-170000.gz, size 97M
pagecounts-20160112-180000.gz, size 99M
pagecounts-20160112-190000.gz, size 97M
pagecounts-20160112-200000.gz, size 98M
pagecounts-20160112-210000.gz, size 95M
pagecounts-20160112-220000.gz, size 97M
pagecounts-20160112-230000.gz, size 90M
pagecounts-20160113-000000.gz, size 84M
pagecounts-20160113-010000.gz, size 86M
pagecounts-20160113-020000.gz, size 85M
pagecounts-20160113-030000.gz, size 84M
pagecounts-20160113-040000.gz, size 81M
pagecounts-20160113-050000.gz, size 80M
pagecounts-20160113-060000.gz, size 71M
pagecounts-20160113-070000.gz, size 77M
pagecounts-20160113-080000.gz, size 81M
pagecounts-20160113-090000.gz, size 85M
pagecounts-20160113-100000.gz, size 90M
pagecounts-20160113-110000.gz, size 92M
pagecounts-20160113-120000.gz, size 91M
pagecounts-20160113-130000.gz, size 92M
pagecounts-20160113-140000.gz, size 100M
pagecounts-20160113-150000.gz, size 103M
pagecounts-20160113-160000.gz, size 103M
pagecounts-20160113-170000.gz, size 101M
pagecounts-20160113-180000.gz, size 101M
pagecounts-20160113-190000.gz, size 101M
pagecounts-20160113-200000.gz, size 99M
pagecounts-20160113-210000.gz, size 98M
pagecounts-20160113-220000.gz, size 97M
pagecounts-20160113-230000.gz, size 93M
pagecounts-20160114-000000.gz, size 83M
pagecounts-20160114-010000.gz, size 87M
pagecounts-20160114-020000.gz, size 85M
pagecounts-20160114-030000.gz, size 79M
pagecounts-20160114-040000.gz, size 80M
pagecounts-20160114-050000.gz, size 82M
pagecounts-20160114-060000.gz, size 86M
pagecounts-20160114-070000.gz, size 85M
pagecounts-20160114-080000.gz, size 92M
pagecounts-20160114-090000.gz, size 96M
pagecounts-20160114-100000.gz, size 100M
pagecounts-20160114-110000.gz, size 101M
pagecounts-20160114-120000.gz, size 100M
pagecounts-20160114-130000.gz, size 97M
pagecounts-20160114-140000.gz, size 102M
pagecounts-20160114-150000.gz, size 103M
pagecounts-20160114-160000.gz, size 100M
pagecounts-20160114-170000.gz, size 100M
pagecounts-20160114-180000.gz, size 101M
pagecounts-20160114-190000.gz, size 102M
pagecounts-20160114-200000.gz, size 102M
pagecounts-20160114-210000.gz, size 102M
pagecounts-20160114-220000.gz, size 98M
pagecounts-20160114-230000.gz, size 92M
pagecounts-20160115-000000.gz, size 86M
pagecounts-20160115-010000.gz, size 88M
pagecounts-20160115-020000.gz, size 86M
pagecounts-20160115-030000.gz, size 82M
pagecounts-20160115-040000.gz, size 81M
pagecounts-20160115-050000.gz, size 80M
pagecounts-20160115-060000.gz, size 80M
pagecounts-20160115-070000.gz, size 80M
pagecounts-20160115-080000.gz, size 88M
pagecounts-20160115-090000.gz, size 93M
pagecounts-20160115-100000.gz, size 94M
pagecounts-20160115-110000.gz, size 92M
pagecounts-20160115-120000.gz, size 92M
pagecounts-20160115-130000.gz, size 90M
pagecounts-20160115-140000.gz, size 94M
pagecounts-20160115-150000.gz, size 99M
pagecounts-20160115-160000.gz, size 99M
pagecounts-20160115-170000.gz, size 98M
pagecounts-20160115-180000.gz, size 95M
pagecounts-20160115-190000.gz, size 95M
pagecounts-20160115-200000.gz, size 95M
pagecounts-20160115-210000.gz, size 92M
pagecounts-20160115-220000.gz, size 89M
pagecounts-20160115-230000.gz, size 88M
pagecounts-20160116-000000.gz, size 79M
pagecounts-20160116-010000.gz, size 79M
pagecounts-20160116-020000.gz, size 77M
pagecounts-20160116-030000.gz, size 75M
pagecounts-20160116-040000.gz, size 77M
pagecounts-20160116-050000.gz, size 79M
pagecounts-20160116-060000.gz, size 81M
pagecounts-20160116-070000.gz, size 82M
pagecounts-20160116-080000.gz, size 82M
pagecounts-20160116-090000.gz, size 84M
pagecounts-20160116-100000.gz, size 90M
pagecounts-20160116-110000.gz, size 91M
pagecounts-20160116-120000.gz, size 89M
pagecounts-20160116-130000.gz, size 89M
pagecounts-20160116-140000.gz, size 92M
pagecounts-20160116-150000.gz, size 93M
pagecounts-20160116-160000.gz, size 95M
pagecounts-20160116-170000.gz, size 92M
pagecounts-20160116-180000.gz, size 94M
pagecounts-20160116-190000.gz, size 92M
pagecounts-20160116-200000.gz, size 89M
pagecounts-20160116-210000.gz, size 90M
pagecounts-20160116-220000.gz, size 89M
pagecounts-20160116-230000.gz, size 89M
pagecounts-20160117-000000.gz, size 83M
pagecounts-20160117-010000.gz, size 83M
pagecounts-20160117-020000.gz, size 81M
pagecounts-20160117-030000.gz, size 77M
pagecounts-20160117-040000.gz, size 74M
pagecounts-20160117-050000.gz, size 77M
pagecounts-20160117-060000.gz, size 76M
pagecounts-20160117-070000.gz, size 78M
pagecounts-20160117-080000.gz, size 83M
pagecounts-20160117-090000.gz, size 88M
pagecounts-20160117-100000.gz, size 91M
pagecounts-20160117-110000.gz, size 94M
pagecounts-20160117-120000.gz, size 93M
pagecounts-20160117-130000.gz, size 89M
pagecounts-20160117-140000.gz, size 95M
pagecounts-20160117-150000.gz, size 100M
pagecounts-20160117-160000.gz, size 99M
pagecounts-20160117-170000.gz, size 94M
pagecounts-20160117-180000.gz, size 95M
pagecounts-20160117-190000.gz, size 91M
pagecounts-20160117-200000.gz, size 91M
pagecounts-20160117-210000.gz, size 88M
pagecounts-20160117-220000.gz, size 86M
pagecounts-20160117-230000.gz, size 86M
pagecounts-20160118-000000.gz, size 85M
pagecounts-20160118-010000.gz, size 88M
pagecounts-20160118-020000.gz, size 85M
pagecounts-20160118-030000.gz, size 81M
pagecounts-20160118-040000.gz, size 83M
pagecounts-20160118-050000.gz, size 83M
pagecounts-20160118-060000.gz, size 84M
pagecounts-20160118-070000.gz, size 83M
pagecounts-20160118-080000.gz, size 89M
pagecounts-20160118-090000.gz, size 96M
pagecounts-20160118-100000.gz, size 101M
pagecounts-20160118-110000.gz, size 100M
pagecounts-20160118-120000.gz, size 98M
pagecounts-20160118-130000.gz, size 95M
pagecounts-20160118-140000.gz, size 100M
pagecounts-20160118-150000.gz, size 104M
pagecounts-20160118-160000.gz, size 104M
pagecounts-20160118-170000.gz, size 103M
pagecounts-20160118-180000.gz, size 103M
pagecounts-20160118-190000.gz, size 102M
pagecounts-20160118-200000.gz, size 99M
pagecounts-20160118-210000.gz, size 98M
pagecounts-20160118-220000.gz, size 96M
pagecounts-20160118-230000.gz, size 90M
pagecounts-20160119-000000.gz, size 88M
pagecounts-20160119-010000.gz, size 89M
pagecounts-20160119-020000.gz, size 86M
pagecounts-20160119-030000.gz, size 81M
pagecounts-20160119-040000.gz, size 80M
pagecounts-20160119-050000.gz, size 81M
pagecounts-20160119-060000.gz, size 85M
pagecounts-20160119-070000.gz, size 87M
pagecounts-20160119-080000.gz, size 94M
pagecounts-20160119-090000.gz, size 97M
pagecounts-20160119-100000.gz, size 102M
pagecounts-20160119-110000.gz, size 100M
pagecounts-20160119-120000.gz, size 98M
pagecounts-20160119-130000.gz, size 97M
pagecounts-20160119-140000.gz, size 101M
pagecounts-20160119-150000.gz, size 102M
pagecounts-20160119-160000.gz, size 101M
pagecounts-20160119-170000.gz, size 97M
pagecounts-20160119-180000.gz, size 95M
pagecounts-20160119-190000.gz, size 95M
pagecounts-20160119-200000.gz, size 95M
pagecounts-20160119-210000.gz, size 96M
pagecounts-20160119-220000.gz, size 93M
pagecounts-20160119-230000.gz, size 89M
pagecounts-20160120-000000.gz, size 82M
pagecounts-20160120-010000.gz, size 84M
pagecounts-20160120-020000.gz, size 83M
pagecounts-20160120-030000.gz, size 79M
pagecounts-20160120-040000.gz, size 77M
pagecounts-20160120-050000.gz, size 76M
pagecounts-20160120-060000.gz, size 81M
pagecounts-20160120-070000.gz, size 83M
pagecounts-20160120-080000.gz, size 88M
pagecounts-20160120-090000.gz, size 97M
pagecounts-20160120-100000.gz, size 100M
pagecounts-20160120-110000.gz, size 103M
pagecounts-20160120-120000.gz, size 100M
pagecounts-20160120-130000.gz, size 96M
pagecounts-20160120-140000.gz, size 97M
pagecounts-20160120-150000.gz, size 100M
pagecounts-20160120-160000.gz, size 101M
pagecounts-20160120-170000.gz, size 102M
pagecounts-20160120-180000.gz, size 98M
pagecounts-20160120-190000.gz, size 97M
pagecounts-20160120-200000.gz, size 96M
pagecounts-20160120-210000.gz, size 94M
pagecounts-20160120-220000.gz, size 90M
pagecounts-20160120-230000.gz, size 84M
pagecounts-20160121-000000.gz, size 81M
pagecounts-20160121-010000.gz, size 88M
pagecounts-20160121-020000.gz, size 83M
pagecounts-20160121-030000.gz, size 82M
pagecounts-20160121-040000.gz, size 83M
pagecounts-20160121-050000.gz, size 81M
pagecounts-20160121-060000.gz, size 82M
pagecounts-20160121-070000.gz, size 86M
pagecounts-20160121-080000.gz, size 90M
pagecounts-20160121-090000.gz, size 95M
pagecounts-20160121-100000.gz, size 98M
pagecounts-20160121-110000.gz, size 101M
pagecounts-20160121-120000.gz, size 99M
pagecounts-20160121-130000.gz, size 95M
pagecounts-20160121-140000.gz, size 98M
pagecounts-20160121-150000.gz, size 99M
pagecounts-20160121-160000.gz, size 99M
pagecounts-20160121-170000.gz, size 98M
pagecounts-20160121-180000.gz, size 97M
pagecounts-20160121-190000.gz, size 95M
pagecounts-20160121-200000.gz, size 92M
pagecounts-20160121-210000.gz, size 92M
pagecounts-20160121-220000.gz, size 95M
pagecounts-20160121-230000.gz, size 91M
pagecounts-20160122-000000.gz, size 88M
pagecounts-20160122-010000.gz, size 95M
pagecounts-20160122-020000.gz, size 89M
pagecounts-20160122-030000.gz, size 87M
pagecounts-20160122-040000.gz, size 84M
pagecounts-20160122-050000.gz, size 82M
pagecounts-20160122-060000.gz, size 84M
pagecounts-20160122-070000.gz, size 85M
pagecounts-20160122-080000.gz, size 90M
pagecounts-20160122-090000.gz, size 92M
pagecounts-20160122-100000.gz, size 99M
pagecounts-20160122-110000.gz, size 99M
pagecounts-20160122-120000.gz, size 98M
pagecounts-20160122-130000.gz, size 92M
pagecounts-20160122-140000.gz, size 97M
pagecounts-20160122-150000.gz, size 100M
pagecounts-20160122-160000.gz, size 97M
pagecounts-20160122-170000.gz, size 95M
pagecounts-20160122-180000.gz, size 94M
pagecounts-20160122-190000.gz, size 93M
pagecounts-20160122-200000.gz, size 89M
pagecounts-20160122-210000.gz, size 86M
pagecounts-20160122-220000.gz, size 82M
pagecounts-20160122-230000.gz, size 82M
pagecounts-20160123-000000.gz, size 78M
pagecounts-20160123-010000.gz, size 83M
pagecounts-20160123-020000.gz, size 84M
pagecounts-20160123-030000.gz, size 79M
pagecounts-20160123-040000.gz, size 81M
pagecounts-20160123-050000.gz, size 83M
pagecounts-20160123-060000.gz, size 83M
pagecounts-20160123-070000.gz, size 82M
pagecounts-20160123-080000.gz, size 86M
pagecounts-20160123-090000.gz, size 89M
pagecounts-20160123-100000.gz, size 93M
pagecounts-20160123-110000.gz, size 93M
pagecounts-20160123-120000.gz, size 94M
pagecounts-20160123-130000.gz, size 93M
pagecounts-20160123-140000.gz, size 95M
pagecounts-20160123-150000.gz, size 95M
pagecounts-20160123-160000.gz, size 96M
pagecounts-20160123-170000.gz, size 99M
pagecounts-20160123-180000.gz, size 100M
pagecounts-20160123-190000.gz, size 97M
pagecounts-20160123-200000.gz, size 95M
pagecounts-20160123-210000.gz, size 92M
pagecounts-20160123-220000.gz, size 92M
pagecounts-20160123-230000.gz, size 91M
pagecounts-20160124-000000.gz, size 85M
pagecounts-20160124-010000.gz, size 91M
pagecounts-20160124-020000.gz, size 83M
pagecounts-20160124-030000.gz, size 82M
pagecounts-20160124-040000.gz, size 81M
pagecounts-20160124-050000.gz, size 86M
pagecounts-20160124-060000.gz, size 85M
pagecounts-20160124-070000.gz, size 85M
pagecounts-20160124-080000.gz, size 86M
pagecounts-20160124-090000.gz, size 89M
pagecounts-20160124-100000.gz, size 96M
pagecounts-20160124-110000.gz, size 96M
pagecounts-20160124-120000.gz, size 96M
pagecounts-20160124-130000.gz, size 93M
pagecounts-20160124-140000.gz, size 98M
pagecounts-20160124-150000.gz, size 99M
pagecounts-20160124-160000.gz, size 98M
pagecounts-20160124-170000.gz, size 96M
pagecounts-20160124-180000.gz, size 94M
pagecounts-20160124-190000.gz, size 96M
pagecounts-20160124-200000.gz, size 96M
pagecounts-20160124-210000.gz, size 93M
pagecounts-20160124-220000.gz, size 90M
pagecounts-20160124-230000.gz, size 87M
pagecounts-20160125-000000.gz, size 82M
pagecounts-20160125-010000.gz, size 85M
pagecounts-20160125-020000.gz, size 83M
pagecounts-20160125-030000.gz, size 79M
pagecounts-20160125-040000.gz, size 74M
pagecounts-20160125-050000.gz, size 73M
pagecounts-20160125-060000.gz, size 75M
pagecounts-20160125-070000.gz, size 82M
pagecounts-20160125-080000.gz, size 89M
pagecounts-20160125-090000.gz, size 94M
pagecounts-20160125-100000.gz, size 99M
pagecounts-20160125-110000.gz, size 97M
pagecounts-20160125-120000.gz, size 99M
pagecounts-20160125-130000.gz, size 96M
pagecounts-20160125-140000.gz, size 101M
pagecounts-20160125-150000.gz, size 103M
pagecounts-20160125-160000.gz, size 104M
pagecounts-20160125-170000.gz, size 102M
pagecounts-20160125-180000.gz, size 100M
pagecounts-20160125-190000.gz, size 97M
pagecounts-20160125-200000.gz, size 97M
pagecounts-20160125-210000.gz, size 97M
pagecounts-20160125-220000.gz, size 93M
pagecounts-20160125-230000.gz, size 89M
pagecounts-20160126-000000.gz, size 85M
pagecounts-20160126-010000.gz, size 88M
pagecounts-20160126-020000.gz, size 86M
pagecounts-20160126-030000.gz, size 83M
pagecounts-20160126-040000.gz, size 83M
pagecounts-20160126-050000.gz, size 82M
pagecounts-20160126-060000.gz, size 84M
pagecounts-20160126-070000.gz, size 85M
pagecounts-20160126-080000.gz, size 90M
pagecounts-20160126-090000.gz, size 94M
pagecounts-20160126-100000.gz, size 95M
pagecounts-20160126-110000.gz, size 95M
pagecounts-20160126-120000.gz, size 96M
pagecounts-20160126-130000.gz, size 93M
pagecounts-20160126-140000.gz, size 98M
pagecounts-20160126-150000.gz, size 100M
pagecounts-20160126-160000.gz, size 100M
pagecounts-20160126-170000.gz, size 99M
pagecounts-20160126-180000.gz, size 98M
pagecounts-20160126-190000.gz, size 94M
pagecounts-20160126-200000.gz, size 96M
pagecounts-20160126-210000.gz, size 94M
pagecounts-20160126-220000.gz, size 90M
pagecounts-20160126-230000.gz, size 88M
pagecounts-20160127-000000.gz, size 84M
pagecounts-20160127-010000.gz, size 87M
pagecounts-20160127-020000.gz, size 81M
pagecounts-20160127-030000.gz, size 81M
pagecounts-20160127-040000.gz, size 78M
pagecounts-20160127-050000.gz, size 79M
pagecounts-20160127-060000.gz, size 81M
pagecounts-20160127-070000.gz, size 82M
pagecounts-20160127-080000.gz, size 86M
pagecounts-20160127-090000.gz, size 91M
pagecounts-20160127-100000.gz, size 96M
pagecounts-20160127-110000.gz, size 96M
pagecounts-20160127-120000.gz, size 95M
pagecounts-20160127-130000.gz, size 94M
pagecounts-20160127-140000.gz, size 95M
pagecounts-20160127-150000.gz, size 97M
pagecounts-20160127-160000.gz, size 96M
pagecounts-20160127-170000.gz, size 96M
pagecounts-20160127-180000.gz, size 92M
pagecounts-20160127-190000.gz, size 92M
pagecounts-20160127-200000.gz, size 90M
pagecounts-20160127-210000.gz, size 90M
pagecounts-20160127-220000.gz, size 89M
pagecounts-20160127-230000.gz, size 86M
pagecounts-20160128-000000.gz, size 80M
pagecounts-20160128-010000.gz, size 82M
pagecounts-20160128-020000.gz, size 82M
pagecounts-20160128-030000.gz, size 81M
pagecounts-20160128-040000.gz, size 80M
pagecounts-20160128-050000.gz, size 78M
pagecounts-20160128-060000.gz, size 80M
pagecounts-20160128-070000.gz, size 83M
pagecounts-20160128-080000.gz, size 88M
pagecounts-20160128-090000.gz, size 94M
pagecounts-20160128-100000.gz, size 100M
pagecounts-20160128-110000.gz, size 100M
pagecounts-20160128-120000.gz, size 100M
pagecounts-20160128-130000.gz, size 97M
pagecounts-20160128-140000.gz, size 96M
pagecounts-20160128-150000.gz, size 99M
pagecounts-20160128-160000.gz, size 99M
pagecounts-20160128-170000.gz, size 97M
pagecounts-20160128-180000.gz, size 95M
pagecounts-20160128-190000.gz, size 96M
pagecounts-20160128-200000.gz, size 96M
pagecounts-20160128-210000.gz, size 96M
pagecounts-20160128-220000.gz, size 94M
pagecounts-20160128-230000.gz, size 93M
pagecounts-20160129-000000.gz, size 87M
pagecounts-20160129-010000.gz, size 90M
pagecounts-20160129-020000.gz, size 87M
pagecounts-20160129-030000.gz, size 86M
pagecounts-20160129-040000.gz, size 84M
pagecounts-20160129-050000.gz, size 85M
pagecounts-20160129-060000.gz, size 83M
pagecounts-20160129-070000.gz, size 87M
pagecounts-20160129-080000.gz, size 91M
pagecounts-20160129-090000.gz, size 94M
pagecounts-20160129-100000.gz, size 99M
pagecounts-20160129-110000.gz, size 96M
pagecounts-20160129-120000.gz, size 97M
pagecounts-20160129-130000.gz, size 96M
pagecounts-20160129-140000.gz, size 100M
pagecounts-20160129-150000.gz, size 98M
pagecounts-20160129-160000.gz, size 97M
pagecounts-20160129-170000.gz, size 97M
pagecounts-20160129-180000.gz, size 94M
pagecounts-20160129-190000.gz, size 97M
pagecounts-20160129-200000.gz, size 97M
pagecounts-20160129-210000.gz, size 95M
pagecounts-20160129-220000.gz, size 89M
pagecounts-20160129-230000.gz, size 83M
pagecounts-20160130-000000.gz, size 79M
pagecounts-20160130-010000.gz, size 81M
pagecounts-20160130-020000.gz, size 79M
pagecounts-20160130-030000.gz, size 72M
pagecounts-20160130-040000.gz, size 70M
pagecounts-20160130-050000.gz, size 71M
pagecounts-20160130-060000.gz, size 72M
pagecounts-20160130-070000.gz, size 73M
pagecounts-20160130-080000.gz, size 77M
pagecounts-20160130-090000.gz, size 81M
pagecounts-20160130-100000.gz, size 87M
pagecounts-20160130-110000.gz, size 90M
pagecounts-20160130-120000.gz, size 95M
pagecounts-20160130-130000.gz, size 94M
pagecounts-20160130-140000.gz, size 94M
pagecounts-20160130-150000.gz, size 96M
pagecounts-20160130-160000.gz, size 99M
pagecounts-20160130-170000.gz, size 96M
pagecounts-20160130-180000.gz, size 92M
pagecounts-20160130-190000.gz, size 89M
pagecounts-20160130-200000.gz, size 89M
pagecounts-20160130-210000.gz, size 91M
pagecounts-20160130-220000.gz, size 88M
pagecounts-20160130-230000.gz, size 85M
pagecounts-20160131-000000.gz, size 83M
pagecounts-20160131-010000.gz, size 87M
pagecounts-20160131-020000.gz, size 86M
pagecounts-20160131-030000.gz, size 84M
pagecounts-20160131-040000.gz, size 81M
pagecounts-20160131-050000.gz, size 79M
pagecounts-20160131-060000.gz, size 83M
pagecounts-20160131-070000.gz, size 79M
pagecounts-20160131-080000.gz, size 81M
pagecounts-20160131-090000.gz, size 88M
pagecounts-20160131-100000.gz, size 93M
pagecounts-20160131-110000.gz, size 98M
pagecounts-20160131-120000.gz, size 98M
pagecounts-20160131-130000.gz, size 97M
pagecounts-20160131-140000.gz, size 98M
pagecounts-20160131-150000.gz, size 99M
pagecounts-20160131-160000.gz, size 102M
pagecounts-20160131-170000.gz, size 107M
pagecounts-20160131-180000.gz, size 106M
pagecounts-20160131-190000.gz, size 104M
pagecounts-20160131-200000.gz, size 101M
pagecounts-20160131-210000.gz, size 98M
pagecounts-20160131-220000.gz, size 92M
pagecounts-20160131-230000.gz, size 89M
"""

file_names = re.findall(r'pagecounts\-201601\d\d\-\d\d0000.gz', file_names_raw)
pageview_dir = os.path.join('data', 'pageviews')
pageview_dir_filtered = os.path.join('data', 'pageviews', 'filtered')

def read_pickle(fpath):
    with open(fpath, 'rb') as infile:
        obj = pickle.load(infile)
    return obj


def write_pickle(fpath, obj):
    with open(fpath, 'wb') as outfile:
        pickle.dump(obj, outfile, -1)


def download():
    # via http://stackoverflow.com/questions/24346872
    base_url = 'http://dumps.wikimedia.org/other/pagecounts-raw/2016/2016-01/'
    if not os.path.exists(pageview_dir):
            os.makedirs(pageview_dir)
    files_present = set([f for f in os.listdir(pageview_dir) if f.endswith('.gz')])
    num_files = len(file_names)
    start = 488
    stop = 500
    for fidx, file_name in enumerate(file_names[start:stop]):
        print(fidx+1+start, '/', num_files, '-', file_name)
        if file_name in files_present:
            print('    already downloaded')
            continue
        attempts = 0
        while attempts < 3:
            try:
                response = urllib2.urlopen(base_url + file_name, timeout=5)
                content = response.read()
                with open(os.path.join(pageview_dir, file_name), 'w') as outfile:
                    outfile.write(content)
                break
            except urllib2.URLError as e:
                attempts += 1
                print(type(e))
                pdb.set_trace()


def check_hashes(start=None, stop=None):
    d = {}
    for line in open(os.path.join(pageview_dir, 'md5sums.txt')):
        d[line.split()[1]] = line.split()[0]

    for file_name in file_names[start:stop]:
        f = open(os.path.join(pageview_dir, file_name), 'rb')
        md5 = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
        m = md5.hexdigest()
        if d[file_name] != m:
            print(file_name, " ", m, "MD5 HASH NOT OK")
        else:
            print(file_name, "OK")


def parse(start=None, stop=None):
    if not os.path.exists(pageview_dir_filtered):
        os.makedirs(pageview_dir_filtered)
    file_names = [f for f in os.listdir(pageview_dir) if f.endswith('.gz')]
    file_names = sorted(file_names)
    file_names = file_names[start:stop]
    prefixes = set(['en', 'de', 'fr', 'es', 'ru', 'it', 'ja', 'nl'])
    d = {prefix: collections.defaultdict(int) for prefix in prefixes}

    for fidx, file_name in enumerate(file_names):
        print(fidx+1, '/', len(file_names), file_name)
        with gzip.open(os.path.join(pageview_dir, file_name), 'rb') as infile:
            data = infile.readlines()
        for line in data:
            line = line.decode('utf-8')
            if line.split(' ', 1)[0] not in prefixes:
                continue
            prefix, title, views = line.strip().split(' ')[:3]
            d[prefix][title] += int(views)
        # fpath = os.path.join(pageview_dir_filtered,
        #                      file_name.rsplit('.', 1)[0] + '.obj')
        # write_pickle(fpath, d)
    if start is not None and stop is not None:
        fname = 'd-%d-%d.obj' % (start, stop)
    else:
        fname = 'd.obj'
    fpath = os.path.join(pageview_dir_filtered, fname)
    write_pickle(fpath, d)


def combine_parsed_chunks():
    file_names = [f for f in os.listdir(pageview_dir_filtered)
                  if f.endswith('.obj')]
    file_names = sorted(file_names)
    d = read_pickle(os.path.join(pageview_dir_filtered, file_names[0]))
    for fidx, file_name in enumerate(file_names[1:]):
        print(fidx+2, '/', len(file_names), file_name)
        d2 = read_pickle(os.path.join(pageview_dir_filtered, file_name))
        for prefix in d2:
            for k, v in d2[prefix].items():
                d[prefix][k] += v
    print()

    for prefix in d:
        print(prefix)
        fpath = os.path.join(pageview_dir_filtered,
                             'id2title-' + prefix + 'obj')
        write_pickle(fpath, d[prefix])


if __name__ == '__main__':
    # download()
    # check_hashes()

    if len(sys.argv) < 3:
        print('ERROR')
    parse(start=int(sys.argv[1]), stop=int(sys.argv[2]))
