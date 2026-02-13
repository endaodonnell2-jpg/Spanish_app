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

# 1. SETUP & NEW VERB LIST
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

# Initialize Session States using your settings preference
if 'step' not in st.session_state:
    st.session_state.step = 0
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
        if "[ES]" in part:
            current_lang, current_tld = "es", "es"
        elif "[EN]" in part:
            current_lang, current_tld = "en", "com"
        elif part.strip():
            fname = f"temp_{uuid.uuid4().hex}.mp3"
            tts = gTTS(part.strip(), lang=current_lang, tld=current_tld)
            tts.save(fname)
            combined += AudioSegment.from_mp3(fname)
            if os.path.exists(fname): os.remove(fname)

    buf = io.BytesIO()
    combined.export(buf, format="mp3")
    duration = len(combined) / 1000.0
    st.audio(buf, format="audio/mp3", autoplay=True)
    return duration

# 3. TEACHER LOGIC
if st.session_state.step < len(jugar_verbs):
    en_q, es_a = jugar_verbs[st.session_state.step]
    
    if not st.session_state.lock:
        st.subheader(f"Lesson Progress: {st.session_state.step + 1} / {len(jugar_verbs)}")
        st.info(f"How do you say: '{en_q}'?")
        
        # Fresh key for every step to avoid the "Error has occurred" bug
        audio_input = st.audio_input("Answer in Spanish", key=f"mic_step_{st.session_state.step}")
        
        if audio_input:
            st.session_state.lock = True
            st.session_state.current_audio = audio_input
            st.rerun()

    if st.session_state.lock and st.session_state.get('current_audio'):
        # Transcription (Whisper)
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=st.session_state.current_audio, language="es"
        ).text
        
        # Validation Prompt
        prompt = f"""User said: "{transcript}". Correct answer is: "{es_a}". 
        If correct, reply ONLY: [ES] ¡Correcto! [ES] {es_a}
        If incorrect, reply ONLY: [ES] ¡Incorrecto! [EN] Afraid not, it's more like this: [ES] {es_a}"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a precise Spanish tutor. Follow tags strictly."} ,
                      {"role": "user", "content": prompt}]
        ).choices[0].message.content

        st.write(f"**You:** {transcript}")
        st.write(f"**Lucas11:** {response.replace('[ES]', '').replace('[EN]', '')}")
        
        # Play audio and hold the lock while speaking
        dur = speak_bilingual(response)
        
        bar = st.progress(0, text="Lucas11 is speaking...")
        steps = 20
        for i in range(steps + 1):
            time.sleep(dur / steps)
            bar.progress(i / steps)
        
        # Auto-advance to the next verb
        st.session_state.step += 1
        st.session_state.lock = False
        st.rerun()

else:
    st.balloons()
    st.success("¡Enhorabuena! Has terminado la lección.")
    speak_bilingual("[ES] ¡Enhorabuena! Has terminado la lección. [EN] End of conversation.")
    if st.button("Restart Lesson"):
        st.session_state.step = 0
        st.rerun()
