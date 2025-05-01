import streamlit as st
from zodiac import handle_zodiac_upload
from daymaster import handle_daymaster_upload
from calendar_profiles import handle_calendar_upload

# ---------------------------
# หน้าเว็บหลัก
# ---------------------------
st.title("📂 Upload Excel ➔ Update MongoDB NoSQL")

# เลือกประเภทข้อมูล
option = st.selectbox(
    "เลือกประเภทข้อมูลที่ต้องการอัปโหลด",
    (
        "นักษัตร (Zodiac Profiles)",
        "Day Master Profiles",
        "Calendar Profiles 2568",
        "AI Prompt"  # ✅ เพิ่มตรงนี้
    )
)

...

if uploaded_file:
    if option == "นักษัตร (Zodiac Profiles)":
        handle_zodiac_upload(uploaded_file)
    elif option == "Day Master Profiles":
        handle_daymaster_upload(uploaded_file)
    elif option == "Calendar Profiles 2568":
        handle_calendar_upload(uploaded_file)
    elif option == "AI Prompt":
        handle_ai_prompt_upload(uploaded_file)  # ✅ ตรงนี้

