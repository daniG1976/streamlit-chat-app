import streamlit as st
import requests
import html
import re
from streamlit_javascript import st_javascript

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
    """Abfrage an OpenRouter"""
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Du bist Jaques Bubu, ein entspannter, sympathischer Kumpel. Antworte locker und nur auf Deutsch."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ API-Fehler: {e}"

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

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Eingabeleiste unten */
.input-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: fixed;
    bottom: 65px;
    left: 12px;
    right: 12px;
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 8px 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    backdrop-filter: blur(10px);
}

/* Eingabefeld */
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

/* Buttons */
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

/* Menü & Footer ausblenden */
#MainMenu, footer, div[data-testid="stToolbar"],
footer div, .stActionButton {
    visibility: hidden !important;
    height: 0 !important;
}

/* Mobile */
@media (max-width: 600px) {
    .input-row {
        bottom: 80px;
    }
    .chat-bubble {
        max-width: 90%;
        font-size: 16px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Titel ---
st.title("💬 KumpelBot")
st.write("Lass uns quatschen 👋")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def clean_response(text: str) -> str:
    text = re.sub(r'\[/?BOUT\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.escape(text.strip())
    return text

# --- Nachrichten anzeigen ---
for sender, msg in st.session_state.messages:
    alignment = "user" if sender == "Du" else "bot"
    bubble_class = "user-bubble" if sender == "Du" else "bot-bubble"
    msg = clean_response(msg)
    st.markdown(
        f"<div class='chat-row {alignment}'><div class='chat-bubble {bubble_class}'><b>{sender}:</b> {msg}</div></div>",
        unsafe_allow_html=True
    )

# --- Eingabezeile mit Mikro & Senden ---
components_html = """
<div class="input-row">
    <input id="chatInput" type="text" placeholder="Hier sprechen oder schreiben..." />
    <button id="micBtn">🎤</button>
    <button id="sendBtn">📨</button>
</div>

<script>
let recognizing = false;
let recognition;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'de-DE';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event) => {
        const result = event.results[0][0].transcript;
        document.getElementById("chatInput").value = result;
    };

    recognition.onend = () => {
        recognizing = false;
        document.getElementById("micBtn").classList.remove("listening");
    };
}

document.getElementById("micBtn").addEventListener("click", () => {
    if (recognizing) {
        recognition.stop();
        recognizing = false;
        document.getElementById("micBtn").classList.remove("listening");
    } else {
        recognition.start();
        recognizing = true;
        document.getElementById("micBtn").classList.add("listening");
    }
});

document.getElementById("sendBtn").addEventListener("click", () => {
    const input = document.getElementById("chatInput").value;
    if (input.trim() !== "") {
        window.parent.postMessage({ type: "SEND_MESSAGE", text: input }, "*");
        document.getElementById("chatInput").value = "";
    }
});
</script>
"""
st.components.v1.html(components_html, height=100)

# --- Nachricht von JS empfangen ---
message = st_javascript("""
    await new Promise(resolve => {
        window.addEventListener("message", (event) => {
            if (event.data.type === "SEND_MESSAGE") {
                resolve(event.data.text);
            }
        });
    });
""")

if message:
    st.session_state.messages.append(("Du", message))
    reply = clean_response(get_openrouter_response(message))
    st.session_state.messages.append(("Jaques Bubu", reply))
    st.rerun()
