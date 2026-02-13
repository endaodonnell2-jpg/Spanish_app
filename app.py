import sys
import base64
import io
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from pydub import AudioSegment

# Python 3.13 audio fix
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Colab Tutor (Lucas11)")

# ---- AUDIO COMPONENT ----
audio_b64 = components.html("""
<script src="https://unpkg.com/streamlit-component-lib@1.4.0/dist/index.js"></script>

<div style="text-align:center;">
<button id="rec" style="width:120px;height:120px;border-radius:60px;background:#00a884;color:white;font-size:16px;border:none;">
HOLD
</button>
<p id="status">Hold to Speak</p>
</div>

<script>
const btn = document.getElementById("rec");
const status = document.getElementById("status");
let mediaRecorder;
let chunks = [];

async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, {type:'audio/webm'});
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            const base64 = reader.result.split(',')[1];
            Streamlit.setComponentValue(base64);
        };
    };
    mediaRecorder.start();
}

btn.onmousedown = async () => {
    chunks = [];
    btn.style.background = "red";
    status.innerText = "Recording...";
    await start();
};

btn.onmouseup = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        btn.style.background = "#00a884";
        status.innerText = "Hold to Speak";
    }
};
</script>
""", height=200)

# ---- BACKEND ----
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

        except Exception as e:
            st.error(e)

