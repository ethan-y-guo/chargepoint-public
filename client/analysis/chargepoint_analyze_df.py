import os
import shutil
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib.image as image
import matplotlib as mpl
from matplotlib import animation
from tqdm import tqdm
import pandas as pd
from numbers_parser import Document
import sklearn.linear_model
import numpy as np

from cutoffscale import *

root = '/Users/ethanguo/chargers'
root_df = os.path.join(root, 'dataframes')
root_anim = os.path.join(root, 'animations')

data = {}

# (start, end), comment
HOLIDAYS = [(('20221121', '20221125'), 'Thanksgiving')]

for date in os.listdir(root_df):
    f = os.path.join(root_df, date)
    
    if '.' in date and 'h5' not in date:
        continue
        
    dow = datetime.strptime(date, '%Y%m%d.h5').weekday()
    
    # skip weekend
    if dow > 4:
        continue
        
    # skip holidays
    to_skip = False
    for hdate, _ in HOLIDAYS:
        hs, he = hdate
        if hs <= date[:8] and date[:8] <= he:
            to_skip = True
    if to_skip:
        continue
    
    print(f'loading {f}')
    
    d, _ = date.split('.')
    data[d] = pd.read_hdf(f, key='df')
    
    data[d]['datetime'] = (data[d].date + data[d].time).apply(lambda dt: datetime.strptime(dt, '%Y%m%d%H%M'))
    
    data[d].floor.replace({'B1': '1R', 'B2': '2R'}, inplace=True) # conform to FloorRegion
    
    data[d]['plot_cgy'] = data[d].floor.apply(lambda fl: fl if fl[1] == 'R' else (fl[0] + ('N' if fl[1] in 'ABC' else 'S')))
    
doc = Document("/Users/ethanguo/Documents/parking.numbers")
sheets = doc.sheets()
tables = sheets[0].tables()
pk_data = tables[0].rows(values_only=True)

parking_df = pd.DataFrame(pk_data[1:], columns=pk_data[0])

all_days = pd.concat(data.values(), ignore_index=True, sort=False)
all_days['day_of_week'] = all_days.date.apply(lambda x: datetime.strptime(x, '%Y%m%d').weekday())

fig, ax = plt.subplots()

pk_x = []
pk_y = []

for wday in range(5):

    parking_data = parking_df[parking_df.Day == wday]
    for grp in parking_data.Lot.unique():
        if grp == '3N':
            continue
    
        parking_df2 = parking_data[parking_data.Lot == grp].groupby('Time').mean().reset_index()
        for date in data.keys():
            date_dt = datetime.strptime(date, '%Y%m%d')
            weekday = date_dt.weekday()
            weekday_name = date_dt.strftime('%A')
            
            if weekday != wday:
                continue
            
            df = data[date]
            df = df[df.plot_cgy == grp]
            df = df.groupby(['time', 'datetime']).sum().reset_index()
            
            for i in range(len(parking_df2)):
                cur_time = parking_df2.iloc[i].Time.to_pydatetime().strftime('%H%M')
                
                df2 = df[df.time == cur_time]
                if len(df2) == 0:
                    continue
                                    
                pk_x.append(parking_df2.iloc[i].Percent)
                
                df2 = df2.sum()
                pk_y.append((1.0 - df2.port_count_available / df2.port_count_total) * 100)
                
#                print(pk_x[-1], pk_y[-1], wday, grp)
    
ax.scatter(pk_x, pk_y)

pk_x_arr = np.array(pk_x).reshape(-1, 1)

lr = sklearn.linear_model.LinearRegression().fit(pk_x_arr, pk_y)
pk_y_pred = lr.predict(pk_x_arr)
ax.plot(pk_x, pk_y_pred, color="blue")
print(lr.coef_, lr.intercept_)

plt.show()

THRESHOLD = 90

IN_THRESH = (THRESHOLD - lr.intercept_) / lr.coef_[0]

opt_times = {}

for wday in range(5):
        
    df = all_days[all_days.day_of_week == wday]
    
    for cg in df.plot_cgy.unique():
        if 'R' not in cg:
            continue
        df2 = df[df.plot_cgy == cg]
        df2 = df2.groupby(['time', 'datetime']).sum().reset_index()
        
        pct = (1.0 - df2.port_count_available / df2.port_count_total) * 100
        pct.index = df2.time
        pct = pct.sort_index()
        
        if pct.max() < IN_THRESH:
            print(wday, cg, 'any time')
        else:
            opt_time = pct.index[(pct >= IN_THRESH).argmax() - 1]
            
            print(wday, cg, opt_time)
            
            opt_times[(wday, cg)] = opt_time

my_day = datetime.now().date()

def strip_date(dt):
    return datetime.combine(my_day, dt.time())

fig, axs = plt.subplots(1, 2)
for ax in axs:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

"""
['building', 'section', 'floor', 'id', 'lat', 'lon', 'device_id',
       'station_name', 'loc', 'date', 'port_count_total',
       'port_count_available', 'time']
"""
for loc in ['ring', 'south']:
    for date in data.keys():
        date_dt = datetime.strptime(date, '%Y%m%d')
        weekday = date_dt.weekday()
        weekday_name = date_dt.strftime('%A')

        if weekday >= 5:
            continue

        df = data[date]
        df = df[df.building == loc].groupby(['time', 'datetime']).sum().reset_index().sort_values('time')

        x = df.datetime.apply(strip_date)
        y1 = df.port_count_available
        y2 = df.port_count_total

        axs[int(loc == 'south')].plot(x, y2 - y1, label=f'{loc} {date} {weekday_name}')
#        axs[int(loc == 'south')].plot(x, y2, label=f'{loc} {date} max')

for ax in axs:
    ax.legend()
    ax.tick_params(axis='x', labelrotation=45)

plt.show()

#for date in data.keys():
#    date_dt = datetime.strptime(date, '%Y%m%d')
#    weekday = date_dt.weekday()
#    weekday_name = date_dt.strftime('%A')
#
#    if weekday >= 5:
#        continue
#
#    fig, axs = plt.subplots(1, 2)
#    for ax in axs:
#        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
#
#    for loc in ['ring', 'south']:
#        df = data[date]
#        df = df[df.building == loc].groupby(['time', 'datetime', 'plot_cgy']).sum().reset_index().sort_values('time')
#
#        floors = df.plot_cgy.unique()
#        for fl in floors:
#            df2 = df[df.plot_cgy == fl]
#            x = df2.datetime.apply(strip_date)
#            y1 = df2.port_count_available
#            y2 = df2.port_count_total
#
#            axs[int(loc == 'south')].plot(x, (y2 - y1) / y2 * 100, label=f'{loc} {date} {fl}')
#
#    for ax in axs:
#        ax.legend()
#        ax.tick_params(axis='x', labelrotation=45)
#
#    plt.show()
    
#    fig, ax = plt.subplots()
#    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
#    for loc in ['ring', 'south']:
#        df = data[date]
#        df = df[df.building == loc].groupby(['time', 'datetime', 'floor']).sum().reset_index().sort_values('time')
#
#        floors = df.floor.unique()
#        for fl in floors:
#            df2 = df[df.floor == fl]
#            x = df2.datetime.apply(strip_date)
#            y1 = df2.port_count_available
#            y2 = df2.port_count_total
#
#            ax.plot(x, (y2 - y1) / y2 * 100, label=f'{loc} {date} {fl}')
#
#    ax.legend()
#    ax.tick_params(axis='x', labelrotation=45)
#
#    plt.show()
    
        
    
fig, axs = plt.subplots(1, 2)
for ax in axs:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

for date in data.keys():
    date_dt = datetime.strptime(date, '%Y%m%d')
    weekday = date_dt.weekday()
    weekday_name = date_dt.strftime('%A')
    
    if weekday >= 5:
        continue
        
    for loc in ['ring', 'south']:
        df = data[date]
        df = df[df.building == loc].groupby(['time', 'datetime', 'plot_cgy']).sum().reset_index().sort_values('time')
        
        floors = df.plot_cgy.unique()
        for fl in floors:
            df2 = df[df.plot_cgy == fl]
            x = df2.datetime.apply(strip_date)
            y1 = df2.port_count_available
            y2 = df2.port_count_total
            
            axs[int(loc == 'south')].plot(x, (y2 - y1) / y2 * 100, label=f'{loc} {date} {fl}')
            
for ax in axs:
    ax.legend()
    ax.tick_params(axis='x', labelrotation=45)
        
plt.show()

#colors_1 = ['darkred', 'darkorange', 'gold', 'darkgreen', 'darkblue']
#colors = ['red', 'orange', 'yellow', 'green', 'blue']

colors_1 = ['darkviolet', 'darkred', 'gold', 'darkgreen', 'darkblue']
colors = ['violet', 'red', 'yellow', 'green', 'blue']

fig, ax = plt.subplots()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

for date in data.keys():
    date_dt = datetime.strptime(date, '%Y%m%d')
    weekday = date_dt.weekday()
    weekday_name = date_dt.strftime('%A')
    
    if weekday >= 5:
        continue
        
    for loc in ['ring']:
        df = data[date]
        df = df[df.building == loc].groupby(['time', 'datetime', 'plot_cgy']).sum().reset_index().sort_values('time')
        
        floors = df.plot_cgy.unique()
        for fl in floors:
            df2 = df[df.plot_cgy == fl]
            x = df2.datetime.apply(strip_date)
            y1 = df2.port_count_available
            y2 = df2.port_count_total
            ser = (y2 - y1) / y2 * 100
            
            cur = ax.plot(x, ser, label=f'{loc} {date} {fl} {weekday_name}', color=(colors_1[weekday] if '1' in fl else colors[weekday]))
            
            if (weekday, fl) in opt_times:
                opt_time = opt_times[(weekday, fl)] # HHMM
                opt_time_dt = datetime.combine(date_dt.date(), datetime.strptime(opt_time,'%H%M').time())
                opt_x = strip_date(opt_time_dt)
                opt_y = ser[x == opt_x]
                if len(opt_y) == 0:
                    continue
                ax.scatter(opt_x, opt_y, s=60, facecolors='none', edgecolors=cur[0].get_color())
                ax.scatter(opt_x, 0, s=60, facecolors='none', edgecolors=cur[0].get_color())
        
ax.legend()
ax.tick_params(axis='x', labelrotation=45)
ax.xaxis.grid(True)
ax.yaxis.grid(True)

hours = mdates.HourLocator(interval = 1)
ax.xaxis.set_major_locator(hours)
        
plt.show()

def plot_by_day(use_avg=False, scaled=False, morning=False):

    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    for wd in range(5):
        df = all_days[all_days.day_of_week == wd]
        
        weekday_name = None
        
        for date in data.keys():
            date_dt = datetime.strptime(date, '%Y%m%d')
            weekday = date_dt.weekday()
            
            if weekday != wd:
                continue
            weekday_name = date_dt.strftime('%A')
            
        weekday = wd
                
        for loc in ['ring']:
            df = df[df.building == loc].groupby(['time', 'plot_cgy']).aggregate({k:(max if k in {'datetime'} else sum) for k in df.columns if k not in {'time', 'plot_cgy'}}).reset_index().sort_values('time')
            
            floors = df.plot_cgy.unique()
            for fl in floors:
                df2 = df[df.plot_cgy == fl]
                x = df2.datetime.apply(strip_date)
                y1 = df2.port_count_available
                y2 = df2.port_count_total
                ser = (y2 - y1) / y2 * 100
                
                ser = ser.set_axis(x)
                if use_avg:
                    ser = ser.rolling(5).mean().dropna()
                
                cur = ax.plot(ser.index, ser, label=f'{loc} {fl} {weekday_name}', color=(colors_1[weekday] if '1' in fl else colors[weekday]))
                
    #            if (weekday, fl) in opt_times:
    #                opt_time = opt_times[(weekday, fl)] # HHMM
    #                opt_time_dt = datetime.combine(date_dt.date(), datetime.strptime(opt_time,'%H%M').time())
    #                opt_x = strip_date(opt_time_dt)
    #                opt_y = ser[x == opt_x]
    #                if len(opt_y) == 0:
    #                    continue
    #                ax.scatter(opt_x, opt_y, s=60, facecolors='none', edgecolors=cur[0].get_color())
    #                ax.scatter(opt_x, 0, s=60, facecolors='none', edgecolors=cur[0].get_color())
                
    ax.axhline(IN_THRESH, linestyle='--', color='black')

    ax.legend()
    ax.tick_params(axis='x', labelrotation=45)
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    
    def create_ax_time(hours, minutes):
        return mdates.date2num(datetime.combine(my_day, datetime.min.time()) + timedelta(hours=hours, minutes=minutes))
    
    if scaled:
        if morning:
            ax.set_xscale('cutoff', args=[create_ax_time(6, 0), 0.1,
                                        create_ax_time(11, 0), 1])
        else:
            ax.set_xscale('cutoff', args=[create_ax_time(7, 0), 0.25,
                                        create_ax_time(10, 0), 1,
                                        create_ax_time(12+4, 0), 0.25,
                                        create_ax_time(12+7, 0), 1])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    hours = mdates.HourLocator(interval = 1)
    ax.xaxis.set_major_locator(hours)
                
    fig.set_size_inches(11, 8.5)
    fig.savefig(f"/Users/ethanguo/Desktop/plot_by_day{'_avg' if use_avg else ''}{'_scaled' if scaled else ''}{'morning' if morning else ''}.svg")
    plt.show()
        
plot_by_day(use_avg=False)
plot_by_day(use_avg=True)
plot_by_day(use_avg=False, scaled=True)
plot_by_day(use_avg=True, scaled=True)
plot_by_day(use_avg=False, scaled=True, morning=True)
plot_by_day(use_avg=True, scaled=True, morning=True)

#im_file = '/Users/ethanguo/Downloads/map-4.svg'
im_file = '/Users/ethanguo/Downloads/map-2.png'
img = plt.imread(im_file)

M, N, _ = img.shape

lat_min = 37.3270
lat_max = 37.3380
long_min = -122.0150
long_max = -122.0050

interval = 50

def normalize(lat, lon):
    return (lon - long_min) / (long_max - long_min) * N, M - (lat - lat_min) / (lat_max - lat_min) * M

#fig, ax = plt.subplots()
#implot = plt.imshow(img)
#
#for date in data.keys():
#    date_dt = datetime.strptime(date, '%Y%m%d')
#    weekday = date_dt.weekday()
#    weekday_name = date_dt.strftime('%A')
#
#    if weekday >= 5:
#        continue
#
#    df = data[date]
#
#
#    df['floor_group'] = df.floor.apply(lambda x: x[1])
#
#    floor_groups = list(df.floor_group.unique())
#    floor_groups.sort()
#
#    for fl in floor_groups:
#        df2 = df[df.floor_group == fl]
#        ax.scatter(*normalize(df2.lat, df2.lon), s=2**2, marker='.', label=f'{fl}')
#
#    break
#
#ax.legend()
#
#plt.show()
