import numpy as np
import pandas as pd
import time
from tqdm import tqdm
import re
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
danawa_data['review_count'].value_counts()  # 리뷰 갯수에 대한 분포 확인


# 이에 대한 그래프
plt.figure(figsize=(28,4))
sns.barplot(x=danawa_data['review_count'].value_counts().index, y=danawa_data['review_count'].value_counts().values)

danawa_data.loc[danawa_data['review_count'].isnull(), ['review_count']] = 0

danawa_data['review_count'].value_counts()  # 결측값들을 0이라는 값을 집어넣음으로인해 전체의 데이터에 대한 분포를 확인할 수 있게됨

# 이에 대한 그래프
plt.figure(figsize=(28,4))
sns.barplot(x=danawa_data['review_count'].value_counts().index, y=danawa_data['review_count'].value_counts().values)

len(danawa_data[danawa_data['review_count'] > danawa_data['review_count'].quantile(0.95)])


# 상위 5%데이터 (95개)를 이용해 리뷰가 많은 제품의 특성 파악
danawa_review_count_5per = danawa_data[danawa_data['review_count'] > danawa_data['review_count'].quantile(0.95)]

danawa_review_count_5per.reset_index(inplace=True, drop=True)
danawa_review_count_5per.info()

danawa_review_count_5per.head(5)

'''
상위 5%에 대해 분석을 하고싶은 것들   

1. 사이즈
2. 가격(최저가 기준)
3. 최저가 판매가 많은 쇼핑몰?
4. 평점
5. 제조사
6. 등록일자가 오래되었는지


사이즈 -> 분리   
사이즈의 경우, 결측값이 존재해서 이를 제거후 분석해야함 -> 데이터프레임 새로 생성
'''


danawa_review_count_5per_sizeall = danawa_review_count_5per[danawa_review_count_5per['size'].notnull()]
danawa_review_count_5per_sizeall.reset_index(inplace=True, drop=True)
danawa_review_count_5per_sizeall.info()

danawa_review_count_5per_sizeall['size']


# cm없애는 함수
def del_cm(data):
    size = data.rstrip('cm')
    return size

del_cm_size = [del_cm(i) for i in danawa_review_count_5per_sizeall['size']]

del_cm_size

# 잘못된 수집으로 인한 한글 및 특정 특수문자 제거
def del_hangul(data): 
    hangul = '[:/\[\]가-힣+]'
    result = re.sub(hangul, '', data) 
    return result

del_hangul_size = [del_hangul(i) for i in del_cm_size]
del_hangul_size

# 범위로 주어진 사이즈를 범위의 가장 큰 부분으로 대체하는 함수
def del_range(list):
    if '~' in list:
        if 'x' in list[:list.find('~')+1]:
            range = list[list.find('x', list.find('x')+2)+1:list.find('~')+1]
        else:
            range = list[:list.find('~')+1]
        
        result = re.sub(range, '', list)
    else:
        result = list
    
    return result

del_range_size = [del_range(i) for i in del_hangul_size]
del_range_size



# 가로*세로*높이를 각각 나누는 함수
def divide_size(data):
    division = data.split('x')
    return division

# 가로, 세로, 높이의 값들을 하나씩 얻어 하나로 반환하는 함수
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



division = [divide_size(i) for i in del_range_size]
division

har = [get_har_size(i) for i in division]
ver = [get_ver_size(i) for i in division]
hei = [get_hei_size(i) for i in division]

har

hei



# 값들을 가시적으로 보기위해 그래프 작성, 또한 요약값

plt.boxplot(har)
plt.show()

plt.boxplot(ver)
plt.show()

hei_array = np.array(hei)
plt.boxplot(hei_array[~np.isnan(hei_array)])
plt.show()

print('가로  평균:', round(np.mean(har), 3), ', 중앙값: ', round(np.median(har), 3))
print('세로  평균:', round(np.mean(ver), 3), ', 중앙값: ', round(np.median(ver), 3))
print('높이  평균:', round(np.mean(hei_array[~np.isnan(hei_array)]), 3), ', 중앙값: ', round(np.median(hei_array[~np.isnan(hei_array)]), 3))


# 가격(최저가 기준)

np.mean(list(danawa_review_count_5per.shoppingmall_price[1].values()))

min(list(danawa_review_count_5per.shoppingmall_price[1].values()))

# 최저가를 뽑아내는 함수
def get_min_price(data):
    value_list = list(data.values())
    min_price = min(value_list)
    return min_price

get_min_price(danawa_review_count_5per.shoppingmall_price[1])

danawa_5per_min_price = [get_min_price(i) for i in danawa_review_count_5per.shoppingmall_price]

print('최저가: ', min(danawa_5per_min_price))
print('최고가: ', max(danawa_5per_min_price))
print('평균가: ', np.mean(danawa_5per_min_price))
print('표준편차: ', np.std(danawa_5per_min_price))
print('중앙값: ', np.median(danawa_5per_min_price))



# 최저가를 가장 많이 보유한 쇼핑몰

# 최저가의 쇼핑몰을 뽑는 함수
def get_min_price_shoppingmall(data, min_value):
    min_shoppingmall = [key for key, value in data.items() if value == min_value]
    return min_shoppingmall

get_min_price_shoppingmall(danawa_review_count_5per.shoppingmall_price[1], danawa_5per_min_price[1])

danawa_5per_min_shoppingmall = [get_min_price_shoppingmall(danawa_review_count_5per.shoppingmall_price[i], danawa_5per_min_price[i]) for i in range(95)]
danawa_5per_min_shoppingmall
danawa_5per_min_shoppingmall_all = sum(danawa_5per_min_shoppingmall, [])
pd.DataFrame(danawa_5per_min_shoppingmall_all).value_counts()


# 추가적으로 전체 데이터에서 가장 많은 최저가를 보유한 쇼핑몰을 알아보자!!
danawa_price_notnull_data = danawa_data.loc[danawa_data.shoppingmall_price != {}]
danawa_price_notnull_data.reset_index(drop=True, inplace=True)
danawa_price_notnull_data.info()

danawa_min_price_all = [get_min_price(i) for i in danawa_price_notnull_data.shoppingmall_price]

danawa_min_shoppingmall = [get_min_price_shoppingmall(danawa_price_notnull_data.shoppingmall_price[i], danawa_min_price_all[i]) for i in range(1958)]
danawa_min_shoppingmall_all = sum(danawa_min_shoppingmall, [])
pd.DataFrame(danawa_min_shoppingmall_all).value_counts()

df = pd.DataFrame(danawa_min_shoppingmall_all).value_counts()

df.index = df.index.values

df.index

# 이에 대한 그래프
plt.figure(figsize=(28,4))
sns.barplot(x=df.index, y=df.values)
plt.show()