import pandas as pd
import streamlit as st
from datetime import datetime
from db import db

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
            full_date_text = col_data[0].strip()
            parts = full_date_text.split()

            try:
                day = int(parts[1])
                month_thai = parts[2]
                year_thai = int(parts[4])

                month = thai_months.get(month_thai)
                if not month:
                    continue

                year = year_thai - 543
                date_obj = datetime(year, month, day)

                record = {
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "day_name": full_date_text,
                    "theme": col_data[1].strip(),
                    "power_of_day": col_data[3].strip(),
                    "seasonal_effect": col_data[5].strip(),
                    "highlight_of_day": col_data[7].strip(),
                    "things_to_do": [
                        col_data[10].strip(),
                        col_data[11].strip(),
                        col_data[12].strip()
                    ],
                    "things_to_avoid": [
                        col_data[14].strip(),
                        col_data[15].strip()
                    ],
                    "zodiac_relations": [
                        col_data[17].strip(),
                        col_data[18].strip()
                    ],
                    "lucky_colors": [
                        col_data[20].strip(),
                        col_data[21].strip()
                    ],
                    "summary": [
                        col_data[23].strip()
                    ],
                    "day_quote": col_data[24].strip()
                }
                records.append(record)
            except Exception:
                continue
    return records

def handle_calendar_upload(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    upload_mode = st.radio("เลือกรูปแบบการอัปโหลด", ("📅 เดือนเดียว", "📅 ทั้งปี"))

    if upload_mode == "📅 เดือนเดียว":
        month = st.selectbox("เลือกเดือน:", xls.sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=month, header=None)
        st.subheader(f"🔍 Preview Data: เดือน {month}")
        st.dataframe(df)
        all_records = transform_calendar_dataframe(df)

    else:
        st.subheader("🔍 Preview Data: ทั้งปี (โชว์เดือนแรก)")
        first_month = xls.sheet_names[0]
        df = pd.read_excel(uploaded_file, sheet_name=first_month, header=None)
        st.dataframe(df)

        all_records = []
        for month in xls.sheet_names:
            df_month = pd.read_excel(uploaded_file, sheet_name=month, header=None)
            records = transform_calendar_dataframe(df_month)
            all_records.extend(records)

    if st.button("💾 Insert/Update Database"):
        collection = db["calendar_profiles_2568"]
        inserted, updated = 0, 0

        for record in all_records:
            filter_query = {"date": record["date"]}
            update_data = {"$set": record}
            result = collection.update_one(filter_query, update_data, upsert=True)
            if result.matched_count > 0:
                updated += 1
            else:
                inserted += 1

        st.success(f"🚀 Inserted {inserted} and updated {updated} records into calendar_profiles_2568!")
