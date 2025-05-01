import pandas as pd
import streamlit as st
from db import db

def extract_prompt_sections(text):
    sections = {
        "description": "",
        "guidelines": [],
        "criteria": [],
        "objective": ""
    }

    lines = str(text).splitlines()
    mode = "description"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("ให้คำตอบเป็นไปตามแนวทาง"):
            mode = "guidelines"
            continue
        elif line.startswith("หลักเกณฑ์ในการให้คำตอบ"):
            mode = "criteria"
            continue
        elif line.startswith("เป้าหมาย"):
            mode = "objective"
            continue

        if mode == "description":
            sections["description"] += line + " "
        elif mode == "guidelines":
            sections["guidelines"].append(line.strip("● ").strip("- ").strip("✅ ").strip())
        elif mode == "criteria":
            sections["criteria"].append(line.strip("● ").strip("- ").strip("✅ ").strip())
        elif mode == "objective":
            sections["objective"] += line + " "

    # Clean up whitespace
    sections["description"] = sections["description"].strip()
    sections["objective"] = sections["objective"].strip()
    return sections

def handle_ai_prompt_upload(uploaded_file):
    df = pd.read_excel(uploaded_file)
    st.subheader("🔍 Preview Data:")
    st.dataframe(df)

    records = []
    for _, row in df.iterrows():
        parsed_prompt = extract_prompt_sections(row["Prompt"])
        record = {
            "order": int(row["ลำดับคำถาม"]),
            "topic": str(row["หัวข้อ"]).strip(),
            "api1": str(row["API1"]).strip() if pd.notna(row["API1"]) else "-",
            "api2": str(row["API2"]).strip() if pd.notna(row["API2"]) else "-",
            "prompt": parsed_prompt
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
