import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

import os
import shutil

root = config.SERVER_ROOT
root_data = os.path.join(root, 'data')
root_ring = os.path.join(root_data, 'ring')
root_south = os.path.join(root_data, 'south')

with open(os.path.join(root_data, f'latest.txt'), 'r') as reader:
    maxes = reader.readlines()[0].split(' ')

to_remove = []

for path, is_ring, cur_max in [(root_ring, True, maxes[0]), (root_south, False, maxes[1])]:
    max_datetime = '20221026_0000'
    second_max_datetime = max_datetime
    for fname in os.listdir(path):
        f = os.path.join(path, fname)
        if os.path.isdir(f) and '_' in f:
            date = fname[:8]
            time = fname[9:]
            if fname < cur_max:
                to_remove.append(f)
                print(fname, is_ring)

for path in to_remove:
    shutil.rmtree(path)
