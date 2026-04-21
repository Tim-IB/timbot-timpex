import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from pypdf import PdfReader

# 1. ZÁKLADNÍ NASTAVENÍ A VZHLED TIMPEX
st.set_page_config(page_title="TimBot Servis", page_icon="🔧")
st.markdown("<h1 style='text-align: center; color: #0054a6;'>🔧 TimBot: Seniorní Asistent Timpex</h1>", unsafe_allow_html=True)

# 2. PŘIPOJENÍ KE GOOGLE SLUŽBÁM (Používá Secrets ze Streamlitu)
try:
    # Načtení klíčů
    creds_info = st.secrets["google_cloud"]
    creds = service_account.Credentials.from_service_account_info(creds_info)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Konfigurace Gemini
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Chyba v nastavení klíčů: {e}")
    st.stop()

# 3. FUNKCE PRO PROHLEDÁVÁNÍ SLOŽKY NA DISKU
def get_manuals_context():
    # Zde vložte ID vaší složky 01_ZDROJOVA_DATA (z URL adresy na Disku)
    FOLDER_ID = "1t8NQCKe97xP2Xq0KCQZft_J3Wvjgkv-1" 
    
    try:
        results = drive_service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            return "V zadané složce nebyly nalezeny žádné PDF manuály."

        full_text = ""
        for file in files:
            request = drive_service.files().get_media(fileId=file['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Čtení obsahu PDF
            reader = PdfReader(fh)
            file_content = f"\n--- MANUÁL: {file['name']} ---\n"
            for page in reader.pages:
                file_content += page.extract_text() + "\n"
            full_text += file_content
            
        return full_text
    except Exception as e:
        return f"Chyba při čtení Disku: {e}"

# 4. CHAT A LOGIKA ODPOVĚDÍ
SYSTEM_PROMPT = """Jsi Seniorní servisní asistent Timpex. Tvým úkolem je pomáhat technikům v terénu.
ZÁSADNÍ PRAVIDLA:
1. Odpovídej VÝHRADNĚ na základě poskytnutých manuálů v KONTEXTU.
2. Piš telegraficky, stručně a v odrážkách.
3. Všechny číselné hodnoty (napětí, odpor, tlak, teploty) piš vždy TUČNĚ.
4. Pokud se dotaz týká opravy, první bod musí být VŽDY: "Odpojit od sítě 230V!".
5. Pokud uživatel neuvede model regulace (ECO, REG, TimNet), nejdříve se na něj zeptej.
6. U každé rady uveď na konci: Zdroj: [Název souboru], strana [X].
7. Pokud informaci v manuálu nenajdeš, napiš: 'Lituji, v dostupných manuálech jsem tuto informaci nenalezl.'"""

query = st.text_input("Zadejte kód chyby nebo dotaz (např. chyba E01 u ECO100):")

if st.button("Odeslat dotaz"):
    if query:
        with st.spinner("Prohledávám technickou dokumentaci Timpex..."):
            # 1. Získání textu z PDF na Disku
            context = get_manuals_context()
            
            # 2. Sestavení dotazu pro Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            full_prompt = f"{SYSTEM_PROMPT}\n\nKONTEXT Z MANUÁLŮ:\n{context}\n\nDOTAZ TECHNIKA: {query}"
            
            # 3. Generování odpovědi
            response = model.generate_content(full_prompt)
            
            st.markdown("### Odpověď asistenta:")
            st.info(response.text)
    else:
        st.warning("Prosím, zadejte dotaz.")
