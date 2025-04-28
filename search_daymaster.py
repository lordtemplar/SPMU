# streamlit_app.py

import streamlit as st
from pymongo import MongoClient

# ------------------------------
# เชื่อมต่อ MongoDB ด้วย Secret
# ------------------------------
MONGO_URI = st.secrets["MONGO_URI"]
DATABASE_NAME = st.secrets["DATABASE_NAME"]

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# ------------------------------
# โหลดข้อมูลทั้งหมดจาก Collection
# ------------------------------
@st.cache_data
def load_profiles(collection_name):
    collection = db[collection_name]
    profiles = list(collection.find({}))
    return profiles

# ------------------------------
# หาโปรไฟล์จากคีย์เวิร์ด
# ------------------------------
def find_profile(profiles, field, keyword):
    for profile in profiles:
        if keyword in str(profile.get(field, "")):
            return profile
    return None

# ------------------------------
# เริ่มต้นหน้าเว็บ Streamlit
# ------------------------------
st.set_page_config(page_title="Profiles Explorer", page_icon="🌟")

st.title("🌟 ระบบค้นหาข้อมูล Profiles 🌟")

# ------------------------------
# เลือกประเภทการค้นหา
# ------------------------------
search_type = st.radio(
    "เลือกประเภทข้อมูลที่ต้องการค้นหา",
    ("Day Master (ธาตุประจำตัว)", "Zodiac Profile (นักสัตว์)", "Calendar Profile (ปฏิทิน)")
)

# Mapping
collection_map = {
    "Day Master (ธาตุประจำตัว)": "daymaster_profiles",
    "Zodiac Profile (นักสัตว์)": "zodiac_profiles",
    "Calendar Profile (ปฏิทิน)": "calendar_profiles_2568"
}

field_map = {
    "Day Master (ธาตุประจำตัว)": "day_master",
    "Zodiac Profile (นักสัตว์)": "zodiac_sign",  # สมมุติว่า field ชื่อ zodiac_sign
    "Calendar Profile (ปฏิทิน)": "date"  # สมมุติว่า field ชื่อ date เช่น "1 มกราคม 2568"
}

selected_collection = collection_map[search_type]
search_field = field_map[search_type]

# ------------------------------
# โหลดข้อมูล
# ------------------------------
profiles = load_profiles(selected_collection)

# ------------------------------
# ช่องค้นหา
# ------------------------------
search_keyword = st.text_input(f"🔎 พิมพ์ {search_field} ที่ต้องการค้นหา:")

if search_keyword:
    profile = find_profile(profiles, search_field, search_keyword)

    if profile:
        st.success(f"✅ พบข้อมูลที่ตรงกับ {search_keyword}")

        # แสดงข้อมูลโปรไฟล์
        st.json(profile)

    else:
        st.error(f"❌ ไม่พบข้อมูลที่เกี่ยวข้องกับ \"{search_keyword}\"")

else:
    st.info("ℹ️ กรุณากรอกคำค้นหา")

