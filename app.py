import streamlit as st
import base64
import io
from openai import OpenAI

# --- Streamlit UI ---
st.title("🎙 Hold-to-Speak Demo")

st.markdown("""
<div style="text-align:center;">
    <canvas id="visualizer" width="300" height="60" style="margin-bottom:10px;"></canvas><br>
    <button id="mic" style="width:120px; height:120px; border-radius:60px; background:#00a884; color:white; font-size:16px; border:none;">
        HOLD
    </button>
    <p id="status" style="font-weight:bold;">Press and hold to speak</p>
</div>

<script>
const btn = document.getElementById('mic');
const status = document.getElementById('status');
const canvas = document.getElementById('visualizer');
const ctx = canvas.getContext('2d');

let chunks = [];
let mediaRecorder;
let audioCtx;
let analyser;
let animId;

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);

    mediaRecorder = new MediaRecorder(stream);
    chunks = [];

    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, {type:'audio/webm'});
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            const base64 = reader.result.split(',')[1];
            window.parent.postMessage({
                type:'streamlit:set_component_value',
                key:'audio_bridge',
                value:base64
            }, '*');
        };
    };

    mediaRecorder.start();

    // Visualizer
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const render = () => {
        animId = requestAnimationFrame(render);
        analyser.getByteFrequencyData(dataArray);
        ctx.clearRect(0,0,canvas.width,canvas.height);
        let x=0;
        for(let i=0;i<dataArray.length;i++){
            let h = dataArray[i]/2;
            ctx.fillStyle='#00a884';
            ctx.fillRect(x,(60-h)/2,4,h);
            x+=6;
        }
    };
    render();
}

function stopRecording() {
    if(mediaRecorder && mediaRecorder.state==='recording') mediaRecorder.stop();
    if(audioCtx) audioCtx.close();
    if(animId) cancelAnimationFrame(animId);
}

btn.onmousedown = btn.ontouchstart = () => {
    btn.style.background='#ff4b4b';
    status.innerText='Recording...';
    startRecording();
};

btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
    btn.style.background='#00a884';
    status.innerText='Press and hold to speak';
    stopRecording();
};
</script>
""", unsafe_allow_html=True)

# --- Invisible input to catch Base64 audio ---
audio_b64 = st.text_input("Audio bridge", key="audio_bridge", label_visibility="collapsed")

# --- OpenAI Whisper transcription ---
if audio_b64:
    client = OpenAI(api_key=st.secrets["Lucas13"])
    with st.spinner("Transcribing..."):
        try:
            audio_bytes = base64.b64decode(audio_b64)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "input.webm"

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            ).text

            st.write(f"**You said:** {transcript}")
        except Exception as e:
            st.error(f"Error transcribin

