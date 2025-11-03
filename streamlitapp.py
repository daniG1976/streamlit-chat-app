import streamlit as st
import requests
import html
import re
from streamlit_javascript import st_javascript

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Chat App 💬", page_icon="💬")

# --- OpenRouter API Setup ---
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["OPENROUTER_API_KEY"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_openrouter_response(user_input):
    """Fragt Mistral über OpenRouter ab."""
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Du bist ein lockerer, sympathischer Kumpel, der immer ausschließlich auf Deutsch antwortet."},
            {"role": "user", "content": f"Antworte bitte auf Deutsch: {user_input}"}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Fehler bei der Verbindung zur API: {e}"

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

/* Chatlayout */
.chat-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    margin-bottom: 8px;
    width: 100%;
}
.chat-row.bot { justify-content: flex-end; }

/* Chatblasen */
.chat-bubble {
    position: relative;
    padding: 10px 14px 14px 14px;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    border-radius: 16px;
    animation: fadeInUp 0.35s ease-out;
}
.user-bubble { background-color: #f1f1f1; color: #222; }
.bot-bubble { background-color: #b2f2bb; color: #1b4332; }

/* Animation */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Mikrofonbutton */
.mic-btn {
    background: none;
    border: none;
    font-size: 26px;
    cursor: pointer;
    color: #ffffffcc;
    transition: all 0.3s ease;
}
.mic-btn.listening {
    color: #ff4d4d;
    text-shadow: 0 0 8px #ff4d4d;
    transform: scale(1.2);
}

/* Chat Input Styling */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.08) !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 12px !important;
    padding: 6px 10px !important;
}

/* Menü ausblenden */
#MainMenu, footer, div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}
</style>
""", unsafe_allow_html=True)

# --- Titel ---
st.title("💬 KumpelBot")
st.write("Lass uns einfach quatschen 👋")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def clean_response(text: str) -> str:
    text = re.sub(r'\[/?BOUT\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.escape(text.strip())
    return text

# --- Nachrichten anzeigen ---
for i, (sender, msg) in enumerate(st.session_state.messages):
    alignment = "user" if sender == "Du" else "bot"
    bubble_class = "user-bubble" if sender == "Du" else "bot-bubble"
    msg = clean_response(msg)
    st.markdown(
        f"<div class='chat-row {alignment}'><div class='chat-bubble {bubble_class}'><b>{sender}:</b> {msg}</div></div>",
        unsafe_allow_html=True
    )

# --- Sprachsteuerung via Browser SpeechRecognition ---
speech_text = st_javascript("""
async function recordSpeech() {
    const btn = document.getElementById('micButton');
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'de-DE';
    recognition.interimResults = false;
    return new Promise((resolve, reject) => {
        recognition.onresult = event => resolve(event.results[0][0].transcript);
        recognition.onerror = event => reject(event.error);
        btn.classList.add('listening');
        recognition.start();
        btn.onmouseup = btn.ontouchend = () => {
            recognition.stop();
            btn.classList.remove('listening');
        };
    });
}
""")

# --- Layout: Mikro + Input nebeneinander ---
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.markdown("<button id='micButton' class='mic-btn'>🎤</button>", unsafe_allow_html=True)

with col2:
    if user_input := st.chat_input("Hier schreiben oder Mikro halten..."):
        st.session_state.messages.append(("Du", user_input))
        bot_reply = clean_response(get_openrouter_response(user_input))
        st.session_state.messages.append(("Jaques Bubu", bot_reply))
        st.rerun()
