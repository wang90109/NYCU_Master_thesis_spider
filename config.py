BASE_URL = "https://thesis.lib.nycu.edu.tw"

# 定義學院資訊（使用實際的 communities ID）
COLLEGES = {
    "1": {"name": "電機學院", "id": "4f5fa0f1-428d-473a-b0f7-44c41c0e7302", "en_name": "College of Electrical and Computer Engineering"},
    "2": {"name": "資訊學院", "id": "94f36579-78b1-4a5d-a6ad-153e6519f000", "en_name": "College of Computer Science"},
    "3": {"name": "電機學院與資訊學院", "id": "094893f0-e81a-434a-9922-f359fd65f773", "en_name": "Electrical Engineering and Computer Science"},
    "4": {"name": "工學院", "id": "4f0f4ee8-12ce-49d1-b701-981f0415f2eb", "en_name": "College of Engineering"},
    "5": {"name": "理學院", "id": "cc5071f1-c88b-4323-9fb7-bf7ef9293b4e", "en_name": "College of Science"},
    "6": {"name": "光電學院", "id": "aca3f516-5895-4ff0-831e-dda0ec1c02eb", "en_name": "College of Photonics"},
    "7": {"name": "生命科學院", "id": "7f8c3382-aa4b-4d1a-b030-f47f5e12add8", "en_name": "College of Life Sciences"},
    "8": {"name": "生物科技學院", "id": "5bee0005-1f43-426d-b137-024de564af1b", "en_name": "College of Biological Science and Technology"},
    "9": {"name": "管理學院", "id": "06c50750-e8e7-454c-bbf7-1e2d9e551615", "en_name": "College of Management"},
    "10": {"name": "人文藝術與社會學院", "id": "83f430e1-9013-4804-8bab-a909ed0fbaea", "en_name": "College of Humanities and Social Sciences"},
    "11": {"name": "客家文化學院", "id": "19b8b09e-4750-4004-81f9-324c0ddd3dab", "en_name": "College of Hakka Studies"},
    "12": {"name": "生物醫學暨工程學院", "id": "d296acf6-16bf-422b-98ad-218e4b98aafa", "en_name": "College of Biomedical Science and Engineering"},
    "13": {"name": "工程生物科學學院", "id": "37f23e18-18de-499f-85f0-ac6b206c0b30", "en_name": "College of Engineering Bioscience"},
    "14": {"name": "智慧科學暨綠能學院", "id": "a015987d-dd75-4177-88ce-0913d4945d58", "en_name": "College of Artificial Intelligence"},
    "15": {"name": "國際半導體產業學院", "id": "40b6971d-3f76-416b-80ac-cf88ccf39a9c", "en_name": "International College of Semiconductor Technology"},
    "16": {"name": "醫學院", "id": "41c477f2-1d2d-4b26-9aff-f7069729639b", "en_name": "College of Medicine"},
    "17": {"name": "牙醫學院", "id": "d0bb78ba-cc3c-4d62-afa3-78f81b1c08e9", "en_name": "College of Dentistry"},
    "18": {"name": "藥物科學院", "id": "40c0d121-1a61-441b-8e96-a4fe86b612d2", "en_name": "College of Pharmaceutical Sciences"},
    "19": {"name": "護理學院", "id": "0c8fe292-12aa-493c-bd46-d453f2bf2810", "en_name": "College of Nursing"},
    "20": {"name": "科技法律學院", "id": "1734c0ad-4e3a-4df9-af1d-e059ef6afec9", "en_name": "School of Law"},
    "21": {"name": "產學創新研究學院", "id": "30e1acee-6a25-4a74-892d-230ceeb241e9", "en_name": "Industry Academia Innovation School"},
    "22": {"name": "博雅書苑", "id": "187f18cf-f18f-45fd-8a5e-f33ae04655c3", "en_name": "Liberal Arts College"}
}

# HTTP 請求標頭
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Cache-Control': 'max-age=0',
}
