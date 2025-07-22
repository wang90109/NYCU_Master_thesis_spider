import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_colleges():
    """載入學院資料（優化版本）"""
    try:
        with open('college_links.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 使用列表推導式，更高效
        colleges = [
            {
                'name': item['text'],
                'id': item['href'].split('/')[-1]
            }
            for item in data
            if 'College' in item.get('text', '') and 
               item.get('href', '').startswith('https://thesis.lib.nycu.edu.tw/communities/')
        ]
        return colleges
    except Exception as e:
        print(f"載入學院資料時出錯: {str(e)}")
        return []

def fetch_departments(college_uuid):
    """抓取特定學院的系所資料（支援分頁）"""
    departments = []
    page = 1
    max_pages = 20  # 設定最大頁數防止無限循環
    consecutive_empty_pages = 0  # 連續空頁計數
    max_empty_pages = 3  # 最多允許3頁連續空頁
    
    while page <= max_pages and consecutive_empty_pages < max_empty_pages:
        # 構建帶分頁的 URL
        if page == 1:
            url = f'https://thesis.lib.nycu.edu.tw/communities/{college_uuid}'
        else:
            url = f'https://thesis.lib.nycu.edu.tw/communities/{college_uuid}?cmcl.page={page}'
        
        print(f"\n正在掃描第 {page} 頁: {url}")
        
        try:
            # 訪問頁面
            driver.get(url)
            time.sleep(3)
            
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
            print(f"第 {page} 頁找到的連結數量：{len(dept_links)}")

            if not dept_links:
                consecutive_empty_pages += 1
                print(f"第 {page} 頁沒有找到系所連結（連續空頁: {consecutive_empty_pages}）")
                page += 1
                continue
            
            # 重置連續空頁計數
            consecutive_empty_pages = 0
            page_departments = []

            # 批量處理連結，避免重複查詢
            for i, link in enumerate(dept_links, 1):
                try:
                    # 取得系所名稱和連結
                    name = link.text.strip()
                    href = link.get_attribute('href')
                    
                    print(f"  連結 {i}: 名稱='{name}', URL='{href}'")
                    
                    # 更寬鬆的篩選條件：只要有名稱和是 collections 連結就接受
                    if name and 'collections' in href:
                        # 從完整 URL 中提取 UUID（使用 rsplit 更高效）
                        uuid = href.rsplit('/', 1)[-1]
                        page_departments.append({
                            'name': name,
                            'uuid': uuid,
                            'url': href
                        })
                        print(f"    ✓ 找到系所：{name}")
                    else:
                        print(f"    ✗ 跳過（名稱='{name}', collections在URL中={'collections' in href if href else False}）")
                        
                except Exception as e:
                    print(f"  連結 {i}: 處理時出錯: {str(e)}")
                    continue
            
            # 將此頁的系所加入總列表
            departments.extend(page_departments)
            print(f"第 {page} 頁掃描完成，找到 {len(page_departments)} 個系所")
            
            # 檢查是否有下一頁
            try:
                # 檢查是否有可以點擊的下一頁按鈕
                next_buttons = driver.find_elements(By.CSS_SELECTOR, 'a.page-link[aria-label="Next"]')
                if next_buttons:
                    next_button = next_buttons[0]
                    parent_element = next_button.find_element(By.XPATH, '..')
                    parent_class = parent_element.get_attribute('class') or ""
                    
                    # 檢查按鈕是否可以點擊（沒有 disabled class）
                    if 'disabled' not in parent_class:
                        print(f"找到可點擊的下一頁按鈕，繼續掃描...")
                        page += 1
                        time.sleep(2)  # 避免請求太頻繁
                    else:
                        print(f"\n下一頁按鈕已禁用，停止掃描")
                        break
                else:
                    print(f"\n找不到下一頁按鈕，停止掃描")
                    break
                    
            except Exception as e:
                print(f"\n檢查下一頁時出錯，停止掃描: {str(e)}")
                break
                
        except Exception as e:
            consecutive_empty_pages += 1
            print(f"訪問第 {page} 頁時出錯: {str(e)}（連續空頁: {consecutive_empty_pages}）")
            page += 1
            continue
    
    if consecutive_empty_pages >= max_empty_pages:
        print(f"\n連續 {max_empty_pages} 頁沒有找到系所，停止掃描")
    
    print(f"\n學院掃描完成，總共找到 {len(departments)} 個系所")
    return departments

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
    
    # 將所有資料儲存到JSON檔案（可複寫的固定檔名）
    output_file = 'departments.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_departments, f, ensure_ascii=False, indent=2)
    
    print(f"\n所有系所資料已儲存到 {output_file}")
    print(f"總共處理 {len(colleges)} 個學院，找到 {sum(len(depts) for depts in all_departments.values())} 個系所")

if __name__ == "__main__":
    # 初始化瀏覽器 - 改進設定以確保穩定性
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        main()
    finally:
        # 確保瀏覽器正確關閉
        driver.quit()
