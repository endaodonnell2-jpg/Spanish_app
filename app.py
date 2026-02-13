import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Spanish App")

st.markdown("""
    <style>
    .stApp { background-color: #111; color: white; }
    /* The WhatsApp Mic Button */
    .mic-btn {
        width: 120px; height: 120px; border-radius: 50%;
        background-color: #00a884; border: none; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        margin: auto; touch-action: none; outline: none;
    }
    .mic-btn:active { background-color: #ff4b4b; transform: scale(0.95); }
    .status { text-align: center; margin-top: 10px; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

# The JavaScript handles the HOLD logic and the AUTO-DELETE after play
hold_to_record_js = """
<div id="container">
    <button class="mic-btn" id="mic">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <div class="status" id="status">HOLD TO SPEAK</div>
    <div id="player-container" style="margin-top:20px; text-align:center;"></div>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    const playerContainer = document.getElementById('player-container');
    let mediaRecorder;
    let audioChunks = [];

    // START RECORDING ON PRESS
    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        playerContainer.innerHTML = ''; // Clear previous player
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            // UI Update
            status.innerText = "PLAYING BACK...";
            audio.play();
            
            // THE AUTO-DELETE LOGIC
            audio.onended = () => {
                status.innerText = "HOLD TO SPEAK";
                URL.revokeObjectURL(audioUrl); // Deletes from browser memory
                playerContainer.innerHTML = ''; // Removes player from UI
            };
        };
        
        mediaRecorder.start();
        status.innerText = "RECORDING...";
    };

    // STOP RECORDING ON RELEASE
    btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
    };
</script>

<style>
    .mic-btn { width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; margin: auto; }
    .mic-btn:active { background-color: #ff4b4b; }
    .status { color: #aaa; text-align: center; margin-top: 10px; font-family: sans-serif; font-weight: bold; }
</style>
"""

components.html(hold_to_record_js, height=250)
    
    if st.button("🗑️ Delete & Clear"):
        st.rerun()
else:
    st.info("Press and hold the button above.")
