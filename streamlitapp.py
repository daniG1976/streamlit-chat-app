import streamlit as st
import requests
import html
import re
import streamlit.components.v1 as components

# --- Seitenkonfiguration ---
st.set_page_config(page_title="KumpelBot 💬", page_icon="💬")

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
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Fehler bei der Verbindung zur API: {e}"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #015258;
}
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #FF9479 !important;
}

/* --- Chatlayout --- */
.chat-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    margin-bottom: 8px;
    width: 100%;
}
.chat-row.bot { justify-content: flex-end; }

/* --- Chatblasen --- */
.chat-bubble {
    position: relative;
    padding: 10px 14px;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    border-radius: 16px;
    animation: fadeInUp 0.35s ease-out;
}
.user-bubble {
    background-color: #f1f1f1;
    color: #222;
}
.bot-bubble {
    background-color: #b2f2bb;
    color: #1b4332;
}

/* --- Animierte Blasen --- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* --- Eingabeleiste unten --- */
.input-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: fixed;
    bottom: 65px; /* <<-- Abstand vergrößert (vorher 12px) */
    left: 12px;
    right: 12px;
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 8px 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    backdrop-filter: blur(10px);
}

/* --- Schreibfeld --- */
#chatInput {
    flex-grow: 1;
    background: transparent;
    border: none;
    color: #fff;
    font-size: 16px;
    outline: none;
    resize: none;
    padding: 6px;
}
#chatInput::placeholder {
    color: rgba(255,255,255,0.5);
}

/* --- Buttons --- */
#micBtn, #sendBtn {
    background: none;
    border: none;
    font-size: 22px;
    color: #ff9479;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-left: 6px;
}
#micBtn.listening {
    color: #ff4d4d;
    text-shadow: 0 0 12px #ff4d4d;
    transform: scale(1.2);
}
#sendBtn:hover {
    color: #b2f2bb;
    transform: scale(1.2);
}

/* --- Menü & Footer ausblenden --- */
#MainMenu, footer, div[data-testid="stToolbar"],
footer div, .stActionButton {
    visibility: hidden !important;
    height: 0 !important;
}

/* --- Mobile Optimierung --- */
@media (max-width: 600px) {
    .input-row {
        bottom: 80px; /* etwas mehr Platz auf iPhones */
    }
    .chat-bubble {
        max-width: 90%;
        font-size: 16px;
    }
    #chatInput {
        font-size: 18px;
    }
    #micBtn, #sendBtn {
        font-size: 26px;
    }
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
    """Bereinigt Modellantworten."""
    text = re.sub(r'\[/?BOUT\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return html.escape(text.strip())

# --- Nachrichten anzeigen ---
for sender, msg in st.session_state.messages:
    alignment = "user" if sender == "Du" else "bot"
    bubble_class = "user-bubble" if sender == "Du" else "bot-bubble"
    msg = clean_response(msg)
    st.markdown(
        f"""
        <div class='chat-row {alignment}'>
            <div class='chat-bubble {bubble_class}'>
                <b>{sender}:</b> {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Eingabeleiste mit Mic + Send ---
st.markdown("""
<div class="input-row">
    <textarea id="chatInput" placeholder="Hier schreiben oder sprechen..." rows="1"></textarea>
    <button id="micBtn">🎤</button>
    <button id="sendBtn">📨</button>
</div>
""", unsafe_allow_html=True)

# --- JavaScript ---
components.html("""
<script>
const micBtn = document.getElementById('micBtn');
const sendBtn = document.getElementById('sendBtn');
const chatInput = document.getElementById('chatInput');
let recognition;
let listening = false;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'de-DE';
    recognition.continuous = false;
    recognition.interimResults = false;

    micBtn.onclick = function() {
        if (!listening) {
            recognition.start();
            listening = true;
            micBtn.classList.add('listening');
        } else {
            recognition.stop();
            listening = false;
            micBtn.classList.remove('listening');
        }
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
    };

    recognition.onend = function() {
        listening = false;
        micBtn.classList.remove('listening');
    };
}

// --- Send Button Funktion ---
sendBtn.onclick = function() {
    const msg = chatInput.value.trim();
    if (msg.length > 0) {
        const streamlitEvent = new Event("sendMessage");
        window.dispatchEvent(streamlitEvent);
        window.parent.postMessage({isStreamlitMessage: true, type: "streamlit:setComponentValue", value: msg}, "*");
        chatInput.value = "";
    }
};
</script>
""", height=0)

# --- Eingabe vom JS abfangen ---
msg = st.experimental_get_query_params().get("value", [None])[0]
if msg:
    st.session_state.messages.append(("Du", msg))
    bot_reply = clean_response(get_openrouter_response(msg))
    st.session_state.messages.append(("Jaques Bubu", bot_reply))
    st.experimental_set_query_params(value=None)
    st.rerun()
