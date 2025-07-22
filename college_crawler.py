import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_colleges_from_homepage():
    """從主網頁爬取學院資料"""
    url = 'https://thesis.lib.nycu.edu.tw/home'
    colleges = []
    
    try:
        print(f"正在訪問主網頁: {url}")
        driver.get(url)
        
        # 等待頁面載入
        time.sleep(8)  # 增加等待時間
        
        # 等待 Angular 應用載入
        wait = WebDriverWait(driver, 45)  # 增加等待時間
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'ds-app')))
            print("Angular 應用已載入")
        except Exception as e:
            print(f"等待 Angular 應用載入時出錯: {str(e)}")
        
        # 再等待確保動態內容載入
        time.sleep(5)  # 增加等待時間
        
        # 滾動頁面確保所有內容載入
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 尋找學院連結 - 根據您提供的原始碼格式
        college_links = driver.find_elements(By.CSS_SELECTOR, 'a.lead.ng-star-inserted[href*="/communities/"]')
        print(f"找到的學院連結數量：{len(college_links)}")
        
        # 調試：列出所有找到的連結
        print("\n--- 調試資訊：所有找到的連結 ---")
        all_community_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/communities/"]')
        print(f"所有包含 /communities/ 的連結數量：{len(all_community_links)}")
        
        for i, link in enumerate(all_community_links):
            try:
                text = link.text.strip()
                href = link.get_attribute('href')
                class_attr = link.get_attribute('class')
                print(f"  {i+1}. 文字: '{text}', class: '{class_attr}', href: '{href}'")
            except Exception as e:
                print(f"  {i+1}. 處理連結時出錯: {str(e)}")
        print("--- 調試資訊結束 ---\n")
        
        # 批量處理所有找到的 communities 連結（優化版本）
        college_data = []
        seen_urls = set()  # 使用集合去重，提高效率
        
        for link in all_community_links:
            try:
                name = link.text.strip()
                href = link.get_attribute('href')
                
                # 不篩選，只要有文字內容和有效連結就加入（優化條件檢查）
                if name and href and '/communities/' in href and href not in seen_urls:
                    seen_urls.add(href)
                    # 使用 rsplit 提高效率
                    uuid = href.rsplit('/', 1)[-1]
                    college_data.append({
                        'name': name,
                        'id': uuid,
                        'url': href
                    })
                    print(f"找到: {name}")
                    
            except Exception as e:
                print(f"處理連結時出錯: {str(e)}")
                continue
        
        return college_data
        
    except Exception as e:
        print(f"爬取學院資料時出錯: {str(e)}")
        return []

def save_colleges_to_json(colleges):
    """將所有找到的 communities 資料儲存到 college_links.json（優化版本）"""
    # 預先分配列表大小，提高效率
    college_data = [{
        "text": "學院和系所",
        "href": "https://thesis.lib.nycu.edu.tw/community-list",
        "router_link": "/community-list",
        "class": "nav-item nav-link"
    }]
    
    # 使用列表推導式，更高效
    college_data.extend([
        {
            "text": college['name'],
            "href": college['url'],
            "router_link": f"/communities/{college['id']}",
            "class": "dropdown-item"
        }
        for college in colleges
    ])
    
    # 一次性寫入檔案
    with open('college_links.json', 'w', encoding='utf-8') as f:
        json.dump(college_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n已儲存 {len(college_data)} 筆資料到 college_links.json")
    print(f"包含 {len(colleges)} 個學院/社群")
    return len(college_data)

def main():
    global driver
    
    print("開始爬取所有 communities 資料...")
    
    # 從主網頁爬取所有 communities 資料
    colleges = fetch_colleges_from_homepage()
    
    if not colleges:
        print("未找到任何資料")
        return
    
    print(f"\n共找到 {len(colleges)} 個項目:")
    for college in colleges:
        print(f"- {college['name']}")
    
    # 儲存所有資料到 JSON 檔案
    save_colleges_to_json(colleges)
    
    print(f"\n資料爬取完成！共儲存 {len(colleges)} 個項目到 college_links.json")

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
