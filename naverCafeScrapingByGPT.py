import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import csv

# chatGPT가 생성한 소스코드

# CSV 파일 생성 및 열기
with open("./naverCafeScappedData.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # 데이터 컬럼 정의
    writer.writerow(['prompt', 'completion'])

    op = Options()
    chrome_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=op)

    driver.get("https://nid.naver.com/nidlogin.login")

    # 자바스크립트 코드: Enter 키 입력시 alert
    script = """
    alert("아이디, 패스워드 입력 후 console에서 엔터키 입력");
    """
    driver.execute_script(script)

    # 계정 정보 입력 후 키 입력 대기
    input("브라우저에 아이디, 패스워드 입력 후 엔터키")

    try:
        driver.find_element(By.XPATH, '//*[@id="log.login"]').click()
    except NoSuchElementException:
        print("로그인 버튼을 찾을 수 없습니다.")

    script = """
    window.location.href = 'https://cafe.naver.com/stegrnd';
    """
    # 카페로 이동
    driver.execute_script(script)

    # 메뉴별 key setting
    board_dict = {
        "Global config": "32",
        "Form Manager": "29",
        "List Manager": "18",
        "Relation Manager": "19",
        "Control Manager": "31",
        "자바스크립트": "12",
        "Data Manager & SQL": "28",
        "SLM/KPI": "40",
        "PPMS": "48",
        "모바일환경": "45",
        "인터페이스": "47",
        "클라우드": "77",
        "신규/개선 Atom": "78",
        "기타": "46"
    }
    board_keys = list(board_dict.keys())
    maxContentCnt = 10

    # 메뉴로 이동
    for boardNm in board_keys:
        board = driver.find_element(By.CSS_SELECTOR, f"#menuLink{board_dict[boardNm]}")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#menuLink{board_dict[boardNm]}")))
        board.click()

        # iframe으로 전환
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "cafe_main")))

        # 해당 게시판의 첫 번째 게시물로 이동
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-area"]/div[4]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]'))).click()
        time.sleep(0.5)

        for i in tqdm(range(1, maxContentCnt)):
            try:
                # 데이터 스크랩
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'title_text')))
                title = driver.find_element(By.CLASS_NAME, 'title_text').text
                content = driver.find_element(By.CLASS_NAME, 'se-main-container').text
                writer.writerow([title, content])

                # 다음 글로 이동
                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div > div > div.ArticleTopBtns > div.right_area > a.BaseButton.btn_next.BaseButton--skinGray.size_default")))
                next_button.click()
            except NoSuchElementException:
                print(f"더 이상 게시물이 없습니다: {i-1}")
                break
            except Exception as e:
                print(f"오류 발생: {e}")
                pass

        # 프레임에서 나가기
        driver.switch_to.default_content()

    driver.quit()
