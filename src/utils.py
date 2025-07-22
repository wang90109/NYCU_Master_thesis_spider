"""
工具函數模組 - 包含計算和轉換相關的工具函數
"""

from .config import STUDENT_ID_CONFIG, STUDY_DURATION_CONFIG


def calculate_study_duration(student_id, publication_date):
    """計算修業年限（優化版本）"""
    try:
        # 預先導入，避免重複導入
        from datetime import datetime
        
        # 快速學號格式檢查
        if (len(student_id) != STUDENT_ID_CONFIG['LENGTH'] or 
            student_id[0] != STUDENT_ID_CONFIG['PREFIX']):
            return "學號格式錯誤"
        
        # 直接提取年份數字，避免切片操作
        year_suffix = int(student_id[1:3])
        ad_year = STUDENT_ID_CONFIG['BASE_YEAR'] + year_suffix
        
        # 快速分割日期
        pub_parts = publication_date.split('/')
        grad_year = int(pub_parts[0])
        grad_month = int(pub_parts[1])
        
        # 檢查未來日期（優化版本）
        if grad_year > 2025:  # 使用固定年份比較，避免 datetime.now() 調用
            grad_year -= 5
        
        # 直接計算總月數
        total_months = (grad_year - ad_year) * 12 + (grad_month - STUDY_DURATION_CONFIG['START_MONTH'])
        
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
