import re
import numpy as np
import pandas as pd
import time
from tqdm import tqdm
import matplotlib.pylab as plt
import seaborn as sns
from pymongo import MongoClient

connection_url = ''
connection = MongoClient(connection_url)

db = connection.get_database('')
collection = db.get_collection('')

cursor = collection.find()
list_c = list(cursor)

danawa_data = pd.DataFrame(list_c)
danawa_data.info()



# 리뷰 데이터 제거
danawa_data = danawa_data.drop(danawa_data.iloc[:, [17,18,19]].columns, axis=1)

# null값을 제거한 데이터프레임
danawa_notnull_data = danawa_data.dropna(axis=0)
danawa_notnull_data.info()

# 전체 size의 값이 없는 데이터 제거(51개)
danawa_size_drop_data = danawa_notnull_data.loc[danawa_notnull_data['size'].notnull()]
danawa_size_drop_data.reset_index(inplace=True, drop=True)
danawa_size_drop_data.info()

# 수납칸수 수치형으로 변환
danawa_size_drop_data['closet']

# closet 수납칸수를 int형으로 바꾸는 함수(수납칸수가 없는경우는 0)
def change_closet_int(data):
    if not data:
        closet_int = 0
    elif '~' in data:
        closet_int = data.lstrip('~').rstrip('칸')
    else:
        closet_int = data.rstrip('칸')
    return int(closet_int)
danawa_size_drop_data['int_closet'] = [change_closet_int(i) for i in danawa_size_drop_data['closet']]
danawa_size_drop_data.info()


# size변수를 를 각각 하나로 변경  

# cm없애는 함수
def del_cm(data):
    size = data.rstrip('cm')
    return size

# 잘못된 수집으로 인한 한글제거
def del_hangul(data): 
    remove_in = '\(.*\)'
    hangul = '[:/\[\]\(\)가-힣+]'
    result = re.sub(remove_in, '', data) 
    result = re.sub(hangul, '', result)
    return result.strip()

# 범위로 주어진 사이즈를 범위의 가장 큰 부분으로 대체하는 함수
def del_range(lst):
    if lst[lst.find('~')+1] == 'x':
        lst = lst[:lst.find('~')] + lst[lst.find('~')+1:]
    else:
        lst = lst
    if '~' in lst:
        if 'x' in lst[:lst.find('~')+1]:
            range1 = lst[lst.find('x', lst.find('x')+2)+1:lst.find('~')+1]
        else:
            range1 = lst[:lst.find('~')+1]
        
        result = re.sub(range1, '', lst)
    else:
        result = lst
    
    return result

# 가로*세로*높이를 각각 나누는 함수
def divide_size(data):
    if 'x' in data:
        division = data.split('x')
    elif '×' in data:
        division = data.split('×')
    
    return division

# 사이즈를 하나의 값들로 나누는 함수
def divide_size2(data):
    global data2
    if 'x' in data:
        data2 = data.replace('x', ' ')
    elif '×' in data:
        data2 = data.replace('×', ' ')
    data3 = ' '.join(data2.split()).split()
    return data3

# 각각의 값을 구하는 함수
def get_har_size(data):
    har = float(data[0])
    return har

def get_ver_size(data):
    ver = float(data[1])
    return ver

def get_hei_size(data):
    if len(data) != 2:
        hei = float(data[2])
    else:
        hei = np.nan
    return hei

danawa_size_drop_data['modified_size'] = [divide_size2(del_range(del_hangul(del_cm(i)))) for i in danawa_size_drop_data['size']]
list(danawa_size_drop_data['modified_size'])

danawa_size_drop_data['size_har'] = [get_har_size(i) for i in list(danawa_size_drop_data['modified_size'])]
danawa_size_drop_data['size_ver'] = [get_ver_size(i) for i in list(danawa_size_drop_data['modified_size'])]
danawa_size_drop_data['size_hei'] = [get_hei_size(i) for i in list(danawa_size_drop_data['modified_size'])]
danawa_size_drop_data.info()

# 6개월 가격추이의 값이 존재하지 않는 3개의 데이터를 제거
danawa_data2 = danawa_size_drop_data.loc[danawa_size_drop_data['price_6month'].notnull()]
danawa_data2.info()


# 기울기

# y = 최근 minPrice - 과거 minPrice, x = 6(관측된 최근의 개월) - 1(첫달),  기울기 = y/x   
# x1 = 1,    
# x2 = len(가격추이), 만약 1이라면 기울기=0   
# y2 = len(가격추이)의 minPrice   
# y1 = 1의 minPrice   

# 기울기를 가져오는 함수
def get_slope(x1, x2, y1, y2):
    if x2 == 1:
        result = 0
    else:
        result = (y2-y1) / (x2-x1)
    return result

def get_price_slope(data):
    x1 = 1
    x2 = len(data)
    y2 = data[x2-1].get('minPrice')
    y1 = data[0].get('minPrice')
    
    result = get_slope(x1,x2,y1,y2)
    return result

get_price_slope(danawa_data2['price_6month'][0])
danawa_data2['price_slope'] = [get_price_slope(lst) for lst in danawa_data2['price_6month']]





# 토크나이저를 통해 json값으로 돌려주는 함수
def get_token_json(data):
    text = data
    import requests as req
    import json
    url = ''
    body = {
        "text" : text,
        "analyzer": "nori_korean_analyzer",
        # "explain": True
    }
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    noun = req.post(url, json.dumps(body), headers = headers)
    
    return noun.json()

# 데이터의 하나의 컬럼을 넣었을 때, 하나의 값당 토크나이저를 돌리고 그를 공백값으로 join해서 내보내주는 함수
def get_token_df(data):
    json_data = [get_token_json(i) for i in data]
    tokens_data = [i.get('tokens') for i in json_data]
    
    token_df = pd.DataFrame(columns=['data'])
    for q in range(len(tokens_data)):
        token_one = [i.get('token') for i in tokens_data[q]]
        token_df = token_df.append({'data':' '.join(token_one)}, ignore_index=True)
        final = [i.split(' ') for i in token_df['data']]
    return final



# token화가 필요한 변수(info_all, with_in, form, color, function) 수정   
# with_in 수정
danawa_data2['with_in'] = get_token_df(danawa_data2['with_in'])
danawa_data2['with_in']

# form 수정
danawa_data2['form'] = [i.strip('형') for i in danawa_data2['form']]

# color 수정
danawa_data2['color'] = get_token_df(danawa_data2['color'])
danawa_data2['color']

# function 수정
danawa_data2['function'] = get_token_df(danawa_data2['function'])
danawa_data2['function']

# info_all 수정
danawa_data2['info_all'] = get_token_df(danawa_data2['info_all'])
danawa_data2['info_all']


# 화장대의 특성중 하나인 레일의 종류가 토크나이저로 인해 특성을 무시하고 '레일'만 남는다는 사실을 발견!!   
# -> 이부분에 대해 '레일'을 제거하고 '볼'을 남기는 방법을 택함   
#     ('볼 레일' 이런식으로 띄워도 '레일'만 인식됨)
get_token_json(['볼', '레일'])
get_token_json(['볼레일'])

# function의 '볼레일' 수정
a = [' '.join(i).replace('레일', '') if '레일' in ' '.join(i) else i for i in danawa_data2['function']]
b = [i.replace('레일', '') if '레일' in i else i for i in a]
len(b)
danawa_data2['function'] = get_token_df(b)

# info_all의 '볼레일' 수정
a = [' '.join(i).replace('레일', "'/ 레일") if '레일' in ' '.join(i) else i for i in danawa_data2['info_all']]
b = [i.replace('레일', "'/ 레일") if '레일' in i else i for i in a]
len(b)
danawa_data2['info_all'] = get_token_df(b)


# 이 토큰들을 하나의 벡터로 만드는 작업
path = './word2vec/word2vec_210813.bin'
from gensim.models import Word2Vec
models = Word2Vec.load(path)

# token화 처리한 4개의 변수에 대해서 벡터화
form_vector = [np.mean(models.wv[i]) for i in danawa_data2['form']]
len(form_vector)

with_in_vector = [np.mean(models.wv[i]) for i in danawa_data2['with_in']]
len(with_in_vector)

color_vector = [np.mean(models.wv[i]) for i in danawa_data2['color']]
len(color_vector)

function_vector = [np.mean(models.wv[i]) for i in danawa_data2['function']]
len(function_vector)

for i in danawa_data2['info_all']:
    for j in i:
        if j not in models.wv.index_to_key:
            i.remove(j)
info_all_vector = [np.mean(models.wv[i]) for i in danawa_data2['info_all']]
len(info_all_vector)

# 제조사의 경우, word2vec에서 인식하지 못하는 글자가 많고, 다르다는 구분만 존재해도 된다 생각하여 정수 인코딩 실시
made_by = dict(zip(list(danawa_data2.iloc[:,7].unique()), 
                   list(range(len(danawa_data2.iloc[:,7].unique())))))

# 데이터에 추가
danawa_data3 = danawa_data2.copy()

danawa_data3['made_by'] = [made_by.get(i) for i in danawa_data2['made_by']]
danawa_data3['form'] = form_vector
danawa_data3['with_in'] = with_in_vector
danawa_data3['color'] = color_vector
danawa_data3['function'] = function_vector
danawa_data3['info_all'] = info_all_vector
danawa_data3.info()



# 가격이 존재하지 않는 데이터(주로 일시품절로 인해 가격정보가 없음)를 제거후, 최저가를 뽑아내 변수를 하나 만듦
danawa_data4 = danawa_data3.loc[danawa_data3['shoppingmall_price'] != {}]
danawa_data4.reset_index(inplace=True, drop=True)
danawa_data4.info()

# 최저가를 뽑아내는 함수
def get_min_price(data):
    value_list = list(data.values())
    price = min(value_list)
    return price


# 최저가 변수를 넣고, 등록일자를 수치형으로 변환하여 넣음
danawa_data4['min_price'] = [get_min_price(i) for i in danawa_data4['shoppingmall_price']]
danawa_data4['register_date'] = [int(i.replace('.', '')) for i in danawa_data4['regisgter_date']]

# 모든 변수를 포함한 최종 데이터셋
danawa_final_all_data = danawa_data4.copy()
danawa_final_all_data.info()

# 필요한 변수만 추려낸 최종데이터셋
danawa_final_data = danawa_data4.drop(danawa_data4.iloc[:, [0,1,2,3,4,5,6,9,10,11,12,13,14,15,16,18]].columns, axis=1)
danawa_final_data.info()

# 군집에 필요없는 변수 제거하고 최종 데이터셋
danawa_drop_data = danawa_data4.drop(danawa_data4.iloc[:, [0,1,2,3,4,5,6,8,9,14,15,16,18]].columns, axis=1)
danawa_drop_data.info()


