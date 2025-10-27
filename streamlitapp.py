import streamlit as st

st.markdown("""
<style>
div[data-testid="stChatInput"] {
    border: 2px solid #999 !important;
    border-radius: 12px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    padding: 5px;
}
</style>
""", unsafe_allow_html=True)

st.title("Hallo Streamlit 👋")
st.write("Das ist deine erste Streamlit-App!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for i, (sender, msg) in enumerate(st.session_state.messages):
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"**{sender}:** {msg}")
    with col2:
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.messages.pop(i)
            st.rerun()

if user:= st.chat_input("Hier schreiben..."):
    st.session_state.messages.append(("Du", user))  # Speichern
    st.rerun() 

