import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

st.set_page_config(page_title="TimBot", layout="centered")
st.title("🤖 TimBot")

def get_clean_key(raw_key):
    # Vyhodíme hlavičky a konce řádků
    clean = raw_key.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
    # Vyhodíme všechno kromě písmen, čísel a znaků + / = (základ Base64)
    clean = re.sub(r'[^A-Za-z0-9+/=]', '', clean)
    
    # OPRAVA DÉLKY (ta chyba 1625): Pokud chybí padding (=), doplníme ho
    while len(clean) % 4 != 0:
        clean += "="
        
    # Sestavíme PEM formát (64 znaků na řádek)
    lines = [clean[i:i+64] for i in range(0, len(clean), 64)]
    return "-----BEGIN PRIVATE KEY-----\n" + "\n".join(lines) + "\n-----END PRIVATE KEY-----\n"

try:
    # Načtení informací ze Streamlitu
    creds_info = dict(st.secrets["google_cloud"])
    creds_info["private_key"] = get_clean_key(creds_info["private_key"])
    
    # Inicializace
    creds = service_account.Credentials.from_service_account_info(creds_info)
    drive_service = build('drive', 'v3', credentials=creds)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    st.success("✅ TimBot je v pořádku připojen.")
    
    if prompt := st.chat_input("Zeptejte se na manuály:"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Jsi asistent Timpex. Odpověz: {prompt}")
        st.chat_message("assistant").write(response.text)

except Exception as e:
    st.error(f"Omlouvám se, stále je tu problém: {str(e)}")
    st.info("💡 Tip: Zkuste v Secrets v Streamlitu smazat klíč a vložit ho znovu, možná se tam opravdu vloudila mezera.")
