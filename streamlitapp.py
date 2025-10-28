import streamlit as st
import requests

# --- Seitentitel und Icon ---
st.set_page_config(page_title="Chat App 💬", page_icon="💬")

# --- API-Key und Endpoint ---
api_key = "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"
api_url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

st.markdown("""
<style>
div[data-testid^="stButton"] button {
    font-size: 14px !important;  /* kleiner als Standard */
    padding: 2px 4px !important; /* innenrum kleiner */
    color: #e53935 !important;   /* rot behalten */
}
</style>
""", unsafe_allow_html=True)

# --- App Titel ---
st.title("Lass Chatten Kumpel👋")
st.write("Willkommen in deiner persönlichen Chat-App 💬")

# --- Nachrichten speichern ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_mistral_response(user_input):
    data = {
        "model": "mistral-7b-instruct",
        "messages": [{"role": "user", "content": user_input}],
        "max_tokens": 150
    }
    response = requests.post(api_url, headers=headers, json=data)
    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Ups, da ist etwas schiefgelaufen."

# --- Chat anzeigen ---
for i, (sender, msg) in enumerate(st.session_state.messages):
    col1, col2 = st.columns([9, 1])
    with col1:
        st.markdown(f"<div class='chat-bubble'><b>{sender}:</b> {msg}</div>", unsafe_allow_html=True)
    with col2:
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.messages.pop(i)
            st.rerun()

# --- Neue Nachricht hinzufügen ---
if user := st.chat_input("Hier schreiben..."):
    st.session_state.messages.append(("Du", user))
    bot_reply = get_mistral_response(user)
    st.session_state.messages.append(("Kumpel", bot_reply))
    st.rerun()

    
