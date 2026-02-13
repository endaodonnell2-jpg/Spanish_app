import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import io
import uuid
from gtts import gTTS
from pydub import AudioSegment

def play_tts_with_waveform_st(texts, pause_ms=400, title="Colab Tutor"):
    # 1. GENERATE & MERGE AUDIO (Your exact Pydub logic)
    combined = AudioSegment.empty()
    display_texts = []

    for text, lang in texts:
        fname = f"temp_{uuid.uuid4().hex}.mp3"
        tld = "es" if lang == "es" else "com"
        gTTS(text, lang=lang, tld=tld).save(fname)
        
        combined += AudioSegment.from_mp3(fname) + AudioSegment.silent(duration=pause_ms)
        display_texts.append(text)
        os.remove(fname)

    # Export to bytes for the web bridge
    buffer = io.BytesIO()
    combined.export(buffer, format="mp3")
    audio_b64 = base64.b64encode(buffer.getvalue()).decode()

    # 2. RENDER THE UI (Your exact HTML/Canvas logic)
    text_lines = "".join(f"<div style='margin-bottom:5px;'>{t}</div>" for t in display_texts)
    
    html_code = f"""
    <div style="background:white; border:3px solid #2ecc71; border-radius:20px; padding:20px; font-family:sans-serif; box-shadow:0 4px 15px rgba(0,0,0,.1); text-align:center;">
        <h2 style="color:#2ecc71; margin-top:0;">{title}</h2>
        <canvas id="viz" width="300" height="80" style="width:100%; height:80px; background:#fafafa; border-radius:10px; margin-bottom:15px;"></canvas>
        <div style="background:#f9f9f9; border-radius:10px; padding:12px; text-align:left; font-size:14px; color:#333;">
            <div style="color:#27ae60; font-size:11px; font-weight:bold; margin-bottom:5px;">LUCAS11 SAYS:</div>
            {text_lines}
        </div>
        <button id="play" style="margin-top:15px; width:100%; padding:14px; background:#2ecc71; color:white; border:none; border-radius:50px; font-weight:bold; cursor:pointer;">PLAY RESPONSE</button>
    </div>

    <script>
    let audioContext, analyser, dataArray, animId;
    const canvas = document.getElementById("viz");
    const ctx = canvas.getContext("2d");
    const btn = document.getElementById("play");

    function drawWave(color) {{
        analyser.getByteTimeDomainData(dataArray);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 3; ctx.strokeStyle = color; ctx.beginPath();
        let sliceWidth = canvas.width / dataArray.length;
        let x = 0;
        for (let i = 0; i < dataArray.length; i++) {{
            let v = dataArray[i] / 128.0;
            let y = v * canvas.height / 2;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            x += sliceWidth;
        }}
        ctx.lineTo(canvas.width, canvas.height / 2); ctx.stroke();
        animId = requestAnimationFrame(() => drawWave(color));
    }}

    btn.onclick = async () => {{
        if (!audioContext) {{
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 1024;
            dataArray = new Uint8Array(analyser.frequencyBinCount);
        }}
        if (audioContext.state === "suspended") await audioContext.resume();

        const audio = new Audio("data:audio/mp3;base64,{audio_b64}");
        const source = audioContext.createMediaElementSource(audio);
        source.connect(analyser); analyser.connect(audioContext.destination);

        drawWave("#e74c3c");
        btn.style.background = "#e74c3c";
        audio.play();
        audio.onended = () => {{
            cancelAnimationFrame(animId);
            btn.style.background = "#2ecc71";
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.beginPath(); ctx.moveTo(0, 40); ctx.lineTo(300, 40); ctx.stroke();
        }};
    }};
    </script>
    """
    components.html(html_code, height=320)

# --- TEST IT ---
if st.button("Simulate Lucas11 Response"):
    test_data = [
        ("Hello! I am your Colab Tutor.", "en"),
        ("¡Hola! Soy tu tutor de Colab.", "es")
    ]
    play_tts_with_waveform_st(test_data)
