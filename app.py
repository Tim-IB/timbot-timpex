import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

# Nastavení stránky
st.set_page_config(page_title="TimBot", layout="centered")
st.title("🤖 TimBot")

@st.cache_resource
def init_services():
    try:
        # 1. Načtení dat ze Streamlitu
        creds_info = dict(st.secrets["google_cloud"])
        pk = creds_info["private_key"]
        
        # 2. FILTR: Odstraníme tečky, mezery a všechno, co do klíče nepatří
        # Necháme jen písmena, čísla a znaky +, / a =
        clean_key = re.sub(r'[^A-Za-z0-9+/=]', '', pk)
        
        # 3. REKONSTRUKCE: Google vyžaduje zalomení po 64 znacích
        header = "-----BEGIN PRIVATE KEY-----\n"
        footer = "-----END PRIVATE KEY-----\n"
        formatted_key = header
        for i in range(0, len(clean_key), 64):
            formatted_key += clean_key[i:i+64] + "\n"
        formatted_key += footer
        
        creds_info["private_key"] = formatted_key

        # 4. Přihlášení
        creds = service_account.Credentials.from_service_account_info(creds_info)
        drive_service = build('drive', 'v3', credentials=creds)
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service
    except Exception as e:
        st.error(f"Chyba při startu: {str(e)}")
        return None

drive_service = init_services()

if drive_service:
    st.success("✅ TimBot je v pořádku připojen!")
    if prompt := st.chat_input("Zeptejte se na cokoliv:"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Jsi asistent Timpex. Odpověz na: {prompt}")
            st.markdown(response.text)
else:
    st.info("💡 Tip: Pokud vidíte chybu Byte(64, 46), máte v klíči v Secrets tečky. Zkuste ho tam vložit znovu a celý.")
