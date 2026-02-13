import streamlit as st
import streamlit.components.v1 as components
import base64
import speech_recognition as sr
import io

st.set_page_config(page_title="Colab Tutor - Voice", layout="centered")

# 1. Frontend: The Recording Button
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; background: #f0f2f6; padding: 20px; border-radius: 15px;">
    <button id="mic" style="width: 80px; height: 80px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; outline: none; transition: 0.3s;">
        <svg viewBox="0 0 24 24" width="40" height="40" fill="white"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
    </button>
    <p id="status" style="margin-top: 10px; font-family: sans-serif; color: #333;">Click and Hold to Speak</p>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    let mediaRecorder, audioChunks = [];

    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                const b64 = reader.result.split(',')[1];
                window.parent.postMessage({type: 'streamlit:set_widget_value', data: b64, key: 'audio_input'}, '*');
            };
        };
        mediaRecorder.start();
        btn.style.backgroundColor = '#ff4b4b';
        btn.style.transform = 'scale(1.1)';
        status.innerText = 'Listening...';
    };

    btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
        if(mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            btn.style.backgroundColor = '#00a884';
            btn.style.transform = 'scale(1.0)';
            status.innerText = 'Processing...';
        }
    };
</script>
"""

st.title("🎙️ Colab Tutor: Voice-to-Text")
components.html(st_bridge_js, height=180)

# 2. Backend: Catching the data
# We use a standard text_input that the JS communicates with
audio_data_b64 = st.text_input("Audio Data (Hidden)", key="audio_input", label_visibility="collapsed")

if audio_data_b64:
    try:
        # Step A: Decode
        audio_bytes = base64.b64decode(audio_data_b64)
        
        # Step B: Transcribe with relaxed settings
        r = sr.Recognizer()
        # Lowering these so it hears even quiet voices
        r.energy_threshold = 50 
        r.dynamic_energy_threshold = False 
        
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="en-US")
            
            st.success(f"**I heard:** {text}")
            
    except sr.UnknownValueError:
        st.warning("🔄 I heard sounds, but no English words. Try speaking a bit louder!")
    except Exception as e:
        st.error("⚠️ Connection error. Please refresh the page and try again.")

# Clear button to reset the bridge
if st.button("Reset Mic"):
    st.rerun()
