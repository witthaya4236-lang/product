import json
import cloudscraper
from bs4 import BeautifulSoup
import datetime
import sys
import time
import random
import re

print(f"🚀 เริ่มต้นการทำงานของหุ่นยนต์ดึงราคา วันที่: {datetime.datetime.now()}")

# 1. โหลดข้อมูลเดิมจากไฟล์ prices.json
try:
    with open('prices.json', 'r', encoding='utf-8') as f:
        appData = json.load(f)
    print("✅ โหลดไฟล์ prices.json สำเร็จ")
except FileNotFoundError:
    print("❌ ไม่พบไฟล์ prices.json โปรดตรวจสอบว่ามีไฟล์นี้อยู่ในระบบ")
    sys.exit(1)

# สร้างหุ่นยนต์แบบเนียนพิเศษ (Bypass Cloudflare & Bot Protection)
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def extract_number(text):
    """ฟังก์ชันดึงเฉพาะตัวเลขออกจากข้อความที่ปนกัน"""
    if not text: return None
    match = re.search(r'\d+(\.\d+)?', text.replace(',', ''))
    return float(match.group()) if match else None

# ==========================================
# 2. ฟังก์ชันดึงราคาของแต่ละห้าง
# ==========================================
def get_store_price(url, store_name):
    if not url or str(url).strip() == "":
        return None
        
    try:
        response = scraper.get(url, timeout=20)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- ชั้นที่ 1: เจาะข้อมูลจากระบบหลังบ้าน (Next.js Data) ---
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if script_tag:
            data = json.loads(script_tag.string)
            # เพิ่มตรรกะเจาะหาตัวเลขราคาตามโครงสร้าง JSON ของแต่ละเว็บได้ที่นี่
            pass
            
        # --- ชั้นที่ 2: ค้นหาจาก ld+json (Schema.org) ---
        ld_json = soup.find('script', type='application/ld+json')
        if ld_json:
            data = json.loads(ld_json.string)
            pass

        # *ตัวอย่างจำลองการดึงราคาเพื่อทดสอบระบบ (แก้ไขเป็นดึงข้อมูลจริงได้เลย)*
        return float(round(random.uniform(20.0, 150.0), 2))
        
    except Exception as e:
        print(f"  ❌ {store_name} Error: ไม่สามารถดึงข้อมูลได้ ({e})")
        return None

# ==========================================
# 3. เริ่มขั้นตอนวิ่งตรวจเช็คและอัปเดตราคา
# ==========================================
updates_made = False
stores = ['BigC', 'Lotus', 'Tops', 'AllOnline']

for item in appData:
    print(f"\n📦 กำลังเช็คราคา: {item.get('name', 'ไม่ทราบชื่อสินค้า')}")
    
    # ถ้า Object ยังไม่มี Key สำหรับเก็บราคาหรือ URL ให้สร้างเตรียมไว้
    if 'prices' not in item:
        item['prices'] = {}
    if 'urls' not in item:
        item['urls'] = {}

    for store in stores:
        url = item['urls'].get(store)
        if url:
            new_price = get_store_price(url, store)
            if new_price is not None:
                old_price = item['prices'].get(store, 0)
                if float(old_price) != new_price:
                    print(f"  -> 📉 อัปเดต {store} เป็น: {new_price} บาท")
                    item['prices'][store] = new_price
                    updates_made = True
                else:
                    print(f"  -> ➖ {store} ราคาคงเดิม: {new_price} บาท")
        else:
            print(f"  -> ⏭️ ข้าม {store} (ไม่มี URL ในระบบ)")
            
    # หน่วงเวลา 2-4 วินาที เพื่อไม่ให้เว็บปลายทางบล็อก IP
    time.sleep(random.uniform(2, 4))

# ==========================================
# 4. บันทึกข้อมูลกลับลงไฟล์ prices.json
# ==========================================
if updates_made:
    with open('prices.json', 'w', encoding='utf-8') as f:
        json.dump(appData, f, ensure_ascii=False, indent=4)
    print("\n💾 บันทึกการเปลี่ยนแปลงราคาลง prices.json สำเร็จ!")
else:
    print("\n✅ ตรวจสอบเสร็จสิ้น ไม่มีราคาเปลี่ยนแปลง ไม่ต้องเซฟไฟล์ใหม่")

print("🎉 หุ่นยนต์ทำงานเสร็จสิ้นสมบูรณ์!")
