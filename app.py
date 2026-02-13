import streamlit as st
import streamlit.components.v1 as components
#
st.set_page_config(page_title="Spanish App", layout="centered")

# The entire logic is now inside this block to avoid Python Indent Errors
st.title("🎙️ Spanish: Hold to Speak")

# This JS handles: 1. HOLD to record, 2. RELEASE to stop, 3. PLAY, 4. AUTO-DELETE
whatsapp_style_js = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; font-family: sans-serif;">
    <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; outline: none; display: flex; align-items: center; justify-content: center; transition: background 0.2s;">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="color: #555; margin-top: 15px; font-weight: bold; letter-spacing: 1px;">HOLD TO RECORD</p>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    let mediaRecorder;
    let audioChunks = [];

    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        btn.style.backgroundColor = '#ff4b4b';
        status.innerText = 'RECORDING...';
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                status.innerText = 'PLAYING BACK...';
                audio.play();
                
                // AUTO-DELETE: Once finished, clear everything
                audio.onended = () => {
                    status.innerText = 'HOLD TO RECORD';
                    btn.style.backgroundColor = '#00a884';
                    URL.revokeObjectURL(audioUrl); // Wipes file from memory
                };
            };
            mediaRecorder.start();
        } catch (err) {
            status.innerText = 'MIC ERROR: ALLOW ACCESS';
        }
    };

    btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
    };
</script>
"""

components.html(whatsapp_style_js, height=300)
