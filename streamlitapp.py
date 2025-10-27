import streamlit as st

st.set_page_config(page_title="Chat App 💬", page_icon="💬")

# CSS für Chat Input und Layout
st.markdown("""
<style>
/* Chat Input verschönern */
div[data-testid="stChatInput"] {
    border: 2px solid #999 !important;
    border-radius: 12px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    padding: 5px;
}

/* Menü, Footer, Toolbar ausblenden */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden; height:0; position:fixed;}

/* Nachricht & Löschen Button */
.chat-message {
    position: relative;
    padding: 8px 12px;
    border-radius: 12px;
    background-color: #f1f1f1;
    margin-bottom: 6px;
}
.delete-btn {
    position: absolute;
    right: 8px;
    top: 8px;
    background: none;
    border: none;
    color: #f33;
    font-size: 18px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.title("Hallo Streamlit 👋")
st.write("Das ist deine erste Streamlit-App!")

# Session State für Chat-Nachrichten
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat anzeigen
for i, (sender, msg) in enumerate(st.session_state.messages):
    st.markdown(f"""
        <div class="chat-message">
            <b>{sender}:</b> {msg}
            <form action="" method="post">
                <button class="delete-btn" name="delete_{i}">❌</button>
            </form>
        </div>
        """, unsafe_allow_html=True)
    # Python Button als Backup, damit Rerun funktioniert
    if st.button(f"delete_{i}", key=f"delete_{i}"):
        st.session_state.messages.pop(i)
        st.rerun()

# Neue Nachricht
if user := st.chat_input("Hier schreiben..."):
    st.session_state.messages.append(("Du", user))
    st.rerun()
