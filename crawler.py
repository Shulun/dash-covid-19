import pandas as pd
import requests
import json
import time


url = 'https://c.m.163.com/ug/api/wuhan/app/data/list-total'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}
r = requests.get(url, headers=headers)
data_json = json.loads(r.text)
data = data_json['data']
areaTree = data['areaTree']

def get_data(data,info_list):
    info = pd.DataFrame(data)[info_list]
    
    today_data = pd.DataFrame([i['today'] for i in data ])
    today_data.columns = ['today_'+i for i in today_data.columns]
    
    total_data = pd.DataFrame([i['total'] for i in data ])
    total_data.columns = ['total_'+i for i in total_data.columns]
    
    return pd.concat([info,total_data,today_data],axis=1)

today_world = get_data(areaTree, ['id', 'lastUpdateTime', 'name'])
country_dict = {key:value for key, value in zip(today_world['id'], today_world['name'])}

start = time.time()
for country_id in country_dict:
    try:
        url = 'https://c.m.163.com/ug/api/wuhan/app/data/list-by-area-code?areaCode='+country_id
        r = requests.get(url, headers=headers)
        json_data = json.loads(r.text)

        country_data = get_data(json_data['data']['list'],['date'])
        country_data['name'] = country_dict[country_id]

        if country_id == '9577772':
            alltime_world = country_data
        else:
            alltime_world = pd.concat([alltime_world,country_data])
            
        print('-'*20, country_dict[country_id],'成功', country_data.shape,alltime_world.shape,
              ',累计耗时:', round(time.time()-start), 'sec', '-'*20)

        time.sleep(1)

    except:
        print('-'*20, country_dict[country_id], 'wrong', '-'*20)

alltime_world.to_csv("./data/alltime_world_copy.csv", encoding='utf_8_sig')