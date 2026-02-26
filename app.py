import streamlit as st
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("drug_database.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    drug_class TEXT,
    indication TEXT,
    adult_dose TEXT,
    renal_adjustment TEXT,
    pregnancy TEXT,
    schedule TEXT,
    icu BOOLEAN
)
""")

conn.commit()

st.title("ClinPharm AI – Hospital Edition")

# Search section
search = st.text_input("Search Drug")

if search:
    query = f"""
    SELECT * FROM drugs
    WHERE LOWER(name) LIKE '%{search.lower()}%'
    """
    df = pd.read_sql_query(query, conn)

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("Drug not found.")cursor.execute("""
INSERT OR IGNORE INTO drugs
(name, drug_class, indication, adult_dose, renal_adjustment, pregnancy, schedule, icu)
VALUES
('Nitroglycerin', 'Nitrate', 'Angina', 
'0.3-0.6 mg SL', 
'No adjustment usually', 
'Caution', 
'H', 
1)
""")

conn.commit()
