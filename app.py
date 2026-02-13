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

# Python 3.13 audio fix
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Lucas11 – Hold To Speak")

# ---- 1. Hidden bridge input ----
audio_b64 = st.text_input("bridge", key="audio_bridge", label_visibility="collapsed")

# ---- 2. Inline HTML button + visualizer ----
st.markdown("""
<style>
div[data-testid="stTextInput"] { position: absolute; top: -1000px; }
</style>
""", unsafe_allow_html=True)

components.html("""
<div style="text-align:center;">
<canvas id="vis" width="300" height="60" style="margin-bottom:10px;"></canvas>
<button id="rec" style="width:120px;height:120px;border-radius:60px;background:#00a884;color:white;border:none;font-size:16px;">
HOLD
</button>
<p id="status">Hold to Speak</p>
</div>

<script>
const btn = document.getElementById("rec");
const status = document.getElementById("status");
const canvas = document.getElementById("vis");
const ctx = canvas.getContext('2d');
let mediaRecorder, chunks=[], audioCtx, analyser, animId;

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize=64;
    source.connect(analyser);
    const data = new Uint8Array(analyser.frequencyBinCount);
    const render = () => {
        animId = requestAnimationFrame(render);
        analyser.getByteFrequencyData(data);
        ctx.clearRect(0,0,canvas.width,canvas.height);
        let x=0;
        for(let i=0;i<data.length;i++){
            let h = data[i]/2;
            ctx.fillStyle="#00a884";
            ctx.fillRect(x,(60-h)/2,4,h);
            x+=6;
        }
    };
    render();
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e=>chunks.push(e.data);
    mediaRecorder.onstop=()=>{
        const blob = new Blob(chunks,{type:'audio/webm'});
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = ()=>{
            const base64 = reader.result.split(',')[1];
            window.parent.postMessage({type:"streamlit:set_widget_value", key:"audio_bridge", value:base64}, "*");
        };
    };
    mediaRecorder.start();
}

btn.onmousedown = async ()=>{
    chunks=[];
    btn.style.background="red";
    status.innerText="Recording...";
    await startRecording();
};

btn.onmouseup = btn.onmouseleave = ()=>{
    if(mediaRecorder && mediaRecorder.state==="recording"){
        mediaRecorder.stop();
        btn.style.background="#00a884";
        status.innerText="Hold to Speak";
        cancelAnimationFrame(animId);
        if(audioCtx) audioCtx.close();
    }
};
</script>
""", height=220)

# ---- 3. Backend processing ----
if audio_b64:
    with st.spinner("Transcribing..."):
        try:
            audio_bytes = base64.b64decode(audio_b64)

            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            wav_io.name = "input.wav"

            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=wav_io
            ).text

            st.success("Done")
            st.write("**You said:**", transcript)

            # Clear bridge to allow next recording
            st.session_state["audio_bridge"] = ""

        except Exception as e:
            st.error(f"Something went wrong: {e}")
