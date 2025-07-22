"""
論文分析模組 - 處理論文詳細資訊的獲取和分析
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .config import SELECTORS, PUNCTUATION_CHARS, DEGREE_TYPES, SCRAPING_CONFIG
from .utils import calculate_study_duration


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
        time.sleep(SCRAPING_CONFIG['SLEEP_TIME']['PAPER_DETAIL'])
        
        # 等待頁面載入
        wait = WebDriverWait(driver, 10)
        
        # 一次性查找所有需要的元素
        spans = driver.find_elements(By.CSS_SELECTOR, SELECTORS['PAPER_SPANS'])
        
        keywords_temp = []
        
        for span in spans:
            text = span.text.strip()
            if not text:
                continue
            
            # 使用更高效的條件檢查順序
            if text in DEGREE_TYPES:
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
                  not any(char in PUNCTUATION_CHARS for char in text) and
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


def filter_valid_papers(papers):
    """預先篩選有效論文，避免無效查詢"""
    valid_papers = []
    for paper in papers:
        if paper.get('title'):  # 確保標題不為空
            valid_papers.append(paper)
    return valid_papers


def process_papers_batch(driver, papers, advisor_name):
    """批量處理論文"""
    master_students = []
    valid_papers = filter_valid_papers(papers)
    
    print(f"有效論文數量：{len(valid_papers)}")
    
    for i, paper in enumerate(valid_papers, 1):
        print(f"分析第 {i}/{len(valid_papers)} 篇論文...")
        
        # 獲取論文詳細資訊
        details = get_paper_details(driver, paper['url'])
        
        # 只處理有學號的碩士論文，且修業年限不超過4年（優化判斷）
        if (details['degree'] == '碩士' and 
            details['student_id'] and 
            details['study_duration']):
            
            # 快速檢查修業年限
            from .utils import parse_duration_to_months
            duration_months = parse_duration_to_months(details['study_duration'])
            
            if 0 < duration_months <= 48:  # 直接用月數比較，更快
                master_students.append({
                    'title': paper['title'],
                    'student_id': details['student_id'],
                    'publication_date': details['publication_date'],
                    'study_duration': details['study_duration'],
                    'keywords': details['keywords']
                })
    
    return master_students
