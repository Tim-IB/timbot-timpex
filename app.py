import streamlit as st
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

st.set_page_config(page_title="TimBot 2026", layout="centered")
st.title("🤖 TimBot")

@st.cache_resource
def init_services():
    try:
        # 1. Google Drive inicializace
        service_info = json.loads(st.secrets["GOOGLE_JSON_BLOB"])
        creds = service_account.Credentials.from_service_account_info(service_info)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # 2. Gemini inicializace (Moderní klient pro rok 2026)
        # Používáme Client bez dalších parametrů, aby si sám našel nejlepší cestu
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        return drive_service, client
    except Exception as e:
        st.error(f"Kritická chyba startu: {str(e)}")
        return None, None

drive_service, gemini_client = init_services()

if gemini_client:
    # Diagnostická zpráva zmizí po prvním dotazu
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.success("✅ TimBot je připojen přes moderní API.")

    # Zobrazení historie
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Zeptejte se na cokoliv:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # V roce 2026 používáme čistý název modelu
                # Pokud nepůjde 1.5-flash, zkusíme 2.0-flash (který už je v 2026 standardem)
                response = gemini_client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt
                )
                
                answer = response.text
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                # Pokud model 1.5 nebyl nalezen, zkusíme novější 2.0
                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-2.0-flash', 
                        contents=prompt
                    )
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except:
                    st.error(f"AI momentálně neodpovídá: {str(e)}")
else:
    st.error("Nepodařilo se inicializovat AI klienta. Zkontrolujte API klíč v Secrets.")
