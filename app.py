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
from pydub.generators import Sine

# -------------------------
# 1️⃣ Setup OpenAI
# -------------------------
client = OpenAI(api_key=st.secrets["Lucas13"])

# Hide default audio player
st.markdown("<style>audio { display: none !important; }</style>", unsafe_allow_html=True)

st.title("🎙️ Colab Tutor (Lucas11)")
st.caption("Audio is trimmed to 3 seconds. Stop recording warning included.")

# -------------------------
# 2️⃣ Session State
# -------------------------
if "lock" not in st.session_state:
    st.session_state.lock = False
if "temp_audio" not in st.session_state:
    st.session_state.temp_audio = None
if "counter" not in st.session_state:
    st.session_state.counter = 0

# -------------------------
# 3️⃣ Microphone Section
# -------------------------
if not st.session_state.lock:
    audio_key = f"ms_{st.session_state.counter}"
    audio_input = st.audio_input("Click and speak (up to 3 seconds)", key=audio_key)

    if audio_input is not None:
        st.session_state.temp_audio = audio_input
        st.session_state.lock = True
        st.session_state.counter += 1
        st.rerun()

# -------------------------
# 4️⃣ Process Audio
# -------------------------
if st.session_state.lock and st.session_state.temp_audio is not None:
    try:
        # A. Save original audio
        original_fname = f"{uuid.uuid4().hex}_orig.wav"
        with open(original_fname, "wb") as f:
            f.write(st.session_state.temp_audio.getbuffer())

        # Load and trim audio to 3 seconds
        audio = AudioSegment.from_file(original_fname)
        trimmed_audio = audio[:3000]  # first 3 seconds only
        trimmed_fname = f"{uuid.uuid4().hex}_trimmed.wav"
        trimmed_audio.export(trimmed_fname, format="wav")

        # -------------------------
        # B. 3-Second Recording Progress Bar
        # -------------------------
        progress = st.progress(0, text="Recording...")
        for i in range(101):
            time.sleep(3 / 100)
            progress.progress(i)

        # -------------------------
        # C. Flashing Warning + Beep + Vibration
        # -------------------------
        warning_placeholder = st.empty()
        warning_placeholder.markdown(
            """
            <div style="
                color: red;
                font-size: 32px;
                font-weight: bold;
                text-align: center;
                animation: flash 0.5s alternate infinite;">
                ⏱ STOP RECORDING ⏱
            </div>
            <script>
            // Flashing animation
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes flash {
                    0% { opacity: 1; }
                    100% { opacity: 0; }
                }
            `;
            document.head.appendChild(style);

            // Beep-beep-beep sequence
            const context = new (window.AudioContext || window.webkitAudioContext)();
            for (let i=0; i<3; i++){
                const osc = context.createOscillator();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(1000, context.currentTime);
                osc.connect(context.destination);
                osc.start(context.currentTime + i*0.4);
                osc.stop(context.currentTime + i*0.4 + 0.2);
            }

            // Vibration pulses
            if (navigator.vibrate){
                navigator.vibrate([200,100,200,100,200]);
            }
            </script>
            """,
            unsafe_allow_html=True
        )

        # -------------------------
        # D. Whisper Transcription
        # -------------------------
        with open(trimmed_fname, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            ).text

        st.write(f"**You:** {transcript}")

        # -------------------------
        # E. GPT Response
        # -------------------------
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Very short, witty answers. Max 10 words."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = response.choices[0].message.content

        # -------------------------
        # F. gTTS Playback
        # -------------------------
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

        # -------------------------
        # G. Output + Speaking Progress
        # -------------------------
        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

        speak_bar = st.progress(0, text="Lucas11 is speaking...")
        for i in range(101):
            time.sleep(duration / 100)
            speak_bar.progress(i)

        # -------------------------
        # H. Reset for next interaction
        # -------------------------
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.rerun()


