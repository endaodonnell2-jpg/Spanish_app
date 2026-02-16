import streamlit as st
import time

st.title("Test Flashing Warning + Beep + Vibration")

# Simulate 3-second recording
progress = st.progress(0, text="Recording...")
for i in range(101):
    time.sleep(3 / 100)
    progress.progress(i)

# Placeholder for warning
warning_placeholder = st.empty()

# Flashing warning + beep-beep + vibration
warning_placeholder.markdown(
    """
    <div style="
        color: red;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        animation: flash 0.5s alternate infinite;">
        ⏱ STOP RECORDING ⏱
    </div>
    <script>
    // Add flashing animation
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes flash {
            0% { opacity: 1; }
            100% { opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Play beep-beep-beep
    const context = new (window.AudioContext || window.webkitAudioContext)();
    for (let i=0; i<3; i++){
        const oscillator = context.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(1000, context.currentTime);
        oscillator.connect(context.destination);
        oscillator.start(context.currentTime + i*0.4);
        oscillator.stop(context.currentTime + i*0.4 + 0.2);
    }

    // Vibration
    if (navigator.vibrate){
        navigator.vibrate([200,100,200,100,200]);
    }
    </script>
    """,
    unsafe_allow_html=True
)

