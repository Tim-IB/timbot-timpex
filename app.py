import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

st.set_page_config(page_title="TimBot", layout="centered")
st.title("🤖 TimBot")

@st.cache_resource
def init_services():
    try:
        # Načteme celý JSON balíček ze Secrets
        service_info = json.loads(st.secrets["GOOGLE_JSON_BLOB"])
        
        # Přihlášení pomocí balíčku
        creds = service_account.Credentials.from_service_account_info(service_info)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Nastavení Gemini
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return drive_service
    except Exception as e:
        st.error(f"Kritická chyba: {str(e)}")
        return None

drive_service = init_services()

if drive_service:
    st.success("✅ TimBot je připojen a připraven!")
    if prompt := st.chat_input("Zeptejte se na cokoliv:"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Jsi asistent Timpex. Odpověz na: {prompt}")
        st.chat_message("assistant").write(response.text)
else:
    st.error("❌ Nepodařilo se připojit. Zkontrolujte Secrets.")
