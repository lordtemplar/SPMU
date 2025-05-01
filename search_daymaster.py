import streamlit as st
from pymongo import MongoClient
import datetime
import pandas as pd

# ------------------------------
# เชื่อมต่อ MongoDB ด้วย Secret
# ------------------------------
MONGO_URI = st.secrets["MONGO_URI"]
DATABASE_NAME = st.secrets["DATABASE_NAME"]

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# ------------------------------
# โหลดข้อมูลจาก Collection
# ------------------------------
@st.cache_data
def load_profiles(collection_name):
    collection = db[collection_name]
    return list(collection.find({}))

def find_profile(profiles, field, keyword):
    for profile in profiles:
        if keyword == str(profile.get(field, "")):
            return profile
    return None

def format_mongo_date(date_obj):
    return f"{date_obj.year}-{date_obj.month:02d}-{date_obj.day:02d}"

# ------------------------------
# เริ่มต้นหน้าเว็บ Streamlit
# ------------------------------
st.set_page_config(page_title="Profiles Explorer", page_icon="🌟")
st.title("🌟 ระบบค้นหาข้อมูล Profiles 🌟")

# ------------------------------
# เลือกประเภทข้อมูล
# ------------------------------
search_type = st.radio(
    "เลือกประเภทข้อมูลที่ต้องการค้นหา",
    (
        "Day Master (ธาตุประจำตัว)",
        "Zodiac Profile (นักสัตว์)",
        "Calendar Profile (ปฏิทิน)",
        "AI Prompt"
    )
)

collection_map = {
    "Day Master (ธาตุประจำตัว)": "daymaster_profiles",
    "Zodiac Profile (นักสัตว์)": "zodiac_profiles",
    "Calendar Profile (ปฏิทิน)": "calendar_profiles_2568",
    "AI Prompt": "ai_prompts"
}

field_map = {
    "Day Master (ธาตุประจำตัว)": "day_master",
    "Zodiac Profile (นักสัตว์)": "zodiac",
    "Calendar Profile (ปฏิทิน)": "date"
}

selected_collection = collection_map[search_type]
search_field = field_map.get(search_type, None)
profiles = load_profiles(selected_collection)

# ------------------------------
# แสดงข้อมูลตามประเภท
# ------------------------------
if search_type in ("Day Master (ธาตุประจำตัว)", "Zodiac Profile (นักสัตว์)"):
    options = sorted({p.get(search_field, "ไม่ระบุ") for p in profiles})
    selected_option = st.selectbox(f"เลือก {search_type}", options)

    if selected_option:
        profile = find_profile(profiles, search_field, selected_option)

        if profile:
            st.success(f"✅ พบข้อมูลเกี่ยวกับ {selected_option}")

            if search_type == "Day Master (ธาตุประจำตัว)":
                st.subheader(f"ธาตุ: {profile.get('day_master', '-')}")
                st.markdown(f"**ลักษณะทั่วไป:** {profile.get('characteristics', '-')}")
                st.markdown("**จุดแข็ง:**")
                for item in profile.get('strengths', []):
                    st.write(f"- {item}")
                st.markdown("**จุดอ่อน:**")
                for item in profile.get('weaknesses', []):
                    st.write(f"- {item}")
                st.markdown("**คำแนะนำเพื่อสมดุลชีวิต:**")
                for item in profile.get('advice_for_balance', []):
                    st.write(f"- {item}")
                st.markdown(f"**เสน่ห์:** {profile.get('charm', '-')}")

            elif search_type == "Zodiac Profile (นักสัตว์)":
                st.subheader(f"นักษัตร: {profile.get('zodiac', '-')}")
                st.markdown(f"**ลักษณะทั่วไป:** {profile.get('characteristics', '-')}")
                st.markdown("**จุดแข็ง:**")
                for item in profile.get('strengths', []):
                    st.write(f"- {item}")
                st.markdown("**จุดอ่อน:**")
                for item in profile.get('weaknesses', []):
                    st.write(f"- {item}")
                st.markdown("**เสน่ห์:**")
                st.write(profile.get('charm', '-'))
                st.markdown("**คำแนะนำเพื่อสมดุล:**")
                for item in profile.get('advice_for_balance', []):
                    st.write(f"- {item}")
                st.markdown("**ความสัมพันธ์กับนักษัตรอื่น:**")
                for item in profile.get('zodiac_relations', []):
                    st.write(f"- {item}")

elif search_type == "Calendar Profile (ปฏิทิน)":
    today = datetime.date.today()
    default_date = today if datetime.date(2025, 1, 1) <= today <= datetime.date(2025, 12, 31) else datetime.date(2025, 1, 1)

    selected_date = st.date_input(
        "เลือกวัน เดือน ปี",
        value=default_date,
        min_value=datetime.date(2025, 1, 1),
        max_value=datetime.date(2025, 12, 31)
    )

    formatted_date = format_mongo_date(selected_date)
    profile = find_profile(profiles, "date", formatted_date)

    st.info(f"🔍 กำลังค้นหาวันที่: {formatted_date}")

    if profile:
        st.success(f"✅ พบข้อมูลสำหรับวันที่ {formatted_date}")

        st.subheader(f"ธีมของวัน: {profile.get('theme', '-')}")
        st.markdown(f"**คำคมประจำวัน:** {profile.get('day_quote', '-')}")
        st.markdown(f"**ไฮไลท์ของวัน:** {profile.get('highlight_of_day', '-')}")
        st.markdown(f"**พลังของวัน:** {profile.get('power_of_day', '-')}")
        st.markdown(f"**ผลของฤดูกาล:** {profile.get('seasonal_effect', '-')}")
        st.markdown("**สีมงคลและสีที่ควรหลีกเลี่ยง:**")
        for item in profile.get('lucky_colors', []):
            st.write(f"- {item}")
        st.markdown("**สิ่งที่ควรทำ:**")
        for item in profile.get('things_to_do', []):
            st.write(f"- {item}")
        st.markdown("**สิ่งที่ควรหลีกเลี่ยง:**")
        for item in profile.get('things_to_avoid', []):
            st.write(f"- {item}")
        st.markdown("**ความสัมพันธ์ตามนักษัตร:**")
        for item in profile.get('zodiac_relations', []):
            st.write(f"- {item}")
    else:
        st.error(f"❌ ไม่พบข้อมูลสำหรับวันที่ {formatted_date}")

elif search_type == "AI Prompt":
    st.info("📘 เลือกหัวข้อ AI Prompt เพื่อดูรายละเอียด")

    if profiles:
        topic_map = {p.get("topic", "ไม่ระบุหัวข้อ"): p for p in profiles}
        topic_names = sorted(topic_map.keys())
        selected_topic = st.selectbox("เลือกหัวข้อ AI Prompt", topic_names)

        if selected_topic:
            prompt = topic_map[selected_topic]
            st.subheader(f"🧠 หัวข้อ: {prompt.get('topic', '-')}")
            st.markdown(f"**ลำดับ:** {prompt.get('order', '-')}")
            st.markdown(f"**API1:** `{prompt.get('api1', '-')}`")
            st.markdown(f"**API2:** `{prompt.get('api2', '-')}`")
            st.markdown("**Prompt:**")
            st.markdown(prompt.get("prompt", "-").strip(), unsafe_allow_html=True)
    else:
        st.warning("❌ ไม่พบข้อมูล AI Prompt")

