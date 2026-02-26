import streamlit as st

st.set_page_config(page_title="Clinical Pharma AI", layout="wide")

# -------------------- LOGIN SYSTEM --------------------

users = {
    "intern": {"password": "1234", "role": "Intern"},
    "pharmacist": {"password": "admin123", "role": "Clinical Pharmacist"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏥 Hospital Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and password == users[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.role = users[username]["role"]
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

else:

    # -------------------- SIDEBAR --------------------
    st.sidebar.title("🏥 Clinical Dashboard")
    st.sidebar.write(f"Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigation", [
        "High-Risk Alerts",
        "LASA Alerts",
        "IV Compatibility",
        "Pregnancy Risk",
        "Lab Alerts"
    ])

    # -------------------- FUNCTIONS --------------------

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
        if drug1.lower() == "ceftriaxone" and drug2.lower() == "calcium":
            return "❌ Incompatible: Risk of precipitation."
        elif drug1.lower() == "phenytoin" and drug2.lower() == "dextrose":
            return "❌ Incompatible: Precipitation occurs."
        else:
            return "Compatibility data not available."


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

    # -------------------- PAGES --------------------

    if page == "High-Risk Alerts":
        st.title("⚠ High Risk Medication Monitor")
        meds = st.text_area("Enter medications (comma separated)")
        if st.button("Check High Risk"):
            st.write(high_risk_alert(meds))

    elif page == "LASA Alerts":
        st.title("👀 LASA Drug Alert System")
        meds = st.text_area("Enter medications")
        if st.button("Check LASA Risk"):
            st.write(lasa_alert(meds))

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
        potassium = st.number_input("Serum Potassium", min_value=0.0)
        inr = st.number_input("INR", min_value=0.0)
        creatinine = st.number_input("Serum Creatinine", min_value=0.0)

        if st.button("Analyze Labs"):
            st.write(lab_alerts(potassium, inr, creatinine))
