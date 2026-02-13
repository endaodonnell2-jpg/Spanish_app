import sys
import base64
import io
import os
import uuid
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1) Patch for Python 3.13 (if applicable)
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

# 2) Setup OpenAI client
client = OpenAI(api_key=st.secrets["Lucas13"])

st.title("🎙️ Colab Tutor (Lucas11)")

# 3) Frontend: custom HTML component that RETURNS base64 audio to Python
st_bridge_js = """
<div style="display: flex; flex-direction: column; align-items: center; font-family: sans-serif;">
  <canvas id="visualizer" width="300" height="60" style="margin-bottom: 10px;"></canvas>
  <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; outline: none; transition: 0.2s;">
    <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c1.66 0 3 1.34 3 3z"/>
      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
    </svg>
  </button>
  <p id="status" style="color: #555; margin-top: 15px; font-weight: bold;">HOLD TO SPEAK</p>
</div>

<script>
  const btn = document.getElementById('mic');
  const statusEl = document.getElementById('status');
  const canvas = document.getElementById('visualizer');
  const ctx = canvas.getContext('2d');

  let mediaRecorder, audioChunks = [], audioCtx, analyser, rafId, stream;

  function drawBars(analyser) {
    const data = new Uint8Array(analyser.frequencyBinCount);
    const render = () => {
      rafId = requestAnimationFrame(render);
      analyser.getByteFrequencyData(data);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let x = 0;
      for (let i = 0; i < data.length; i++) {
        const h = data[i] / 2;
        ctx.fillStyle = '#00a884';
        ctx.fillRect(x, (60 - h) / 2, 4, h);
        x += 6;
      }
    };
    render();
  }

  async function startRecording() {
    try {
      // Request mic with user gesture
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(stream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      source.connect(analyser);
      drawBars(analyser);

      const options = { mimeType: 'audio/webm;codecs=opus' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        // Fallback without options (browser will pick)
        mediaRecorder = new MediaRecorder(stream);
      } else {
        mediaRecorder = new MediaRecorder(stream, options);
      }

      audioChunks = [];
      mediaRecorder.ondataavailable = e => {
        if (e.data && e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        try {
          const blob = new Blob(audioChunks, { type: 'audio/webm' });
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = reader.result.split(',')[1];

            // Send value back to Streamlit (this is the correct protocol)
            window.parent.postMessage({
              isStreamlitMessage: true,
              type: "streamlit:setComponentValue",
              value: base64
            }, "*");
          };
          reader.readAsDataURL(blob);
        } catch (err) {
          console.error('Finalize error', err);
          window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:setComponentValue",
            value: null
          }, "*");
        } finally {
          cleanup();
        }
      };

      mediaRecorder.start();
    } catch (err) {
      console.error('Mic error', err);
      window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: null
      }, "*");
      cleanup();
    }
  }

  function cleanup() {
    cancelAnimationFrame(rafId);
    if (audioCtx) { audioCtx.close(); audioCtx = null; }
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
  }

  btn.onmousedown = btn.ontouchstart = async (e) => {
    e.preventDefault();
    btn.style.backgroundColor = '#ff4b4b';
    statusEl.innerText = 'RECORDING...';
    startRecording();
  };

  btn.onmouseup = btn.onmouseleave = btn.ontouchend = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      btn.style.backgroundColor = '#00a884';
      statusEl.innerText = 'HOLD TO SPEAK';
    }
  };
</script>
"""

# This returns the base64 audio string FROM JS directly.
audio_b64 = components.html(st_bridge_js, height=240)

# 4) Backend: if we received audio, transcribe and respond
if audio_b64:
    with st.spinner("Processing..."):
        try:
            # Convert base64 to bytes
            audio_bytes = base64.b64decode(audio_b64)

            # Option A: Use BytesIO (file-like)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "input.webm"
            audio_file.seek(0)

            # OpenAI Whisper transcription
            # Depending on SDK version, either of these patterns works:
            # (i) simple file-like:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            ).text

            # (Alternative ii) explicit tuple with MIME:
            # transcript = client.audio.transcriptions.create(
            #     model="whisper-1",
            #     file=("input.webm", audio_bytes, "audio/webm")
            # ).text

            st.write(f"**You said:** {transcript}")

            # TTS + combine with pydub (requires ffmpeg installed)
            def play_combined(texts):
                combined = AudioSegment.empty()
                for text, lang in texts:
                    fname = f"{uuid.uuid4().hex}.mp3"
                    tts = gTTS(text, lang=lang)
                    tts.save(fname)
                    combined += AudioSegment.from_mp3(fname) + AudioSegment.silent(duration=400)
                    if os.path.exists(fname):
                        os.remove(fname)

                buf = io.BytesIO()
                combined.export(buf, format="mp3")
                st.markdown(f"### **Lucas11:** {texts[0][0]}")
                st.audio(buf.getvalue(), format="audio/mp3")

            # Echo back what we heard
            play_combined([(transcript, "en"), ("I heard you clearly.", "en")])

        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.caption("Hold the button to record, then release to transcribe.")
