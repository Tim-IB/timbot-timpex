import streamlit as st
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

st.set_page_config(page_title="TimBot 2026", layout="centered")
st.title("🤖 TimBot")

@st.cache_resource
def init_services():
    try:
        # 1. Google Drive (zůstává stejné)
        service_info = json.loads(st.secrets["GOOGLE_JSON_BLOB"])
        creds = service_account.Credentials.from_service_account_info(service_info)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # 2. Gemini (NOVÝ ZPŮSOB pro rok 2026)
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service, client
    except Exception as e:
        st.error(f"Chyba při startu: {str(e)}")
        return None, None

drive_service, gemini_client = init_services()

if gemini_client:
    st.success("✅ TimBot je online (v1.5 Flash 2026)")
    
    if prompt := st.chat_input("Zeptejte se na Timpex:"):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # Volání moderního modelu gemini-1.5-flash (nebo gemini-2.0-flash)
                response = gemini_client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt
                )
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Chyba komunikace s AI: {str(e)}")
else:
    st.error("Nepodařilo se připojit. Zkontrolujte logy.")
