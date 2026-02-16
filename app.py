import streamlit as st
import time, io, os, uuid
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import numpy as np

# 1️⃣ Setup OpenAI
client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Colab Tutor (Lucas11)")
st.caption("Recording auto-limited to 3 seconds.")

# Initialize state
if 'lock' not in st.session_state:
    st.session_state.lock = False
if 'audio_frames' not in st.session_state:
    st.session_state.audio_frames = []

# 2️⃣ Audio Processing Class
class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame):
        # Convert to numpy array
        pcm = frame.to_ndarray()
        self.frames.append(pcm)
        return frame

# 3️⃣ Start WebRTC Streamer
if not st.session_state.lock:
    if st.button("🎤 Record 3 Seconds"):
        st.session_state.lock = True
        st.session_state.audio_frames = []

        # Start WebRTC streamer
        ctx = webrtc_streamer(
            key="lucas11",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            client_settings=ClientSettings(
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={"audio": True, "video": False}
            ),
            audio_processor_factory=AudioProcessor,
            async_processing=True
        )

        # 3-second visual countdown
        progress = st.progress(0, text="Recording...")
        for i in range(101):
            time.sleep(3 / 100)
            progress.progress(i)

        # Stop streaming
        ctx.stop()
        st.success("Recording finished!")

        # Combine frames into one audio segment
        audio_data = np.concatenate(ctx.audio_processor.frames)
        audio_bytes = (audio_data.astype(np.int16)).tobytes()

        # Save temp WAV
        fname = f"{uuid.uuid4().hex}_record.wav"
        seg = AudioSegment(
            data=audio_bytes,
            sample_width=2,
            frame_rate=48000,
            channels=1
        )
        # Trim exactly 3 sec (just in case)
        seg = seg[:3000]
        seg.export(fname, format="wav")

        st.session_state.temp_audio = fname
        st.rerun()

# 4️⃣ Process Audio After Recording
if st.session_state.lock and st.session_state.get('temp_audio'):

    try:
        # A. Transcribe
        with open(st.session_state.temp_audio, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            ).text

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

        # C. gTTS TTS
        tts_file = f"{uuid.uuid4().hex}_tts.mp3"
        gTTS(ai_text, lang="en").save(tts_file)
        audio_seg = AudioSegment.from_mp3(tts_file)
        duration = len(audio_seg) / 1000.0

        buf = io.BytesIO()
        audio_seg.export(buf, format="mp3")
        if os.path.exists(tts_file): os.remove(tts_file)
        if os.path.exists(st.session_state.temp_audio): os.remove(st.session_state.temp_audio)

        # D. Output
        st.markdown(f"### **Lucas11:** {ai_text}")
        st.audio(buf, format="audio/mp3", autoplay=True)

        # Speaking progress bar
        speak_bar = st.progress(0, text="Lucas11 is speaking...")
        for i in range(101):
            time.sleep(duration / 100)
            speak_bar.progress(i)

        # E. Clean reset
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.session_state.audio_frames = []
        st.rerun()

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.session_state.lock = False
        st.session_state.temp_audio = None
        st.session_state.audio_frames = []
        st.rerun()
