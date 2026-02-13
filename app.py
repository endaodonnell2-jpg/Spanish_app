import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Spanish Push-to-Talk", page_icon="🎙️")

st.title("🎙️ Spanish Practice")
st.write("Hold the button down to record. Let go to play back.")

# WhatsApp Style Styling
st.markdown("""
    <style>
    /* Make the button a big green circle */
    button[title="Click to record"] {
        background-color: #00a884 !important;
        border-radius: 50% !important;
        width: 100px !important;
        height: 100px !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    /* Change color to red while holding */
    button[title="Click to record"]:active {
        background-color: #ff4b4b !important;
    }
    </style>
""", unsafe_allow_html=True)

# The Component
# By default, this component handles the 'mousedown' (start) 
# and 'mouseup' (stop) logic when configured this way.
audio = mic_recorder(
    start_prompt="HOLD",
    stop_prompt="RELEASE",
    key="my_mic"
)

# Playback and Auto-Delete Logic
if audio:
    st.write("### Review your Spanish:")
    st.audio(audio['bytes'])
    
    if st.button("🗑️ Delete & Clear"):
        st.rerun()
else:
    st.info("Press and hold the button above.")
