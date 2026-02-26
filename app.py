import streamlit as st

st.set_page_config(page_title="ClinPharm AI", page_icon="🩺")

st.title("🩺 ClinPharm AI - Clinical Assistant (Free Version)")
st.write("Ask basic drug-related questions.")

drug_database = {
    "paracetamol": "Paracetamol is used for fever and mild to moderate pain. Adult dose: 500-1000 mg every 6 hours. Max: 4g/day.",
    "ibuprofen": "Ibuprofen is an NSAID used for pain and inflammation. Adult dose: 200-400 mg every 6-8 hours.",
    "amoxicillin": "Amoxicillin is a penicillin antibiotic used for bacterial infections.",
    "metformin": "Metformin is used in Type 2 Diabetes. Starting dose: 500 mg once or twice daily with meals."
}

user_input = st.text_input("Enter drug name:")

if user_input:
    drug = user_input.lower()
    if drug in drug_database:
        st.success(drug_database[drug])
    else:
        st.warning("Drug not found in database.")
