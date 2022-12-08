import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from datetime import datetime

from requests import session

payload = config.CHARGEPOINT_CREDENTIALS

root = config.SERVER_ROOT
root_ring = os.path.join(root, 'ring')

coulomb_tkn = None
coulomb_exp = None

with session() as c:
    c.post('https://na.chargepoint.com/users/validate', data=payload)
    c.post('https://na.chargepoint.com/index.php/nghelper/getSession')
    for cookie in c.cookies:
        if cookie.name == 'coulomb_sess':
            coulomb_tkn = cookie.value
            coulomb_exp = cookie.expires
    response = c.get('https://na.chargepoint.com')
    
stamp = datetime.now()
stamp_str = stamp.strftime("%Y%m%d_%H%M")

url = 'https://mc.chargepoint.com/map-prod/get?{%22station_list%22:{%22ne_lat%22:37.337135,%22ne_lon%22:-122.006137,%22sw_lat%22:37.332153,%22sw_lon%22:-122.012157,%22page_size%22:100,%22sort_by%22:%22distance%22,%22filter%22:{%22price_free%22:true,%22status_available%22:false},%22include_map_bound%22:true}}'

url0 = 'https://mc.chargepoint.com/map-prod/get?{%22station_list%22:{%22ne_lat%22:37.33764602999174,%22ne_lon%22:-122.00162219405854,%22sw_lat%22:37.33252771707327,%22sw_lon%22:-122.01465772987092,%22page_size%22:100,%22page_offset%22:%22%22,%22sort_by%22:%22distance%22,%22screen_width%22:1022,%22screen_height%22:707,%22filter%22:{%22connector_l1%22:false,%22connector_l2%22:false,%22is_bmw_dc_program%22:false,%22is_nctc_program%22:false,%22connector_chademo%22:false,%22connector_combo%22:false,%22connector_tesla%22:false,%22price_free%22:false,%22status_available%22:false,%22network_chargepoint%22:false,%22network_blink%22:false,%22network_semacharge%22:false,%22network_evgo%22:false,%22connector_l2_nema_1450%22:false,%22connector_l2_tesla%22:false},%22include_map_bound%22:true,%22estimated_fee_input%22:{%22arrival_time%22:%2214:45%22,%22battery_size%22:30}}}'

import requests
import json
import matplotlib.pyplot as plt
import http.cookies

cookies = f'coulomb_sess={coulomb_tkn};'
    
simple_cookie = http.cookies.SimpleCookie(cookies)
cookie_jar = requests.cookies.RequestsCookieJar()
cookie_jar.update(simple_cookie)

page = requests.get(url, cookies=cookie_jar)

#print(page.text[:100])

page6 = page.json()

page = requests.get(url0, cookies=cookie_jar)

#print(page.text[:100])

page50 = page.json()

def extract(pjson):
    res_x = []
    res_y = []
    res_cnt = 0
    res_av = 0
    for itm in pjson['station_list']['summaries']:
        res_x.append(itm['lat'])
        res_y.append(itm['lon'])
        res_cnt += itm['port_count']['total']
        res_av += itm['port_count']['available']
#    print(res_cnt, res_av)
    return res_x, res_y, res_cnt, res_av

lat, long, _, _ = extract(page6)
#plt.scatter(lat, long, marker='x')

#print(list(zip(lat, long)))

lat, long, _, _ = extract(page50)
#plt.scatter(lat, long, marker='.')
#plt.show()

#print(list(zip(lat, long)))

#print(page6)

import numpy as np

N = 6

lat_vals = np.linspace(37.332153, 37.337135, N)
long_vals = np.linspace(-122.012157, -122.006137, N)

T_cnt = 0
T_av = 0
T_stn = 0

import os

os.mkdir(os.path.join(root_ring, f'{stamp_str}'))

for i in range(N - 1):
    for j in range(N - 1):
        url = f'https://mc.chargepoint.com/map-prod/get?{{%22station_list%22:{{%22ne_lat%22:{lat_vals[i + 1]},%22ne_lon%22:{long_vals[j + 1]},%22sw_lat%22:{lat_vals[i]},%22sw_lon%22:{long_vals[j]},%22page_size%22:100,%22sort_by%22:%22distance%22,%22filter%22:{{%22price_free%22:true,%22status_available%22:false}},%22include_map_bound%22:true}}}}'
#        print(url)

        page = requests.get(url, cookies=cookie_jar)

#        print(page.text[:100])
        page6 = page.json()
        lat, long, cnt, av = extract(page6)
#        print(len(lat))
#        plt.scatter(lat, long, marker='.')
        T_cnt += cnt
        T_av += av
        T_stn += len(lat)
        
        with open(os.path.join(root_ring, f'{stamp_str}/{i}_{j}.json'), 'w') as writer:
            writer.write(page.text)
#print(T_cnt, T_av, T_stn)

#plt.show()

with open(os.path.join(root_ring, f'{stamp_str}/tkn.txt'), 'w') as writer:
    writer.write(f"{coulomb_tkn} {datetime.utcfromtimestamp(int(coulomb_exp)).strftime('%Y-%m-%d %H:%M:%S')}")
    
with open(os.path.join(root_ring, f'{stamp_str}/stats.txt'), 'w') as writer:
    writer.write(f'{T_stn} {T_av}/{T_cnt}')
