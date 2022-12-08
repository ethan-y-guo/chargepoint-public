import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

import os
import shutil

root = config.CLIENT_ROOT
root_data = os.path.join(root, 'data')
root_ring = os.path.join(root_data, 'ring')
root_south = os.path.join(root_data, 'south')
maxes = []

for path, is_ring in [(root_ring, True), (root_south, False)]:
    max_datetime = '20221026_0000'
    second_max_datetime = max_datetime
    for fname in os.listdir(path):
        f = os.path.join(path, fname)
        if os.path.isdir(f) and '_' in f:
            date = fname[:8]
            time = fname[9:]
            if fname >= max_datetime:
                second_max_datetime = max_datetime
                max_datetime = fname
            elif fname >= second_max_datetime:
                second_max_datetime = fname
    maxes.append(second_max_datetime)
    
with open(os.path.join(root_data, f'latest.txt'), 'w') as writer:
    writer.write(f'{maxes[0]} {maxes[1]}')
