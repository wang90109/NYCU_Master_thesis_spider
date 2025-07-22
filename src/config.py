"""
配置文件 - 存放所有配置和常量
"""

# 網頁爬取配置
SCRAPING_CONFIG = {
    'MAX_PAGES': 500,
    'MAX_EMPTY_PAGES': 3,
    'WAIT_TIME': 15,
    'SLEEP_TIME': {
        'PAGE_LOAD': 5,
        'PAPER_DETAIL': 3,
        'ADVISOR_PAPERS': 3
    }
}

# Chrome 瀏覽器配置
CHROME_OPTIONS = [
    '--headless',  # 無頭模式，避免視窗狀態影響
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--window-size=1920,1080',  # 設定虛擬視窗大小
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-blink-features=AutomationControlled'  # 避免被檢測
]

# CSS 選擇器
SELECTORS = {
    'ADVISOR_LINKS': 'a.lead.ng-star-inserted[href*="/browse/advisor"]',
    'PAPER_LINKS': 'a.lead.item-list-title[href*="/items/"]',
    'NEXT_BUTTON': 'a.page-link[aria-label="Next"]',
    'PAPER_SPANS': 'span.dont-break-out.preserve-line-breaks.ng-star-inserted'
}

# 標點符號集合
PUNCTUATION_CHARS = {
    '。', '，', '、', '；', '：', '！', '？', '(', ')', '[', ']', '{', '}',
    '"', "'", '「', '」', '『', '』', '《', '》', '〈', '〉', '-', '_',
    '=', '+', '*', '/', '\\', '|', '@', '#', '$', '%', '^', '&', '~', '`'
}

# 排除的關鍵詞
EXCLUDE_KEYWORDS = {
    '立即公開', '不公開', '一年後公開', '兩年後公開', '三年後公開', '五年後公開',
    '暫不公開', '公開', '開放', '授權', '全文', '論文', '碩士', '博士', 'Master', 'PhD'
}

# 學位類型
DEGREE_TYPES = {'碩士', '博士'}

# 文件路徑
DATA_FILES = {
    'DEPARTMENTS': 'departments.json'
}

# 學號相關配置
STUDENT_ID_CONFIG = {
    'LENGTH': 9,
    'PREFIX': '3',
    'BASE_YEAR': 2011  # 100學年度對應的西元年份基準
}

# 修業年限配置
STUDY_DURATION_CONFIG = {
    'MAX_MONTHS': 48,  # 4年
    'START_MONTH': 9   # 入學月份（9月）
}
