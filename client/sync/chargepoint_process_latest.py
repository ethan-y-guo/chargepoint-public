import os
import shutil

root = '/Users/ethanguo/chargers'
root_south = os.path.join(root, 'south')
maxes = []

for path, is_ring in [(root, True), (root_south, False)]:
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
    
with open(os.path.join(root, f'latest.txt'), 'w') as writer:
    writer.write(f'{maxes[0]} {maxes[1]}')
