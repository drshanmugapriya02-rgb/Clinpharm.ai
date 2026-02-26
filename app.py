import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="ClinPharm AI",
                   page_icon="💊",
                   layout="wide")

st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
.stButton>button {
    background-color:#005BAC;
    color:white;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("clinpharm.db", check_same_thread=False)
cursor = conn.cursor()

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# Drug Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS drugs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    drug_class TEXT,
    indication TEXT,
    adult_dose TEXT,
    renal_adjustment TEXT,
    pregnancy TEXT,
    interactions TEXT
)
""")

# Patient Profile Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    diagnosis TEXT,
    medications TEXT
)
""")

conn.commit()

# ==============================
# HELPER FUNCTIONS
# ==============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, role):
    cursor.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                   (username, hash_password(password), role))
    conn.commit()

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, hash_password(password)))
    return cursor.fetchone()

# ==============================
# LOGIN PAGE
# ==============================
st.title("🏥 ClinPharm AI Dashboard")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    role = st.selectbox("Role", ["Intern", "Clinical Pharmacist"])
    if st.button("Register"):
        add_user(new_user, new_password, role)
        st.success("Account Created Successfully")

elif choice == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.success(f"Welcome {username} ({user[3]})")
            st.session_state["logged_in"] = True
            st.session_state["role"] = user[3]
        else:
            st.error("Invalid Credentials")

# ==============================
# MAIN DASHBOARD
# ==============================
if "logged_in" in st.session_state:

    st.sidebar.title("Navigation")
    module = st.sidebar.radio("Select Module", [
        "Drug Database",
        "Interaction Checker",
        "Renal Dose Calculator",
        "AI Symptom Suggestion",
        "Antibiotic Stewardship",
        "Antibiotic Spectrum",
        "Clinical Calculator",
        "Patient Medication Profile",
        "Prescription Error Detection",
        "Crash Cart"
    ])

    # --------------------------
    # Drug Database
    # --------------------------
    if module == "Drug Database":
        st.header("💊 Drug Database")
        df = pd.read_sql_query("SELECT * FROM drugs", conn)
        st.dataframe(df)

    # --------------------------
    # Interaction Checker
    # --------------------------
    if module == "Interaction Checker":
        st.header("⚠ Drug Interaction Checker")
        drug1 = st.text_input("Drug 1")
        drug2 = st.text_input("Drug 2")
        if st.button("Check Interaction"):
            if drug1.lower() == "warfarin" and drug2.lower() == "aspirin":
                st.error("Major Interaction: Increased Bleeding Risk")
            else:
                st.success("No major interaction found (Demo Version)")

    # --------------------------
    # Renal Dose Calculator
    # --------------------------
    if module == "Renal Dose Calculator":
        st.header("🧮 Renal Dose Calculator")
        age = st.number_input("Age")
        weight = st.number_input("Weight (kg)")
        serum_creat = st.number_input("Serum Creatinine")
        gender = st.selectbox("Gender", ["Male", "Female"])
        if st.button("Calculate CrCl"):
            crcl = ((140 - age) * weight) / (72 * serum_creat)
            if gender == "Female":
                crcl *= 0.85
            st.success(f"Estimated CrCl: {round(crcl,2)} mL/min")

    # --------------------------
    # AI Symptom Suggestion
    # --------------------------
    if module == "AI Symptom Suggestion":
        st.header("🤖 AI Symptom Based Drug Suggestion")
        symptom = st.text_input("Enter Symptom")
        if st.button("Suggest"):
            if "fever" in symptom.lower():
                st.info("Suggested: Paracetamol 500mg")
            elif "pain" in symptom.lower():
                st.info("Suggested: Ibuprofen 400mg")
            else:
                st.warning("Refer Clinical Guidelines")

    # --------------------------
    # Antibiotic Stewardship
    # --------------------------
    if module == "Antibiotic Stewardship":
        st.header("🦠 Antibiotic Stewardship")
        infection = st.selectbox("Infection Type",
                                 ["UTI", "Pneumonia", "Sepsis"])
        if infection == "UTI":
            st.write("Recommended: Nitrofurantoin")
        elif infection == "Pneumonia":
            st.write("Recommended: Ceftriaxone + Azithromycin")

    # --------------------------
    # Antibiotic Spectrum
    # --------------------------
    if module == "Antibiotic Spectrum":
        st.header("📊 Antibiotic Spectrum Chart")
        data = {
            "Antibiotic": ["Ceftriaxone", "Meropenem"],
            "Gram +": ["Yes", "Yes"],
            "Gram -": ["Yes", "Yes"],
            "Anaerobes": ["No", "Yes"]
        }
        st.table(pd.DataFrame(data))

    # --------------------------
    # Clinical Calculator
    # --------------------------
    if module == "Clinical Calculator":
        st.header("🧮 Clinical Calculator")
        glucose = st.number_input("Blood Glucose")
        if st.button("Interpret"):
            if glucose > 200:
                st.error("Hyperglycemia")
            else:
                st.success("Normal")

    # --------------------------
    # Patient Medication Profile
    # --------------------------
    if module == "Patient Medication Profile":
        st.header("📁 Patient Medication Profile")
        name = st.text_input("Patient Name")
        age = st.number_input("Age", 1, 120)
        diagnosis = st.text_input("Diagnosis")
        meds = st.text_area("Medications")
        if st.button("Save Patient"):
            cursor.execute("INSERT INTO patients (name,age,diagnosis,medications) VALUES (?,?,?,?)",
                           (name, age, diagnosis, meds))
            conn.commit()
            st.success("Patient Saved")

        df = pd.read_sql_query("SELECT * FROM patients", conn)
        st.dataframe(df)

    # --------------------------
    # Prescription Error Detection
    # --------------------------
    if module == "Prescription Error Detection":
        st.header("🚨 Prescription Error Detection")
        dose = st.number_input("Entered Dose (mg)")
        if dose > 1000:
            st.error("Possible Overdose Alert!")
        else:
            st.success("Dose within safe range")

    # --------------------------
    # Crash Cart
    # --------------------------
    if module == "Crash Cart":
        st.header("🚑 Emergency Crash Cart")
        crash_cart = [
            "Adrenaline",
            "Atropine",
            "Amiodarone",
            "Dopamine",
            "Magnesium Sulfate",
            "Sodium Bicarbonate"
        ]
        st.write(crash_cart)
