import streamlit as st
import google.generativeai as genai

# --- KONFIGURATION ---
st.set_page_config(page_title="Revo - Renas Vokabeltrainer", page_icon="🎓")

# Titel der App
st.title("🎓 Revo - Vokabeltrainer")

# API Key sicher abrufen (wird später in Streamlit Cloud hinterlegt)
# Wir fangen den Fehler ab, falls der Key noch fehlt
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Warte auf API Key... (Siehe Anleitung Schritt 3)")
    st.stop()

# --- DAS GEHIRN VON REVO (HIER ANPASSEN) ---
# Das hier ist die Anweisung, wie sich die KI verhalten soll.
# Du kannst diesen Text durch deine Version aus AI Studio ersetzen!
SYSTEM_PROMPT = """
Du bist Revo, ein geduldiger und freundlicher Vokabeltrainer für eine Schülerin namens Rena.
Deine Aufgabe ist es, Rena Vokabeln abzufragen oder ihr beim Lernen zu helfen.
Verhalte dich motivierend. Wenn sie etwas falsch macht, korrigiere sie sanft und erkläre es kurz.
Frage immer, welche Sprache sie heute üben möchte, wenn es noch nicht klar ist.
"""

# Modell Konfiguration
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Schnelles, günstiges Modell
    system_instruction=SYSTEM_PROMPT
)

# --- CHAT GESCHICHTE (MEMORY) ---
# Damit Revo sich daran erinnert, was gerade gesagt wurde
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat-Verlauf anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- EINGABE ---
if prompt := st.chat_input("Schreibe hier deine Antwort..."):
    # 1. Benutzer-Nachricht anzeigen
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. KI Antwort generieren
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Wir bauen den Verlauf für die KI zusammen
        chat_history = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages
        ]
        
        try:
            # Da Gemini kein echtes "Chat-Objekt" hier braucht, senden wir die History so:
            # Wir nutzen start_chat nicht, da wir den State manuell verwalten (einfacher für Streamlit)
            # Workaround: Wir senden die History an das Modell.
            # Einfacherer Weg für Streamlit Statelessness:
            chat = model.start_chat(history=chat_history[:-1]) # Historie ohne die letzte Nachricht
            response = chat.send_message(prompt) # Letzte Nachricht senden
            
            response_text = response.text
            message_placeholder.markdown(response_text)
            
            # 3. KI Antwort speichern
            st.session_state.messages.append({"role": "model", "content": response_text})
            
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")
