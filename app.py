import streamlit as st
import sqlite3
import pandas as pd

# ==============================
# PAGE CONFIG (MUST BE FIRST)
# ==============================
st.set_page_config(page_title="ClinPharm AI", layout="wide")

# ==============================
# DATABASE CONNECTION
# ==============================
conn = sqlite3.connect("drug_database.db", check_same_thread=False)
cursor = conn.cursor()

# ==============================
# CREATE TABLE
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    drug_class TEXT,
    indication TEXT,
    adult_dose TEXT,
    renal_adjustment TEXT,
    pregnancy TEXT,
    schedule TEXT,
    icu BOOLEAN
)
""")

# ==============================
# INSERT DATA ONLY IF EMPTY
# ==============================
cursor.execute("SELECT COUNT(*) FROM drugs")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany("""
    INSERT INTO drugs
    (name, drug_class, indication, adult_dose, renal_adjustment, pregnancy, schedule, icu)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [

    ("Nitroglycerin", "Nitrate", "Angina",
     "0.3–0.6 mg SL", "No adjustment", "Caution", "H", 1),

    ("Adrenaline", "Vasopressor", "Anaphylaxis, Cardiac arrest",
     "0.5 mg IM", "No adjustment", "Safe in emergency", "H", 1),

    ("Meropenem", "Carbapenem", "Severe infections",
     "1 g IV q8h", "Reduce in renal impairment", "Caution", "H1", 1),

    ("Metformin", "Biguanide", "Type 2 Diabetes",
     "500 mg BD", "Avoid if eGFR <30", "Safe", "H", 0),

    ("Warfarin", "Anticoagulant", "DVT, Atrial fibrillation",
     "5 mg daily (adjust by INR)", "No change", "Avoid", "H", 0),

    ("Ceftriaxone", "Cephalosporin", "Bacterial infections",
     "1–2 g IV daily", "No major adjustment", "Safe", "H", 1)

    ])

    conn.commit()

# ==============================
# APP TITLE
# ==============================
st.title("🏥 ClinPharm AI – Hospital Edition")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filter Options")

classes = pd.read_sql_query("SELECT DISTINCT drug_class FROM drugs", conn)
class_list = classes["drug_class"].dropna().tolist()

selected_class = st.sidebar.selectbox("Select Drug Class", ["All"] + class_list)

selected_schedule = st.sidebar.selectbox(
    "Select Schedule",
    ["All", "H", "H1", "X"]
)

icu_filter = st.sidebar.selectbox(
    "ICU Drugs Only?",
    ["All", "Yes", "No"]
)

# ==============================
# SEARCH INPUT
# ==============================
search = st.text_input("🔍 Search Drug by Name")

# ==============================
# BUILD QUERY
# ==============================
query = "SELECT * FROM drugs WHERE 1=1"
params = []

if search:
    query += " AND LOWER(name) LIKE ?"
    params.append(f"%{search.lower()}%")

if selected_class != "All":
    query += " AND drug_class = ?"
    params.append(selected_class)

if selected_schedule != "All":
    query += " AND schedule = ?"
    params.append(selected_schedule)

if icu_filter == "Yes":
    query += " AND icu = 1"
elif icu_filter == "No":
    query += " AND icu = 0"

# ==============================
# EXECUTE QUERY
# ==============================
df = pd.read_sql_query(query, conn, params=params)

# ==============================
# DISPLAY RESULTS
# ==============================
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No drugs found based on selected filters.")
    final stable hospital version 
