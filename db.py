from pymongo import MongoClient
import streamlit as st

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = "your_database"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
