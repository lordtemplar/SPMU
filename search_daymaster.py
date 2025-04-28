import streamlit as st
from pymongo import MongoClient
import datetime

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
        if keyword == str(profile.get(field, "")):
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
    "Zodiac Profile (นักสัตว์)": "zodiac_sign",  # สมมุติ field ชื่อนี้
    "Calendar Profile (ปฏิทิน)": "date"  # สมมุติ field เป็น text เช่น "1 มกราคม 2568"
}

selected_collection = collection_map[search_type]
search_field = field_map[search_type]

# ------------------------------
# โหลดข้อมูล
# ------------------------------
profiles = load_profiles(selected_collection)

# ------------------------------
# UI ค้นหา
# ------------------------------

if search_type in ("Day Master (ธาตุประจำตัว)", "Zodiac Profile (นักสัตว์)"):
    # ใช้ Dropdown
    options = sorted({profile.get(search_field, "ไม่ระบุ") for profile in profiles})
    selected_option = st.selectbox(f"เลือก {search_type}", options)

    if selected_option:
        profile = find_profile(profiles, search_field, selected_option)

        if profile:
            st.success(f"✅ พบข้อมูลเกี่ยวกับ {selected_option}")
            st.json(profile)
        else:
            st.error("❌ ไม่พบข้อมูล")

elif search_type == "Calendar Profile (ปฏิทิน)":
    # ใช้ Date Picker
    selected_date = st.date_input(
        "เลือกวัน เดือน ปี",
        value=datetime.date(2025, 1, 1),
        min_value=datetime.date(2025, 1, 1),
        max_value=datetime.date(2025, 12, 31)
    )

    # แปลงวันที่เป็นรูปแบบตรงกับในฐานข้อมูล เช่น "1 มกราคม 2568"
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]

    day = selected_date.day
    month = thai_months[selected_date.month - 1]
    year = selected_date.year + 543  # แปลงเป็น พ.ศ.

    formatted_date = f"{day} {month} {year}"

    st.info(f"🔍 กำลังค้นหาวันที่: {formatted_date}")

    profile = find_profile(profiles, search_field, formatted_date)

    if profile:
        st.success(f"✅ พบข้อมูลสำหรับวันที่ {formatted_date}")
        st.json(profile)
    else:
        st.error(f"❌ ไม่พบข้อมูลวันที่ {formatted_date}")

