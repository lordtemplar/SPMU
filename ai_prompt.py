import pandas as pd
import streamlit as st
from db import db

def handle_ai_prompt_upload(uploaded_file):
    df = pd.read_excel(uploaded_file)
    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    records = []
    for _, row in df.iterrows():
        record = {
            "order": int(row["ลำดับ"]),
            "topic": str(row["หัวข้อ"]).strip(),
            "api1": str(row["API1"]).strip() if pd.notna(row["API1"]) else "-",
            "api2": str(row["API2"]).strip() if pd.notna(row["API2"]) else "-",
            "description": str(row["รายละเอียด"]).strip()
        }
        records.append(record)

    if st.button("💾 Insert/Update Database"):
        collection = db["ai_prompts"]
        inserted, updated = 0, 0

        for record in records:
            filter_query = {"order": record["order"]}
            update_data = {"$set": record}
            result = collection.update_one(filter_query, update_data, upsert=True)
            if result.matched_count > 0:
                updated += 1
            else:
                inserted += 1

        st.success(f"🚀 Inserted {inserted} and updated {updated} records into ai_prompts!")
