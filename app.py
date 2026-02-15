
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import numpy as np
import tempfile
import soundfile as sf
import time

st.title("🎙️ 3-Second Auto Audio Recorder")

# Client settings
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

# Session state
if "audio_data" not in st.session_state:
    st.session_state.audio_data = []

# Audio frame callback
def audio_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio = frame.to_ndarray()
    st.session_state.audio_data.append(audio)
    return frame

# Record button with red while recording
button_style = """
<style>
.stButton>button {{
    height: 80px;
    width: 80px;
    font-size: 20px;
    border-radius: 50%;
    background-color: {};
    color: white;
}}
</style>
"""

def start_recording():
    st.session_state.audio_data = []
    webrtc_ctx.start()
    st.session_state.recording = True
    time.sleep(3)  # Record for 3 seconds
    webrtc_ctx.stop()
    st.session_state.recording = False
    st.success("Recording complete! ✅")

if "recording" not in st.session_state:
    st.session_state.recording = False

# WebRTC streamer (sendonly mode)
webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDONLY,
    client_settings=WEBRTC_CLIENT_SETTINGS,
    audio_frame_callback=audio_callback,
    async_processing=True,
    video_frame_callback=None,
    audio_receiver_size=256,
)

# Update button color dynamically
button_color = "red" if st.session_state.recording else "#4CAF50"
st.markdown(button_style.format(button_color), unsafe_allow_html=True)

# Record button triggers 3-second recording
if st.button("Record (3 sec)"):
    start_recording()

# Save and playback
if st.session_state.audio_data:
    audio_array = np.concatenate(st.session_state.audio_data, axis=1)[0]
    # Save to WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, audio_array, 44100)
        st.audio(tmp.name)
