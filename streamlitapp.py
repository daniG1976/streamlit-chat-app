import streamlit as st
import requests
import html
import re
import streamlit.components.v1 as components

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
    padding: 10px 14px;
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

/* Mikro-Button */
.mic-container {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
}
.mic-btn {
    background: none;
    border: 2px solid #FF9479;
    border-radius: 50%;
    color: white;
    font-size: 22px;
    cursor: pointer;
    width: 42px;
    height: 42px;
    transition: all 0.25s ease-in-out;
}
.mic-btn.glow {
    background-color: #FF9479;
    box-shadow: 0 0 12px #FF9479;
    transform: scale(1.1);
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
    """Bereinigt Modellantworten."""
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

# --- Eingabefeld + Mikro-Button ---
components.html(
    """
    <div class="mic-container">
        <textarea id="user_input" placeholder="Hier sprechen oder schreiben..." rows="1"
            style="flex:1; border-radius:12px; padding:8px; border:none; font-size:16px; resize:none;"></textarea>
        <button id="micBtn" class="mic-btn">🎤</button>
    </div>

    <script>
    const micBtn = document.getElementById("micBtn");
    const input = document.getElementById("user_input");
    let recognition;
    let listening = false;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.lang = 'de-DE';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            micBtn.classList.add("glow");
            listening = true;
        };
        recognition.onend = () => {
            micBtn.classList.remove("glow");
            listening = false;
        };
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            input.value = text;

            // Automatisch senden an Streamlit
            const inputEvent = new Event('input', { bubbles: true });
            input.dispatchEvent(inputEvent);

            setTimeout(() => {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
            }, 300);
        };
    }

    micBtn.addEventListener("click", () => {
        if (!listening) recognition.start();
        else recognition.stop();
    });
    </script>
    """,
    height=90,
)

# --- Empfangenes Transkript aus Browser ---
if (spoken_text := st.experimental_get_query_params().get("text", [None])[0]) or st.session_state.get("spoken_input"):
    if spoken_text:
        user_input = spoken_text
        st.session_state.messages.append(("Du", user_input))
        bot_reply = clean_response(get_openrouter_response(user_input))
        st.session_state.messages.append(("Jaques Bubu", bot_reply))
        st.session_state["spoken_input"] = None
        st.experimental_rerun()
