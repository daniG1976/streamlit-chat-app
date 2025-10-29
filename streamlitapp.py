import streamlit as st
import requests

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
        response = requests.post(API_URL, headers=headers, json=data)
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
/* Chatblasen */
.chat-bubble {
    padding: 10px 14px;
    border-radius: 16px;
    margin-bottom: 6px;
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
}
div[data-testid^="stButton"] button {
    background: none !important;
    border: none !important;
    color: #ff6b6b !important;
    font-size: 16px !important;
    cursor: pointer !important;
    padding: 0 !important;
}
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.3);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 8px;
}
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

# --- Nachrichtenanzeige mit Lösch-Button ---
for i, (sender, msg) in enumerate(st.session_state.messages):
    cols = st.columns([9, 1])
    with cols[0]:
        bubble_class = "user-bubble" if sender == "Du" else "bot-bubble"
        st.markdown(f"<div class='chat-bubble {bubble_class}'><b>{sender}:</b> {msg}</div>", unsafe_allow_html=True)
    with cols[1]:
        with st.container():
            st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.messages.pop(i)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# --- Neue Nachricht senden ---
if user := st.chat_input("Hier schreiben..."):
    st.session_state.messages.append(("Du", user))
    bot_reply = get_openrouter_response(user)
    st.session_state.messages.append(("Kumpel", bot_reply))
    st.rerun()

