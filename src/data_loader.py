"""
資料載入模組 - 處理 JSON 資料載入和系所編碼
"""

import json
from .config import DATA_FILES


def load_departments():
    """從 JSON 檔案載入所有學院和系所資料"""
    try:
        with open(DATA_FILES['DEPARTMENTS'], 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading departments: {str(e)}")
        return {}


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


def display_departments(dept_codes):
    """顯示系所列表"""
    current_college = None
    for code, (college_name, dept) in dept_codes.items():
        if college_name != current_college:
            print(f"\n{college_name}:")
            current_college = college_name
        print(f"{code}. {dept['name']}")


def select_department(dept_codes):
    """讓使用者選擇系所"""
    while True:
        dept_choice = input("\n請輸入系所編碼（例如 A-1）：").strip().upper()
        if dept_choice in dept_codes:
            college_name, department = dept_codes[dept_choice]
            return college_name, department
        print("無效的系所編碼，請重新輸入！")
