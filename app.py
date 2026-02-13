import streamlit as st
import streamlit.components.v1 as components
import base64
import speech_recognition as sr
import io

st.set_page_config(page_title="Colab Tutor", layout="centered")

# Initialize the text in session state
if "text_output" not in st.session_state:
    st.session_state.text_output = ""

st.title("🎙️ English Voice Input")

# 1. The Frontend - Forced Streamlit Update
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; border: 2px solid #00a884; padding: 20px; border-radius: 10px;">
    <button id="mic" style="width: 90px; height: 90px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; outline: none;">
        <svg viewBox="0 0 24 24" width="45" height="45" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="margin-top: 10px; font-weight: bold; color: #555;">HOLD BUTTON TO SPEAK</p>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    let mediaRecorder, audioChunks = [];

    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                const blob = new Blob(audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.readAsDataURL(blob);
                reader.onloadend = () => {
                    const b64 = reader.result.split(',')[1];
                    // FORCE UPDATE: Find the hidden text area and inject data
                    const textAreas = window.parent.document.querySelectorAll('textarea');
                    for (let ta of textAreas) {
                        if (ta.ariaLabel === "hidden_input") {
                            ta.value = b64;
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                    }
                };
            };
            mediaRecorder.start();
            btn.style.backgroundColor = '#ff4b4b';
            status.innerText = 'LISTENING...';
        } catch (err) {
            status.innerText = 'MIC ERROR: ' + err.message;
        }
    };

    btn.onmouseup = btn.ontouchend = () => {
        if(mediaRecorder?.state === 'recording') {
            mediaRecorder.stop();
            btn.style.backgroundColor = '#00a884';
            status.innerText = 'PROCESSING...';
        }
    };
</script>
"""

components.html(st_bridge_js, height=200)

# 2. The Python "Listener" (Hidden Area)
# We use a text_area because it handles long Base64 strings better than a text_input
input_data = st.text_area("hidden_input", label_visibility="collapsed", key="voice_data", help="Do not type here")

if input_data:
    try:
        audio_bytes = base64.b64decode(input_data)
        r = sr.Recognizer()
        
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            # Short calibration to ensure we hear the voice over noise
            r.adjust_for_ambient_noise(source, duration=0.1)
            audio = r.record(source)
            text = r.recognize_google(audio, language="en-US")
            st.session_state.text_output = text
            
    except Exception:
        st.session_state.text_output = "I couldn't catch that. Please try again!"

# 3. Final Output
if st.session_state.text_output:
    st.markdown("### Result:")
    st.info(st.session_state.text_output)
    
    if st.button("Clear Text"):
        st.session_state.text_output = ""
        st.rerun()
