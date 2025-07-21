import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

def load_departments():
    """從 JSON 檔案載入所有學院和系所資料"""
    try:
        with open('departments_20250718_170425.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading departments: {str(e)}")
        return {}

def get_advisors(driver, dept_uuid):
    """獲取系所的所有指導教授"""
    advisors = []
    page = 1
    
    while True:
        url = f'https://thesis.lib.nycu.edu.tw/browse/advisor?scope={dept_uuid}&bbm.page={page}'
        print(f"\n正在掃描第 {page} 頁...")
        
        try:
            driver.get(url)
            time.sleep(3)  # 等待頁面載入
            
            # 等待教授連結出現
            wait = WebDriverWait(driver, 10)
            advisor_links = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.lead[href*="/browse/advisor"]'))
            )
            
            if not advisor_links:
                break
                
            # 收集此頁的教授資訊
            for link in advisor_links:
                name = link.text.strip()
                href = link.get_attribute('href')
                
                # 只收集中文名字（包含至少一個中文字）
                if any('\u4e00' <= char <= '\u9fff' for char in name):
                    advisors.append({
                        'name': name,
                        'url': href
                    })
            
            # 檢查是否有下一頁
            next_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Go to next page"]')
            if not next_buttons or 'disabled' in next_buttons[0].get_attribute('class'):
                break
                
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {str(e)}")
            break
    
    return advisors

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

def create_department_codes(all_departments):
    """建立系所編碼"""
    codes = {}
    college_code = 'A'
    
    for college_name, departments in all_departments.items():
        for i, dept in enumerate(departments, 1):
            code = f"{college_code}-{i}"
            codes[code] = (college_name, dept)
        college_code = chr(ord(college_code) + 1)
    
    return codes

def main():
    # 載入系所資料
    all_departments = load_departments()
    if not all_departments:
        print("無法載入系所資料")
        return
        
    # 初始化瀏覽器
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    
    try:
        # 建立系所編碼
        dept_codes = create_department_codes(all_departments)
        
        # 顯示系所列表
        current_college = None
        for code, (college_name, dept) in dept_codes.items():
            if college_name != current_college:
                print(f"\n{college_name}:")
                current_college = college_name
            print(f"{code}. {dept['name']}")
        
        # 選擇系所
        while True:
            dept_choice = input("\n請輸入系所編碼（例如 A-1）：").strip().upper()
            if dept_choice in dept_codes:
                college_name, department = dept_codes[dept_choice]
                break
            print("無效的系所編碼，請重新輸入！")
        
        print(f"\n開始掃描 {department['name']} 的教授列表...")
        
        # 獲取該系所的所有教授
        advisors = get_advisors(driver, department['uuid'])
        
        if not advisors:
            print("\n未找到任何教授資料")
            return
            
        print(f"\n共找到 {len(advisors)} 位教授")
        
        # 讓使用者搜尋教授
        while True:
            advisor = select_advisor(advisors)
            if advisor is None:
                break
                
            print(f"\n正在訪問 {advisor['name']} 的論文列表...")
            driver.get(advisor['url'])
            time.sleep(3)
            
            # 這裡可以加入爬取論文的邏輯
            # ...
            
            if input("\n是否繼續搜尋其他教授？(y/n): ").lower() != 'y':
                break
                
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
