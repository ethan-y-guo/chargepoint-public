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
import matplotlib.ticker as mtick
import matplotlib.image as image
import matplotlib as mpl
from matplotlib import animation
from tqdm import tqdm
import pandas as pd

root = os.path.join(config.CLIENT_ROOT, 'data')
root_df = os.path.join(root, 'dataframes')
root_anim = os.path.join(root, 'animations')

done = []

for date in os.listdir(root_anim):
    if '.' in date and 'mp4' not in date:
        continue
    
    done.append(date.split('_')[0])

data = {}

for date in os.listdir(root_df):
    f = os.path.join(root_df, date)
    
    if '.' in date and 'h5' not in date:
        continue
        
    print(f'loading {f}')
    d, _ = date.split('.')
    
    if d in done:
        print(f'skipping {d}')
        continue
    
    data[d] = pd.read_hdf(f, key='df')
    
    data[d]['datetime'] = (data[d].date + data[d].time).apply(lambda dt: datetime.strptime(dt, '%Y%m%d%H%M'))

fig, axs = plt.subplots(1, 2)
for ax in axs:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

my_day = datetime.now().date()

def strip_date(dt):
    return datetime.combine(my_day, dt.time())

"""
['building', 'section', 'floor', 'id', 'lat', 'lon', 'device_id',
       'station_name', 'loc', 'date', 'port_count_total',
       'port_count_available', 'time']
"""

#im_file = '/Users/ethanguo/Downloads/map-4.svg'
im_file = '/Users/ethanguo/Downloads/map-2.png'
img = plt.imread(im_file)
#implot = plt.imshow(img)

M, N, _ = img.shape

lat_min = 37.3270
lat_max = 37.3380
long_min = -122.0150
long_max = -122.0050

interval = 50

def normalize(lat, lon):
    return (lon - long_min) / (long_max - long_min) * N, M - (lat - lat_min) / (lat_max - lat_min) * M

from multiprocessing import Pool

inputs = []

for loc in ['ring', 'south', 'all']:
    for date in data.keys():
        inputs.append((loc, date))
    
def process(args):
    loc, date = args
    print(f'processing {loc} {date}')
    df = data[date]
    if loc == 'all':
        df = df.sort_values('time')
    else:
        df = df[df.building == loc].sort_values('time')
    
    ims = []
    fig, ax = plt.subplots()
    plt.imshow(img)
    
    cached = {}
    
    times = df.time.unique()
    for t in times:
        df2 = df[df.time == t]
        
        cnts = df2['loc'].value_counts()
        has = {}
        has['ring'] = 'ring' in cnts and cnts['ring'] > 0
        has['south'] = 'south' in cnts and cnts['south'] > 0
        
        is_free = df2[df2.port_count_available == df2.port_count_total]
        is_partial = df2[(df2.port_count_available != df2.port_count_total) & (df2.port_count_available != 0)]
        is_full = df2[df2.port_count_available == 0]
        title = plt.text(0.5,1.01, f'{t[:2]}:{t[2:]}', ha="center",va="bottom",
                 transform=ax.transAxes, fontsize="large")
        cur = [title]
        
        for sect in ['ring', 'south']:
            if not has[sect]:
                if sect in cached:
                    cur.extend(cached[sect])
                continue
            cur.append(ax.scatter(*normalize(is_free[is_free.building == sect].lat, is_free[is_free.building == sect].lon), s=2**2, marker='.', color='green'))
            cur.append(ax.scatter(*normalize(is_partial[is_partial.building == sect].lat, is_partial[is_partial.building == sect].lon), s=2**2, marker='.', color='orange'))
            cur.append(ax.scatter(*normalize(is_full[is_full.building == sect].lat, is_full[is_full.building == sect].lon), s=2**2, marker='.', color='red'))
            
            cached[sect] = cur[-3:]
        
        ims.append(cur)
        
    ani = animation.ArtistAnimation(fig, ims, interval=interval, repeat=False)
    print(f'saving {loc} {date}')
    ani.save(os.path.join(root_anim, f'{date}_{loc}_{interval}.mp4'))
    
if __name__ == '__main__':
    with Pool(4) as p:
        p.map(process, inputs)
