import streamlit as st
import requests
import html
import re
import base64
import io
import streamlit.components.v1 as components

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Chat App 💬", page_icon="💬")

# --- API Setup ---
API_URL = "https://openrouter.ai/api/v1/chat/completions"
WHISPER_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
API_KEY = st.secrets["OPENROUTER_API_KEY"]

headers = {"Authorization": f"Bearer {API_KEY}"}

# --- Funktion: Chat-Antwort holen ---
def get_openrouter_response(user_input):
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Du bist ein lockerer, sympathischer Kumpel, der immer ausschließlich auf Deutsch antwortet."},
            {"role": "user", "content": f"Antworte bitte auf Deutsch: {user_input}"}
        ],
        "temperature": 0.8
    }
    try:
        r = requests.post(API_URL, headers={**headers, "Content-Type": "application/json"}, json=data)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Fehler: {e}"

# --- Funktion: Speech-to-Text mit Whisper ---
def transcribe_audio(audio_bytes):
    try:
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"model": "openai/whisper-large-v3"}
        r = requests.post(WHISPER_URL, headers=headers, data=data, files=files, timeout=60)
        r.raise_for_status()
        return r.json().get("text", "").strip()
    except Exception as e:
        return f"⚠️ Fehler bei der Spracherkennung: {e}"

# --- Styling ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #015258;
}
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #FF9479 !important;
}
.chat-row {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 8px;
    width: 100%;
}
.chat-row.bot { justify-content: flex-end; }
.chat-bubble {
    position: relative;
    padding: 10px 14px 14px 14px;
    max-width: 80%;
    border-radius: 16px;
    animation: fadeInUp 0.35s ease-out;
}
.user-bubble { background-color: #f1f1f1; color: #222; }
.bot-bubble { background-color: #b2f2bb; color: #1b4332; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 6px 10px;
}
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: white !important;
}
#MainMenu, footer, div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}
</style>
""", unsafe_allow_html=True)

# --- Titel ---
st.title("💬 KumpelBot mit Spracheingabe 🎤")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "recording" not in st.session_state:
    st.session_state.recording = None

# --- Nachrichten anzeigen ---
def clean_response(text: str) -> str:
    text = re.sub(r'\[/?BOUT\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.escape(text.strip())
    return text

for i, (sender, msg) in enumerate(st.session_state.messages):
    align = "user" if sender == "Du" else "bot"
    bubble_class = "user-bubble" if sender == "Du" else "bot-bubble"
    st.markdown(
        f"<div class='chat-row {align}'><div class='chat-bubble {bubble_class}'><b>{sender}:</b> {clean_response(msg)}</div></div>",
        unsafe_allow_html=True
    )

# --- Audioaufnahme (🎤 Button) ---
audio_data = st.audio_input("🎤 Sprachaufnahme (Tippen zum Sprechen)")

if audio_data:
    audio_bytes = audio_data.read()
    st.session_state.recording = audio_bytes
    st.info("🔊 Aufnahme wird transkribiert...")
    text_result = transcribe_audio(audio_bytes)
    if text_result and not text_result.startswith("⚠️"):
        st.session_state.messages.append(("Du (per Sprache)", text_result))
        reply = clean_response(get_openrouter_response(text_result))
        st.session_state.messages.append(("Jaques Bubu", reply))
        st.rerun()
    else:
        st.error(text_result)

# --- Texteingabe ---
if user_input := st.chat_input("Hier schreiben oder Sprachaufnahme nutzen 🎤"):
    st.session_state.messages.append(("Du", user_input))
    bot_reply = clean_response(get_openrouter_response(user_input))
    st.session_state.messages.append(("Jaques Bubu", bot_reply))
    st.rerun()

