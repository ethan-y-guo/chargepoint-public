import os
import shutil
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as image
from tqdm import tqdm

root = '/Users/ethanguo/chargers'
root_archive = os.path.join(root, 'archive')

data = {}

#def hook(obj):
#    for key, value in obj.items():
#        pbar = tqdm(value)
#        if type(value) is list:
#            for _ in pbar:
#                pbar.set_description("Loading " + str(key))
#    return obj

for date in os.listdir(root_archive):
    f = os.path.join(root_archive, date)
    
    if '.' in date:
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

fig, axs = plt.subplots(1, 2)
for ax in axs:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

my_day = datetime.now().date()

def strip_date(dt):
    return datetime.combine(my_day, dt.time())

for loc in ['ring', 'south']:
    for date in data.keys():
        if loc not in data[date]:
            continue
        ckpts = data[date][loc]['checkpoint_list']
        
        x = []
        y = []
        
        for ckpt in ckpts:
            dt = datetime.strptime(date + ckpt['time'], '%Y%m%d%H%M')
            x.append(strip_date(dt))
            y.append(int(ckpt['chargers_count']) - int(ckpt['chargers_available']))
        
        xs, ys = zip(*sorted(zip(x, y)))
        
        axs[int(loc == 'south')].plot(xs, ys, label=f'{loc} {date}')

for ax in axs:
    ax.legend()
    ax.tick_params(axis='x', labelrotation=45)
    
plt.show()

im_file = '/Users/ethanguo/Downloads/map-4.svg'
im_file = '/Users/ethanguo/Downloads/map-2.png'
img = plt.imread(im_file)
implot = plt.imshow(img)

M, N, _ = img.shape

lat_min = 37.3270
lat_max = 37.3380
long_min = -122.0150
long_max = -122.0050

def normalize(lat, lon):
    return (lon - long_min) / (long_max - long_min) * N, M - (lat - lat_min) / (lat_max - lat_min) * M
    
for loc in ['ring', 'south']:
    for date in data.keys():
        if loc not in data[date]:
            continue
        ckpts = data[date][loc]['checkpoint_list']
        
        pts_by_status = {}

        for ckpt in ckpts:
            time = ckpt['time']
            print(loc, date, time)
            for stn in ckpt['data_list']:
                summ = stn['raw_data']['station_list']['summaries']
                
                for itm in summ:
                    lat = float(itm['lat'])
                    lon = float(itm['lon'])
                    st = itm['station_status']
                    
                    if st not in pts_by_status:
                        pts_by_status[st] = []
                    
                    pts_by_status[st].append(normalize(lat, lon))
        
            break
                            
        if 'available' in pts_by_status:
            xs, ys = zip(*sorted(pts_by_status['available']))
            plt.scatter(xs, ys, color='g', marker='.')
        
        if 'closed' in pts_by_status:
            xs, ys = zip(*sorted(pts_by_status['closed']))
            plt.scatter(xs, ys, color='r', marker='.')
        
        
        break

plt.show()

"""
todo:

make a crontab to compress each day's files on process (10x compression!)
make an animation for each day's parking spots
use percentage/plot the total spots to explain the jumps
"""

sample_trim = {
    "station_list": {
        "summaries": [{
            "lat": 37.33341846955485,               # use to plot station
            "lon": -122.00537029901847,             # use to plot station
            "port_count": {
                "total": 2,                         # use to plot graph
                "available": 2                      # use to plot graph
            },
            "device_id": 186945,                    # use to track over time
            "station_name": ["APPLE", "TA16 B3 3"] # use to categorize and track
        }]
    }
}

my_sample = {
    "date": "20221026",
    "is_ring": True,
    "checkpoint_list": [{
        "time": "1055",
        "station_count": 100,
        "chargers_available": 200,
        "chargers_count": 250,
        "token": {
            "value": "abc",
            "date": "2022-10-26",
            "time": "10:55:00"
        },
        "data_list": [{
            "section": "01_01",
            "raw_data": sample_trim
        }]
    }]
}

sample = {
    "station_list": {
        "time": "2022-10-30 18:58:05.154",          # unnecessary, redundant
        "watermark": 31178077215,                   # unnecessary
        "map_data_size": 1,                         # unnecessary
        "summaries": [{
            "lat": 37.33341846955485,               # use to plot station
            "lon": -122.00537029901847,             # use to plot station
            "port_count": {
                "total": 2,                         # use to plot graph
                "available": 2                      # use to plot graph
            },
            "station_status": "available",          # unnecessary
            "map_data": {
                "level2": {
                    "free": {
                        "available": 2,             # unnecessary, redundant
                        "in_use": 0,                # unnecessary, redundant
                        "total": 2                  # unnecessary, redundant
                    }
                }
            },
            "device_id": 186945,                    # use to track over time
            "payment_type": "free",                 # unnecessary
            "tou_status": "open",                   # unnecessary
            "can_remote_start_charge": True,        # unnecessary
            "is_connected": True,                   # unnecessary
            "community_mode": 0,                    # unnecessary
            "distance": 485,                        # unnecessary
            "bearing": 45,                          # unnecessary
            "port_type_count": {                    # unnecessary
                "3": 2                              # unnecessary
            },
            "port_status": {
                "outlet_1": {
                    "port_type": 3,                 # unnecessary
                    "available_power": "5",         # unnecessary
                    "status": "available"           # unnecessary
                },
                "outlet_2": {
                    "port_type": 3,                 # unnecessary
                    "available_power": "5",         # unnecessary
                    "status": "available"           # unnecessary
                }
            },
            "show_port_status": True,               # unnecessary
            "station_name": ["APPLE", "TA16 B3 3"], # use to categorize and track
            "address": {
                "city": "Cupertino",                # unnecessary, redundant
                "state_name": "California",         # unnecessary, redundant
                "address1": "10700 N Tantau Ave"    # unnecessary, redundant
            },
            "description": "-",                     # unnecessary
            "pricing": "pricing_free",              # unnecessary
            "power_select": "30A",                  # unnecessary
            "access_restriction": "NONE",           # unnecessary
            "max_power": {
                "unit": "kW",                       # unnecessary
                "max": 5.0                          # unnecessary
            },
            "station_power_shed_status": True,      # unnecessary
            "power_shed": {
                "outlet_1": {
                    "power_shed_status": True,      # unnecessary
                    "allowed_load": 0.0             # unnecessary
                },
                "outlet_2": {
                    "power_shed_status": True,      # unnecessary
                    "allowed_load": 0.0             # unnecessary
                }
            }
        }],
        "port_type_info": {
            "3": {
                "connector": "J1772",               # unnecessary
                "energy": 6.599999904632568,        # unnecessary
                "high_power": 0.0,                  # unnecessary
                "level": "Level 2",                 # unnecessary
                "name": "J1772",                    # unnecessary
                "unit": "kW"                        # unnecessary
            }
        },
        "port_type_text_map": {
            "3": "J1772 - 6.6kw"                    # unnecessary
        },
        "page_offset": "last_page",                 # unnecessary
        "map_bound": {
            "ne_lon": -122.00537019901847,          # unnecessary, redundant
            "sw_lat": 37.33341841955485,            # unnecessary, redundant
            "ne_lat": 37.33341851955485,            # unnecessary, redundant
            "sw_lon": -122.00537039901846           # unnecessary, redundant
        }
    }
}
