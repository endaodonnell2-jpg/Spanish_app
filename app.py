import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Spanish App", layout="centered")

st.title("🎙️ Spanish: Hold to Speak")

whatsapp_visualizer_js = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif;">
    <canvas id="visualizer" width="300" height="60" style="margin-bottom: 20px;"></canvas>

    <button id="mic" style="width: 100px; height: 100px; border-radius: 50%; background-color: #00a884; border: none; cursor: pointer; outline: none; display: flex; align-items: center; justify-content: center; transition: background 0.2s; z-index: 10;">
        <svg viewBox="0 0 24 24" width="50" height="50" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
    </button>
    <p id="status" style="color: #555; margin-top: 15px; font-weight: bold; letter-spacing: 1px;">HOLD TO RECORD</p>
</div>

<script>
    const btn = document.getElementById('mic');
    const status = document.getElementById('status');
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    
    let audioCtx;
    let analyser;
    let mediaRecorder;
    let audioChunks = [];
    let animationId;

    function drawVisualizer() {
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const draw = () => {
            animationId = requestAnimationFrame(draw);
            analyser.getByteFrequencyData(dataArray);

            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
            const barWidth = (canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            for(let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                canvasCtx.fillStyle = '#00a884'; // WhatsApp Green
                // Draw bars centered vertically
                canvasCtx.fillRect(x, (canvas.height - barHeight) / 2, barWidth, barHeight);
                x += barWidth + 1;
            }
        };
        draw();
    }

    btn.onmousedown = btn.ontouchstart = async (e) => {
        e.preventDefault();
        audioChunks = [];
        btn.style.backgroundColor = '#ff4b4b';
        status.innerText = 'RECORDING...';
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Set up Visualizer
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioCtx.createMediaStreamSource(stream);
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 64; // Small number = wider bars
            source.connect(analyser);
            drawVisualizer();

            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
            
            mediaRecorder.onstop = () => {
                cancelAnimationFrame(animationId);
                canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
                if (audioCtx) audioCtx.close();

                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                status.innerText = 'PLAYING BACK...';
                audio.play();
                
                audio.onended = () => {
                    status.innerText = 'HOLD TO RECORD';
                    btn.style.backgroundColor = '#00a884';
                    URL.revokeObjectURL(audioUrl);
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

components.html(whatsapp_visualizer_js, height=350)
