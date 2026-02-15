
import streamlit as st
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
import time
import matplotlib.pyplot as plt

st.title("Interactive Audio Recorder 🎙️")

# Recording parameters
duration = st.slider("Recording duration (seconds)", 1, 10, 5)
fs = 44100  # Sampling rate

# State to track recording
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

# Function to record audio
def record_audio():
    st.session_state.is_recording = True
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        filename = tmp.name
        # Record audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        sf.write(filename, recording, fs)
    st.session_state.is_recording = False
    return filename, recording

# Dynamic Record Button
record_button_style = """
    <style>
    .stButton>button {
        height: 80px;   /* Double height */
        width: 80px;    /* Double width */
        font-size: 20px;
        border-radius: 50%;
        background-color: %s;
        color: white;
    }
    </style>
"""
button_color = "red" if st.session_state.is_recording else "#4CAF50"
st.markdown(record_button_style % button_color, unsafe_allow_html=True)

# Record button
if st.button("Record"):
    filename, recording = record_audio()
    st.success("Recording complete! ✅")
    
    # Play back audio
    st.audio(filename)
    
    # Plot waveform
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(np.linspace(0, duration, len(recording)), recording)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.set_title("Waveform")
    st.pyplot(fig)
