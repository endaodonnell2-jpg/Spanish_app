import sys, time, io, os, uuid, re
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    sys.modules["audioop"] = audioop

import streamlit as st
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment

# 1. SETUP & THE 16 VERBS
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

if 'step' not in st.session_state: st.session_state.step = 0
if 'failed_steps' not in st.session_state: st.session_state.failed_steps = []
if 'review_mode' not in st.session_state: st.session_state.review_mode = False
if 'lock' not in st.session_state: st.session_state.lock = False

st.title("🎙️ Colab Tutor: Lucas11")

# CSS: Big Button & Hide Players
st.markdown("""
    <style>
    audio { display: none !important; }
    button[data-testid="stAudioInputRecordButton"] {
        transform: scale(2.0) !important;
        margin: 30px auto !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. AUDIO ENGINE
def speak_bilingual(text):
    parts = re.split(r'(\[ES\]|\[EN\])', text)
    combined = AudioSegment.empty()
    curr_l, curr_t = "es", "es"
    for p in parts:
        if "[ES]" in p: curr_l, curr_t = "es", "es"
        elif "[EN]" in p: curr_l, curr_t = "en", "com"
        elif p.strip():
            f = f"t_{uuid.uuid4().hex}.mp3"
            gTTS(p.strip(), lang=curr_l, tld=curr_t).save(f)
            combined += AudioSegment.from_mp3(f)
            if os.path.exists(f): os.remove(f)
    buf = io.BytesIO()
    combined.export(buf, format="mp3")
    st.audio(buf, format="audio/mp3", autoplay=True)
    return len(combined) / 1000.0

# 3. TEACHER LOGIC
q_list = st.session_state.failed_steps if st.session_state.review_mode else list(range(len(jugar_verbs)))
total_q = len(q_list)

if st.session_state.step < total_q:
    idx = q_list[st.session_state.step]
    en_q, es_a = jugar_verbs[idx]
    
    st.subheader(f"{'Review Round' if st.session_state.review_mode else 'Main Lesson'}: {st.session_state.step + 1} / {total_q}")

    if not st.session_state.lock:
        st.warning(f"FAST! 3s LIMIT! How do you say: '{en_q}'?")
        
        if f"q_{idx}_{st.session_state.review_mode}" not in st.session_state:
            speak_bilingual(f"[EN] How do you say: {en_q}?")
            st.session_state[f"q_{idx}_{st.session_state.review_mode}"] = True

        audio_in = st.audio_input("Press, speak, then press Stop immediately!", key=f"mic_{idx}_{st.session_state.review_mode}")
        
        if audio_in:
            # THE SAFETY SNIP:
            # We take the audio and cut it at exactly 3 seconds (3000ms)
            raw_audio = AudioSegment.from_file(audio_in)
            trimmed_audio = raw_audio[:3000] 
            
            buf = io.BytesIO()
            trimmed_audio.export(buf, format="wav")
            st.session_state.temp_audio = buf
            st.session_state.lock = True
            st.rerun()

    if st.session_state.lock and st.session_state.get('temp_audio'):
        trans = client.audio.transcriptions.create(model="whisper-1", file=st.session_state.temp_audio, language="es").text
        st.success(f"**You said:** {trans}")

        prompt = f'User: "{trans}". Target: "{es_a}". Reply: "[ES] ¡Correcto! [ES] {es_a}" OR "[ES] ¡Incorrecto! [EN] It\'s more like this: [ES] {es_a}"'
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":prompt}]).choices[0].message.content

        if "¡Incorrecto!" in res and not st.session_state.review_mode:
            if idx not in st.session_state.failed_steps: st.session_state.failed_steps.append(idx)

        st.markdown(f"**Lucas11:** {res.replace('[ES]','').replace('[EN]','')}")
        dur = speak_bilingual(res)
        
        bar = st.progress(0, text="Lucas is speaking...")
        for i in range(101):
            time.sleep(dur / 100); bar.progress(i)
        
        st.session_state.step += 1
        st.session_state.lock = False
        st.rerun()
else:
    # Review Logic
    if not st.session_state.review_mode and st.session_state.failed_steps:
        st.session_state.review_mode = True
        st.session_state.step = 0
        speak_bilingual("[EN] Time to review the ones you missed!")
        st.rerun()
    else:
        st.balloons()
        speak_bilingual("[ES] ¡Enhorabuena! Has terminado la lección.")
        if st.button("Restart"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
