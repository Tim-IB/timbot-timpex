import streamlit as st
import google.generativeai as genai

# Vzhled aplikace
st.set_page_config(page_title="TimBot Servis", page_icon="🔧")
st.title("🔧 TimBot: Seniorní Asistent Timpex")

# Načtení API klíče ze schovaných nastavení (Secrets)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Instrukce
SYSTEM_PROMPT = "Jsi Seniorní servisní asistent Timpex. Odpovídej stručně v odrážkách z manuálů. Číselné hodnoty piš TUČNĚ. První bod: Odpojit 230V."

query = st.text_input("Zadejte dotaz:")

if st.button("Odeslat"):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"{SYSTEM_PROMPT}\n\nDotaz: {query}")
    st.markdown(response.text)
