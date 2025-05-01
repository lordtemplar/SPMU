import pandas as pd
import streamlit as st
from db import db

# ---------------------------------
# แยก prompt เป็น section ย่อย พร้อมแยก ● ใน guidelines เป็น list
# ---------------------------------
def extract_prompt_sections(text):
    sections = {
        "description": "",
        "guidelines": [],
        "criteria": [],
        "objective": ""
    }

    lines = str(text).splitlines()
    buffer_guidelines = []
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
            if "ให้คำตอบเป็นไปตามแนวทาง" in line:
                before, after = line.split("ให้คำตอบเป็นไปตามแนวทาง", 1)
                sections["description"] += before.strip() + " ให้คำตอบเป็นไปตามแนวทางดังต่อไปนี้:"
                buffer_guidelines.append(after.strip())
                current_section = "guidelines"
            else:
                sections["description"] += line + " "

        elif current_section == "guidelines":
            buffer_guidelines.append(line)

        elif current_section == "criteria":
            clean = line.strip("●✅- ").strip()
            if clean:
                sections["criteria"].append(clean)

        elif current_section == "objective":
            sections["objective"] += line + " "

    # ✅ แยก bullet point `●` ออกจาก buffer_guidelines
    guideline_text = " ".join(buffer_guidelines)
    if "●" in guideline_text:
        sections["guidelines"] = [item.strip("● ").strip() for item in guideline_text.split("●") if item.strip()]
    else:
        sections["guidelines"] = [guideline_text.strip()] if guideline_text.strip() else []

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
