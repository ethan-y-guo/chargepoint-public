import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from datetime import datetime

from requests import session

payload = config.CHARGEPOINT_CREDENTIALS

root = config.SERVER_ROOT
root_south = os.path.join(root, 'south')

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

#
#url = 'https://mc.chargepoint.com/map-prod/get?{%22station_list%22:{%22ne_lat%22:37.33764602999174,%22ne_lon%22:-122.00162219405854,%22sw_lat%22:37.33252771707327,%22sw_lon%22:-122.01465772987092,%22sort_by%22:%22distance%22,%22filter%22:{%22price_free%22:true,%22status_available%22:false},%22include_map_bound%22:true}}'
#
#url0 = 'https://mc.chargepoint.com/map-prod/get?{%22station_list%22:{%22ne_lat%22:37.33764602999174,%22ne_lon%22:-122.00162219405854,%22sw_lat%22:37.33252771707327,%22sw_lon%22:-122.01465772987092,%22page_size%22:100,%22sort_by%22:%22distance%22,%22filter%22:{%22price_free%22:true,%22status_available%22:false},%22include_map_bound%22:true}}'

import requests
import json
import matplotlib.pyplot as plt
import http.cookies
cookies0 = 'ci_ui_session=0ceb14039707e83e24f00266dd380e10%23D20bf747; _ga=GA1.2.1877573187.1666729678; _gid=GA1.2.1562871499.1666905581; datadome=pTEKzjaKxizuA-G-bpo5SL5~hOlLyV3204U8d.tq-ljCdToZ.GvpnY35LKm878CvSOxcJS_wKD.cywLQKZnPk1EJyYs.HVAkDpjrh6FD4YXrgLbZJQPyVOJBWsnTMUS; coulomb_sess=65a216a9c640a1df12c1fa07b8506052%23D20bf747; csrf_cookie_name=a163cc55af028f576f38ce5b8e831b6b; country_code=US; country_id=233; lang_country=United+States; length_unit=miles; locale=en-US; map_latitude=38.5; map_longitude=-95.71; mp_7006b932a849e5649af9ac208147705c_mixpanel=%7B%22distinct_id%22%3A%20%2234338631%22%2C%22%24device_id%22%3A%20%221841b5967bc1f0-01e046e5fb83e48-3f626b4b-201b88-1841b5967bde3b%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.chargepoint.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.chargepoint.com%22%2C%22%24user_id%22%3A%20%2234338631%22%7D; prefLanguage=en; volume_unit=gallons; _ga_R8LZDKZJ1W=GS1.1.1666905580.2.1.1666905915.0.0.0; company_address=254+East+Hacienda+Avenue+%7C+Campbell%2C+CA+95008+USA; company_name=ChargePoint%2C+Inc.; customer_support_number=1-888-758-4389; error_support_number=1-877-850-4562; lang_corporate_url=www.chargepoint.com; sub_domain=na; support_email=support%40chargepoint.com; _fbp=fb.1.1666729678341.1018058191; _biz_nA=7; _biz_pendingA=%5B%5D; _biz_uid=9c16987bed044fcaf0203ce55e63cca6; _mkto_trk=id:079-WYC-990&token:_mch-chargepoint.com-1666729678825-87290; _uetsid=117ebb80563d11edb7525de749b80205; _uetvid=83aefba054a311ed8cb22b22da0b36b9; fs_cid=1.0; fs_uid=#D7C6G#5488234377220096:5702685019885568:::#/1698265678; _clck=w3ggst|1|f62|0; _mkto_trk_http=id:079-WYC-990&token:_mch-chargepoint.com-1666729678825-87290; mp_523fa23e108cb60b8c1aa6a7f57373bd_mixpanel=%7B%22distinct_id%22%3A%20%2218410d5ccb012ca-03606c747bb217-3f626b4b-201b88-18410d5ccb116ae%22%2C%22%24device_id%22%3A%20%2218410d5ccb012ca-03606c747bb217-3f626b4b-201b88-18410d5ccb116ae%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.chargepoint.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.chargepoint.com%22%2C%22User%20Flow%22%3A%20%22Sign%20Up%22%2C%22User%20Type%22%3A%20%22Driver%22%2C%22Chargepoint%20Product%22%3A%20%22Driver%20Portal%22%2C%22Analytics%20Reporting%20Version%22%3A%201%7D; _biz_flagsA=%7B%22Version%22%3A1%2C%22ViewThrough%22%3A%221%22%2C%22XDomain%22%3A%221%22%7D; _gcl_au=1.1.1968483037.1666729678'

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

lat_vals = np.linspace(37.327717, 37.331693, N)
long_vals = np.linspace(-122.012464, -122.007161, N)

T_cnt = 0
T_av = 0
T_stn = 0

import os

os.mkdir(os.path.join(root_south, f'{stamp_str}'))

N_rec = 6

def process(ne_lat, ne_lon, sw_lat, sw_lon, fname, dep=0):
    global T_cnt, T_av, T_stn
    
    url = f'https://mc.chargepoint.com/map-prod/get?{{%22station_list%22:{{%22ne_lat%22:{ne_lat},%22ne_lon%22:{ne_lon},%22sw_lat%22:{sw_lat},%22sw_lon%22:{sw_lon},%22page_size%22:100,%22sort_by%22:%22distance%22,%22filter%22:{{%22price_free%22:true,%22status_available%22:false}},%22include_map_bound%22:true}}}}'
#    print(url)

    page = requests.get(url, cookies=cookie_jar)

#    print(page.text[:100])
    page6 = page.json()
    lat, long, cnt, av = extract(page6)
    
    if len(lat) == 50:
        cur_lat_vals = np.linspace(sw_lat, ne_lat, N_rec)
        cur_lon_vals = np.linspace(sw_lon, ne_lon, N_rec)
        for i in range(N_rec - 1):
            for j in range(N_rec - 1):
                process(cur_lat_vals[i + 1], cur_lon_vals[j + 1], cur_lat_vals[i], cur_lon_vals[j], f'{fname}_{i}_{j}', dep + 1)
        
        return
#    print(len(lat))
        
#    plt.scatter(lat, long, marker='.')
    T_cnt += cnt
    T_av += av
    T_stn += len(lat)
    
    with open(os.path.join(root_south, f'{stamp_str}/{fname}.json'), 'w') as writer:
        writer.write(page.text)

for i in range(N - 1):
    for j in range(N - 1):
        process(lat_vals[i + 1], long_vals[j + 1], lat_vals[i], long_vals[j], f'{i}_{j}')
        
#print(T_cnt, T_av, T_stn)

#plt.show()

with open(fos.path.join(root_south, f'{stamp_str}/tkn.txt'), 'w') as writer:
    writer.write(f"{coulomb_tkn} {datetime.utcfromtimestamp(int(coulomb_exp)).strftime('%Y-%m-%d %H:%M:%S')}")
    
with open(os.path.join(root_south, f'{stamp_str}/stats.txt'), 'w') as writer:
    writer.write(f'{T_stn} {T_av}/{T_cnt}')
