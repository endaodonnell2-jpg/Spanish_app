import streamlit as st
import streamlit.components.v1 as components
import base64
import speech_recognition as sr
import io

# Setup the page
st.set_page_config(page_title="Colab Tutor", layout="centered")

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

st.title("🎙️ English Transcription")
st.write("Hold the button, speak clearly in English, and release.")

# 1. Improved JavaScript (Better Audio Capture)
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; font-family: sans-serif;">
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

    function draw(stream) {
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
                let h = data[i]/2.5; 
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
        status.innerText = 'RECORDING...';
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
                window.parent.postMessage({type: 'streamlit:set_widget_value', data: b64, key: 'audio_b64'}, '*');
            };
        };
        mediaRecorder.start();
    };

    btn.onmouseup = btn.ontouchend = () => {
        if(mediaRecorder?.state === 'recording') {
            mediaRecorder.stop();
            btn.style.backgroundColor = '#00a884';
            status.innerText = 'PROCESSING...';
            cancelAnimationFrame(animId);
            if(audioCtx) audioCtx.close();
        }
    };
</script>
"""

components.html(st_bridge_js, height=220)

# 2. Advanced Python Transcription (Filters Noise)
audio_b64 = st.text_input("hidden", key="audio_b64", label_visibility="collapsed")

if audio_b64:
    with st.spinner("Cleaning audio and transcribing..."):
        try:
            audio_bytes = base64.b64decode(audio_b64)
            r = sr.Recognizer()
            
            # Sensitivity adjustments
            r.energy_threshold = 4000  # Higher means it ignores more background noise
            r.dynamic_energy_threshold = True
            
            audio_file = io.BytesIO(audio_bytes)
            with sr.AudioFile(audio_file) as source:
                # This removes the "irrational" guesses from background hum
                r.adjust_for_ambient_noise(source, duration=0.1)
                audio_data = r.record(source)
                
                # Forced English recognition
                text = r.recognize_google(audio_data, language="en-US")
                st.session_state.transcript = text
        except sr.UnknownValueError:
            st.session_state.transcript = "I couldn't hear any clear English words. Try again!"
        except Exception as e:
            st.session_state.transcript = "Error: Please check your microphone permissions."

# 3. The Text Box (Always visible if there's a transcript)
if st.session_state.transcript:
    st.subheader("Your Text:")
    # Using a text_area so you can copy/paste it easily
    st.text_area("Transcribed result:", value=st.session_state.transcript, height=150)
    
    if st.button("Clear and Start Over"):
        st.session_state.transcript = ""
        st.rerun()
