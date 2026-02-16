import streamlit as st
from openai import OpenAI
from gtts import gTTS
import uuid
import os

# 1. Setup
st.title("Colab Tutor")
client = OpenAI(api_key="Lucas14") # Make sure your real key is here!

# Ensure static folder exists
if not os.path.exists("static"):
    os.makedirs("static")

# 2. Interface
audio_input = st.audio_input("Say something to Lucas11")

if audio_input:
    # Save the audio temporarily
    temp_name = f"{uuid.uuid4().hex}.wav"
    with open(temp_name, "wb") as f:
        f.write(audio_input.getvalue())

    # 3. Whisper Transcription
    with open(temp_name, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=f
        ).text
    
    st.write(f"**You said:** {transcript}")

    # 4. GPT Response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Lucas11. Very short, witty answers. Max 10 words."},
            {"role": "user", "content": transcript}
        ]
    )
    ai_text = response.choices[0].message.content
    st.write(f"**Lucas11:** {ai_text}")

    # 5. TTS Generation
    tts_filename = f"static/{uuid.uuid4().hex}_tts.mp3"
    tts = gTTS(ai_text, lang="en")
    tts.save(tts_filename)

    # Play the response
    st.audio(tts_filename, format="audio/mp3", autoplay=True)

    # Cleanup
    os.remove(temp_name)

