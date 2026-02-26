import streamlit as st
import pandas as pd
import hashlib
from sqlalchemy import create_engine, text
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import speech_recognition as sr
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Page config
st.set_page_config(page_title="AI Clinical Pharmacist Dashboard", page_icon="💊", layout="wide")

# Hospital dark theme
st.markdown("""
<style>
body {background-color: #0E1117;}
.stApp {background-color: #0E1117;}
h1, h2, h3 {color: #00BFFF;}
.stButton>button {background-color: #007BFF; color: white;}
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_engine():
    return create_engine(st.secrets["DATABASE_URL"])

engine = get_engine()

# OpenAI client
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

client = get_openai_client()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login system
def login():
    st.title("🏥 Hospital Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        hashed = hash_password(password)
        query = text("SELECT role FROM users WHERE username=:username AND password=:password")
        try:
            result = pd.read_sql(query, engine, params={'username': username, 'password': hashed})
            if not result.empty:
                st.session_state["user"] = username
                st.session_state["role"] = result.iloc[0]["role"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"Database error: {e}")

# Logout
def logout():
    st.session_state.clear()
    st.rerun()

# AI function
def ask_ai(question):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert Indian clinical pharmacist assistant."},
                {"role": "user", "content": question}
