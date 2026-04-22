import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# --- KONFIGURACE ---
st.set_page_config(page_title="TimBot - Manuály Timpex", layout="centered")
st.title("🤖 TimBot")
st.subheader("Zeptejte se na cokoliv ohledně manuálů Timpex")

@st.cache_resource
def init_services():
    try:
        # Načtení a automatická oprava formátu soukromého klíče
        creds_info = dict(st.secrets["google_cloud"])
        pk = creds_info["private_key"].replace("\\n", "\n")
        
        # Ošetření PEM formátu (64 znaků na řádek)
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        if header in pk:
            content = pk.replace(header, "").replace(footer, "").replace("\n", "").replace(" ", "").strip()
            lines = [content[i:i+64] for i in range(0, len(content), 64)]
            pk = header + "\n" + "\n".join(lines) + "\n" + footer + "\n"
        
        creds_info["private_key"] = pk

        # Inicializace Google Drive a Gemini
        creds = service_account.Credentials.from_service_account_info(creds_info)
        drive_service = build('drive', 'v3', credentials=creds)
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service
    except Exception as e:
        st.error(f"Chyba při inicializaci: {str(e)}")
        return None

drive_service = init_services()

# --- LOGIKA CHATU ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Jak vám mohu pomoci?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if drive_service:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                # Zde je prostor pro budoucí logiku vyhledávání v Drive
                response = model.generate_content(f"Jsi asistent pro manuály Timpex. Odpověz na: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Chyba Gemini: {str(e)}")
        else:
            st.warning("Služby nejsou správně nastaveny. Zkontrolujte Secrets.")
