import streamlit as st
import pandas as pd
import hashlib
from sqlalchemy import create_engine
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import speech_recognition as sr
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Clinical Pharmacist Dashboard",
    page_icon="💊",
    layout="wide"
)

# -----------------------------
# HOSPITAL DARK THEME
# -----------------------------
st.markdown("""
<style>
body {background-color: #0E1117;}
.stApp {background-color: #0E1117;}
h1, h2, h3 {color: #00BFFF;}
.stButton>button {background-color: #007BFF; color: white;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
engine = create_engine(st.secrets["DATABASE_URL"])

# -----------------------------
# OPENAI CLIENT
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# PASSWORD HASHING
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
def login():
    st.title("🏥 Hospital Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        hashed = hash_password(password)
        query = f"SELECT role FROM users WHERE username='{username}' AND password='{hashed}'"
        result = pd.read_sql(query, engine)

        if not result.empty:
            st.session_state["user"] = username
            st.session_state["role"] = result.iloc[0]["role"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# -----------------------------
# LOGOUT
# -----------------------------
def logout():
    st.session_state.clear()
    st.rerun()

# -----------------------------
# AI FUNCTION
# -----------------------------
def ask_ai(question):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert Indian clinical pharmacist assistant."},
            {"role": "user", "content": question}
        ],
        temperature=0.3
    )
    return completion.choices[0].message.content

# -----------------------------
# DRUG DATABASE
# -----------------------------
def get_drugs(search=""):
    if search:
        query = f"SELECT * FROM essential_medicines WHERE generic_name ILIKE '%{search}%'"
    else:
        query = "SELECT * FROM essential_medicines"
    return pd.read_sql(query, engine)

# -----------------------------
# RENAL DOSE CALCULATOR
# -----------------------------
def renal_calculator():
    st.subheader("🧮 Renal Dose Calculator")
    age = st.number_input("Age")
    weight = st.number_input("Weight (kg)")
    serum_creatinine = st.number_input("Serum Creatinine (mg/dL)")

    if st.button("Calculate CrCl"):
        crcl = ((140 - age) * weight) / (72 * serum_creatinine)
        st.success(f"Estimated Creatinine Clearance: {round(crcl,2)} mL/min")

# -----------------------------
# PDF GENERATION
# -----------------------------
def generate_pdf(content):
    file_name = "clinical_report.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("AI Clinical Pharmacist Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(content, styles["Normal"]))
    doc.build(elements)
    return file_name

# -----------------------------
# VOICE INPUT
# -----------------------------
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)
    return r.recognize_google(audio)

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
def dashboard():
    st.sidebar.title("🏥 Navigation")
    page = st.sidebar.radio("Go to", [
        "AI Assistant",
        "Drug Database",
        "Renal Calculator",
        "Patient Profile",
        "Antibiotic Stewardship"
    ])

    st.sidebar.button("Logout", on_click=logout)

    # ---------------- AI ASSISTANT ----------------
    if page == "AI Assistant":
        st.title("💬 AI Clinical Assistant")

        user_input = st.text_area("Ask clinical question")

        if st.button("Ask AI"):
            response = ask_ai(user_input)
            st.write(response)

            if st.button("Generate PDF"):
                file = generate_pdf(response)
                with open(file, "rb") as f:
                    st.download_button("Download Report", f, file_name=file)

        if st.button("🎤 Voice"):
            text = speech_to_text()
            st.write("You said:", text)
            st.write(ask_ai(text))

    # ---------------- DRUG DATABASE ----------------
    elif page == "Drug Database":
        st.title("💊 Indian Essential Medicines")
        search = st.text_input("Search drug")
        drugs = get_drugs(search)
        st.dataframe(drugs, use_container_width=True)

    # ---------------- RENAL ----------------
    elif page == "Renal Calculator":
        renal_calculator()

    # ---------------- PATIENT PROFILE ----------------
    elif page == "Patient Profile":
        st.title("👨‍⚕️ Patient Medication Profile")
        name = st.text_input("Patient Name")
        meds = st.text_area("Current Medications")

        if st.button("Check Interactions"):
            response = ask_ai(f"Check interactions for: {meds}")
            st.write(response)

    # ---------------- ANTIBIOTIC STEWARDSHIP ----------------
    elif page == "Antibiotic Stewardship":
        st.title("🦠 Antibiotic Stewardship Module")
        infection = st.text_input("Infection Type")

        if st.button("Suggest Antibiotic"):
            response = ask_ai(f"Suggest evidence-based antibiotic for {infection} according to Indian guidelines")
            st.write(response)

# -----------------------------
# APP START
# -----------------------------
if "user" not in st.session_state:
    login()
else:
    dashboard()
