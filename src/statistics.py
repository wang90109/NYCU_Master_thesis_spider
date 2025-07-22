"""
統計分析模組 - 處理學生資料統計和關鍵詞分析
"""

from collections import Counter
from .config import EXCLUDE_KEYWORDS
from .utils import parse_duration_to_months


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


def analyze_keywords(master_students):
    """分析關鍵詞統計（優化版本）"""
    # 一次性收集所有關鍵詞
    all_keywords = []
    for student in master_students:
        all_keywords.extend(student['keywords'])
    
    # 使用 Counter 高效計數
    keyword_count = Counter(all_keywords)
    
    chinese_names = []
    filtered_keywords = []
    
    # 只遍歷一次，使用 most_common 直接獲取排序結果
    for keyword, count in keyword_count.most_common():
        if keyword in EXCLUDE_KEYWORDS:
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
