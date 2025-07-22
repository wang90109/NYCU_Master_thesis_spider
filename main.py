<<<<<<< HEAD
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
        with open('departments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading departments: {str(e)}")
        return {}

def get_advisors(driver, dept_uuid):
    """獲取系所的所有指導教授"""
    advisors = []
    page = 1
    max_pages = 500  # 設定最大頁數防止無限循環
    consecutive_empty_pages = 0  # 連續空頁計數
    max_empty_pages = 3  # 最多允許3頁連續空頁
    
    while page <= max_pages and consecutive_empty_pages < max_empty_pages:
        url = f'https://thesis.lib.nycu.edu.tw/browse/advisor?scope={dept_uuid}&bbm.page={page}'
        print(f"\n正在掃描第 {page} 頁...")
        
        try:
            driver.get(url)
            # 確保頁面完全載入
            driver.execute_script("return document.readyState") == "complete"
            time.sleep(5)
            
            # 確保視窗焦點（無頭模式下仍有效）
            driver.execute_script("window.focus();")
            
            # 等待教授連結出現
            wait = WebDriverWait(driver, 15)  # 增加等待時間
            try:
                advisor_links = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.lead.ng-star-inserted[href*="/browse/advisor"]'))
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
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link[aria-label="Next"]')
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

def get_paper_details(driver, paper_url):
    """獲取論文的詳細資訊，包括學生資訊（優化版本）"""
    paper_details = {
        'degree': '',
        'student_id': '',
        'publication_date': '',
        'keywords': [],
        'study_duration': ''
    }
    
    try:
        driver.get(paper_url)
        time.sleep(3)
        
        # 等待頁面載入
        wait = WebDriverWait(driver, 10)
        
        # 一次性查找所有需要的元素
        spans = driver.find_elements(By.CSS_SELECTOR, 'span.dont-break-out.preserve-line-breaks.ng-star-inserted')
        
        # 預先編譯正規表達式和建立集合
        punctuation_chars = {'。', '，', '、', '；', '：', '！', '？', '(', ')', '[', ']', '{', '}', 
                           '"', "'", '「', '」', '『', '』', '《', '》', '〈', '〉', '-', '_', 
                           '=', '+', '*', '/', '\\', '|', '@', '#', '$', '%', '^', '&', '~', '`'}
        
        keywords_temp = []
        
        for span in spans:
            text = span.text.strip()
            if not text:
                continue
            
            # 使用更高效的條件檢查順序
            if text in ('碩士', '博士'):
                paper_details['degree'] = text
            elif (text.isdigit() and len(text) == 9 and text[0] == '3'):
                paper_details['student_id'] = text
            elif ('/' in text and text.count('/') == 2):
                # 快速日期格式檢查
                parts = text.split('/')
                if len(parts[0]) == 4 and parts[0].isdigit():
                    paper_details['publication_date'] = text
            elif (3 <= len(text) <= 20 and 
                  not text.isdigit() and 
                  not any(char in punctuation_chars for char in text) and
                  (any(c.isalpha() for c in text) or any('\u4e00' <= c <= '\u9fff' for c in text))):
                keywords_temp.append(text)
        
        paper_details['keywords'] = keywords_temp
        
        # 備用學號搜尋（只在需要時執行）
        if not paper_details['student_id']:
            all_spans = driver.find_elements(By.TAG_NAME, 'span')
            for span in all_spans:
                text = span.text.strip()
                if text.isdigit() and len(text) == 9 and text[0] == '3':
                    paper_details['student_id'] = text
                    break
        
        # 計算修業年限
        if paper_details['student_id'] and paper_details['publication_date']:
            paper_details['study_duration'] = calculate_study_duration(
                paper_details['student_id'], 
                paper_details['publication_date']
            )
        
    except Exception as e:
        print(f"獲取論文詳細資訊時出錯: {str(e)}")
    
    return paper_details

def calculate_study_duration(student_id, publication_date):
    """計算修業年限（優化版本）"""
    try:
        # 預先導入，避免重複導入
        from datetime import datetime
        
        # 快速學號格式檢查
        if len(student_id) != 9 or student_id[0] != '3':
            return "學號格式錯誤"
        
        # 直接提取年份數字，避免切片操作
        year_suffix = int(student_id[1:3])
        ad_year = 2011 + year_suffix  # 簡化計算：100 + year_suffix + 1911
        
        # 快速分割日期
        pub_parts = publication_date.split('/')
        grad_year = int(pub_parts[0])
        grad_month = int(pub_parts[1])
        
        # 檢查未來日期（優化版本）
        if grad_year > 2025:  # 使用固定年份比較，避免 datetime.now() 調用
            grad_year -= 5
        
        # 直接計算總月數
        total_months = (grad_year - ad_year) * 12 + (grad_month - 9)
        
        # 快速格式化
        if total_months <= 0:
            return f"總計{total_months}個月"
        
        years, months = divmod(total_months, 12)
        
        if years > 0 and months > 0:
            return f"{years}年{months}個月"
        elif years > 0:
            return f"{years}年"
        else:
            return f"{months}個月"
            
    except (ValueError, IndexError):
        return "計算失敗"

def get_advisor_papers(driver, advisor_url):
    """獲取教授的論文列表"""
    papers = []
    page = 1
    max_pages = 50  # 設定最大頁數
    
    while page <= max_pages:
        # 如果 URL 已經包含參數，則加上頁碼
        if 'bbm.return=' in advisor_url:
            url = advisor_url.replace('bbm.return=', f'bbm.page={page}&bbm.return=')
        else:
            url = f"{advisor_url}&bbm.page={page}"
        
        print(f"正在掃描教授論文第 {page} 頁...")
        
        try:
            driver.get(url)
            time.sleep(3)
            
            # 等待論文連結出現
            wait = WebDriverWait(driver, 10)
            try:
                paper_links = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.lead.item-list-title[href*="/items/"]'))
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
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link[aria-label="Next"]')
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

def parse_duration_to_months(duration_str):
    """將修業年限字符串轉換為月數（修復版本）"""
    if not duration_str:
        return 0
    
    total_months = 0
    
    # 處理年份
    if '年' in duration_str:
        try:
            year_part = duration_str.split('年')[0]
            if year_part.isdigit():
                total_months += int(year_part) * 12
        except:
            pass
    
    # 處理月份
    if '月' in duration_str:
        try:
            if '年' in duration_str:
                # 如果有年份，取年份後面的月份部分
                month_part = duration_str.split('年')[1].split('月')[0]
            else:
                # 如果沒有年份，直接取月份部分
                month_part = duration_str.split('月')[0]
            
            # 移除可能的「個」字
            month_part = month_part.replace('個', '')
            
            if month_part.isdigit():
                total_months += int(month_part)
        except:
            pass
    
    return total_months

def format_months_to_duration(total_months):
    """將月數轉換為年月格式"""
    years = total_months // 12
    months = total_months % 12
    
    if years > 0 and months > 0:
        return f"{years}年{months}個月"
    elif years > 0:
        return f"{years}年"
    elif months > 0:
        return f"{months}個月"
    else:
        return "0個月"

def calculate_average_duration(master_students):
    """計算平均修業年限（顯示年月格式）"""
    if not master_students:
        return "無法計算"
    
    # 收集所有有效的修業月數
    total_months = 0
    valid_count = 0
    
    for student in master_students:
        duration_months = parse_duration_to_months(student['study_duration'])
        if duration_months > 0:
            total_months += duration_months
            valid_count += 1
    
    if valid_count == 0:
        return "無法計算"
    
    # 計算平均月數
    avg_months = total_months / valid_count
    
    # 轉換為年和月
    avg_years = int(avg_months // 12)
    avg_remaining_months = round(avg_months % 12)
    
    # 處理四捨五入後可能的12個月情況
    if avg_remaining_months >= 12:
        avg_years += avg_remaining_months // 12
        avg_remaining_months = avg_remaining_months % 12
    
    # 格式化輸出 - 確保顯示月份
    if avg_years > 0 and avg_remaining_months > 0:
        return f"{avg_years}年{avg_remaining_months}個月"
    elif avg_years > 0 and avg_remaining_months == 0:
        return f"{avg_years}年"
    elif avg_years == 0 and avg_remaining_months > 0:
        return f"{avg_remaining_months}個月"
    else:
        return f"{round(avg_months)}個月"  # 如果都是0，直接顯示原始月數

def display_student_details(advisor_name, master_students):
    """顯示學生詳細資訊"""
    print(f"\n📊 {advisor_name} 碩士生詳細資訊:")
    print(f"   碩士生總數: {len(master_students)} 人 (修業年限 ≤ 4年)")
    print("=" * 80)
    
    # 顯示每位學生的資訊
    for i, student in enumerate(master_students, 1):
        print(f"\n{i}. 論文標題: {student['title']}")
        print(f"   學號: {student['student_id']}")
        print(f"   發表日期: {student['publication_date']}")
        print(f"   修業年限: {student['study_duration']}")
        if student['keywords']:
            print(f"   關鍵詞: {', '.join(student['keywords'][:5])}")
        print("-" * 40)

def analyze_keywords(master_students):
    """分析關鍵詞統計（優化版本）"""
    # 使用 Counter 進行高效計數
    from collections import Counter
    
    # 一次性收集所有關鍵詞
    all_keywords = []
    for student in master_students:
        all_keywords.extend(student['keywords'])
    
    # 使用 Counter 高效計數
    keyword_count = Counter(all_keywords)
    
    # 預先定義排除詞彙集合（查找更快）
    exclude_words = {'立即公開', '不公開', '一年後公開', '兩年後公開', '三年後公開', '五年後公開', 
                   '暫不公開', '公開', '開放', '授權', '全文', '論文', '碩士', '博士', 'Master', 'PhD'}
    
    chinese_names = []
    filtered_keywords = []
    
    # 只遍歷一次，使用 most_common 直接獲取排序結果
    for keyword, count in keyword_count.most_common():
        if keyword in exclude_words:
            continue
        
        # 優化中文人名判斷
        if (2 <= len(keyword) <= 4 and 
            keyword.isalpha() and  # 更快的字母檢查
            all('\u4e00' <= char <= '\u9fff' for char in keyword) and
            len(chinese_names) < 5):
            chinese_names.append((keyword, count))
        elif (',' in keyword and keyword.count(',') == 1):
            continue  # 跳過英文人名
        else:
            filtered_keywords.append((keyword, count))
    
    return chinese_names, filtered_keywords[:10]  # 直接截取前10個

def display_statistics(advisor_name, master_students):
    """顯示統計摘要"""
    if not master_students:
        print(f"\n{advisor_name} 沒有找到符合條件的碩士論文（有學號且修業年限 ≤ 4年）")
        return
    
    # 顯示學生詳細資訊
    display_student_details(advisor_name, master_students)
    
    # 計算並顯示平均修業年限
    avg_duration = calculate_average_duration(master_students)
    
    print(f"\n📈 統計摘要:")
    print(f"   平均修業年限: {avg_duration}")
    
    # 分析關鍵詞
    chinese_names, filtered_keywords = analyze_keywords(master_students)
    
    # 顯示指導教授
    if chinese_names:
        print(f"   指導教授 (前5位):")
        for name, count in chinese_names:
            print(f"     - {name} ({count}次)")
    
    # 顯示研究關鍵詞
    if filtered_keywords:
        print(f"   研究關鍵詞 (前10個):")
        for keyword, count in filtered_keywords[:10]:
            print(f"     - {keyword} ({count}次)")

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
        
    # 初始化瀏覽器 - 加強穩定性設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式，避免視窗狀態影響
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')  # 設定虛擬視窗大小
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被檢測
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
            
            # 獲取教授的論文列表
            papers = get_advisor_papers(driver, advisor['url'])
            
            if not papers:
                print(f"\n{advisor['name']} 沒有找到任何論文")
            else:
                print(f"\n{advisor['name']} 共有 {len(papers)} 篇論文")
                print("正在分析論文詳細資訊...")
                print("=" * 80)
                
                # 統計資料（優化版本）
                master_students = []
                
                # 預先篩選有效論文，避免無效查詢
                valid_papers = []
                for paper in papers:
                    if paper.get('title'):  # 確保標題不為空
                        valid_papers.append(paper)
                
                print(f"有效論文數量：{len(valid_papers)}")
                
                # 批量處理論文
                for i, paper in enumerate(valid_papers, 1):
                    print(f"分析第 {i}/{len(valid_papers)} 篇論文...")
                    
                    # 獲取論文詳細資訊
                    details = get_paper_details(driver, paper['url'])
                    
                    # 只處理有學號的碩士論文，且修業年限不超過4年（優化判斷）
                    if (details['degree'] == '碩士' and 
                        details['student_id'] and 
                        details['study_duration']):
                        
                        # 快速檢查修業年限
                        duration_months = parse_duration_to_months(details['study_duration'])
                        
                        if 0 < duration_months <= 48:  # 直接用月數比較，更快
                            master_students.append({
                                'title': paper['title'],
                                'student_id': details['student_id'],
                                'publication_date': details['publication_date'],
                                'study_duration': details['study_duration'],
                                'keywords': details['keywords']
                            })
                
                # 顯示統計結果
                display_statistics(advisor['name'], master_students)
            
            if input("\n是否繼續搜尋其他教授？(y/n): ").lower() != 'y':
                break
                
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
=======
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
    max_pages = 500  # 設定最大頁數防止無限循環
    consecutive_empty_pages = 0  # 連續空頁計數
    max_empty_pages = 3  # 最多允許3頁連續空頁
    
    while page <= max_pages and consecutive_empty_pages < max_empty_pages:
        url = f'https://thesis.lib.nycu.edu.tw/browse/advisor?scope={dept_uuid}&bbm.page={page}'
        print(f"\n正在掃描第 {page} 頁...")
        
        try:
            driver.get(url)
            # 確保頁面完全載入
            driver.execute_script("return document.readyState") == "complete"
            time.sleep(5)
            
            # 確保視窗焦點（無頭模式下仍有效）
            driver.execute_script("window.focus();")
            
            # 等待教授連結出現
            wait = WebDriverWait(driver, 15)  # 增加等待時間
            try:
                advisor_links = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.lead.ng-star-inserted[href*="/browse/advisor"]'))
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
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link[aria-label="Next"]')
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

def get_paper_details(driver, paper_url):
    """獲取論文的詳細資訊，包括學生資訊"""
    paper_details = {
        'degree': '',
        'student_id': '',
        'publication_date': '',
        'keywords': [],
        'study_duration': ''
    }
    
    try:
        driver.get(paper_url)
        time.sleep(3)
        
        # 等待頁面載入
        wait = WebDriverWait(driver, 10)
        
        # 查找所有 span 元素來提取資訊
        spans = driver.find_elements(By.CSS_SELECTOR, 'span.dont-break-out.preserve-line-breaks.ng-star-inserted')
        
        for span in spans:
            text = span.text.strip()
            
            # 檢查是否為學位資訊
            if text in ['碩士', '博士']:
                paper_details['degree'] = text
            
            # 檢查是否為學號（9位數字，3開頭的碩士生）
            elif text.isdigit() and len(text) == 9 and text.startswith('3'):
                paper_details['student_id'] = text
            
            # 檢查是否為日期格式 (YYYY/MM/DD)
            elif '/' in text and len(text.split('/')) == 3:
                try:
                    parts = text.split('/')
                    if len(parts[0]) == 4 and parts[0].isdigit():  # 年份格式
                        paper_details['publication_date'] = text
                except:
                    pass
            
            # 檢查是否為關鍵詞（包含英文字母或中文，但不是日期和學號）
            elif text and not text.isdigit() and text not in ['碩士', '博士']:
                # 過濾關鍵詞：
                # 1. 長度限制：3-20字符（避免太短或太長的摘要）
                # 2. 不包含標點符號
                # 3. 包含有意義的字母或中文
                punctuation_chars = {'。', '，', '、', '；', '：', '！', '？', '(', ')', '[', ']', '{', '}', 
                                   '"', "'", '「', '」', '『', '』', '《', '》', '〈', '〉', '-', '_', 
                                   '=', '+', '*', '/', '\\', '|', '@', '#', '$', '%', '^', '&', '~', '`'}
                
                if (3 <= len(text) <= 20 and 
                    not any(char in text for char in punctuation_chars) and
                    (any(c.isalpha() for c in text) or any('\u4e00' <= c <= '\u9fff' for c in text))):
                    paper_details['keywords'].append(text)
        
        # 如果沒有找到學號，嘗試其他選擇器（只找3開頭的碩士生）
        if not paper_details['student_id']:
            all_spans = driver.find_elements(By.TAG_NAME, 'span')
            for span in all_spans:
                text = span.text.strip()
                if text.isdigit() and len(text) == 9 and text.startswith('3'):
                    paper_details['student_id'] = text
                    break
        
        # 計算修業年限
        if paper_details['student_id'] and paper_details['publication_date']:
            paper_details['study_duration'] = calculate_study_duration(
                paper_details['student_id'], 
                paper_details['publication_date']
            )
        
    except Exception as e:
        print(f"獲取論文詳細資訊時出錯: {str(e)}")
    
    return paper_details

def calculate_study_duration(student_id, publication_date):
    """計算修業年限"""
    try:
        from datetime import datetime
        
        # 學號格式分析：3 + 學年度後兩位數 + 其他數字
        # 例如：313xxxxx 代表113學年度入學的碩士生
        if len(student_id) == 9 and student_id.startswith('3'):
            # 第2-3位是學年度的後兩位數
            year_suffix = int(student_id[1:3])
            
            # 轉換為民國年（學年度就是民國年）
            roc_year = 100 + year_suffix  # 例如：13 -> 113年
            ad_year = roc_year + 1911     # 轉換為西元年
            entry_month = 9  # 預設9月入學
        else:
            return "學號格式錯誤"
        
        # 從發表日期提取畢業年月
        pub_parts = publication_date.split('/')
        grad_year = int(pub_parts[0])
        grad_month = int(pub_parts[1])
        
        # 檢查是否為未來發表日期
        current_date = datetime.now()
        pub_date = datetime(grad_year, grad_month, 1)
        
        # 如果發表日期大於現在時間，減5年（鎖發表相關）
        if pub_date > current_date:
            grad_year -= 5
        
        # 計算年數差異
        year_diff = grad_year - ad_year
        month_diff = grad_month - entry_month
        
        # 計算總月數
        total_months = year_diff * 12 + month_diff
        
        # 轉換為年月格式
        years = total_months // 12
        months = total_months % 12
        
        if years > 0 and months > 0:
            return f"{years}年{months}個月"
        elif years > 0:
            return f"{years}年"
        elif months > 0:
            return f"{months}個月"
        else:
            return f"總計{total_months}個月"
            
    except Exception as e:
        return f"計算失敗: {str(e)}"

def get_advisor_papers(driver, advisor_url):
    """獲取教授的論文列表"""
    papers = []
    page = 1
    max_pages = 50  # 設定最大頁數
    
    while page <= max_pages:
        # 如果 URL 已經包含參數，則加上頁碼
        if 'bbm.return=' in advisor_url:
            url = advisor_url.replace('bbm.return=', f'bbm.page={page}&bbm.return=')
        else:
            url = f"{advisor_url}&bbm.page={page}"
        
        print(f"正在掃描教授論文第 {page} 頁...")
        
        try:
            driver.get(url)
            time.sleep(3)
            
            # 等待論文連結出現
            wait = WebDriverWait(driver, 10)
            try:
                paper_links = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.lead.item-list-title[href*="/items/"]'))
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
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a.page-link[aria-label="Next"]')
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

def parse_duration_to_months(duration_str):
    """將修業年限字符串轉換為月數"""
    try:
        if '年' in duration_str and '月' in duration_str:
            years = int(duration_str.split('年')[0])
            months = int(duration_str.split('年')[1].split('月')[0])
            return years * 12 + months
        elif '年' in duration_str:
            years = int(duration_str.split('年')[0])
            return years * 12
        elif '月' in duration_str:
            months = int(duration_str.split('月')[0])
            return months
        else:
            return 0
    except:
        return 0

def format_months_to_duration(total_months):
    """將月數轉換為年月格式"""
    years = total_months // 12
    months = total_months % 12
    
    if years > 0 and months > 0:
        return f"{years}年{months}個月"
    elif years > 0:
        return f"{years}年"
    elif months > 0:
        return f"{months}個月"
    else:
        return "0個月"

def calculate_average_duration(master_students):
    """計算平均修業年限"""
    valid_durations = []
    for student in master_students:
        duration_months = parse_duration_to_months(student['study_duration'])
        if duration_months > 0:
            valid_durations.append(duration_months)
    
    if valid_durations:
        avg_months = sum(valid_durations) / len(valid_durations)
        return format_months_to_duration(int(avg_months))
    else:
        return "無法計算"

def display_student_details(advisor_name, master_students):
    """顯示學生詳細資訊"""
    print(f"\n📊 {advisor_name} 碩士生詳細資訊:")
    print(f"   碩士生總數: {len(master_students)} 人 (修業年限 ≤ 4年)")
    print("=" * 80)
    
    # 顯示每位學生的資訊
    for i, student in enumerate(master_students, 1):
        print(f"\n{i}. 論文標題: {student['title']}")
        print(f"   學號: {student['student_id']}")
        print(f"   發表日期: {student['publication_date']}")
        print(f"   修業年限: {student['study_duration']}")
        if student['keywords']:
            print(f"   關鍵詞: {', '.join(student['keywords'][:5])}")
        print("-" * 40)

def analyze_keywords(master_students):
    """分析關鍵詞統計"""
    # 收集所有關鍵詞
    all_keywords = []
    for student in master_students:
        all_keywords.extend(student['keywords'])
    
    # 統計關鍵詞頻率
    keyword_count = {}
    for keyword in all_keywords:
        keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
    
    # 分離人名和其他關鍵詞
    chinese_names = []
    filtered_keywords = []
    exclude_words = {'立即公開', '不公開', '一年後公開', '兩年後公開', '三年後公開', '五年後公開', 
                   '暫不公開', '公開', '開放', '授權', '全文', '論文', '碩士', '博士', 'Master', 'PhD'}
    
    if keyword_count:
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        
        for keyword, count in sorted_keywords:
            # 過濾掉排除詞彙
            if keyword in exclude_words:
                continue
            
            # 判斷是否為中文人名
            is_chinese_name = (
                len(keyword) >= 2 and len(keyword) <= 4 and
                all('\u4e00' <= char <= '\u9fff' for char in keyword) and
                not any(char in keyword for char in ['、', '，', '。', '；', '：', '（', '）', '[', ']', '-', '_'])
            )
            
            # 判斷是否為英文人名
            is_english_name = (
                ',' in keyword and 
                any(char.isalpha() for char in keyword) and
                keyword.count(',') == 1
            )
            
            if is_chinese_name and len(chinese_names) < 5:
                chinese_names.append((keyword, count))
            elif not is_chinese_name and not is_english_name:
                filtered_keywords.append((keyword, count))
    
    return chinese_names, filtered_keywords

def display_statistics(advisor_name, master_students):
    """顯示統計摘要"""
    if not master_students:
        print(f"\n{advisor_name} 沒有找到符合條件的碩士論文（有學號且修業年限 ≤ 4年）")
        return
    
    # 顯示學生詳細資訊
    display_student_details(advisor_name, master_students)
    
    # 計算並顯示平均修業年限
    avg_duration = calculate_average_duration(master_students)
    print(f"\n📈 統計摘要:")
    print(f"   平均修業年限: {avg_duration}")
    
    # 分析關鍵詞
    chinese_names, filtered_keywords = analyze_keywords(master_students)
    
    # 顯示指導教授
    if chinese_names:
        print(f"   指導教授 (前5位):")
        for name, count in chinese_names:
            print(f"     - {name} ({count}次)")
    
    # 顯示研究關鍵詞
    if filtered_keywords:
        print(f"   研究關鍵詞 (前10個):")
        for keyword, count in filtered_keywords[:10]:
            print(f"     - {keyword} ({count}次)")

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
        
    # 初始化瀏覽器 - 加強穩定性設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式，避免視窗狀態影響
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')  # 設定虛擬視窗大小
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被檢測
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
            
            # 獲取教授的論文列表
            papers = get_advisor_papers(driver, advisor['url'])
            
            if not papers:
                print(f"\n{advisor['name']} 沒有找到任何論文")
            else:
                print(f"\n{advisor['name']} 共有 {len(papers)} 篇論文")
                print("正在分析論文詳細資訊...")
                print("=" * 80)
                
                # 統計資料
                master_students = []
                
                for i, paper in enumerate(papers, 1):
                    print(f"分析第 {i}/{len(papers)} 篇論文...")
                    
                    # 獲取論文詳細資訊
                    details = get_paper_details(driver, paper['url'])
                    
                    # 只處理有學號的碩士論文，且修業年限不超過4年
                    if details['degree'] == '碩士' and details['student_id'] and details['study_duration']:
                        # 檢查修業年限是否超過4年
                        duration_str = details['study_duration']
                        is_valid_duration = True
                        
                        if '年' in duration_str:
                            try:
                                years = int(duration_str.split('年')[0])
                                if years > 4:
                                    is_valid_duration = False
                            except:
                                pass
                        
                        if is_valid_duration:
                            master_students.append({
                                'title': paper['title'],
                                'student_id': details['student_id'],
                                'publication_date': details['publication_date'],
                                'study_duration': details['study_duration'],
                                'keywords': details['keywords']
                            })
                
                # 顯示統計結果
                display_statistics(advisor['name'], master_students)
            
            if input("\n是否繼續搜尋其他教授？(y/n): ").lower() != 'y':
                break
                
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
>>>>>>> eeba2313b92720800c3a21be234389bc91718839
