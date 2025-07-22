"""
NYCU 論文資料庫爬蟲與分析工具 - 主程式

這是重構後的主程式，各功能模組已分離到 src 資料夾中
"""

from src.data_loader import (
    load_departments, 
    create_department_codes, 
    display_departments, 
    select_department
)
from src.web_scraper import (
    create_driver, 
    get_advisors, 
    get_advisor_papers, 
    select_advisor
)
from src.paper_analyzer import process_papers_batch
from src.statistics import display_statistics


def main():
    """主函數"""
    print("🎓 NYCU 論文資料庫爬蟲與分析工具")
    print("=" * 50)
    
    # 載入系所資料
    print("📂 載入系所資料...")
    all_departments = load_departments()
    if not all_departments:
        print("❌ 無法載入系所資料")
        return
    print("✅ 系所資料載入成功")
    
    # 初始化瀏覽器
    print("\n🌐 初始化瀏覽器...")
    driver = create_driver()
    print("✅ 瀏覽器初始化完成")
    
    try:
        # 建立系所編碼
        dept_codes = create_department_codes(all_departments)
        
        # 顯示系所列表
        print("\n📋 系所列表:")
        display_departments(dept_codes)
        
        # 選擇系所
        college_name, department = select_department(dept_codes)
        print(f"\n🎯 已選擇：{department['name']}")
        
        print(f"\n🔍 開始掃描 {department['name']} 的教授列表...")
        
        # 獲取該系所的所有教授
        advisors = get_advisors(driver, department['uuid'])
        
        if not advisors:
            print("\n❌ 未找到任何教授資料")
            return
            
        print(f"\n✅ 共找到 {len(advisors)} 位教授")
        
        # 讓使用者搜尋教授
        while True:
            advisor = select_advisor(advisors)
            if advisor is None:
                break
                
            print(f"\n📑 正在訪問 {advisor['name']} 的論文列表...")
            
            # 獲取教授的論文列表
            papers = get_advisor_papers(driver, advisor['url'])
            
            if not papers:
                print(f"\n❌ {advisor['name']} 沒有找到任何論文")
            else:
                print(f"\n📊 {advisor['name']} 共有 {len(papers)} 篇論文")
                print("🔬 正在分析論文詳細資訊...")
                print("=" * 80)
                
                # 處理論文並獲取碩士生資料
                master_students = process_papers_batch(driver, papers, advisor['name'])
                
                # 顯示統計結果
                display_statistics(advisor['name'], master_students)
            
            # 詢問是否繼續
            print("\n" + "=" * 80)
            if input("🔄 是否繼續搜尋其他教授？(y/n): ").lower() != 'y':
                break
                
    except Exception as e:
        print(f"❌ 發生錯誤：{str(e)}")
        
    finally:
        print("\n🔧 關閉瀏覽器...")
        driver.quit()
        print("✅ 程式執行完畢")


if __name__ == "__main__":
    main()
