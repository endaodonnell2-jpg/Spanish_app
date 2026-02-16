import streamlit as st
import time

# Placeholder for flashing warning
warning_placeholder = st.empty()

progress = st.progress(0, text="Recording...")

for i in range(101):
    time.sleep(3 / 100)  # total 3 seconds

    # Update progress bar
    progress.progress(i)

# After 3 seconds: show flashing red warning + beep-beep + vibration
warning_placeholder.markdown(
    """
    <div id="flash-warning" style="
        color: red;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        animation: flash 0.5s alternate infinite;">
        ⏱ STOP RECORDING ⏱
    </div>
    <script>
    // Flashing effect
    var style = document.createElement('style');
    style.innerHTML = `
        @keyframes flash {
            0% { opacity: 1; }
            100% { opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Beep-beep-beep sequence
    function beep(duration, frequency, times) {
        var context = new (window.AudioContext || window.webkitAudioContext)();
        for (let i=0; i<times; i++) {
            let oscillator = context.createOscillator();
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(frequency, context.currentTime);
            oscillator.connect(context.destination);
            oscillator.start(context.currentTime + i * 0.4);
            oscillator.stop(context.currentTime + i * 0.4 + duration/1000);
        }
    }
    beep(200, 1000, 3); // 3 beeps of 200ms at 1000Hz

    // Phone vibration
    if (navigator.vibrate) {
        navigator.vibrate([200, 100, 200, 100, 200]); // 3 short pulses
    }
    </script>
    """,
    unsafe_allow_html=True
)

