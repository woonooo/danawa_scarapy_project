import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request as req
import pandas as pd
import time



# Chrome드라이버를 버전에 맞춰 다운받아 같은 폴더에 저장
driver = webdriver.Chrome('c:/workspace/danawa/chromedriver.exe')
driver.get('http://www.danawa.com/')  # 다나와 페이지 열기
time.sleep(2)

# 화장대를 검색
search = driver.find_element_by_xpath('//*[@id="AKCSearch"]')
search.send_keys('화장대')  # 검색창에 검색하고자하는 제품 입력
time.sleep(2)

driver.find_element_by_xpath('//*[@id="srchFRM_TOP"]/fieldset/div[1]/button').click()  # 검색버튼 클릭

# 상품에 대한 데이터프레임 틀 미리 만들어두기
df = pd.DataFrame(columns=['product_name', 'shoppingmall_price', 'made_by', 'date', 'review_count', 'review_point', 'form', 'with_in', 'closet', 'func', 'color', 'img_url'])

# 10페이지 반복하는 while문
page = 1
while page < 11:
    page += 1

# 화장대 페이지에서 각각의 화장대를 선택하는 반복문
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    li = soup.select('#productListArea > div.main_prodlist.main_prodlist_list > ul > li')
    data1=[]
    for i in soup.select('#productListArea > div.main_prodlist.main_prodlist_list > ul > li'):
        if i.has_attr('id'):
            data1.append(i['id'])

# 한 페이지에서 반복 -> 40개
# 상품하나 클릭
    for i in range(0,40):
        driver.find_element_by_css_selector('#'+data1[i]+'> div > div.prod_info > p > a').click()
        # 탭 이동 (다나와의 경우, 상품을 클릭시 새로운탭에서 제품창이 열림)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)

        # 제품명
        name = driver.find_element_by_xpath('//*[@id="blog_content"]/div[2]/div[1]/h3').text
        # 가격
        time.sleep(2)
        shoppingmall = []
        price = []
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        tr = soup2.select('div#blog_content > div.summary_info > div.detail_summary > div.summary_left > div.lowest_area > div.lowest_list > table > tbody.high_list > tr')
        for j in range(1,len(tr)+1):
            if driver.find_element_by_xpath('//*[@id="blog_content"]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr['+str(j)+']/td[1]/div/a').text == '':
                a = driver.find_element_by_xpath('//*[@id="blog_content"]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr['+str(j)+']/td[1]/div/a/img').get_attribute('alt')
            else:
                a = driver.find_element_by_xpath('//*[@id="blog_content"]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr['+str(j)+']/td[1]/div/a').text
            
            b = driver.find_element_by_xpath('//*[@id="blog_content"]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr['+str(j)+']/td[2]').text.rstrip().lstrip('최저가 ')                          
            if a != '':
                shoppingmall.append(a)
                price.append(b)

        shopping = dict(zip(shoppingmall, price))

        # 사진
        img_url1 = driver.find_element_by_xpath('//*[@id="baseImage"]').get_attribute('src')
        # req.urlretrieve(img_url1, 'c:/danawa/image'+str(i)+'.jpg')  # 사진을 저장하는 코드이지만 용량문제로 저장을 하지 않겠음
        # 평점, 리뷰수
        point = driver.find_element_by_xpath('//*[@id="productReviewArea"]/div[1]/a').text.lstrip('상품리뷰 ')[0:3]
        count = driver.find_element_by_xpath('//*[@id="productReviewArea"]/div[1]/a').text.lstrip('상품리뷰 ')[6:].rstrip(')')

        time.sleep(2)

        # 제조회사
        made_by1 = driver.find_element_by_xpath('//*[@id="productDescriptionArea"]/div/div[1]/table/tbody/tr[1]/td[1]').text
        # 등록년월
        date1 = driver.find_element_by_xpath('//*[@id="productDescriptionArea"]/div/div[1]/table/tbody/tr[1]/td[2]').text
        time.sleep(2)
        # 수납정보
        info2 = driver.find_element_by_xpath('//*[@id="blog_content"]/div[2]/div[1]/div/div[1]/div/dl/dd/div/div').text
        if '형태' in info2:
            form1 = info2[info2.find('형태')+4 : ][:info2[info2.find('형태')+4:].find(' /')]
        if '포함' in info2:
            with_in1 = info2[info2.find('포함')+4 : ][:info2[info2.find('포함')+4:].find(' /')]
        if '하단수납칸수' in info2:
            closet1 = info2[info2.find('하단수납칸수')+7 : ][:info2[info2.find('하단수납칸수')+7:].find(' /')]
        if '기능' in info2:
            func1 = info2[info2.find('기능')+4 : ][:info2[info2.find('기능')+4:].find(' /')]
        if '색상' in info2:
            color1 = info2[info2.find('색상')+4 : ]

        time.sleep(2)

        df = df.append({'product_name': name, 'shoppingmall_price': shopping, 'made_by':made_by1, 'date':date1, 'review_count': count, 'review_point': point,
        'form':form1, 'with_in': with_in1, 'closet': closet1, 'func':func1, 'color':color1, 'img_url':img_url1}, ignore_index=True)

        print(len(df))

        # 수집하던 페이지 닫기
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)
    
    driver.find_element_by_xpath('//*[@id="productListArea"]/div[4]/div/div/a['+str(page)+']').click()
    time.sleep(2)
driver.close()

driver.close()

# mongoDB의 '_id'는 건들이지 말아야한다는 사실을 알기전 건들임..^^ 다시는 건들이지말고 새로운 'id'변수를 추가하자
df['_id'] = pd.Series(range(1,401))

df.head(3)

# 데이터프레임의 파일을 몽고DB에 넣기 위해 딕셔너리형으로 변환
df_dict = df.to_dict('records')
df_dict[:3]

import pymongo
conn = pymongo.MongoClient("")
mydb = conn['']
SeleniumData = mydb['']

# 한번에 insert하는 insert_many를 이용
data_insert = SeleniumData.insert_many(df_dict)

print(data_insert.inserted_ids)