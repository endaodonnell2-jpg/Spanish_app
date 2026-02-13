import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Spanish Practice", page_icon="🎙️")

st.title("🎙️ Spanish Practice: Hold to Speak")
st.write("Hold the green button to record. Release to stop and play.")

# 1. Custom CSS for the WhatsApp Look
st.markdown("""
<style>
    .mic-container { display: flex; justify-content: center; margin: 20px; }
    #hold-mic {
        width: 100px; height: 100px; border-radius: 50%;
        background-color: #00a884; border: none; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    #hold-mic:active { background-color: #ff4b4b; transform: scale(1.1); }
    .mic-icon { fill: white; width: 50px; height: 50px; }
</style>
""", unsafe_allow_html=True)

# 2. The JavaScript Bridge
# This listens for the physical 'mousedown' and 'mouseup'
record_js = """
<div class="mic-container">
    <button id="hold-mic">
        <svg class="mic-icon" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
    </button>
</div>

<script>
    const btn = document.getElementById('hold-mic');
    let mediaRecorder;
    let audioChunks = [];

    btn.onmousedown = async () => {
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                const base64 = reader.result.split(',')[1];
                // Sending data back to Streamlit using a hidden input trick
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    data: base64,
                    key: 'audio_hex_data'
                }, '*');
            };
        };
        mediaRecorder.start();
    };

    btn.onmouseup = () => { if(mediaRecorder) mediaRecorder.stop(); };
    btn.onmouseleave = () => { if(mediaRecorder && mediaRecorder.state==='recording') mediaRecorder.stop(); };
</script>
"""

# 3. Handle the Logic in Python
# We render the HTML component
components.html(record_js, height=150)

# We use a text input (hidden via CSS or just placed at the bottom) 
# to catch the data from the JavaScript 'key'
audio_data_base64 = st.text_input("Audio Data (Hidden)", key="audio_hex_data", label_visibility="collapsed")

if audio_data_base64:
    # Decode and Play
    audio_bytes = base64.b64decode(audio_data_base64)
    st.audio(audio_bytes, format="audio/wav")
    
    # 4. The Delete/Clear Button
    if st.button("🗑️ Delete Recording & Reset"):
        # This clears the app state so the audio disappears
        st.rerun()

else:
    st.info("No recording found. Press and hold the mic to start.")
