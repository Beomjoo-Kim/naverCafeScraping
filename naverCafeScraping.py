import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm

from collections import deque

import pyperclip
import json
import pickle

import csv

# csv 파일 생성
f = open("./naverCafeScappedData.csv","w")

# data column 정의
data = [['prompt', 'completion']]

# csv writer
writer = csv.writer(f);


op = webdriver.ChromeOptions()
chrome_service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service = chrome_service, options=op)


driver.get("https://nid.naver.com/nidlogin.login")

# javascript 코드 : enter 키 입력시 alert
script = """
alert("아이디, 패스워드 입력 후 console에서 엔터키 입력");
"""
driver.execute_script(script)

# 계정 정보 입력 후 키입력 대기
input("브라우저에 아이디, 패스워드 입력 후 엔터키");

try: 
    driver.find_element(By.XPATH,'//*[@id="log.login"]').click()
    #time.sleep(3)
except: 
    print("no such element")          #예외처리

script = """
window.location.href = 'https://cafe.naver.com/stegrnd';
"""

# 카페로 이동
driver.execute_script(script)

# 메뉴별 key setting
board_dict = {
    "Global config" : "32",
    "Form Manager" : "29",
    "List Manager" : "18",
    "Relation Manager" : "19",
    "Control Manager" : "31",
    "자바스크립트" : "12",
    "Data Manager & SQL" : "28",
    "SLM/KPI" : "40",
    "PPMS" : "48",
    "모바일환경" : "45",
    "인터페이스":"47",
    "클라우드" : "77",
    "신규/개선 Atom" : "78",
    "기타" : "46"
    }
board_keys = list(board_dict.keys())
maxContentCnt = 1900
# 메뉴로 이동
# f"#menuLink{board_dict[board_keys[n]]}"
for boardNm in board_keys :
    board = driver.find_element(By.CSS_SELECTOR, f"#menuLink{board_dict[boardNm]}")
    driver.implicitly_wait(1)
    board.click()

    # ifame으로 전환
    driver.switch_to.frame("cafe_main")

    # 해당 게시판의 첫번째 게시물로 이동
    # 게시물 XPath -> [@id="main-area"]/div[4]/table/tbody/tr[n]/td[1]/div[2]/a[1]
    driver.find_element(By.XPATH, '//*[@id="main-area"]/div[4]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]').click()
    time.sleep(0.5)

    for i in tqdm(range(1, maxContentCnt)):
        try :  
            # data scrap
            time.sleep(0.5)
            title = driver.find_element(By.CLASS_NAME, 'title_text').text
            content = driver.find_element(By.CLASS_NAME, 'se-main-container').text
            data.append([title, content])

            # 다음글로 이동
            driver.find_element(By.CSS_SELECTOR, "#app > div > div > div.ArticleTopBtns > div.right_area > a.BaseButton.btn_next.BaseButton--skinGray.size_default").click()
        except NoSuchElementException :
            # 다음글이 없을 경우
            print(f"no more articles in {boardNm} : {i}")
            break
        except Exception as e:
            print(f"an error occurred : {e}")
            pass
        
    
    # iframe 내로 driver를 전환했으므로, 메뉴를 선택하기 위해선 다시 돌려주어야 한다.
    driver.switch_to.default_content()

# scrapped data write
print(f"scrapped item : {data.count}")
writer.writerows(data)
f.close
driver.quit()