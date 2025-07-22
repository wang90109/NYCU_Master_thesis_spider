# NYCU 論文資料庫爬蟲

這是一個用於爬取國立陽明交通大學論文資料庫的爬蟲工具。目前支援以下功能：

1. 瀏覽各學院系所
2. 搜尋指導教授
3. 查看教授的論文列表（開發中）

## 安裝需求

1. Python 3.8+
2. Chrome 瀏覽器
3. ChromeDriver（需與您的 Chrome 版本相符）

## 安裝步驟

1. 克隆此專案：
```bash
git clone https://github.com/wang90109/thesis_analyzer.git
cd thesis_analyzer
```

2. **安裝依賴**：
```bash
pip install selenium webdriver-manager
```

3. 確保 ChromeDriver 已正確安裝並在系統路徑中。

## 使用方式

執行主程式：
```bash
python main.py
```

程式會顯示學院及系所列表，使用編碼（如 A-1、B-2）來選擇系所，接著可以：
1. 瀏覽該系所的所有教授
2. 搜尋特定教授
3. 查看教授的論文列表

## 注意事項

1. 請確保您的網路連線正常
2. 請遵守學校網站的使用規範
3. 建議不要過於頻繁地訪問，以免影響伺服器負載

## 授權條款

[待定義]

## 貢獻指南

歡迎提出 Issue 或 Pull Request 來改善此專案。
