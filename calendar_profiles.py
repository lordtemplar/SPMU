import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# ----------------------
# ตั้งค่าการเชื่อมต่อ MongoDB
# ----------------------
MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = "your_database"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ----------------------
# ฟังก์ชันสำหรับทำความสะอาดข้อมูลก่อน Insert
# ----------------------
def clean_record(record):
    cleaned = {}
    for key, value in record.items():
        if isinstance(value, str):
            cleaned[key] = value.strip()
        else:
            cleaned[key] = value
    return cleaned

# ----------------------
# ฟังก์ชันค้นหาวันที่จริง
# ----------------------
def find_real_date_text(col_data):
    for text in col_data:
        if text.startswith("วัน") and "ที่" in text:
            return text.strip()
    return None

# ----------------------
# Transform ฟังก์ชัน Calendar Profiles
# ----------------------
def transform_calendar_dataframe(df, month_name):
    thai_months = {
        "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4,
        "พฤษภาคม": 5, "มิถุนายน": 6, "กรกฎาคม": 7, "สิงหาคม": 8,
        "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12
    }
    records = []
    for col in df.columns:
        col_data = df[col].dropna().tolist()
        if len(col_data) >= 25:
            full_date_text = find_real_date_text(col_data)
            if not full_date_text:
                continue

            day_part, date_part = full_date_text.split("ที่", 1)
            day_name = full_date_text.strip()
            date_text = date_part.strip().replace("พ.ศ.", "").replace(" พ.ศ.", "").strip()

            parts = date_text.split()
            if len(parts) != 3:
                continue

            day = int(parts[0])
            month_thai = parts[1]
            year_thai = int(parts[2])

            month = thai_months.get(month_thai)
            if not month:
                continue

            year = year_thai - 543
            date_obj = datetime(year, month, day)

            record = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "theme": col_data[1],
                "power_of_day": col_data[3],
                "seasonal_effect": col_data[5],
                "highlight_of_day": col_data[7],
                "things_to_do": [col_data[10], col_data[11], col_data[12]],
                "things_to_avoid": [col_data[14], col_data[15], col_data[16]],
                "zodiac_relations": [col_data[18], col_data[19]],
                "lucky_colors": [col_data[21], col_data[22]],
                "summary": col_data[23],
                "day_quote": col_data[24]
            }
            records.append(record)
    return records

# ----------------------
# UI
# ----------------------
st.title("📂 Upload Excel ➔ Update MongoDB NoSQL")

option = st.selectbox("เลือกประเภทข้อมูลที่ต้องการอัปโหลด", ("Calendar Profiles 2568",))
uploaded_file = st.file_uploader("📎 Upload your Excel file:", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    month = st.selectbox("เลือกเดือน:", xls.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=month)

    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    collection = db["calendar_profiles_2568"]
    records = transform_calendar_dataframe(df, month)

    if st.button("💾 Insert/Update Database"):
        if records:
            inserted, updated = 0, 0
            for record in records:
                record = clean_record(record)
                filter_query = {"date": record["date"]}
                update_data = {"$set": record}
                result = collection.update_one(filter_query, update_data, upsert=True)
                if result.matched_count > 0:
                    updated += 1
                else:
                    inserted += 1
            st.success(f"🚀 Inserted {inserted} and updated {updated} records into {collection.name}!")
        else:
            st.warning("No data to insert!")

    st.subheader("📊 Current Database Records:")
    docs = list(collection.find({}, {"_id": 0}))
    if docs:
        st.dataframe(pd.DataFrame(docs))
    else:
        st.info("📚 No records found in database.")
