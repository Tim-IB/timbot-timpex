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
        # 1. Načtení dat ze Streamlit Secrets
        creds_info = dict(st.secrets["google_cloud"])
        raw_key = creds_info["private_key"]
        
        # 2. OČIŠTĚNÍ KLÍČE (odstraníme všechno smetí, co způsobuje chybu 1625)
        # Vyndáme čistý kód mezi hlavičkou a patičkou
        clean_key = raw_key.replace("-----BEGIN PRIVATE KEY-----", "")
        clean_key = clean_key.replace("-----END PRIVATE KEY-----", "")
        # Odstraníme konce řádků, mezery a uvozovky, které tam Streamlit mohl nechat
        clean_key = re.sub(r'\s+', '', clean_key).strip()
        
        # 3. REKONSTRUKCE (Google vyžaduje zalomení po 64 znacích)
        formatted_key = "-----BEGIN PRIVATE KEY-----\n"
        for i in range(0, len(clean_key), 64):
            formatted_key += clean_key[i:i+64] + "\n"
        formatted_key += "-----END PRIVATE KEY-----\n"
        
        creds_info["private_key"] = formatted_key

        # 4. Přihlášení ke službám
        creds = service_account.Credentials.from_service_account_info(creds_info)
        drive_service = build('drive', 'v3', credentials=creds)
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service
    except Exception as e:
        st.error(f"Chyba při startu: {str(e)}")
        return None

# Spuštění botu
drive_service = init_services()

if drive_service:
    st.success("✅ TimBot je online a připraven.")
    if prompt := st.chat_input("Zeptejte se na manuály Timpex:"):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Jsi asistent Timpex. Odpověz na: {prompt}")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Chyba Gemini: {e}")
else:
    st.warning("Aplikace čeká na správné nastavení Secrets.")
