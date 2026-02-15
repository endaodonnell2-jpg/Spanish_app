
import streamlit as st
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
import matplotlib.pyplot as plt

st.title("🎙️ 3-Second Live Recorder with Waveform")

# Recording parameters
DURATION = 3  # seconds
FS = 44100
CHANNELS = 1

# Session state
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_data" not in st.session_state:
    st.session_state.audio_data = []

# Button style: red while recording
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
button_color = "red" if st.session_state.recording else "#4CAF50"
st.markdown(button_style.format(button_color), unsafe_allow_html=True)

# Live waveform figure
fig, ax = plt.subplots(figsize=(10, 3))
line, = ax.plot([], [], lw=1)
ax.set_xlim(0, DURATION)
ax.set_ylim(-0.5, 0.5)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Amplitude")
ax.set_title("Live Waveform")
st.pyplot(fig, clear_figure=True)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    st.session_state.audio_data.append(indata.copy())
    # Update waveform
    audio_array = np.concatenate(st.session_state.audio_data, axis=0).flatten()
    times = np.linspace(0, len(audio_array)/FS, num=len(audio_array))
    line.set_data(times, audio_array)
    ax.set_xlim(max(0, times[-1]-DURATION), times[-1])
    fig.canvas.draw()
    fig.canvas.flush_events()

def record_3_seconds():
    st.session_state.audio_data = []
    st.session_state.recording = True
    with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=FS):
        sd.sleep(DURATION * 1000)
    st.session_state.recording = False
    st.success("Recording complete!")

    # Save audio
    audio_array = np.concatenate(st.session_state.audio_data, axis=0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, audio_array, FS)
        st.audio(tmp.name)
    # Plot final waveform
    fig2, ax2 = plt.subplots(figsize=(10, 3))
    times = np.linspace(0, len(audio_array)/FS, num=len(audio_array))
    ax2.plot(times, audio_array)
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Amplitude")
    ax2.set_title("Recorded Waveform")
    st.pyplot(fig2)

# Record button
if st.button("Record (3 sec)"):
    record_3_seconds()
