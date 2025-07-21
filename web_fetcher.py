import requests
from bs4 import BeautifulSoup
import urllib3
from config import HEADERS

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebFetcher:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def fetch_page(self, url):
        """
        獲取網頁內容
        """
        try:
            # 首先訪問首頁，獲取必要的 cookies
            self.session.get(self.base_url, headers=HEADERS, verify=False, timeout=10)
            
            # 然後使用同一個 session 訪問目標頁面
            response = self.session.get(
                url, 
                headers=HEADERS, 
                verify=False, 
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            
            if 'text/html' not in response.headers.get('Content-Type', ''):
                print(f"警告：回應不是 HTML 格式 (Content-Type: {response.headers.get('Content-Type')})")
            
            return response.text
        except requests.RequestException as e:
            print(f"錯誤：無法擷取頁面 {url}")
            print(f"錯誤訊息：{str(e)}")
            print(f"回應狀態碼：{getattr(e.response, 'status_code', 'N/A')}")
            print(f"回應標頭：{getattr(e.response, 'headers', {})}")
            return None

class HTMLParser:
    @staticmethod
    def parse_departments(html_content, base_url):
        """
        解析系所資訊
        """
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        try:
            # 尋找所有系所的區塊
            dept_sections = soup.find_all('div', class_='col-md-9')
            
            for section in dept_sections:
                link = section.find('a')
                if link:
                    dept_name = link.text.strip()
                    dept_url = link['href'] if link['href'].startswith('http') else f"{base_url}{link['href']}"
                    
                    # 獲取系所論文數量
                    count_span = section.find('span', class_='badge badge-dark')
                    thesis_count = count_span.text.strip() if count_span else "0"
                    
                    items.append({
                        'department': dept_name,
                        'url': dept_url,
                        'thesis_count': thesis_count
                    })
        except Exception as e:
            print(f"解析頁面時發生錯誤：{str(e)}")
        
        return items
