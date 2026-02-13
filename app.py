import streamlit as st
import streamlit.components.v1 as components
import base64
import speech_recognition as sr
import io

st.set_page_config(page_title="Spanish App", layout="centered")

# Initialize session state to hold the text
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

st.title("🎙️ English: Record & Transcribe")

# 1. The Bridge (JavaScript)
# This version includes a 'trigger' to make sure Streamlit sees the data
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; font-family: sans-serif;">
    <canvas id="visualizer" width="300" height="60" style="margin-bottom: 10px;"></canvas>
    <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; outline: none; -webkit-tap-highlight-color: transparent;">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="color: #555; margin-top: 15px; font-weight: bold; text-transform: uppercase;">Hold to Speak</p>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    let mediaRecorder, audioChunks = [], audioCtx, analyser, animId;

    function draw(stream) {
        audioCtx = new AudioContext();
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
    }

    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        btn.style.backgroundColor = '#ff4b4b';
        status.innerText = 'Recording...';
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        draw(stream);
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                const b64 = reader.result.split(',')[1];
                // THIS IS THE TRIGGER: Sending data back to the hidden input
                const streamlitInput = window.parent.document.querySelector('input[aria-label="hidden_audio_input"]');
                if (streamlitInput) {
                    streamlitInput.value = b64;
                    streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                // Backup method
                window.parent.postMessage({type: 'streamlit:set_widget_value', data: b64, key: 'audio_b64'}, '*');
            };
        };
        mediaRecorder.start();
    };

    btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
        if(mediaRecorder?.state === 'recording') {
            mediaRecorder.stop();
            btn.style.backgroundColor = '#00a884';
            status.innerText = 'Processing...';
            cancelAnimationFrame(animId);
            if(audioCtx) audioCtx.close();
        }
    };
</script>
"""

# Render the button
components.html(st_bridge_js, height=220)

# 2. The Python "Receiver"
# We use a text_input that is specifically labeled for the JS to find it
audio_b64 = st.text_input("hidden_audio_input", key="audio_b64", label_visibility="collapsed")

if audio_b64:
    try:
        audio_bytes = base64.b64decode(audio_b64)
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = r.record(source)
            # Transcribing English
            text = r.recognize_google(audio_data, language="en-US")
            st.session_state.transcript = text
            
    except Exception as e:
        st.session_state.transcript = "Could not hear clearly. Try again!"

# 3. The Display (This is where your text lives)
if st.session_state.transcript:
    st.markdown("### You said:")
    st.info(st.session_state.transcript)
    
    if st.button("🗑️ Clear Text"):
        st.session_state.transcript = ""
        st.rerun()
