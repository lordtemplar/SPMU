import pandas as pd
import streamlit as st
from datetime import datetime
from db import db  # ดึงการเชื่อมต่อจาก db.py

def handle_calendar_upload(uploaded_file):
    # โหลดไฟล์ Excel
    xls = pd.ExcelFile(uploaded_file)
    month = st.selectbox("เลือกเดือน:", xls.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=month)

    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    # แปลงข้อมูล
    records = transform_calendar_dataframe(df)

    collection = db["calendar_profiles_2568"]

    if st.button("💾 Insert/Update Database"):
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
            st.success(f"🚀 Inserted {inserted} and updated {updated} records into {collection.name}!")
        else:
            st.warning("No data to insert!")

    # แสดงข้อมูลปัจจุบัน
    st.subheader("📊 Current Database Records:")
    docs = list(collection.find({}, {"_id": 0}))
    if docs:
        st.dataframe(pd.DataFrame(docs))
    else:
        st.info("📚 No records found in database.")

def transform_calendar_dataframe(df):
    thai_months = {
        "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4,
        "พฤษภาคม": 5, "มิถุนายน": 6, "กรกฎาคม": 7, "สิงหาคม": 8,
        "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12
    }

    records = []

    for col in df.columns:
        col_data = df[col].dropna().tolist()
        if len(col_data) >= 25:
            # หา date text
            full_date_text = next((t for t in col_data if t.startswith("วัน") and "ที่" in t), None)
            if not full_date_text:
                continue

            day_name = full_date_text.strip()
            date_text = full_date_text.split("ที่", 1)[1].strip().replace("พ.ศ.", "").replace(" พ.ศ.", "").strip()
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

            # จัดการข้อมูล list
            things_to_do = [col_data[10], col_data[11], col_data[12]]
            things_to_avoid = [col_data[14], col_data[15], col_data[16]]
            zodiac_relations = [col_data[18], col_data[19]]
            lucky_colors = [col_data[21], col_data[22]]

            record = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "theme": col_data[1],
                "power_of_day": col_data[3],
                "seasonal_effect": col_data[5],
                "highlight_of_day": col_data[7],
                "things_to_do": things_to_do,
                "things_to_avoid": things_to_avoid,
                "zodiac_relations": zodiac_relations,
                "lucky_colors": lucky_colors,
                "summary": col_data[23],
                "day_quote": col_data[24]
            }
            records.append(record)

    return records
