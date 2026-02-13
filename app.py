import sys
import base64
import io
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from pydub import AudioSegment

# 1. PYTHON 3.13 PATCH
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

# 2. SETUP
client = OpenAI(api_key=st.secrets["Lucas13"])

st.set_page_config(page_title="Colab Tutor", layout="centered")

# Hide the bridge input box from view
st.markdown("""
    <style>
    div[data-testid="stTextInput"] { position: absolute; top: -1000px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Colab Tutor")
st.write("Hold the button to speak to Lucas.")

# 3. THE FRONTEND (JavaScript Hold-to-Speak)
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center;">
    <canvas id="visualizer" width="300" height="60" style="margin-bottom: 10px;"></canvas>
    <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; outline: none;">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="color: #555; margin-top: 15px; font-weight: bold;">HOLD TO SPEAK</p>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    let mediaRecorder, audioChunks = [], audioCtx, analyser, animId;

    async function startMic() {
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
        return stream;
    }

    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        btn.style.backgroundColor = '#ff4b4b';
        status.innerText = 'RECORDING...';
        const stream = await startMic();
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    data: reader.result.split(',')[1],
                    key: 'audio_b64'
                }, '*');
            };
        };
        mediaRecorder.start();
    };

    btn.onmouseup = btn.ontouchend = () => {
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

# 4. THE BACKEND (Wait for Data)
audio_b64 = st.text_input("bridge", key="audio_b64")

if audio_b64:
    with st.spinner("Transcribing..."):
        try:
            # Convert Base64 back to file
            audio_bytes = base64.b64decode(audio_b64)
            audio_file = io.BytesIO(audio_bytes)
            
            # Use Pydub to ensure the file is clean before sending to OpenAI
            audio_segment = AudioSegment.from_file(audio_file)
            clean_wav = io.BytesIO()
            audio_segment.export(clean_wav, format="wav")
            clean_wav.name = "input.wav"
            clean_wav.seek(0)

            # OpenAI Whisper
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=clean_wav
            ).text
            
            st.markdown("### You said:")
            st.info(transcript)

        except Exception as e:
            st.error(f"Error: {e}")
