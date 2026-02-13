import streamlit as st
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Spanish App", page_icon="🎙️")

# 1. Initialize session state to handle the "deletion"
if "recording_finished" not in st.session_state:
    st.session_state.recording_finished = False

st.title("🎙️ Spanish Practice: Hold to Speak")
st.write("Hold the mic to record. Release to hear it. Click 'Delete' to wipe it.")

# 2. The Recorder
# This naturally stops when you release the mouse/touch
audio_bytes = audio_recorder(
    text="Hold to speak",
    recording_color="#e8b62c", # Yellow when recording
    neutral_color="#00a884",   # WhatsApp Green
    icon_size="3x",
)

# 3. Playback and Deletion Logic
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    # This button "re-runs" the app and clears the audio_bytes variable
    if st.button("🗑️ Delete & Record New"):
        st.session_state.recording_finished = False
        st.rerun() 

else:
    st.info("No recording currently in memory.")

# --- CSS to make it look clean ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #f15c5c;
        color: white;
        border-radius: 20px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)
