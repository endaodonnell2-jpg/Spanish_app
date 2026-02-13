import streamlit as st
from audio_recorder_streamlit import audio_recorder

# Set page title
st.set_page_config(page_title="WhatsApp Style Recorder", page_icon="🎙️")

st.title("🎙️ WhatsApp Style Recorder")
st.write("Hold the microphone to record, release to hear it back!")

# Custom CSS to make it look a bit more like WhatsApp
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        text-align: center;
    }
    /* Make the recorder look like a floating action button */
    .stAudioRecorder {
        justify-content: center;
        display: flex;
    }
    </style>
""", unsafe_allow_html=True)

# The Recorder Component
# 'pause_threshold' at 2.0 ensures it doesn't cut off if you take a quick breath
# but stops once you stop sending audio data (releasing the click)
audio_bytes = audio_recorder(
    text="Hold to speak",
    recording_color="#e8b62c",
    neutral_color="#00a884", # WhatsApp Green
    icon_size="3x",
    pause_threshold=2.0 
)

# Playback Logic
if audio_bytes:
    st.success("Recording captured!")
    st.audio(audio_bytes, format="audio/wav")
    
    # Option to download the file
    st.download_button(
        label="Download Recording",
        data=audio_bytes,
        file_name="my_voice_message.wav",
        mime="audio/wav"
    )

