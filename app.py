import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# --- 1. ZÁKLADNÍ NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="TimBot - Expertní rádce Timpex", layout="centered")

# Skrytí menu Streamlitu pro profesionálnější vzhled
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🤖 TimBot")
st.caption("Verze 1.0 | Připojen k manuálům Timpex")

# --- 2. INICIALIZACE SLUŽEB (Google Drive & Gemini) ---
@st.cache_resource
def init_all_services():
    try:
        # Načtení JSON balíčku ze Streamlit Secrets
        service_info = json.loads(st.secrets["GOOGLE_JSON_BLOB"])
        
        # Přihlášení ke Google Drive
        creds = service_account.Credentials.from_service_account_info(service_info)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Konfigurace Gemini AI
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service
    except Exception as e:
        st.error(f"Nepodařilo se nastartovat služby: {str(e)}")
        return None

drive_service = init_all_services()

# --- 3. LOGIKA CHATU ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Dobrý den! Jsem TimBot. Jak vám mohu pomoci s manuály nebo technickými dotazy Timpex?"}
    ]

# Zobrazení historie chatu
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Vstup od uživatele
if prompt := st.chat_input("Zadejte svůj dotaz..."):
    # Přidání dotazu uživatele do historie
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generování odpovědi od Gemini
    with st.chat_message("assistant"):
        if drive_service:
            try:
                # Použití modelu Gemini 1.5 Flash
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # Zatím odpovídáme přímo (v dalším kroku propojíme čtení PDF z Drive)
                full_prompt = f"Jsi technický asistent pro produkty firmy Timpex. Odpovídej věcně a srozumitelně. Dotaz: {prompt}"
                
                response = model.generate_content(full_prompt)
                answer = response.text
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"Chyba při generování odpovědi: {str(e)}"
                st.error(error_msg)
        else:
            st.warning("Systém není správně připojen ke Google službám.")
