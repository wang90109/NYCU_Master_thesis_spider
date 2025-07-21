import csv
from datetime import datetime

class DataSaver:
    @staticmethod
    def save_to_csv(items, filename):
        """
        將資料儲存為 CSV 檔案
        """
        if not items:
            print("沒有資料可以儲存")
            return False

        try:
            # 加入爬取時間
            for item in items:
                item['crawl_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
            print(f"資料已成功儲存至 {filename}")
            return True
        except Exception as e:
            print(f"儲存資料時發生錯誤：{str(e)}")
            return False
