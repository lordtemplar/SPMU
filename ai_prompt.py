import pandas as pd
import streamlit as st
from db import db

# ---------------------------------
# แยก prompt เป็น section ย่อย
# ---------------------------------
def extract_prompt_sections(text):
    sections = {
        "description": "",
        "guidelines": [],
        "criteria": [],
        "objective": ""
    }

    lines = str(text).splitlines()
    current_section = "description"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("หลักเกณฑ์ในการให้คำตอบ"):
            current_section = "criteria"
            continue
        elif line.startswith("เป้าหมาย"):
            current_section = "objective"
            continue
        elif line.startswith("ให้คำตอบเป็นไปตามแนวทาง"):
            current_section = "guidelines"
            continue

        if current_section == "description":
            sections["description"] += line + " "
        elif current_section == "guidelines":
            clean = line.strip("●✅- ").strip()
            if clean:
                sections["guidelines"].append(clean)
        elif current_section == "criteria":
            clean = line.strip("●✅- ").strip()
            if clean:
                sections["criteria"].append(clean)
        elif current_section == "objective":
            sections["objective"] += line + " "

    sections["description"] = sections["description"].strip()
    sections["objective"] = sections["objective"].strip()
    return sections

# ---------------------------------
# โหลด + Insert AI Prompts
# ---------------------------------
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
