import streamlit as st
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Spanish Practice", page_icon="🎙️")

st.title("🎙️ Spanish Practice")
st.write("Click the mic to record. It will stop and play back automatically when you finish speaking.")

# WhatsApp Style Styling
st.markdown("""
    <style>
    /* Center the mic and make it green */
    .stAudioRecorder {
        display: flex;
        justify-content: center;
    }
    button {
        border-radius: 50% !important;
    }
    </style>
""", unsafe_allow_html=True)

# The Recorder
# pause_threshold=1.0 means if you stop talking for 1 second, it finishes and plays back.
audio_bytes = audio_recorder(
    text="Click to Speak",
    recording_color="#e8b62c",
    neutral_color="#00a884",
    icon_size="3x",
    pause_threshold=1.0, 
)

# Playback and Auto-Delete Logic
if audio_bytes:
    st.write("### Hear your Spanish:")
    st.audio(audio_bytes, format="audio/wav")
    
    # This button wipes the memory
    if st.button("🗑️ Delete & Try Again"):
        st.rerun()
else:
    st.info("Mic is ready. Speak clearly in Spanish!")
