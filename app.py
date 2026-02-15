import streamlit as st
import base64

st.set_page_config(page_title="3-Second Audio Recorder", layout="centered")
st.title("Press-to-Record (3 Seconds) Audio Demo")

st.write("Click the button to record 3 seconds of audio:")

# Placeholder for audio playback
audio_placeholder = st.empty()

# HTML + JS for recording
st.components.v1.html("""
<button id="recordBtn">Record 3 Seconds</button>
<p id="status"></p>
<audio id="audioPlayback" controls></audio>

<script>
const button = document.getElementById("recordBtn");
const status = document.getElementById("status");
const audioPlayback = document.getElementById("audioPlayback");

button.addEventListener("mousedown", async () => {
    status.innerText = "Recording...";
    
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    
    mediaRecorder.start();

    // Stop automatically after 3 seconds
    setTimeout(() => {
        mediaRecorder.stop();
        status.innerText = "Recording complete!";
    }, 3000);

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        audioPlayback.src = audioUrl;

        // Convert audio to base64
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
            const base64data = reader.result.split(",")[1];
            // Put it in a hidden input so Streamlit can read it
            const hidden = document.createElement("input");
            hidden.type = "hidden";
            hidden.id = "audio_data";
            hidden.value = base64data;
            document.body.appendChild(hidden);
        };
    };
});
</script>
""", height=250)

# Button to send audio to Streamlit
if st.button("Get Recorded Audio"):
    audio_data = st.components.v1.html("""
    <script>
    const el = document.getElementById("audio_data");
    if(el){
        window.parent.postMessage({type:"audio_data", data: el.value}, "*");
    }
    </script>
    """, height=0)

    # Use Streamlit JS listener to capture base64 (works immediately after press)
    st.info("Press the button above first to record audio. Then click here to fetch it.")

# Placeholder to show the recorded audio
if "audio_bytes" in st.session_state:
    audio_placeholder.audio(st.session_state["audio_bytes"], format="audio/wav")
