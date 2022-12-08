import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

import os
import shutil
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as image
from tqdm import tqdm
from collections import Counter
import pandas as pd

root = os.path.join(config.CLIENT_ROOT, 'data')
root_archive = os.path.join(root, 'archive')
root_df = os.path.join(root, 'dataframes')

data = {}

done = []

for date in os.listdir(root_df):
    if '.' in date and 'h5' not in date:
        continue
    
    done.append(date.split('.')[0])
    
print(f'skipping {done}')

for date in os.listdir(root_archive):
    f = os.path.join(root_archive, date)
    
    if '.' in date:
        continue
        
    if date in done:
        print(f'skipping {date} load')
        continue
    
    cur = {}
    
    for fname in os.listdir(f):
        f2 = os.path.join(f, fname)
        
        loc = fname.split('.')[0]
        
        if len(loc) == 0:
            continue
        
        with open(f2, 'r') as reader:
            print(f2)
            cur[loc] = json.load(reader)#, object_hook=hook)
        
    data[date] = cur
    
def process_name(nm):
    if nm[0] != 'APPLE' and nm[0] != 'AP 4 S':
        return None
    
    nm_split = nm[1].split(' ')
    
    if ':' in nm_split[0]: # should be ring
        bldg, sec = nm_split[0].split(':')
        
        if bldg != 'AP01' and bldg != 'AP1':
            return None
            
        if len(nm_split) != 3:
            return None
            
        bldg = 'ring'
        floor = nm_split[1]
        
        if nm_split[2] == 'RSVD':
            id = 0
        else:
            id = int(nm_split[2])
    else:
        if len(nm_split) != 4:
            return None
            
        bldg = nm_split[0]
        
        if bldg != 'AP':
            return None
            
        bldg = 'south'
            
        sec = nm_split[1]
        if sec == 'WOLFE': # visitor lot for AP
            return None
            
        floor = nm_split[2]
        id = int(nm_split[3])
        
    return {'building': bldg,
            'section': sec,
            'floor': floor,
            'id': id}

#bldg_counter = Counter()
#section_counter = Counter()
#floor_counter = Counter()
#id_arr = []

for date in data.keys():
    if date in done:
        continue

    stations = []
    for loc in ['ring', 'south']:
        if loc not in data[date]:
            continue
        ckpts = data[date][loc]['checkpoint_list']
        
        pts_by_status = {}

        for ckpt in ckpts:
            time = ckpt['time']
            for sec in ckpt['data_list']:
                secnum = sec['section']
                stn = sec['raw_data']
                summ = stn['station_list']['summaries']
                
                for itm in summ:
                    lat = float(itm['lat'])
                    lon = float(itm['lon'])
                    st = itm['station_status']
                    
                    if st not in pts_by_status:
                        pts_by_status[st] = []
                    
                    pts_by_status[st].append((lat, lon))
                    nm = process_name(itm['station_name'])
                    if nm is not None:
#                        bldg_counter[nm['building']] += 1
#                        section_counter[nm['section']] += 1
#                        floor_counter[nm['floor']] += 1
#                        id_arr.append(nm['id'])
                        nm['lat'] = lat
                        nm['lon'] = lon
                        nm['device_id'] = int(itm['device_id'])
                        nm['station_name'] = ' '.join(itm['station_name'])
                        nm['loc'] = loc
                        nm['date'] = date
                        nm['port_count_total'] = int(itm['port_count']['total'])
                        nm['port_count_available'] = int(itm['port_count']['available'])
                        nm['time'] = time
                        nm['section'] = secnum
                        stations.append(nm)
    print(f'creating df for {date}...')
    df = pd.DataFrame.from_records(stations)
    print(f'writing h5 for {date}...')
    df.to_hdf(os.path.join(root_df, f'{date}.h5'), key='df', mode='w')
