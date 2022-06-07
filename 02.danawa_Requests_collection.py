import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
from tqdm import tqdm

# 전체 검색페이지에서 상품과 페이지를 정해 html을 가져오는 함수
def search_productname_urlpage_change_soup(product,page):
    url = 'http://search.danawa.com/ajax/getProductList.ajax.php'
    headers = {'Host': 'search.danawa.com',
            'Referer': 'http://search.danawa.com/dsearch.php?query=%ED%99%94%EC%9E%A5%EB%8C%80&originalQuery=%ED%99%94%EC%9E%A5%EB%8C%80&previousKeyword=%ED%99%94%EC%9E%A5%EB%8C%80&volumeType=allvs&page=2&limit=40&sort=saveDESC&list=list&boost=true&addDelivery=N&recommendedSort=Y&defaultUICategoryCode=1523439&defaultPhysicsCategoryCode=1826%7C47159%7C54196%7C0&defaultVmTab=3606&defaultVaTab=986946&tab=goods',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    data = {'query': product, 'page':page, 'limit':100, 'sort': 'saveDESC'}
    req = requests.post(url, headers = headers, data = data)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

# 상품검색 url중에서 각 상품의 url을 가져오는 대신 product-pot을 제거하는 함수
def soup_to_page_url_deleteAD(soup):
    soup.find('li','prod_item product-pot').decompose()
    product_list = soup.find_all('li',{'class':'prod_item'})
    page_url = [list.find_all('a', {'class' : 'click_log_product_standard_title_'})[0]['href'] for list in product_list if list.find_all('a', {'class' : 'click_log_product_standard_title_'}) != []]
    return page_url

# 상품 코드인 pcode를 가져오는 함수
def get_pcode(url):
    pcode = url[url.find('pcode=')+6:url.find('&')]
    return pcode

# 상품 url에서 requests를 이용해 html을 가져오는 함수
def convert_page_url_to_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    req = requests.get(url, headers = headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

# 전체 검색페이지에서 상품과 페이지를 정해 '가격비교'탭의 html을 가져오는 함수
def search_compareTab_productname_urlpage_change_soup(product, page):
    url = 'http://search.danawa.com/ajax/getProductList.ajax.php'
    headers = {'Host': 'search.danawa.com',
            'Referer': 'http://search.danawa.com/dsearch.php?query=%ED%99%94%EC%9E%A5%EB%8C%80&originalQuery=%ED%99%94%EC%9E%A5%EB%8C%80&previousKeyword=%ED%99%94%EC%9E%A5%EB%8C%80&volumeType=allvs&page=2&limit=40&sort=saveDESC&list=list&boost=true&addDelivery=N&recommendedSort=Y&defaultUICategoryCode=1523439&defaultPhysicsCategoryCode=1826%7C47159%7C54196%7C0&defaultVmTab=3606&defaultVaTab=986946&tab=goods',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    data = {'query': product, 'page': page, 'limit':100, 'sort': 'saveDESC', 'volumeType': 'vmvs'}
    req = requests.post(url, headers = headers, data = data)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

# 제품명
def get_product_name(product_soup):
    name = product_soup.find('div', 'top_summary').find('h3').text
    return name

# 상품몰과 가격
def get_product_shoppingmall_price_dict(product_soup):
    shoppingmall = []
    price = []

    if product_soup.find('tbody', {'class':'high_list'}) is not None:
        product_price_table = product_soup.find('tbody', {'class':'high_list'})
        if product_price_table.find('tr',{'class':'product-pot'}) is not None:
            product_price_table.find('tr',{'class':'product-pot'}).decompose()
    
        for i in range(0,len(product_price_table.find_all('img'))):
            shoppingmall.append(product_price_table.find_all('img')[i]['alt'])
            price.append(int(product_price_table.find_all('em')[i].text.replace(',','')))
    shopping = dict(zip(shoppingmall, price))
    return shopping

# 이미지 url
def get_product_img_url(product_soup):
    img_url = product_soup.select('#baseImage')[0]['src']
    return img_url

# 등록년월
def get_regisgter_date(product_soup):
    register_date = product_soup.find('div', {'class': 'made_info'}).find('span', {'class': 'txt'}).text.lstrip('등록월: ')
    return register_date

# 제조회사
def get_made_by(product_soup):
    if product_soup.find('div', {'class': 'made_info'}).find('a') is not None:
        made_by = product_soup.find('div', {'class': 'made_info'}).find('a').text
    else:
        made_by = product_soup.find('div', {'class': 'made_info'}).find('span', {'id':'makerTxtArea'}).text.strip('제조사:').strip()
    return made_by

# 세부정보
def get_product_detail_info(product_soup):
    import re
    product_info = product_soup.find('div', {'class': 'items'}).text
    types = []
    form = []
    with_in = []
    color = []
    closet = []
    size = []
    
    if product_info.find('/') != -1:
        types = product_info[:product_info.find('/')].strip()
    else:
        types = product_info

    if '형태' in product_info:
        form = product_info[product_info.find('형태')+3 : ][:product_info[product_info.find('형태')+4:].find('/')].strip()
    else: 
        form = np.nan
        
    if '포함:' in product_info:
        with_in = product_info[product_info.find('포함')+3 : ][:product_info[product_info.find('포함')+4:].find('/')].strip().split(',')
    else: 
        with_in = np.nan
        
    if product_info.find('색상') == -1:
        color = np.nan
    elif product_info.find('색상', product_info.find('색상')+2) != -1:
        color = product_info[product_info.find('색상', product_info.find('색상')+2)+2 :].strip(':').strip().split(',')
    elif '/' in product_info[product_info.find('색상')+2 : ]:
        color = product_info[product_info.find('색상')+2 :][:product_info[product_info.find('색상')+2 :].find('/')].strip(':').strip().split(',')
    elif '/' not in product_info[product_info.find('색상')+2 : ]:
        color = product_info[product_info.find('색상')+2 : ].strip(':').strip().split(',')
        
    if '기능' in product_info:
        function = product_info[product_info.find('기능')+3 : ][:product_info[product_info.find('기능')+4:].find('/')].strip().split(',')
        if '레일' in product_info:
            function.append(re.findall('..레일', product_info[:product_info.find('기능')])[0].strip())
    elif '레일' in product_info:
        function = re.findall('..레일', product_info[:product_info.find('기능')])[0].strip()
    else: 
        function = np.nan
        
    if '하단수납칸수' in product_info:
        closet = product_info[product_info.find('하단수납칸수')+7: ][:product_info[product_info.find('하단수납칸수')+7:].find('/')].strip()
    else: 
        closet_int = np.nan
    
    if '화장대크기(가로x세로x높이)' in product_info:
        size = product_info[product_info.find('화장대크기(가로x세로x높이)') +17 :][:product_info[product_info.find('화장대크기(가로x세로x높이)') +17 :].find('m')+1]
    elif '크기(가로x세로x높이)' in product_info:
        size = product_info[product_info.find('크기(가로x세로x높이)') +14 :][:product_info[product_info.find('크기(가로x세로x높이)') +14 :].find('m')+1]
    elif '크기:' in product_info:
        size = product_info[product_info.find('크기:') +4 :][:product_info[product_info.find('크기:') +4 :].find('m')+1]
    else: 
        size = np.nan
    
    return product_info, types, form, with_in, color, function, closet, size

# 가격추이
def get_changing_price_6month(pcode):
    headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
              'Referer': 'http://prod.danawa.com/info/?pcode='+pcode+'&keyword=%ED%99%94%EC%9E%A5%EB%8C%80'}
    req = requests.get('http://prod.danawa.com/info/ajax/getProductPriceList.ajax.php?productCode='+pcode,
                      headers = headers)
    price_json = req.json()
    price_6month = price_json.get('6').get('result')
    
    return price_6month

# 리뷰가 들어있는 html를 가져오는 함수
def get_review_html(pcode):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    req = requests.get('http://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?prodCode='+pcode+'&cate1Code=1826&page=1&limit=100&score=0&sortType=NEW&usefullScore=Y',
                       headers = headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

# 개별 리뷰의 정보(평점, 날짜, 리뷰내용)
def convert_product_review_dict(product_soup):
    review_df = pd.DataFrame(columns=['review_point', 'review_date', 'review_content'])
  
    if review_url_soup.find('div', {'class':'area_left'}) is not None:     
        product_review_table_li = product_soup.find_all('li', {'class':'danawa-prodBlog-companyReview-clazz-more'})
      
        for i in product_review_table_li:
            review_point=i.find('span', {'class':'star_mask'})
            review_date=i.find('span', {'class': 'date'})
            review_content=i.find('div', {'class': 'atc'})
  
            review_point2 = int(review_point.text.rstrip('점'))
            review_date2 = review_date.text
            review_content2 = review_content.text
  
            review_df = review_df.append({'review_point': review_point2, 'review_date': review_date2, 'review_content': review_content2}, ignore_index=True)
        review_dict = review_df.to_dict('records')
    
        return review_dict


# 리뷰 평점
def get_review_mean_point(review_soup):
    if review_soup.find('div', {'class':'area_left'}) is not None:
        review_mean_point = review_soup.find('div', {'class': 'point_num'}).find('strong', {'class': 'num_c'}).text
        review_mean_point_float = float(review_mean_point)
        return review_mean_point_float

# 리뷰 수
def get_review_count(review_soup):
    if review_soup.find('div', {'class':'area_left'}) is not None:
        review_count = review_soup.find('div', {'class': 'point_num'}).find('span', {'class': 'cen_w'}).text.strip('(|)')
        review_count_int = int(review_count)
        return review_count_int







# 데이터 수집

import pymongo
conn = pymongo.MongoClient("")
mydb = conn['']
collection = mydb['']


product_data=pd.DataFrame()
for page in tqdm(range(1, 51)):
    page_url = soup_to_page_url_deleteAD(search_productname_urlpage_change_soup('화장대', page))
    
    for count in range(0,len(page_url)):
        product_dict={}
        product_soup = convert_page_url_to_html(page_url[count])
        
        # 제품의 카테고리가 화장대인 경우만 수집
        if ('화장대' in product_soup.find('div', {'class': 'items'}).text.split(' /')[0]) or ('화장대' in product_soup.find('div', 'top_summary').find('h3').text):
            product_dict['product_id'] = get_pcode(page_url[count])
            
            product_dict['name'] = get_product_name(product_soup)  # 상품명
            product_dict['shoppingmall_price'] = get_product_shoppingmall_price_dict(product_soup)  # 상품가격
            product_dict['img_url'] = get_product_img_url(product_soup)  # 이미지 URL
            product_dict['regisgter_date'] = get_regisgter_date(product_soup)  # 등록년월
            product_dict['made_by'] = get_made_by(product_soup)  # 제조회사
            product_dict['form'], product_dict['with_in'], product_dict['color'], product_dict['function'], product_dict['closet'] = get_product_detail_info(product_soup)  # 세부정보
            product_dict['price_6month'] = get_changing_price_6month(get_pcode(page_url[count]))
            
            
            # review
            review_url_soup = get_review_html(get_pcode(page_url[count]))
            product_dict['product_review'] = convert_product_review_dict(review_url_soup)  # 개별 리뷰의 정보
            product_dict['review_count'] = get_review_count(review_url_soup)  # 리뷰수
            product_dict['review_mean_point'] = get_review_mean_point(review_url_soup)  # 평균리뷰수

            
            product_data = product_data.append(product_dict, ignore_index=True)
            collection.insert_one(product_dict)




# 1. danawa_request_all에 unique key를 이용한 중복제거 수집

import pymongo
conn = pymongo.MongoClient("")
mydb = conn['']
collection = mydb['']


product_data=pd.DataFrame()
for page in tqdm(range(1, 11)):
    page_url = soup_to_page_url_deleteAD(search_compareTab_productname_urlpage_change_soup('화장대', page))
    
    for count in range(0,len(page_url)):
        product_dict={}
        product_soup = convert_page_url_to_html(page_url[count])
        
        product_dict['product_url'] = page_url[count]
        product_dict['product_id'] = get_pcode(page_url[count])
        
        product_dict['name'] = get_product_name(product_soup)  # 상품명
        product_dict['shoppingmall_price'] = get_product_shoppingmall_price_dict(product_soup)  # 상품가격
        product_dict['img_url'] = get_product_img_url(product_soup)  # 이미지 URL
        product_dict['regisgter_date'] = get_regisgter_date(product_soup)  # 등록년월
        product_dict['made_by'] = get_made_by(product_soup)  # 제조회사
        product_dict['info_all'], product_dict['type'], product_dict['form'], product_dict['with_in'], product_dict['color'], product_dict['function'], product_dict['closet'], product_dict['size'] = get_product_detail_info(product_soup)  # 세부정보
        product_dict['price_6month'] = get_changing_price_6month(get_pcode(page_url[count]))
            
        # review
        review_url_soup = get_review_html(get_pcode(page_url[count]))
        product_dict['product_review'] = convert_product_review_dict(review_url_soup)  # 개별 리뷰의 정보
        product_dict['review_count'] = get_review_count(review_url_soup)  # 리뷰수
        product_dict['review_mean_point'] = get_review_mean_point(review_url_soup)  # 평균리뷰수

        
        product_data = product_data.append(product_dict, ignore_index=True)
        try:
            collection.insert_one(product_dict)
        except:
            print('duplicate key: %s' %product_dict['product_id'])
        


product_data





# 2. danawa_request3에 find를 이용해서 중복된 값이 삽입된다면 exist를 아니면 new를  삽입

import pymongo
conn = pymongo.MongoClient("")
mydb = conn['']
collection = mydb['']


product_data=pd.DataFrame()
for page in tqdm(range(1, 11)):
    page_url = soup_to_page_url_deleteAD(search_compareTab_productname_urlpage_change_soup('화장대', page))
    
    for count in range(0,len(page_url)):
        product_dict={}
        product_soup = convert_page_url_to_html(page_url[count])
        
        product_dict['product_url'] = page_url[count]
        product_dict['product_id'] = get_pcode(page_url[count])
        
        product_dict['name'] = get_product_name(product_soup)  # 상품명
        product_dict['shoppingmall_price'] = get_product_shoppingmall_price_dict(product_soup)  # 상품가격
        product_dict['img_url'] = get_product_img_url(product_soup)  # 이미지 URL
        product_dict['regisgter_date'] = get_regisgter_date(product_soup)  # 등록년월
        product_dict['made_by'] = get_made_by(product_soup)  # 제조회사
        product_dict['info_all'], product_dict['type'], product_dict['form'], product_dict['with_in'], product_dict['color'], product_dict['function'], product_dict['closet'], product_dict['size'] = get_product_detail_info(product_soup)  # 세부정보
        product_dict['price_6month'] = get_changing_price_6month(get_pcode(page_url[count]))
            
        # review
        review_url_soup = get_review_html(get_pcode(page_url[count]))
        product_dict['product_review'] = convert_product_review_dict(review_url_soup)  # 개별 리뷰의 정보
        product_dict['review_count'] = get_review_count(review_url_soup)  # 리뷰수
        product_dict['review_mean_point'] = get_review_mean_point(review_url_soup)  # 평균리뷰수

        
        if list(collection.find({"product_id": product_dict['product_id']})) !=[]:
            product_dict['exist'] = 'exist'
        else:
            product_dict['exist'] = 'new'
        product_data = product_data.append(product_dict, ignore_index=True)
        collection.insert_one(product_dict)

product_dict['product_id']





# 3. 새로운 collection을 만들어서 삽입 - unique key 생성

import pymongo
conn = pymongo.MongoClient("")
mydb = conn['']
collection = mydb['']

collection.create_index([('product_id', pymongo.ASCENDING)],unique=True)


product_data=pd.DataFrame()
for page in tqdm(range(10, 101)):
    page_url = soup_to_page_url_deleteAD(search_compareTab_productname_urlpage_change_soup('화장대', page))
    
    for count in range(0,len(page_url)):
        product_dict={}
        product_soup = convert_page_url_to_html(page_url[count])
        
        product_dict['product_url'] = page_url[count]
        product_dict['product_id'] = get_pcode(page_url[count])
        
        product_dict['name'] = get_product_name(product_soup)  # 상품명
        product_dict['shoppingmall_price'] = get_product_shoppingmall_price_dict(product_soup)  # 상품가격
        product_dict['img_url'] = get_product_img_url(product_soup)  # 이미지 URL
        product_dict['regisgter_date'] = get_regisgter_date(product_soup)  # 등록년월
        product_dict['made_by'] = get_made_by(product_soup)  # 제조회사
        product_dict['info_all'], product_dict['type'], product_dict['form'], product_dict['with_in'], product_dict['color'], product_dict['function'], product_dict['closet'], product_dict['size'] = get_product_detail_info(product_soup)  # 세부정보
        product_dict['price_6month'] = get_changing_price_6month(get_pcode(page_url[count]))
            
        # review
        review_url_soup = get_review_html(get_pcode(page_url[count]))
        product_dict['product_review'] = convert_product_review_dict(review_url_soup)  # 개별 리뷰의 정보
        product_dict['review_count'] = get_review_count(review_url_soup)  # 리뷰수
        product_dict['review_mean_point'] = get_review_mean_point(review_url_soup)  # 평균리뷰수

        
        product_data = product_data.append(product_dict, ignore_index=True)
        try:
            collection.insert_one(product_dict)
        except:
            pass







# mongodb에서 데이터 불러오기

cursor = collection.find()
data = pd.DataFrame(list(cursor))

data.info()

data['product_url'].nunique()