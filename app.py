import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="WhatsApp Style Spanish App")

st.title("🎙️ Spanish Practice: Hold to Speak")
st.write("Hold the button to record your Spanish. Release to hear it back.")

# 1. This CSS creates the look and the "Pressing" effect
st.markdown("""
<style>
    .mic-container { display: flex; justify-content: center; margin: 30px; }
    #hold-mic {
        width: 100px; height: 100px; border-radius: 50%;
        background-color: #00a884; border: none; cursor: pointer;
        outline: none; transition: transform 0.1s;
        display: flex; align-items: center; justify-content: center;
    }
    #hold-mic:active {
        background-color: #ff4b4b;
        transform: scale(1.1);
    }
    .mic-icon { fill: white; width: 50px; height: 50px; }
</style>
""", unsafe_allow_html=True)

# 2. The JavaScript Bridge
# This handles the actual 'Hold' and 'Release' logic
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
                // Send the base64 audio string to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    data: reader.result.split(',')[1],
                    key: 'audio_result'
                }, '*');
            };
        };
        mediaRecorder.start();
    };

    btn.onmouseup = () => {
        if (mediaRecorder) mediaRecorder.stop();
    };

    // If mouse leaves the button area, stop recording too
    btn.onmouseleave = () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop();
    };
</script>
"""

# 3. Handle the Data in Streamlit
# We use a unique key 'audio_result' to catch the JS output
# Note: components.html height must be enough for the button
audio_base64 = components.html(record_js, height=200)

# Check if we have received a recording
# Because of the way Streamlit works, we use the chat_input or a state trick
# to catch the 'audio_result' from the JS message.
if st.button("🗑️ Clear Recording"):
    st.rerun()

# To catch the value from JS, we need to check the query params or a session state
# This part "listens" for the 'audio_result' key we sent from JavaScript
if st.get_query_params().get("audio_result"):
    audio_data = base64.b64decode(st.get_query_params()["audio_result"][0])
    st.audio(audio_data, format="audio/wav")
