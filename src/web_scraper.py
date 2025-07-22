"""
網頁爬取模組 - 處理 Selenium 相關的網頁爬取功能
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .config import CHROME_OPTIONS, SCRAPING_CONFIG, SELECTORS


def create_driver():
    """創建 Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    for option in CHROME_OPTIONS:
        options.add_argument(option)
    return webdriver.Chrome(options=options)


def get_advisors(driver, dept_uuid):
    """獲取系所的所有指導教授"""
    advisors = []
    page = 1
    max_pages = SCRAPING_CONFIG['MAX_PAGES']
    consecutive_empty_pages = 0
    max_empty_pages = SCRAPING_CONFIG['MAX_EMPTY_PAGES']
    
    while page <= max_pages and consecutive_empty_pages < max_empty_pages:
        url = f'https://thesis.lib.nycu.edu.tw/browse/advisor?scope={dept_uuid}&bbm.page={page}'
        print(f"\n正在掃描第 {page} 頁...")
        
        try:
            driver.get(url)
            # 確保頁面完全載入
            driver.execute_script("return document.readyState") == "complete"
            time.sleep(SCRAPING_CONFIG['SLEEP_TIME']['PAGE_LOAD'])
            
            # 確保視窗焦點（無頭模式下仍有效）
            driver.execute_script("window.focus();")
            
            # 等待教授連結出現
            wait = WebDriverWait(driver, SCRAPING_CONFIG['WAIT_TIME'])
            try:
                advisor_links = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS['ADVISOR_LINKS']))
                )
                
                if not advisor_links:
                    consecutive_empty_pages += 1
                    print(f"第 {page} 頁沒有找到教授連結（連續空頁: {consecutive_empty_pages}）")
                    page += 1
                    continue
                
                # 重置連續空頁計數
                consecutive_empty_pages = 0
                
                # 收集此頁的教授資訊
                for link in advisor_links:
                    try:
                        name = link.text.strip()
                        href = link.get_attribute('href')
                        
                        # 只收集中文名字（包含至少兩個中文字）
                        chinese_chars = [char for char in name if '\u4e00' <= char <= '\u9fff']
                        if len(chinese_chars) >= 2:
                            print(f"找到教授：{name}")
                            advisors.append({
                                'name': name,
                                'url': href
                            })
                    except Exception as e:
                        print(f"處理教授連結時出錯: {str(e)}")
                        continue
                
                print(f"第 {page} 頁掃描完成")
                
                # 檢查是否有下一頁按鈕且未被禁用
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, SELECTORS['NEXT_BUTTON'])
                    parent_li = next_button.find_element(By.XPATH, '..')  # 獲取父元素 li
                    
                    # 檢查父元素是否有 disabled class
                    if 'disabled' in parent_li.get_attribute('class'):
                        print("\n已到達最後一頁")
                        break
                    else:
                        page += 1
                        print(f"繼續掃描下一頁...")
                        
                except Exception as e:
                    print(f"\n找不到下一頁按鈕，停止掃描: {str(e)}")
                    break
                    
            except Exception as e:
                consecutive_empty_pages += 1
                print(f"在第 {page} 頁處理教授連結時出錯: {str(e)}（連續空頁: {consecutive_empty_pages}）")
                page += 1
                continue
                
        except Exception as e:
            consecutive_empty_pages += 1
            print(f"訪問第 {page} 頁時出錯: {str(e)}（連續空頁: {consecutive_empty_pages}）")
            page += 1
            continue
    
    if consecutive_empty_pages >= max_empty_pages:
        print(f"\n連續 {max_empty_pages} 頁沒有找到教授，停止掃描")
    
    return advisors


def get_advisor_papers(driver, advisor_url):
    """獲取教授的論文列表"""
    papers = []
    page = 1
    max_pages = 50  # 論文頁面較少，設定較小的最大頁數
    
    while page <= max_pages:
        # 如果 URL 已經包含參數，則加上頁碼
        if 'bbm.return=' in advisor_url:
            url = advisor_url.replace('bbm.return=', f'bbm.page={page}&bbm.return=')
        else:
            url = f"{advisor_url}&bbm.page={page}"
        
        print(f"正在掃描教授論文第 {page} 頁...")
        
        try:
            driver.get(url)
            time.sleep(SCRAPING_CONFIG['SLEEP_TIME']['ADVISOR_PAPERS'])
            
            # 等待論文連結出現
            wait = WebDriverWait(driver, 10)
            try:
                paper_links = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS['PAPER_LINKS']))
                )
                
                if not paper_links:
                    print(f"第 {page} 頁沒有找到論文，結束掃描")
                    break
                
                # 收集此頁的論文資訊
                for link in paper_links:
                    title = link.text.strip()
                    href = link.get_attribute('href')
                    
                    if title:  # 確保標題不為空
                        papers.append({
                            'title': title,
                            'url': href
                        })
                        print(f"找到論文：{title}")
                
                # 檢查是否有下一頁
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, SELECTORS['NEXT_BUTTON'])
                    parent_li = next_button.find_element(By.XPATH, '..')
                    
                    if 'disabled' in parent_li.get_attribute('class'):
                        print("已到達論文列表最後一頁")
                        break
                    else:
                        page += 1
                        
                except Exception:
                    print("沒有更多論文頁面")
                    break
                    
            except Exception as e:
                print(f"處理論文列表時出錯: {str(e)}")
                break
                
        except Exception as e:
            print(f"訪問論文頁面時出錯: {str(e)}")
            break
    
    return papers


def select_advisor(advisors):
    """讓使用者選擇教授"""
    # 顯示所有教授
    print("\n找到的教授列表：")
    for i, advisor in enumerate(advisors, 1):
        print(f"{i}. {advisor['name']}")
    
    while True:
        search = input("\n請輸入教授姓名（或部分姓名）搜尋，輸入 0 返回：").strip()
        
        if search == "0":
            return None
            
        # 搜尋符合的教授
        matches = []
        for advisor in advisors:
            if search in advisor['name']:
                matches.append(advisor)
        
        if not matches:
            print("\n找不到符合的教授，請重新輸入！")
            continue
            
        # 如果找到多個符合的教授，讓使用者選擇
        if len(matches) > 1:
            print("\n找到多位符合的教授：")
            for i, advisor in enumerate(matches, 1):
                print(f"{i}. {advisor['name']}")
                
            choice = input("\n請選擇教授編號（0 返回）：").strip()
            if choice == "0":
                continue
                
            try:
                index = int(choice) - 1
                if 0 <= index < len(matches):
                    return matches[index]
            except ValueError:
                print("\n無效的選擇！")
                continue
        else:
            return matches[0]
