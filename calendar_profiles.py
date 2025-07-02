import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# -------------------
# ตั้งค่าการเชื่อม MongoDB
# -------------------
MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = "your_database"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["calendar_profiles_2568"]

# -------------------
# ฟังก์ชันแปลง DataFrame เป็น list of dict
# -------------------
def transform_calendar_dataframe(df):
    thai_months = {
        "มกราคม": 1,
        "กุมภาพันธ์": 2,
        "มีนาคม": 3,
        "เมษายน": 4,
        "พฤษภาคม": 5,
        "มิถุนายน": 6,
        "กรกฎาคม": 7,
        "สิงหาคม": 8,
        "กันยายน": 9,
        "ตุลาคม": 10,
        "พฤศจิกายน": 11,
        "ธันวาคม": 12
    }

    records = []

    for col in df.columns:
        col_data = df[col].dropna().tolist()

        if len(col_data) < 24:
            st.warning(f"❗️ Column '{col}' มีข้อมูลไม่ครบ (rows < 24)")
            continue

        full_date_text = col_data[0].strip()

        try:
            day_part, date_part = full_date_text.split("ที่", 1)
            day_name = full_date_text

            date_text = date_part.replace("พ.ศ.", "").strip()
            parts = date_text.split()

            day = int(parts[0])
            month_thai = parts[1]
            year_thai = int(parts[2])

            month = thai_months.get(month_thai)
            if not month:
                st.warning(f"❗️ ไม่รู้จักเดือน: {month_thai}")
                continue

            year = year_thai - 543
            date_obj = datetime(year, month, day)

            record = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "theme": col_data[1].strip(),
                "power_of_day": col_data[3].strip(),
                "seasonal_effect": col_data[5].strip(),
                "highlight_of_day": col_data[7].strip(),
                "things_to_do": [col_data[9].strip(), col_data[10].strip(), col_data[11].strip()],
                "things_to_avoid": [col_data[13].strip(), col_data[14].strip()],
                "zodiac_relations": [col_data[16].strip(), col_data[17].strip()],
                "lucky_colors": [col_data[19].strip(), col_data[20].strip()],
                "summary": [col_data[22].strip()],
                "day_quote": col_data[23].strip()
            }

            records.append(record)

        except Exception as e:
            st.warning(f"⚠️ Error parsing column '{col}': {e}")
            continue

    return records

# -------------------
# ฟังก์ชันหลักจัดการ upload
# -------------------
def handle_calendar_upload(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    month = st.selectbox("เลือกเดือน:", xls.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=month)

    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    records = transform_calendar_dataframe(df)

    if st.button("💾 Insert/Update Calendar Database"):
        if records:
            inserted, updated = 0, 0
            for record in records:
                filter_query = {"date": record["date"]}
                update_data = {"$set": record}
                result = collection.update_one(filter_query, update_data, upsert=True)
                if result.matched_count > 0:
                    updated += 1
                else:
                    inserted += 1
            st.success(f"✅ Inserted: {inserted}, Updated: {updated} records!")
        else:
            st.warning("⚠️ No data to insert!")

    st.subheader("📊 Current Database Records:")
    docs = list(collection.find({}, {"_id": 0}).sort("date", 1))
    if docs:
        st.dataframe(pd.DataFrame(docs))
    else:
        st.info("📚 No records found in database.")
