import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_colleges():
    """載入學院資料"""
    with open('college_links.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        # 篩選出學院資料
        colleges = []
        for item in data:
            if 'College' in item.get('text', '') and item.get('href', '').startswith('https://thesis.lib.nycu.edu.tw/communities/'):
                college_uuid = item['href'].split('/')[-1]
                colleges.append({
                    'name': item['text'],
                    'id': college_uuid
                })
        return colleges

def fetch_departments(college_uuid):
    """抓取特定學院的系所資料"""
    # 使用 communities URL 來訪問學院頁面
    url = f'https://thesis.lib.nycu.edu.tw/communities/{college_uuid}'
    departments = []
    
    try:
        # 使用 Selenium 取得動態內容
        driver.get(url)
        
        print(f"正在訪問 URL: {url}")
        
        # 等待頁面基本元素載入
        time.sleep(2)
        
        # 等待 ds-app 元素出現（Angular 應用的根元素）
        wait = WebDriverWait(driver, 30)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'ds-app')))
            print("Angular 應用已載入")
        except Exception as e:
            print(f"等待 Angular 應用載入時出錯: {str(e)}")
        
        # 再等待一下確保動態內容載入
        time.sleep(5)
        
        # 使用精確的選擇器來找到系所連結
        dept_links = driver.find_elements(By.CSS_SELECTOR, 'a.lead.ng-star-inserted[ng-reflect-target="_self"][href*="/collections/"]')
        print(f"\n找到的連結數量：{len(dept_links)}")

        for link in dept_links:
            try:
                # 取得系所名稱和連結
                name = link.text.strip()
                href = link.get_attribute('href')
                router_link = link.get_attribute('ng-reflect-router-link')
                print(f"\n找到連結：")
                print(f"名稱: {name}")
                print(f"HREF: {href}")
                print(f"Router Link: {router_link}")
                
                # 只處理包含學系名稱的連結
                if name and '::' in name and 'collections' in href:
                    # 從完整 URL 中提取 UUID
                    uuid = href.split('/')[-1]
                    departments.append({
                        'name': name,
                        'uuid': uuid,
                        'url': href
                    })
            except Exception as e:
                print(f"處理連結時出錯: {str(e)}")
                continue
        
        return departments
        
    except Exception as e:
        print(f"Error fetching departments: {str(e)}")
        return []

def main():
    global driver
    # 載入學院資料
    colleges = load_colleges()
    
    # 用於儲存所有學院的系所資料
    all_departments = {}
    
    # 對每個學院進行爬取
    for college in colleges:
        college_name = college.get('name', '')
        college_uuid = college.get('id', '')
        print(f"\n正在爬取 {college_name} 的系所資料...")
        
        # 抓取該學院的系所
        departments = fetch_departments(college_uuid)
        
        # 儲存該學院的系所資料
        all_departments[college_name] = departments
        
        # 顯示找到的系所
        print(f"找到 {len(departments)} 個系所：")
        for dept in departments:
            print(f"- {dept['name']}")
        
        # 避免請求太頻繁
        time.sleep(1)
    
    # 將所有資料儲存到JSON檔案
    output_file = f'departments_{time.strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_departments, f, ensure_ascii=False, indent=2)
    
    print(f"\n所有系所資料已儲存到 {output_file}")

if __name__ == "__main__":
    # 初始化瀏覽器
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 暫時取消無頭模式，方便觀察
    options.add_argument('--disable-gpu')  # 禁用GPU加速
    options.add_argument('--no-sandbox')  # 禁用沙箱
    options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
    options.add_argument('--window-size=1920,1080')  # 設置窗口大小
    driver = webdriver.Chrome(options=options)
    
    try:
        main()
    finally:
        # 確保瀏覽器正確關閉
        driver.quit()
