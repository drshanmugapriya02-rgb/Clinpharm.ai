import streamlit as st
import pandas as pd
import hashlib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Clinical Pharmacist Dashboard",
    page_icon="💊",
    layout="wide"
)

# ---------------- HOSPITAL DARK THEME ----------------
st.markdown("""
<style>
.stApp {background-color: #0E1117;}
h1, h2, h3 {color: #00BFFF;}
.stButton>button {background-color: #007BFF; color: white;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIMPLE USER DATABASE ----------------
users = {
    "intern": {"password": hashlib.sha256("1234".encode()).hexdigest(), "role": "Intern"},
    "pharmacist": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "Clinical Pharmacist"}
}

# ---------------- DRUG DATABASE (Sample Essential Medicines) ----------------
drug_data = pd.DataFrame([
    ["Paracetamol", "Tablet", "500 mg", "Analgesic"],
    ["Amoxicillin", "Capsule", "500 mg", "Antibiotic"],
    ["Ceftriaxone", "Injection", "1 g", "Antibiotic"],
    ["Metformin", "Tablet", "500 mg", "Antidiabetic"],
    ["Aspirin", "Tablet", "75 mg", "Antiplatelet"],
    ["Atorvastatin", "Tablet", "10 mg", "Statin"],
    ["Pantoprazole", "Tablet", "40 mg", "PPI"],
    ["Salbutamol", "Inhaler", "100 mcg", "Bronchodilator"]
], columns=["Generic Name", "Dosage Form", "Strength", "Category"])

# ---------------- LOGIN ----------------
def login():
    st.title("🏥 Hospital Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        hashed = hashlib.sha256(password.encode()).hexdigest()

        if username in users and users[username]["password"] == hashed:
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- LOGOUT ----------------
def logout():
    st.session_state.clear()
    st.rerun()

# ---------------- RENAL CALCULATOR ----------------
def renal_calculator():
    st.subheader("🧮 Renal Dose Calculator")
    age = st.number_input("Age", min_value=1)
    weight = st.number_input("Weight (kg)", min_value=1)
    serum_creatinine = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1)

    if st.button("Calculate"):
        crcl = ((140 - age) * weight) / (72 * serum_creatinine)
        st.success(f"Creatinine Clearance: {round(crcl,2)} mL/min")

# ---------------- INTERACTION CHECKER ----------------
def interaction_checker(meds):
    meds = meds.lower()

    if "aspirin" in meds and "warfarin" in meds:
        return "⚠ Major Interaction: Increased bleeding risk."
    elif "ceftriaxone" in meds and "calcium" in meds:
        return "⚠ Risk of precipitation in neonates."
    else:
        return "No major interaction found (basic database)."

# ---------------- ANTIBIOTIC STEWARDSHIP ----------------
def antibiotic_suggestion(infection):
    infection = infection.lower()

    if "uti" in infection:
        return "Suggested: Nitrofurantoin / Fosfomycin (Uncomplicated UTI)"
    elif "pneumonia" in infection:
        return "Suggested: Amoxicillin + Clavulanate / Ceftriaxone"
    elif "sepsis" in infection:
        return "Suggested: Piperacillin-Tazobactam"
    else:
        return "Refer to hospital antibiotic policy."

# ---------------- PDF GENERATION ----------------
def generate_pdf(content):
    file_name = "clinical_report.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Clinical Pharmacist Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(content, styles["Normal"]))

    doc.build(elements)
    return file_name

# ---------------- DASHBOARD ----------------
def dashboard():
    st.sidebar.title(f"Welcome {st.session_state['role']}")
    page = st.sidebar.radio("Navigation", [
        "Drug Database",
        "Renal Calculator",
        "Interaction Checker",
        "Antibiotic Stewardship",
        "Patient Profile"
    ])

    st.sidebar.button("Logout", on_click=logout)

    if page == "Drug Database":
        st.title("💊 Essential Medicines")
        search = st.text_input("Search Drug")
        if search:
            filtered = drug_data[drug_data["Generic Name"].str.contains(search, case=False)]
            st.dataframe(filtered)
        else:
            st.dataframe(drug_data)

    elif page == "Renal Calculator":
        renal_calculator()

    elif page == "Interaction Checker":
        st.title("⚠ Drug Interaction Checker")
        meds = st.text_area("Enter medications separated by comma")
        if st.button("Check Interaction"):
            result = interaction_checker(meds)
            st.write(result)

    elif page == "Antibiotic Stewardship":
        st.title("🦠 Antibiotic Stewardship")
        infection = st.text_input("Enter Infection Type")
        if st.button("Suggest"):
            result = antibiotic_suggestion(infection)
            st.write(result)

    elif page == "Patient Profile":
        st.title("👨‍⚕ Patient Medication Profile")
        name = st.text_input("Patient Name")
        meds = st.text_area("Current Medications")

        if st.button("Analyze"):
            result = interaction_checker(meds)
            st.write(result)

            file = generate_pdf(result)
            with open(file, "rb") as f:
                st.download_button("Download Report", f, file_name=file)

# ---------------- APP START ----------------
if "user" not in st.session_state:
    login()
else:
    dashboard()
def high_risk_alert(meds):
    high_risk = ["warfarin", "insulin", "heparin", "morphine", "digoxin"]
    alerts = []

    for drug in high_risk:
        if drug in meds.lower():
            alerts.append(f"⚠ High Risk Medication Detected: {drug.title()}")

    if alerts:
        return "\n".join(alerts)
    else:
        return "No high-risk medications detected."
        def lasa_alert(meds):
    lasa_pairs = {
        "dopamine": "dobutamine",
        "prednisolone": "prednisone",
        "clopidogrel": "clozapine"
    }

    alerts = []
    for drug1, drug2 in lasa_pairs.items():
        if drug1 in meds.lower() or drug2 in meds.lower():
            alerts.append(f"⚠ LASA Alert: {drug1.title()} ↔ {drug2.title()}")

    if alerts:
        return "\n".join(alerts)
    else:
        return "No LASA risk detected."
        def iv_compatibility(drug1, drug2):
    if (drug1.lower() == "ceftriaxone" and drug2.lower() == "calcium"):
        return "❌ Incompatible: Risk of precipitation."
    elif (drug1.lower() == "phenytoin" and drug2.lower() == "dextrose"):
        return "❌ Incompatible: Precipitation occurs."
    else:
        return "Compatibility data not in basic database."
        def pregnancy_risk(med):
    risk_categories = {
        "isotretinoin": "Category X – Contraindicated",
        "warfarin": "Category X – Teratogenic",
        "paracetamol": "Category B – Generally safe",
        "amoxicillin": "Category B – Safe in pregnancy"
    }

    return risk_categories.get(med.lower(), "Risk data not available.")
    def lab_alerts(potassium, inr, creatinine):
    alerts = []

    if potassium > 5.5:
        alerts.append("⚠ Hyperkalemia detected.")
    if inr > 3:
        alerts.append("⚠ High INR – Bleeding risk.")
    if creatinine > 2:
        alerts.append("⚠ Renal impairment alert.")

    if alerts:
        return "\n".join(alerts)
    else:
        return "No critical lab alerts."
        page = st.sidebar.radio("Navigation", [
    "Drug Database",
    "Renal Calculator",
    "Interaction Checker",
    "High-Risk Alerts",
    "IV Compatibility",
    "Pregnancy Risk",
    "Lab Alerts",
    "Antibiotic Stewardship",
    "Patient Profile"
])
        elif page == "High-Risk Alerts":
    st.title("⚠ High Risk Medication Monitor")
    meds = st.text_area("Enter medications")
    if st.button("Check High Risk"):
        st.write(high_risk_alert(meds))
        elif page == "IV Compatibility":
    st.title("💉 IV Compatibility Checker")
    drug1 = st.text_input("Drug 1")
    drug2 = st.text_input("Drug 2")
    if st.button("Check Compatibility"):
        st.write(iv_compatibility(drug1, drug2))
        elif page == "Pregnancy Risk":
    st.title("🤰 Pregnancy Risk Category")
    med = st.text_input("Enter Drug Name")
    if st.button("Check Risk"):
        st.write(pregnancy_risk(med))
        elif page == "Lab Alerts":
    st.title("🧪 Clinical Lab Red Flags")
    potassium = st.number_input("Serum Potassium")
    inr = st.number_input("INR")
    creatinine = st.number_input("Serum Creatinine")

    if st.button("Analyze Labs"):
        st.write(lab_alerts(potassium, inr, creatinine))
