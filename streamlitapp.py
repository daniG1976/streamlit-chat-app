import streamlit as st
import requests
import html
import re


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

st.markdown("""
<style>
/* --- Hintergrund & Font --- */
[data-testid="stAppViewContainer"] {
    background-color: #015258;
}
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #FF9479 !important;
}

/* --- Chat Container --- */
.chat-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    margin-bottom: 8px;
    width: 100%;
}
.chat-row.bot {
    justify-content: flex-end;
}

/* --- Chatblasen --- */
.chat-bubble {
    position: relative;
    padding: 10px 14px;
    border-radius: 16px;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* Benutzer (links, grau) */
.user-bubble {
    background-color: #f1f1f1;
    color: #222;
    text-align: left;
    align-self: flex-start;
}

/* KI (rechts, hellgrün) */
.bot-bubble {
    background-color: #b2f2bb;
    color: #1b4332;
    text-align: right;
    align-self: flex-end;
}

/* --- Delete-Button im Bubble --- */
.delete-btn {
    position: absolute;
    top: 4px;
    right: 6px;
    background: none;
    border: none;
    color: #ff6b6b;
    font-size: 14px;
    cursor: pointer;
    padding: 0;
}
.delete-btn:hover {
    transform: scale(1.2);
}

/* --- Chat Input Styling --- */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.3);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 8px;
}

/* --- Menü & Footer ausblenden --- */
#MainMenu, footer, div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}

/* --- Responsive Fix für iPhone --- */
@media (max-width: 600px) {
    .chat-bubble {
        max-width: 90%;
        font-size: 16px;
    }
    .delete-btn {
        font-size: 12px;
        top: 2px;
        right: 4px;
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
    """Bereinigt Modellantworten von Markup und Sonderzeichen."""
    # Entfernt [BOUT], [/BOUT], <tags>, etc.
    text = re.sub(r'\[/?BOUT\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    return text

# --- Chat anzeigen ---
for i, (sender, msg) in enumerate(st.session_state.messages):
    # Alignment & Farbe bestimmen
    if sender == "Du":
        alignment = "user"
        bubble_class = "user-bubble"
    else:
        alignment = "bot"
        bubble_class = "bot-bubble"

    # Layout
    st.markdown(f"<div class='chat-row {alignment}'>", unsafe_allow_html=True)
    col1, col2 = st.columns([10, 1])

    with col1:
        st.markdown(
            f"<div class='chat-bubble {bubble_class}'><b>{sender}:</b> {msg}</div>",
            unsafe_allow_html=True
        )

    with col2:
        if st.button("❌", key=f"delete_{i}", help="Nachricht löschen"):
            st.session_state.messages.pop(i)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# --- Neue Nachricht senden ---
if user := st.chat_input("Hier schreiben..."):
    st.session_state.messages.append(("Du", user))
    bot_reply = clean_response(get_openrouter_response(user))
    st.session_state.messages.append(("Jaques Bubu", bot_reply))
    st.rerun()

