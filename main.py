import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_departments():
    """從 JSON 檔案載入所有學院和系所資料"""
    try:
        with open('departments_20250718_170425.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading departments: {str(e)}")
        return {}

def get_college_choice(colleges):
    """讓使用者選擇學院"""
    # 建立學院列表
    college_list = list(colleges.keys())
    
    while True:
        print("\n請選擇要爬取的學院：")
        for i, college_name in enumerate(college_list, 1):
            print(f"{i}. {college_name}")
        print("0. 退出程式")
        
        choice = input(f"\n請輸入學院編號（0-{len(college_list)}）: ").strip()
        
        if choice == "0":
            return None
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(college_list):
                return college_list[index]
        except ValueError:
            pass
            
        print("\n無效的選擇，請重新輸入！")

def get_department_choice(departments):
    """讓使用者選擇系所"""
    while True:
        print("\n請選擇要爬取的系所：")
        for i, dept in enumerate(departments, 1):
            print(f"{i}. {dept['name']}")
        print("0. 返回學院選擇")
        
        choice = input(f"\n請輸入系所編號（0-{len(departments)}）: ").strip()
        
        if choice == "0":
            return None
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(departments):
                return departments[index]
        except ValueError:
            pass
            
        print("\n無效的選擇，請重新輸入！")

def main():
    global driver
    
    # 載入所有學院和系所資料
    all_departments = load_departments()
    if not all_departments:
        print("無法載入學院和系所資料")
        return
    
    while True:
        # 讓使用者選擇學院
        college_name = get_college_choice(all_departments)
        if college_name is None:  # 使用者選擇退出
            print("\n程式結束")
            break
            
        # 獲取該學院的系所列表
        departments = all_departments[college_name]
        if not departments:
            print(f"\n未找到{college_name}的系所資料")
            continue
            
        while True:
            # 讓使用者選擇系所
            department = get_department_choice(departments)
            if department is None:  # 使用者選擇返回
                break
                
            # 開始爬取選擇的系所資料
            print(f"\n開始爬取 {department['name']} 的論文資料...")
            
            # 訪問系所的論文頁面
            driver.get(department['url'])
            time.sleep(3)  # 等待頁面載入
            
            # 這裡可以加入爬取論文的邏輯
            # ...
            
            # 儲存結果
            filename = f"{department['name']}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            print(f"\n資料已儲存到 {filename}")
            
            # 詢問是否繼續爬取其他系所
            if input("\n是否繼續爬取其他系所？(y/n): ").lower() != 'y':
                break

if __name__ == "__main__":
    # 初始化瀏覽器
    options = webdriver.ChromeOptions()
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
