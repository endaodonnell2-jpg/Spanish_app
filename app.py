import sys, time, io, os, uuid
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

import streamlit as st
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1️⃣ Setup OpenAI
client = OpenAI(api_key=st.secrets["Lucas13"])

# CSS to hide audio player but still allow playback
st.markdown("<style>audio { display: none !important; }</style>", unsafe_allow_html=True)

st.title("🎙️ Colab Tutor (Lucas11)")
st.caption("Audio automatically trimmed to 3 seconds.")

# Initialize session state
if "lock" not in st.session_state:
    st.session_state.lock = False
if "temp_audio" not in st.session_state:
    st.session_state.temp_audio = None
if "counter" not in st.session_state:
    st.session_state.counter = 0

# 2️⃣ Microphone Section
if not st.session_state.lock:
    # Unique key to force new widget each time
    audio_key = f"ms_{st.session_state.counter}"
    audio_input = st.audio_input("Click and speak (up to 3 seconds)", key=audio_key)

    if audio_input is not None:
        st.session_state.temp_audio = audio_input
        st.session_state.lock = True
        st.session_state.counter += 1
        st.rerun()

# 3️⃣ Processing Audio
if st.session_state.lock and st.session_state.temp_audio is not None:
    try:
        # A. Save temp audio to disk
        original_fname = f"{uuid.uuid4().hex}_orig.wav"
        with open(original_fname, "wb") as f:
            f.write(st.session_state.temp_audio.getbuffer())

        # Load audio
        audio = AudioSegment.from_file(original_fname)

        # Trim to exactly 3 seconds
        trimmed_audio = audio[:3000]
        trimmed_fname = f"{uuid.uuid4().hex}_trimmed.wav"
        trimmed_audio.export(trimmed_fname, format="wav")

        # B. Show 3-second visual progress bar (simulate recording)
        progress = st.progress(0, text="Processing audio...")
        for i in range(101):
            time.sleep(3 / 100)
            progress.progress(i)

        # C. Send trimmed audio to Whisper
        with open(trimmed_fname, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            ).text

        st.write(f"**You:** {transcript}")

        # D. GPT Response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Very short, witty answers. Max 10 words."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = response.choices[0].message.content

        # E. Text-to-Speech
        tts_file = f"{uuid.uuid4().hex}_tts.mp3"
        gTTS(ai_text, lang="en").save(tts_file)
        audio_seg = AudioSegment.from_mp3(tts_file)
        duration = len(audio_seg) / 1000.0

        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")

        # Cleanup temp files
        for file in [original_fname, trimmed_fname, tts_file]:
            if os.path.exists(file):
                os.remove(file)

        # F. Output text + audio
        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

        # G. Speaking progress bar
        speak_bar = st.progress(0, text="Lucas11 is speaking...")
        for i in range(101):
            time.sleep(duration / 100)
            speak_bar.progress(i)

        # H. Clean reset
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()

