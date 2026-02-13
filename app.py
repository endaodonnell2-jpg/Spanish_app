import sys
import base64
import io
import os
import uuid
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# ----------------------------
# PYTHON 3.13 AUDIO PATCH
# ----------------------------
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

# ----------------------------
# OPENAI CLIENT
# ----------------------------
client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Colab Tutor (Lucas11)")

# ----------------------------
# HIDE THE BRIDGE INPUT
# ----------------------------
st.markdown("""
    <style>
    div[data-testid="stTextInput"] { 
        position: absolute; 
        top: -1000px; 
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# FRONTEND AUDIO BUTTON
# ----------------------------
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; font-family: sans-serif;">
    <canvas id="visualizer" width="300" height="60" style="margin-bottom: 10px;"></canvas>
    <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="margin-top: 15px; font-weight: bold;">HOLD TO SPEAK</p>
</div>

<script>
const btn = document.getElementById('mic');
const status = document.getElementById('status');
const canvas = document.getElementById('visualizer');
const canvasCtx = canvas.getContext('2d');

let mediaRecorder, audioChunks = [], audioCtx, analyser, animId;

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);

    const data = new Uint8Array(analyser.frequencyBinCount);

    const render = () => {
        animId = requestAnimationFrame(render);
        analyser.getByteFrequencyData(data);
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        let x = 0;
        for(let i=0; i<data.length; i++) {
            let h = data[i]/2;
            canvasCtx.fillStyle = '#00a884';
            canvasCtx.fillRect(x, (60-h)/2, 4, h);
            x += 6;
        }
    };
    render();

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.readAsDataURL(blob);

        reader.onloadend = () => {
            const audioData = reader.result.split(',')[1];

            window.parent.postMessage({
                type: "streamlit:set_widget_value",
                key: "audio_bridge",
                value: audioData
            }, "*");
        };
    };

    mediaRecorder.start();
}

btn.onmousedown = btn.ontouchstart = async (e) => {
    e.preventDefault();
    audioChunks = [];
    btn.style.backgroundColor = '#ff4b4b';
    status.innerText = 'RECORDING...';
    await startRecording();
};

btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
    if(mediaRecorder?.state === 'recording') {
        mediaRecorder.stop();
        btn.style.backgroundColor = '#00a884';
        status.innerText = 'HOLD TO SPEAK';
        cancelAnimationFrame(animId);
        if(audioCtx) audioCtx.close();
    }
};
</script>
"""

components.html(st_bridge_js, height=220)

# ----------------------------
# INVISIBLE BRIDGE INPUT
# ----------------------------
audio_b64 = st.text_input("bridge", key="audio_bridge", label_visibility="collapsed")

# ----------------------------
# BACKEND PROCESSING
# ----------------------------
if audio_b64:

    with st.spinner("Transcribing..."):

        try:
            audio_bytes = base64.b64decode(audio_b64)

            # Convert WEBM → WAV
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")

            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            wav_io.name = "input.wav"

            # Transcribe
            transcript_response = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=wav_io
            )

            transcript = transcript_response.text

            st.write(f"**You said:** {transcript}")

            # Clear bridge so it can record again
            st.session_state["audio_bridge"] = ""

        except Exception as e:
            st.error(f"Something went wrong: {e}")

