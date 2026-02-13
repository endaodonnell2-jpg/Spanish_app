import streamlit as st
from openai import OpenAI
import tempfile
import io

st.title("🎙 Simple Audio Recorder + Whisper")

# Ask user to upload or record audio
st.write("Record a short audio or upload a file (.wav, .mp3)")

audio_file = st.file_uploader("Upload your audio", type=["wav","mp3","m4a"])

# Optional: use streamlit’s experimental audio recorder
if st.button("Record using microphone (experimental)"):
    st.info("Recording will use your browser's microphone (experimental).")
    st.write("Currently requires Streamlit >=1.24 and only works in some browsers.")

# Once audio is uploaded
if audio_file:
    st.audio(audio_file)

    client = OpenAI(api_key=st.secrets["Lucas13"])
    with st.spinner("Transcribing..."):
        try:
            # If file_uploader gives a BytesIO, use it directly
            audio_bytes = audio_file.read()
            audio_file_like = io.BytesIO(audio_bytes)
            audio_file_like.name = getattr(audio_file, "name", "input.wav")

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_like
            ).text

            st.write(f"**You said:** {transcript}")
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")

