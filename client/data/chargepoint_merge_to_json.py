import os
import shutil

root = '/Users/ethanguo/chargers'
root_south = os.path.join(root, 'south')
root_archive = os.path.join(root, 'archive')
root_df = os.path.join(root, 'dataframes')
root_trash = os.path.join(root, 'trash')
root_trash_ring = os.path.join(root_trash, 'ring')
root_trash_south = os.path.join(root_trash, 'south')

archives = []
dates = set()
max_date = '20221026'

for path, is_ring in [(root, True), (root_south, False)]:
    for fname in os.listdir(path):
        f = os.path.join(path, fname)
        if os.path.isdir(f) and '_' in f:
            date = fname[:8]
            time = fname[9:]
            archives.append((date, time, f, is_ring))
            dates.add(date)
            max_date = max(max_date, date)

print(dates)

done = []

for date in os.listdir(root_df):
    if '.' in date and 'h5' not in date:
        continue
    
    done.append(date.split('.')[0])
    
print(f'skipping {done}')

for is_ring in [True, False]:
    for date in dates:
        if date == max_date or date in done:
            continue
            
        dpath = os.path.join(root_archive, date)
        if not os.path.exists(dpath):
            os.mkdir(dpath)
                
        loc = 'ring' if is_ring else 'south'
        
        with open(os.path.join(dpath, f'{loc}.json'), 'w') as writer:
            writer.write('{')
            
            writer.write(f'"date":"{date}",')
            writer.write(f'"is_ring":{str(is_ring).lower()},')
            
            writer.write('"checkpoint_list":[')
            
            is_first = True
            
            for date_cur, time, path, is_ring_cur in archives:
                if is_ring_cur != is_ring or date_cur != date:
                    continue
                    
                has_stats = False
                for fname in os.listdir(path):
                    f = os.path.join(path, fname)
                    if fname == 'stats.txt':
                        has_stats = True
                
                if not has_stats:
                    shutil.move(path, path.replace(root if is_ring else root_south, root_trash_ring if is_ring else root_trash_south))
                    print('incomplete', path)
                    continue
                            
                if not is_first:
                    writer.write(',')
                else:
                    is_first = False
                    
                writer.write('{')
                
                writer.write(f'"time":"{time}"')
                    
                for fname in os.listdir(path):
                    f = os.path.join(path, fname)
                    if fname == 'stats.txt':
                        with open(f, 'r') as reader:
                            data = reader.readlines()[0]
                            stn_count, rest = data.split(' ')
                            chg_av, chg_cnt = rest.split('/')
                            writer.write(f',"station_count":{stn_count}')
                            writer.write(f',"chargers_available":{chg_av}')
                            writer.write(f',"chargers_count":{chg_cnt}')
                    elif fname == 'tkn.txt':
                        with open(f, 'r') as reader:
                            data = reader.readlines()[0]
                            tkn, tkn_date, tkn_time = data.split(' ')
                            writer.write(',"token":{')
                            
                            writer.write(f'"value":"{tkn}","date":"{tkn_date}","time":"{tkn_time}"')
                            
                            writer.write('}')
                                              
                writer.write(f',"data_list":[')
                
                is_first_d = True
                
                for fname in os.listdir(path):
                    f = os.path.join(path, fname)
                    
                    if 'json' in fname:
                        if not is_first_d:
                            writer.write(',')
                        else:
                            is_first_d = False
                        
                        with open(f, 'r') as reader:
                            nm_split = fname.split('.')
                            if len(nm_split) > 2:
                                is_first_d = True
                                print(f'skipping {time} {fname}')
                                continue
                            sec, _ = nm_split
                            writer.write('{')
                            writer.write(f'"section":"{sec}"')
                            writer.write(f',"raw_data":{reader.readlines()[0]}')
                            writer.write('}')
                
                writer.write(']}')
                
                shutil.move(path, path.replace(root if is_ring else root_south, root_trash_ring if is_ring else root_trash_south))

            writer.write(']}')
