import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from pypdf import PdfReader

# 1. KONFIGURACE STRÁNKY A VZHLED
st.set_page_config(page_title="TimBot Servis", page_icon="🔧")
st.markdown("<h1 style='text-align: center; color: #0054a6;'>🔧 TimBot: Seniorní Asistent Timpex</h1>", unsafe_allow_html=True)

# 2. BEZPEČNÉ NAČTENÍ KLÍČŮ (OPRAVENO PRO PEM CHYBU)
try:
    # Načtení informací ze Streamlit Secrets
    creds_info = dict(st.secrets["google_cloud"])
    
    # OPRAVA: Převedení textových značek \n na skutečné konce řádků
    if "private_key" in creds_info:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        
    # Inicializace Google Drive a Gemini
    creds = service_account.Credentials.from_service_account_info(creds_info)
    drive_service = build('drive', 'v3', credentials=creds)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
except Exception as e:
    st.error(f"⚠️ Chyba v konfiguraci klíčů: {e}")
    st.stop()

# 3. FUNKCE PRO ZÍSKÁNÍ DAT Z DISKU
def get_manuals_context():
    # ID VAŠÍ SLOŽKY 01_ZDROJOVA_DATA (zkopírujte z adresy v prohlížeči)
    FOLDER_ID = "1t8NQCKe97xP2Xq0KCQZft_J3Wvjgkv-1" # <--- SEM VLOŽTE SVÉ ID (toto je příklad)
    
    try:
        results = drive_service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            return "V zadané složce na Disku nebyly nalezeny žádné PDF manuály."

        full_text = ""
        for file in files:
            request = drive_service.files().get_media(fileId=file['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            reader = PdfReader(fh)
            full_text += f"\n--- MANUÁL: {file['name']} ---\n"
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
        return full_text
    except Exception as e:
        return f"Chyba při čtení Google Disku: {e}"

# 4. INSTRUKCE PRO MOZEK AI (SYSTEM PROMPT)
SYSTEM_PROMPT = """Jsi Seniorní servisní asistent Timpex. Odpovídej VÝHRADNĚ z manuálů.
PRAVIDLA PRO ODPOVĚĎ:
1. První bod u oprav: "Odpojit od sítě 230V!".
2. Piš stručně v odrážkách.
3. Všechny číselné hodnoty (napětí, odpor, tlak) piš TUČNĚ.
4. Pokud nevíš model (ECO, REG, TimNet), zeptej se na něj.
5. Uveď vždy Zdroj: [Název souboru], strana [X]."""

# 5. UŽIVATELSKÉ ROZHRANÍ (UI)
query = st.text_input("Zadejte kód chyby nebo dotaz (např. chyba E01 u ECO100):")

if st.button("Odeslat dotaz"):
    if query:
        with st.spinner("Prohledávám technickou dokumentaci Timpex..."):
            context = get_manuals_context()
            model = genai.GenerativeModel('gemini-3-flash')
            full_prompt = f"{SYSTEM_PROMPT}\n\nKONTEXT Z MANUÁLŮ:\n{context}\n\nDOTAZ: {query}"
            
            response = model.generate_content(full_prompt)
            
            st.markdown("### Odpověď asistenta:")
            st.info(response.text)
    else:
        st.warning("Prosím, zadejte dotaz.")
