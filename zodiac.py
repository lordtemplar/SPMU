import pandas as pd
import streamlit as st
from utils import split_or_single
from db import db

def handle_zodiac_upload(uploaded_file):
    df = pd.read_excel(uploaded_file)
    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    records = []
    for _, row in df.iterrows():
        record = {
            "gender": row["เพศ"].strip(),
            "zodiac": row["นักษัตร"].strip(),
            "characteristics": str(row["ลักษณะโดยทั่วไป"]).strip(),
            "strengths": split_or_single(row["จุดแข็ง"]),
            "weaknesses": split_or_single(row["จุดอ่อน"]),
            "advice_for_balance": split_or_single(row["คำแนะนำเพื่อสร้างสมดุลในชีวิต"]),
            "charm": str(row["เสน่ห์ที่ดึงดูดใจ"]).strip(),
            "zodiac_relations": split_or_single(row["นักษัตรสัมพันธ์และปะทะ"]),
            "summary": str(row["สรุป"]).strip()
        }
        records.append(record)

    if st.button("💾 Insert/Update Database"):
        collection = db["zodiac_profiles"]
        inserted, updated = 0, 0

        for record in records:
            filter_query = {"gender": record["gender"], "zodiac": record["zodiac"]}
            update_data = {"$set": record}
            result = collection.update_one(filter_query, update_data, upsert=True)
            if result.matched_count > 0:
                updated += 1
            else:
                inserted += 1

        st.success(f"🚀 Inserted {inserted} and updated {updated} records into zodiac_profiles!")
