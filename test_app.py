import streamlit as st
from hold_to_speak_component.hold_to_speak import HoldToSpeak

st.title("Test Hold-to-Speak Component")

hts = HoldToSpeak()
audio_b64 = hts.call()

st.write("audio_b64 type:", type(audio_b64))
