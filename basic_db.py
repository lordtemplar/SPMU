import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# ----------------------
# ตั้งค่าการเชื่อมต่อ MongoDB
# ----------------------
MONGO_URI = st.secrets["MONGO_URI"]  # เก็บ Secret นี้ใน Streamlit Cloud Settings
DB_NAME = "your_database"

# Connect MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ----------------------
# ฟังก์ชันแปลง DataFrame เป็น List of Dict สำหรับ Zodiac Profiles
# ----------------------
def transform_zodiac_dataframe(df):
    records = []
    for _, row in df.iterrows():
        record = {
            "gender": row["เพศ"],
            "zodiac": row["นักษัตร"],
            "characteristics": row["ลักษณะโดยทั่วไป"],
            "strengths": row["จุดแข็ง"],
            "weaknesses": row["จุดอ่อน"],
            "advice_for_balance": row["คำแนะนำเพื่อสร้างสมดุลในชีวิต"],
            "charm": row["เสน่ห์ที่ดึงดูดใจ"],
            "zodiac_relations": row["นักษัตรสัมพันธ์และปะทะ"],
            "summary": row["สรุป"]
        }
        records.append(record)
    return records

# ----------------------
# ฟังก์ชันแปลง DataFrame เป็น List of Dict สำหรับ Day Master Profiles
# ----------------------
def transform_daymaster_dataframe(df):
    records = []
    for _, row in df.iterrows():
        record = {
            "gender": row["เพศ"],
            "day_master": row["Day Master"],
            "characteristics": row["ลักษณะโดยทั่วไป"],
            "strengths": row["จุดแข็ง"],
            "weaknesses": row["จุดอ่อน"],
            "advice_for_balance": row["คำแนะนำเพื่อสร้างสมดุล"],
            "charm": row["เสน่ห์ที่ดึงดูดใจ"],
            "summary": row["สรุป"]
        }
        records.append(record)
    return records

# ----------------------
# ฟังก์ชันแปลง DataFrame เป็น List of Dict สำหรับ Calendar Profiles
# ----------------------
def transform_calendar_dataframe(df, month_name):
    records = []
    for col in df.columns:
        col_data = df[col].dropna().tolist()
        if len(col_data) >= 19:
            # ดึงวันและวันที่
            full_date_text = col_data[0]
            day_name = full_date_text.split("ที่")[0].strip()
            date_text = full_date_text.split("ที่")[-1].strip()
            date_obj = datetime.strptime(date_text.replace(" พ.ศ. ", "/"), "%d %B/%Y")
            date_obj = date_obj.replace(year=date_obj.year - 543)

            record = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "theme": col_data[1],
                "power_of_day": col_data[3],
                "seasonal_effect": col_data[5],
                "highlight_of_day": col_data[7],
                "things_to_do": col_data[10],
                "things_to_avoid": col_data[12],
                "zodiac_relations": col_data[14],
                "lucky_colors": col_data[16],
                "summary": col_data[18]
            }
            records.append(record)
    return records

# ----------------------
# UI - Streamlit Layout
# ----------------------
st.title("📂 Upload Excel ➔ Update MongoDB NoSQL")

option = st.selectbox(
    "เลือกประเภทข้อมูลที่ต้องการอัปโหลด",
    ("นักษัตร (Zodiac Profiles)", "Day Master Profiles", "Calendar Profiles 2568")
)

uploaded_file = st.file_uploader("📎 Upload your Excel file:", type=["xlsx"])

if uploaded_file:
    # อ่านไฟล์ Excel
    xls = pd.ExcelFile(uploaded_file)
    if option == "Calendar Profiles 2568":
        month = st.selectbox("เลือกเดือน:", xls.sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=month)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    # เลือกการแปลงข้อมูลตามประเภท
    if option == "นักษัตร (Zodiac Profiles)":
        collection = db["zodiac_profiles"]
        records = transform_zodiac_dataframe(df)
    elif option == "Day Master Profiles":
        collection = db["daymaster_profiles"]
        records = transform_daymaster_dataframe(df)
    else:
        collection = db["calendar_profiles_2568"]
        records = transform_calendar_dataframe(df, month)

    if st.button("💾 Insert/Update Database"):
        if records:
            inserted, updated = 0, 0
            for record in records:
                if option == "นักษัตร (Zodiac Profiles)":
                    filter_query = {"gender": record["gender"], "zodiac": record["zodiac"]}
                elif option == "Day Master Profiles":
                    filter_query = {"gender": record["gender"], "day_master": record["day_master"]}
                else:
                    filter_query = {"date": record["date"]}
                update_data = {"$set": record}
                result = collection.update_one(filter_query, update_data, upsert=True)
                if result.matched_count > 0:
                    updated += 1
                else:
                    inserted += 1
            st.success(f"🚀 Successfully inserted {inserted} and updated {updated} records into {collection.name}!")
        else:
            st.warning("No data to insert!")

    st.subheader("📊 Current Database Records:")
    docs = list(collection.find({}, {"_id": 0}))
    if docs:
        st.dataframe(pd.DataFrame(docs))
    else:
        st.info("📚 No records found in database.")

# ----------------------
# Tips
# ----------------------
# • ไปที่ Streamlit Cloud Settings > Secrets เพื่อเก็บ MONGO_URI เช่น
# • ปรับ df.columns ให้ตรงกับชื่อคอลัมน์ให้ตรง
# • โปรแกรมข้อมูลแบบ Bulk Insert/Update
# • รองรับหน้า Dashboard เพื่อแสดงข้อมูลแยกตาม Collection
