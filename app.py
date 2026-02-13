import streamlit as st
import streamlit.components.v1 as components
import base64
import speech_recognition as sr
import io

st.set_page_config(page_title="Colab Tutor", layout="centered")

st.title("🎙️ English Practice")

# 1. THE FRONTEND: Pure Hold-to-Speak (No Changes to the Feel)
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center;">
    <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; outline: none;">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="margin-top: 15px; font-family: sans-serif; font-weight: bold; color: #555;">HOLD TO SPEAK</p>
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
                // Direct update to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    data: b64,
                    key: 'raw_audio_b64'
                }, '*');
            };
        };
        mediaRecorder.start();
        btn.style.backgroundColor = '#ff4b4b';
        status.innerText = 'LISTENING...';
    };

    btn.onmouseup = btn.ontouchend = btn.onmouseleave = () => {
        if(mediaRecorder?.state === 'recording') {
            mediaRecorder.stop();
            btn.style.backgroundColor = '#00a884';
            status.innerText = 'TRANSCRIBING...';
        }
    };
</script>
"""

components.html(st_bridge_js, height=180)

# 2. THE BACKEND: Force Transcription
# This catches the 'raw_audio_b64' from the JS
audio_input = st.text_input("hidden", key="raw_audio_b64", label_visibility="collapsed")

if audio_input:
    with st.spinner("Decoding..."):
        try:
            # Step 1: Decode the base64 string
            audio_bytes = base64.b64decode(audio_input)
            
            # Step 2: Initialize recognizer with ZERO filtering (Let it hear everything)
            r = sr.Recognizer()
            
            # Step 3: Convert bytes to a format the Recognizer understands
            audio_file = io.BytesIO(audio_bytes)
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                
                # Step 4: Hit Google's API hard
                text = r.recognize_google(audio_data, language="en-US")
                
                # Show the result clearly
                st.markdown("---")
                st.subheader("Transcription:")
                st.success(text)
                
        except sr.UnknownValueError:
            st.error("Could not understand audio. Try speaking closer to the mic.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Clear button
if st.button("Clear Screen"):
    st.rerun()
