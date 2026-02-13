
import sys, time, io, os, uuid, re, base64
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1. SETUP & VERB LIST
client = OpenAI(api_key=st.secrets["Lucas13"])

jugar_verbs = [
    ("I speak Chinese", "Yo hablo chino"),
    ("You speak Chinese", "Tú hablas chino"),
    ("He speaks Chinese", "Él habla chino"),
    ("She speaks Chinese", "Ella habla chino"),
    ("I walk to the park", "Yo camino al parque"),
    ("You walk to the park", "Tú caminas al parque"),
    ("He walks to the park", "Él camina al parque"),
    ("She walks in the park", "Ella camina al parque"),
    ("I watch television", "Yo miro televisión"),
    ("You watch television", "Tú miras televisión"),
    ("He watches television", "Él mira televisión"),
    ("She watches television", "Ella mira televisión"),
    ("I teach Maths", "Yo enseño matemáticas"),
    ("You teach Maths", "Tú enseñas matemáticas"),
    ("He teaches Maths", "Él enseña matemáticas"),
    ("She teaches Maths", "Ella enseña matemáticas"),
]

# Initialize Session States
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'failed_steps' not in st.session_state:
    st.session_state.failed_steps = []
if 'review_mode' not in st.session_state:
    st.session_state.review_mode = False
if 'lock' not in st.session_state:
    st.session_state.lock = False

st.title("🎙️ Colab Tutor: Lucas11")
st.markdown("<style>audio { display: none !important; }</style>", unsafe_allow_html=True)

# 2. BILINGUAL AUDIO ENGINE
def speak_bilingual(text):
    parts = re.split(r'(\[ES\]|\[EN\])', text)
    combined = AudioSegment.empty()
    current_lang, current_tld = "es", "es"
    for part in parts:
        if "[ES]" in part: current_lang, current_tld = "es", "es"
        elif "[EN]" in part: current_lang, current_tld = "en", "com"
        elif part.strip():
            fname = f"temp_{uuid.uuid4().hex}.mp3"
            gTTS(part.strip(), lang=current_lang, tld=current_tld).save(fname)
            combined += AudioSegment.from_mp3(fname)
            if os.path.exists(fname): os.remove(fname)
    buf = io.BytesIO()
    combined.export(buf, format="mp3")
    st.audio(buf, format="audio/mp3", autoplay=True)
    return len(combined) / 1000.0

# 🎤 2.5 SECOND ONE-TOUCH RECORDER
def touch_start_recorder():
    return components.html("""
        <button id="recBtn" style="
            padding:15px 25px;
            font-size:18px;
            border-radius:10px;
            background-color:#ff4b4b;
            color:white;
            border:none;">
            🎤 Touch & Speak
        </button>

        <script>
        const btn = document.getElementById("recBtn");
        let mediaRecorder;
        let chunks = [];

        async function init() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = e => chunks.push(e.data);

            mediaRecorder.onstop = e => {
                const blob = new Blob(chunks, { type: "audio/webm" });
                chunks = [];

                const reader = new FileReader();
                reader.readAsDataURL(blob);
                reader.onloadend = function() {
                    window.parent.postMessage({
                        type: "streamlit:setComponentValue",
                        value: reader.result
                    }, "*");
                };
            };
        }

        init();

        btn.ontouchstart = () => {
            btn.innerText = "Recording...";
            btn.disabled = true;
            chunks = [];
            mediaRecorder.start();

            setTimeout(() => {
                mediaRecorder.stop();
                btn.innerText = "🎤 Touch & Speak";
                btn.disabled = false;
            }, 2500);
        };
        </script>
    """, height=120)

# 3. TEACHER LOGIC
queue = st.session_state.failed_steps if st.session_state.review_mode else list(range(len(jugar_verbs)))
total_in_queue = len(queue)

if st.session_state.step < total_in_queue:
    current_idx = queue[st.session_state.step]
    en_q, es_a = jugar_verbs[current_idx]
    
    mode_label = "Review Round" if st.session_state.review_mode else "Main Lesson"
    st.markdown(f"### {mode_label}: {st.session_state.step + 1} / {total_in_queue}")

    if not st.session_state.lock:
        st.info(f"How do you say: '{en_q}'?")
        
        if f"asked_{current_idx}_{st.session_state.review_mode}" not in st.session_state:
            speak_bilingual(f"[EN] How do you say: {en_q}?")
            st.session_state[f"asked_{current_idx}_{st.session_state.review_mode}"] = True

        audio_base64 = touch_start_recorder()

        if audio_base64:
            header, encoded = audio_base64.split(",", 1)
            audio_bytes = base64.b64decode(encoded)
            st.session_state.current_audio = io.BytesIO(audio_bytes)
            st.session_state.lock = True
            st.rerun()

    if st.session_state.lock and st.session_state.get('current_audio'):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=st.session_state.current_audio,
            language="es"
        ).text

        st.success(f"**You said:** {transcript}")

        prompt = f'User: "{transcript}". Correct: "{es_a}". Reply only: "[ES] ¡Correcto! [ES] {es_a}" OR "[ES] ¡Incorrecto! [EN] It\'s more like this: [ES] {es_a}"'
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}]
        ).choices[0].message.content

        if "¡Incorrecto!" in res and not st.session_state.review_mode:
            if current_idx not in st.session_state.failed_steps:
                st.session_state.failed_steps.append(current_idx)

        clean_res = res.replace('[ES]','').replace('[EN]','')
        st.markdown(f"**Lucas11:** {clean_res}")
        
        dur = speak_bilingual(res)
        
        bar = st.progress(0, text="Lucas is speaking...")
        for i in range(101):
            time.sleep(dur / 100)
            bar.progress(i)
        
        st.session_state.step += 1
        st.session_state.lock = False
        st.rerun()

else:
    if not st.session_state.review_mode and st.session_state.failed_steps:
        st.session_state.review_mode = True
        st.session_state.step = 0
        st.warning("Let's review the ones you missed!")
        speak_bilingual("[EN] Now, we'll review the wrong ones.")
        time.sleep(2)
        st.rerun()
    else:
        st.balloons()
        st.success("Lesson Complete!")
        speak_bilingual("[ES] ¡Enhorabuena! Has terminado la lección. [EN] End of conversation.")
        if st.button("Restart Lesson"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
