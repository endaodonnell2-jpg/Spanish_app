import sys
import time
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

import streamlit as st
import io, os, uuid
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1. SETUP
client = OpenAI(api_key=st.secrets["Lucas13"])

st.markdown("<style>audio { display: none !important; }</style>", unsafe_allow_html=True)

st.title("🎙️ Colab Tutor (Lucas11)")
st.caption("Recording limited to 3 seconds.")

# Initialize state
if 'lock' not in st.session_state:
    st.session_state.lock = False
if 'temp_audio' not in st.session_state:
    st.session_state.temp_audio = None

# 2. RECORD BUTTON (3 sec visual capture)
if not st.session_state.lock:

    if st.button("🎤 Record (3 sec)"):
        st.session_state.lock = True

        # Visual recording countdown
        bar = st.progress(0, text="Recording...")
        for i in range(101):
            time.sleep(3 / 100)
            bar.progress(i)

        # Capture audio AFTER countdown
        audio_input = st.audio_input("Speak now")

        if audio_input is not None:
            st.session_state.temp_audio = audio_input
            st.rerun()
        else:
            st.session_state.lock = False
            st.rerun()

# 3. PROCESS AUDIO
if st.session_state.lock and st.session_state.temp_audio is not None:

    try:
        # A. Save original file
        with st.spinner("Decoding..."):

            original_fname = f"{uuid.uuid4().hex}_orig.wav"
            with open(original_fname, "wb") as f:
                f.write(st.session_state.temp_audio.getbuffer())

            audio = AudioSegment.from_file(original_fname)

            # Hard trim to 3 seconds
            trimmed_audio = audio[:3000]

            trimmed_fname = f"{uuid.uuid4().hex}_trimmed.wav"
            trimmed_audio.export(trimmed_fname, format="wav")

            # Send trimmed file to Whisper
            with open(trimmed_fname, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                ).text

            if os.path.exists(original_fname): os.remove(original_fname)
            if os.path.exists(trimmed_fname): os.remove(trimmed_fname)

        st.write(f"**You:** {transcript}")

        # B. GPT Response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Very short, witty answers. Max 10 words."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = response.choices[0].message.content

        # C. Text-to-Speech
        fname = f"{uuid.uuid4().hex}.mp3"
        gTTS(ai_text, lang="en").save(fname)

        audio_seg = AudioSegment.from_mp3(fname)
        duration = len(audio_seg) / 1000.0

        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")

        if os.path.exists(fname): os.remove(fname)

        # D. Output
        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

        # Speaking progress bar
        speak_bar = st.progress(0, text="Lucas11 is speaking...")
        for i in range(101):
            time.sleep(duration / 100)
            speak_bar.progress(i)

        # E. Reset cleanly
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()

    except Exception as e:
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.error("Something went wrong. Try again.")
        st.rerun()

