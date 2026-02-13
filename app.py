import sys
import io
import streamlit as st
from openai import OpenAI
from pydub import AudioSegment

# Python 3.13 audio fix
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Colab Tutor (Lucas11)")

# ---- BUILT-IN STREAMLIT MIC ----
audio_file = st.audio_input("Hold to speak")

if audio_file is not None:

    with st.spinner("Transcribing..."):

        try:
            # Convert uploaded audio to WAV
            audio = AudioSegment.from_file(audio_file)

            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            wav_io.name = "input.wav"

            # Transcribe
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=wav_io
            ).text

            st.success("Done")
            st.write("**You said:**", transcript)

        except Exception as e:
            st.error(e)

