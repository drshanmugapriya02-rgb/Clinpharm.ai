import streamlit as st
from openai import OpenAI

st.title("🩺 ClinPharm AI - Clinical Assistant")
st.write("Ask any clinical or drug-related question")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

user_input = st.text_area("Enter your question")

if st.button("Ask AI"):
    if user_input:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a clinical pharmacy AI assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        st.write(response.choices[0].message.content)
