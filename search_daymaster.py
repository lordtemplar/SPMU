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
# แปลงวันที่เป็นรูปแบบ text ตรงกับฐานข้อมูล
# ------------------------------
def format_thai_date(date_obj):
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    day = date_obj.day
    month = thai_months[date_obj.month - 1]
    year = date_obj.year
    return f"{year}-{date_obj.month:02d}-{date_obj.day:02d}"

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
    "Zodiac Profile (นักสัตว์)": "zodiac",
    "Calendar Profile (ปฏิทิน)": "date"
}

selected_collection = collection_map[search_type]
search_field = field_map[search_type]

# ------------------------------
# โหลดข้อมูล
# ------------------------------
profiles = load_profiles(selected_collection)

# ------------------------------
# ค้นหา และ แสดงข้อมูล
# ------------------------------
if search_type in ("Day Master (ธาตุประจำตัว)", "Zodiac Profile (นักสัตว์)"):
    # Dropdown ให้เลือก
    options = sorted({profile.get(search_field, "ไม่ระบุ") for profile in profiles})
    selected_option = st.selectbox(f"เลือก {search_type}", options)

    if selected_option:
        profile = find_profile(profiles, search_field, selected_option)

        if profile:
            st.success(f"✅ พบข้อมูลเกี่ยวกับ {selected_option}")

            if search_type == "Day Master (ธาตุประจำตัว)":
                # แสดงข้อมูล Day Master
                st.subheader(f"ธาตุ: {profile.get('day_master', '-')}")
                st.markdown(f"**ลักษณะทั่วไป:** {profile.get('characteristics', '-')}")
                st.markdown("**จุดแข็ง:**")
                for strength in profile.get('strengths', []):
                    st.write(f"- {strength}")
                st.markdown("**จุดอ่อน:**")
                for weakness in profile.get('weaknesses', []):
                    st.write(f"- {weakness}")
                st.markdown("**คำแนะนำเพื่อสร้างสมดุลในชีวิต:**")
                for advice in profile.get('advice_for_balance', []):
                    st.write(f"- {advice}")
                st.markdown(f"**เสน่ห์ที่ดึงดูดใจ:** {profile.get('charm', '-')}")

            elif search_type == "Zodiac Profile (นักสัตว์)":
                # แสดงข้อมูล Zodiac
                st.subheader(f"นักษัตร: {profile.get('zodiac', '-')}")
                st.markdown(f"**ลักษณะทั่วไป:** {profile.get('characteristics', '-')}")
                st.markdown("**จุดแข็ง:**")
                for strength in profile.get('strengths', []):
                    st.write(f"- {strength}")
                st.markdown("**จุดอ่อน:**")
                for weakness in profile.get('weaknesses', []):
                    st.write(f"- {weakness}")
                st.markdown("**เสน่ห์:**")
                st.write(profile.get('charm', '-'))
                st.markdown("**คำแนะนำเพื่อสร้างสมดุล:**")
                for advice in profile.get('advice_for_balance', []):
                    st.write(f"- {advice}")
                st.markdown("**ความสัมพันธ์กับนักษัตรอื่น:**")
                for relation in profile.get('zodiac_relations', []):
                    st.write(f"- {relation}")

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

    formatted_date = format_thai_date(selected_date)

    st.info(f"🔍 กำลังค้นหาวันที่: {formatted_date}")

    profile = find_profile(profiles, search_field, formatted_date)

    if profile:
        st.success(f"✅ พบข้อมูลสำหรับวันที่ {formatted_date}")

        st.subheader(f"ธีมของวัน: {profile.get('theme', '-')}")
        st.markdown(f"**คำคมประจำวัน:** {profile.get('day_quote', '-')}")
        st.markdown(f"**ไฮไลท์ของวัน:** {profile.get('highlight_of_day', '-')}")
        st.markdown(f"**พลังของวัน:** {profile.get('power_of_day', '-')}")
        st.markdown(f"**ผลของฤดูกาล:** {profile.get('seasonal_effect', '-')}")
        st.markdown("**สีมงคลและสีที่ควรหลีกเลี่ยง:**")
        for color in profile.get('lucky_colors', []):
            st.write(f"- {color}")
        st.markdown("**สิ่งที่ควรทำ:**")
        for todo in profile.get('things_to_do', []):
            st.write(f"- {todo}")
        st.markdown("**สิ่งที่ควรหลีกเลี่ยง:**")
        for avoid in profile.get('things_to_avoid', []):
            st.write(f"- {avoid}")
        st.markdown("**ความสัมพันธ์ตามนักษัตร:**")
        for relation in profile.get('zodiac_relations', []):
            st.write(f"- {relation}")

    else:
        st.error(f"❌ ไม่พบข้อมูลสำหรับวันที่ {formatted_date}")
