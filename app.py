import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- KONFIGURACE ---
st.set_page_config(page_title="TimBot", layout="centered")
st.title("🤖 TimBot")

@st.cache_resource
def init_services():
    try:
        creds_info = dict(st.secrets["google_cloud"])
        pk = creds_info["private_key"]
        
        # SUPER-PRAČKA: Vyčistíme klíč od všeho (hlavičky, patičky, lomítka, mezery)
        clean = pk.replace("-----BEGIN PRIVATE KEY-----", "")
        clean = clean.replace("-----END PRIVATE KEY-----", "")
        clean = clean.replace("\\n", "").replace("\n", "").replace(" ", "").strip()
        
        # ZNOVU POSTAVÍME PEM: Google chce 64 znaků na řádek
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        lines = [clean[i:i+64] for i in range(0, len(clean), 64)]
        creds_info["private_key"] = header + "\n" + "\n".join(lines) + "\n" + footer + "\n"

        # Inicializace
        creds = service_account.Credentials.from_service_account_info(creds_info)
        drive_service = build('drive', 'v3', credentials=creds)
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return drive_service
    except Exception as e:
        st.error(f"Kritická chyba: {str(e)}")
        return None

drive_service = init_services()

if drive_service:
    st.success("✅ TimBot je připraven a připojen k manuálům!")
    if prompt := st.chat_input("Zeptejte se na cokoliv:"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Jsi asistent Timpex. Odpověz na: {prompt}")
        st.chat_message("assistant").write(response.text)
else:
    st.error("❌ Nepodařilo se připojit. Zkontrolujte prosím Secrets ve Streamlitu.")
