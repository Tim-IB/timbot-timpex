import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

st.set_page_config(page_title="TimBot Diagnostic", layout="centered")
st.title("🤖 TimBot: Diagnostika")

# Zpráva pro nás, že se script vůbec spustil
st.write("🔄 1. Startuji aplikaci...")

@st.cache_resource
def init_services():
    try:
        st.write("🔄 2. Kontroluji Secrets...")
        if "GOOGLE_JSON_BLOB" not in st.secrets:
            st.error("❌ Chyba: V Secrets chybí 'GOOGLE_JSON_BLOB'!")
            return None
        
        st.write("🔄 3. Rozbaluji JSON balíček...")
        service_info = json.loads(st.secrets["GOOGLE_JSON_BLOB"])
        
        st.write("🔄 4. Přihlašuji se ke Google Drive (tady to může trvat)...")
        creds = service_account.Credentials.from_service_account_info(service_info)
        drive_service = build('drive', 'v3', credentials=creds)
        
        st.write("🔄 5. Nastavuji Gemini...")
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service
    except Exception as e:
        st.error(f"❌ Kritická chyba při startu: {str(e)}")
        return None

# Spuštění
drive_service = init_services()

if drive_service:
    st.success("✅ Všechno proběhlo v pořádku! TimBot je připraven.")
    prompt = st.chat_input("Zeptejte se na cokoliv:")
    if prompt:
        st.write(f"Zpracovávám dotaz: {prompt}")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Jsi asistent Timpex. Odpověz: {prompt}")
        st.chat_message("assistant").write(response.text)
else:
    st.warning("⚠️ Aplikace se nepodařila plně inicializovat. Podívejte se na chyby výše.")
