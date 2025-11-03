import streamlit as st
import requests
import html
import re
import streamlit.components.v1 as components

# --- Seitenkonfiguration ---
st.set_page_config(page_title="💬 KumpelBot", page_icon="💬")

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

/* --- Chatlayout --- */
.chat-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    margin-bottom: 8px;
    width: 100%;
}
.chat-row.bot { justify-content: flex-end; }

/* --- Chatblasen + Animation --- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.chat-bubble {
    position: relative;
    padding: 10px 14px 14px 14px;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    border-radius: 16px;
    animation: fadeInUp 0.35s ease-out;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.chat-bubble:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}
.user-bubble { background-color: #f1f1f1; color: #222; }
.bot-bubble { background-color: #b2f2bb; color: #1b4332; }

/* --- Delete Button --- */
.delete-btn {
    position: absolute;
    top: -6px;
    right: -6px;
    background: none;
    border: none;
    color: #ff6b6b;
    font-size: 16px;
    cursor: pointer;
    padding: 0;
    line-height: 1;
    z-index: 10;
}
.delete-btn:hover { transform: scale(1.2); }

/* --- Chat Input --- */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.08) !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 12px !important;
    padding: 6px 10px !important;
}
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    color: #ffffff !important;
    font-size: 16px !important;
}
div[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.5);
}

/* --- Menü ausblenden --- */
#MainMenu, footer, div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}

/* --- Mobile Anpassung --- */
@media (max-width: 600px) {
    .chat-bubble { max-width: 90%; font-size: 16px; }
    .delete-btn { font-size: 12px; top: 2px; right: 4px; }
}

/* --- Mic Button Animation --- */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0.6); }
    70% { box-shadow: 0 0 0 10px rgba(255, 80, 80, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0); }
}
.mic-active {
    color: red !important;
    animation: pulseGlow 1.5s infinite;
    transform: scale(1.2);
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
    text = html.escape(text.strip())
    return text

# --- Nachrichten anzeigen ---
for i, (sender, msg) in enumerate(st.session_state.messages):
    alignment = "user" if sender == "Du" else "bot"
    bubble_class = "user-bubble" if sender == "Du" else "bot-bubble"
    msg = clean_response(msg)

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
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
    with col2:
        if st.button("❌", key=f"delete_{i}", help="Nachricht löschen"):
            st.session_state.messages.pop(i)
            st.rerun()

# --- 🎤 Sprachaufnahme + Button in einer Zeile mit Input ---
components.html("""
<script>
const recognitionSupported = !!(window.webkitSpeechRecognition || window.SpeechRecognition);
const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition || null;
let recognition = null;
let recognizing = false;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'de-DE';
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log("Erkannt:", transcript);

        // Versuche, Textfeld zu finden
        const findInput = () => {
            const allTextareas = window.parent.document.querySelectorAll("textarea");
            for (const t of allTextareas) {
                if (t.placeholder?.includes("Hier schreiben")) {
                    t.value = transcript;
                    t.dispatchEvent(new Event("input", { bubbles: true }));
                    console.log("✅ Text erfolgreich eingefügt:", transcript);
                    return true;
                }
            }
            console.log("❌ Kein passendes Textfeld gefunden");
            return false;
        };

        // Wiederhole Suche (iOS braucht kleinen Delay)
        setTimeout(findInput, 300);
        setTimeout(findInput, 1000);
    };

    recognition.onerror = (event) => {
        console.log("SpeechRecognition Fehler:", event.error);
    };

    recognition.onend = () => {
        recognizing = false;
        const micBtn = document.getElementById('mic-btn');
        if (micBtn) micBtn.classList.remove('mic-active');
    };
}

function startRecording() {
    if (!recognition) {
        alert("Dein Browser unterstützt keine Spracherkennung.");
        return;
    }
    try {
        recognition.start();
        recognizing = true;
        const micBtn = document.getElementById('mic-btn');
        if (micBtn) micBtn.classList.add('mic-active');
    } catch (e) {
        console.log("Startfehler:", e);
    }
}

function stopRecording() {
    if (recognition && recognizing) {
        recognition.stop();
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('mic-btn');
    if (!micBtn) return;

    micBtn.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        startRecording();
    });
    document.addEventListener('pointerup', (e) => {
        if (recognizing) stopRecording();
    });

    // Touch Fallback für iOS
    micBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    }, {passive:false});
    document.addEventListener('touchend', (e) => {
        if (recognizing) stopRecording();
    });
});
</script>

<style>
#mic-btn {
  background:none;
  border:none;
  font-size:28px;
  color:white;
  cursor:pointer;
  border-radius:50%;
  padding:6px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

/* Glüh-Effekt beim Aufnehmen */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0.6); }
    70% { box-shadow: 0 0 0 12px rgba(255, 80, 80, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0); }
}
.mic-active {
    color: #ff4d4d !important;
    animation: pulseGlow 1.2s infinite;
    transform: scale(1.12);
}

/* Positioniert das Mic rechts neben dem Input */
.mic-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 8px;
    width: 100%;
    margin-top: 4px;
}
</style>

<div class="mic-container">
  <button id="mic-btn" aria-label="Gedrückt halten zum Sprechen">🎤</button>
</div>
""", height=90)


# --- Chat Input ---
if user_input := st.chat_input("Hier schreiben..."):
    st.session_state.messages.append(("Du", user_input))
    bot_reply = clean_response(get_openrouter_response(user_input))
    st.session_state.messages.append(("Jaques Bubu", bot_reply))
    st.rerun()
