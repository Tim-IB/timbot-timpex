import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

st.set_page_config(page_title="TimBot", layout="centered")
st.title("🤖 TimBot")

@st.cache_resource
def init_services():
    try:
        # 1. Načtení dat
        creds_info = dict(st.secrets["google_cloud"])
        pk = creds_info["private_key"]
        
        # 2. CHIRURGICKÁ OPRAVA (To "hluboké zamyšlení" v praxi)
        # Nejdřív získáme jen čistá data (písmena a čísla)
        clean = re.sub(r'[^A-Za-z0-9+/=]', '', pk)
        
        # Base64 MUSÍ být dělitelné 4. Pokud máte 1625 znaků, ten poslední (1625.) je smetí.
        # Tento řádek klíč ořízne na nejbližší správnou délku (např. 1624)
        clean = clean[:(len(clean) // 4) * 4]
        
        # 3. REKONSTRUKCE PEM FORMÁTU
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        lines = [clean[i:i+64] for i in range(0, len(clean), 64)]
        creds_info["private_key"] = header + "\n" + "\n".join(lines) + "\n" + footer + "\n"

        # 4. Spuštění služeb
        creds = service_account.Credentials.from_service_account_info(creds_info)
        drive_service = build('drive', 'v3', credentials=creds)
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return drive_service
    except Exception as e:
        st.error(f"Kritická chyba: {str(e)}")
        return None

drive_service = init_services()

if drive_service:
    st.success("✅ TimBot je konečně připraven!")
    if prompt := st.chat_input("Zeptejte se na cokoliv:"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Jsi asistent Timpex. Odpověz na: {prompt}")
        st.chat_message("assistant").write(response.text)
else:
    st.error("❌ Připojení selhalo. Zkontrolujte prosím Secrets.")
