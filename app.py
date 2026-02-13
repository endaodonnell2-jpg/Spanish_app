import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="WhatsApp Recorder")

st.markdown("""
    <style>
    /* Styling the button to look like a green WhatsApp mic */
    button[title="Click to record"] {
        background-color: #00a884 !important;
        border-radius: 50% !important;
        width: 80px !important;
        height: 80px !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Hold to Speak")
st.info("Press and HOLD the mic button. Release when you are finished.")

# The magic component
# 'key' is essential for Streamlit to track it
audio = mic_recorder(
    start_prompt="Hold to Record",
    stop_prompt="Release to Stop",
    just_once=False,
    use_signer=True,
    key="my_mic"
)

# Playback Logic: This appears as soon as you release the button
if audio:
    st.write("### Your Recording:")
    st.audio(audio['bytes'])
