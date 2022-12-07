import os
import shutil

with open(os.path.join('/home/aa/users/cs199-beg/tmp/', f'latest.txt'), 'r') as reader:
    maxes = reader.readlines()[0].split(' ')
    
root = '/home/aa/users/cs199-beg/tmp/chargers'
root_south = os.path.join(root, 'south')

to_remove = []

for path, is_ring, cur_max in [(root, True, maxes[0]), (root_south, False, maxes[1])]:
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
