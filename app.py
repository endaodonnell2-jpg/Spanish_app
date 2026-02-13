import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

st.set_page_config(page_title="Colab Tutor", layout="centered")

st.title("🎙️ English Practice")
st.write("Click 'Start Recording', speak, and then click 'Stop'.")

# 1. The Recorder Component
# This replaces the custom JS button with a pre-built, stable version
audio = mic_recorder(
    start_prompt="🔴 Start Recording",
    stop_prompt="⏹️ Stop & Process",
    key='recorder'
)

# 2. The Processing Logic
if audio:
    # 'audio' contains a dictionary with 'bytes'
    audio_bytes = audio['bytes']
    
    with st.spinner("Transcribing..."):
        try:
            r = sr.Recognizer()
            # Use the bytes directly in an AudioFile
            audio_file = io.BytesIO(audio_bytes)
            
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                # Google Speech Recognition
                text = r.recognize_google(audio_data, language="en-US")
                
                st.success("### What I heard:")
                st.write(text)
                
                # Option to use the text for Colab Tutor tasks
                st.session_state.last_speech = text

        except sr.UnknownValueError:
            st.error("I couldn't understand the audio. Please speak clearly and try again.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# 3. Sidebar for Colab Tutor Reference
with st.sidebar:
    st.info("Logged in as: **Colab Tutor** student")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
