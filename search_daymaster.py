# streamlit_app.py

import streamlit as st
from pymongo import MongoClient

# ------------------------------
# เชื่อมต่อ MongoDB ด้วย Secret
# ------------------------------
MONGO_URI = st.secrets["MONGO_URI"]
DATABASE_NAME = st.secrets["DATABASE_NAME"]
COLLECTION_NAME = st.secrets["COLLECTION_NAME"]

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# ------------------------------
# โหลดข้อมูลทั้งหมด
# ------------------------------
@st.cache_data
def load_all_profiles():
    profiles = list(collection.find({}))
    return profiles

# ------------------------------
# ดึงชื่อธาตุทั้งหมด สำหรับเลือก
# ------------------------------
def get_day_masters(profiles):
    return [profile["day_master"] for profile in profiles]

# ------------------------------
# หาโปรไฟล์จากชื่อธาตุ
# ------------------------------
def find_profile_by_day_master(profiles, day_master):
    for profile in profiles:
        if profile["day_master"] == day_master:
            return profile
    return None

# ------------------------------
# เริ่มต้นหน้าเว็บ Streamlit
# ------------------------------
st.set_page_config(page_title="Day Master Profiles", page_icon="🌟")

st.title("🌟 ข้อมูลธาตุประจำตัว (Day Master) 🌟")

# โหลดโปรไฟล์ทั้งหมด
profiles = load_all_profiles()
day_masters = get_day_masters(profiles)

# Selectbox ให้เลือกธาตุ
selected_day_master = st.selectbox("เลือกธาตุที่ต้องการดูข้อมูล", day_masters)

# หาและแสดงข้อมูลโปรไฟล์
profile = find_profile_by_day_master(profiles, selected_day_master)

if profile:
    st.subheader(f"ชื่อธาตุประจำตัว: {profile['day_master']}")
    st.markdown(f"**ลักษณะโดยทั่วไป:** {profile['characteristics']}")
    
    st.markdown("**จุดแข็ง:**")
    for strength in profile.get('strengths', []):
        st.write(f"- {strength}")
    
    st.markdown("**จุดอ่อน:**")
    for weakness in profile.get('weaknesses', []):
        st.write(f"- {weakness}")
    
    st.markdown("**คำแนะนำเพื่อสร้างสมดุลในชีวิต:**")
    for advice in profile.get('advice_for_balance', []):
        st.write(f"- {advice}")

    st.markdown(f"**เสน่ห์ที่ดึงดูดใจ:** {profile['charm']}")
    
    st.success("✅ ข้อมูลแสดงผลเรียบร้อยแล้ว")
else:
    st.error("❌ ไม่พบข้อมูลของธาตุที่เลือก")

