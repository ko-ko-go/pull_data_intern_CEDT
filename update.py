
import time

def update_data():
    print("⏳ กำลังอัปเดตข้อมูล...")

    import requests

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
    }

    params = {
        'search': '',
        'page': '1',
        'onlyBookmarked': 'false',
        'onlyAvailablePositions': 'false',
    }

    response = requests.get('https://cedtintern.cp.eng.chula.ac.th/api/sessions/4/openings', params=params, headers=headers)
    
    import pandas as pd
    data = response.json()
    df = pd.json_normalize(data['items'])



    # import json

    # with open("/kaggle/input/int-25-11/int-25112025.json", "r", encoding="utf-8") as file:
    #     data = json.load(file)


    # df = pd.json_normalize(data["items"])

    print(df.head())
    from bs4 import BeautifulSoup
    import pandas as pd
    import re

    # ฟังก์ชันล้าง HTML
    def clean_html(text):
        # 1. เช็คว่าเป็นค่าว่าง/None หรือไม่ (สำคัญมาก เพราะข้อมูลแถว 4 เป็น None)
        if pd.isna(text) or text == "" or str(text).lower() == 'none':
            return ""
        
        # 2. แปลง HTML เป็น Text
        soup = BeautifulSoup(str(text), "html.parser")
        
        # 3. ดึงข้อความโดยใช้ separator=' ' เพื่อกันข้อความติดกัน
        clean_text = soup.get_text(separator=' ')
        
        # 4. ลบช่องว่างซ้ำซ้อน และพวก \xa0 (Non-breaking space)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    # --- เรียกใช้ ---
    # สมมติ df คือ DataFrame ของคุณ
    cols_to_clean = ['description', 'requirements']

    for col in cols_to_clean:
        # สร้างคอลัมน์ใหม่ หรือ ทับคอลัมน์เดิมก็ได้
        df[col] = df[col].apply(clean_html)



    # ลองแสดงผลดู
    print(df[['title', 'description', 'requirements']].head())
    import ast
    import pandas as pd

    def clean_tags(tag_data):
        # 1. เช็คว่าเป็น List ก่อนเลย (เพื่อเลี่ยง Error ของ pd.isna กับ List)
        if isinstance(tag_data, list):
            if len(tag_data) == 0:
                return ""
            # ดึง tagName ออกมา (เช็คด้วยว่าเป็น dict หรือเปล่าเพื่อความชัวร์)
            tag_names = [str(t.get('tagName', '')) for t in tag_data if isinstance(t, dict)]
            return ", ".join(filter(None, tag_names)) # filter(None) ช่วยกรองค่าว่างทิ้ง
        
        # 2. ค่อยเช็คว่าเป็น NaN หรือค่าว่าง (สำหรับกรณีที่ไม่ใช่ List)
        if pd.isna(tag_data) or tag_data == "" or tag_data == "[]":
            return ""
        
        # 3. กรณีเป็น String ที่หน้าตาเหมือน List (เผื่อหลุดมา)
        if isinstance(tag_data, str):
            try:
                tags_list = ast.literal_eval(tag_data)
                if isinstance(tags_list, list):
                    tag_names = [str(t.get('tagName', '')) for t in tags_list if isinstance(t, dict)]
                    return ", ".join(filter(None, tag_names))
            except:
                return ""
                
        return ""

    # เรียกใช้ใหม่
    df['tags_clean'] = df['tags'].apply(clean_tags)



    # ลบหลายคอลัมน์พร้อมกัน
    cols_to_drop = [ 'compensationType', 'tags'] # ใส่ชื่อคอลัมน์ที่จะลบ

    df = df.drop(columns=cols_to_drop)





    # สร้างคู่ชื่อเดิม-ชื่อใหม่
    new_names = {
        'company.companyNameTh': 'company',
        'compensationType.compensationType': 'compensation_Type',
        'tags_clean':'tags'
    }

    # สั่งเปลี่ยนชื่อ
    df = df.rename(columns=new_names)

    # ลองแสดงผลดู
    print(df.head())

    # ดูผลลัพธ์
    print(df[['title', 'tags']].head())
    print(df.head())
    # 1. เช็คชื่อคอลัมน์ที่มีอยู่จริงก่อน (เพื่อความชัวร์)
    print("รายชื่อคอลัมน์ที่มีอยู่ตอนนี้:", df.columns.tolist())

    # 2. แก้ไขรายชื่อคอลัมน์ที่จะเก็บ (ตัดคำว่า _clean ออกจาก description และ requirements)
    keep_cols = [
        'company',
        'title', 
        'quota', 
        'inStudentDraftCount',
        'compensationAmount',
        'compensation_Type',
        'tags',
        'workingCondition',
        'description',        # แก้จาก description_clean
        'requirements',
        # --- เพิ่มส่วนนี้ครับ ---
        'officeName',
        'officeAddressLine1',
        'officeAddressLine2'
        
        # อันนี้เก็บไว้ เพราะเราสร้างใหม่จากโค้ด tags
        
        
    ]

    # 3. เลือกคอลัมน์อีกครั้ง
    df = df[keep_cols]

    # ดูผลลัพธ์
    print(df.head())
    # # ส่งออกเป็นไฟล์ CSV
    df.to_csv('cleaned_data-1.csv', index=False, encoding='utf-8-sig')

    print("Export เรียบร้อยแล้วครับ!")
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials




    # ตั้งค่าการเชื่อมต่อ (ต้องไปเอาไฟล์ key.json มาจาก Google Cloud Console ก่อน)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope) 
    client = gspread.authorize(creds)

    # เปิด Google Sheet ที่เตรียมไว้
    sheet = client.open("intern-25-11-25").sheet1

    # 1. แก้ปัญหาค่าว่าง (ต้องมี df = นำหน้า)
    df = df.fillna('')

    # 2. แก้ปัญหาเรื่องวันที่/ตัวเลขประหลาด (แปลงทุกอย่างเป็นข้อความให้หมด)
    # วิธีนี้ชัวร์ที่สุดสำหรับ Dashboard เพราะ Google Sheets จะรับได้ทุกค่าไม่ Error

    # 3. เตรียมข้อมูล
    all_data = [df.columns.values.tolist()] + df.values.tolist()

    # 4. ส่งข้อมูล (ระบุ parameter ชื่อ values= เพื่อความชัวร์)
    try:
        sheet.clear()
        sheet.update(values=all_data) 
        print("✅ สำเร็จ! ข้อมูลขึ้น Dashboard แล้วครับ")
    except Exception as e:
        print(f"❌ ยัง Error อยู่: {e}")

    print("อัปเดตข้อมูลขึ้น Dashboard เรียบร้อยแล้ว!")
    # เปิด Google Sheet ที่เตรียมไว้
    sheet = client.open("intern_cedt").sheet1

    # 1. จัดการค่าว่าง (NaN) ให้เป็นช่องว่างเฉยๆ (String) เพื่อไม่ให้ Error
    df = df.fillna('')

    # 2. จากนั้นค่อยสั่งอัปเดต (โค้ดเดิมของคุณ)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("อัปเดตข้อมูลขึ้น Dashboard เรียบร้อยแล้ว!")
    # ---------------------------------------
    # วางโค้ดทั้งหมดของคุณไว้ตรงนี้
    # ดึง API → ทำความสะอาด → ส่งขึ้น Google Sheet
    # ---------------------------------------

    print("✅ อัปเดตเสร็จแล้ว!")

# รันทุก 10 นาที
while True:
    update_data()
    print("🕒 รอ 10 นาทีเพื่ออัปเดตครั้งต่อไป...\n")
    time.sleep(600)   # 600 วินาที = 10 นาที




