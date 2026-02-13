import streamlit.components.v1 as components
import os

class HoldToSpeak:
    def __init__(self):
        # Path to the frontend build folder
        self._component_func = components.declare_component(
            "hold_to_speak",
            path=os.path.join(os.path.dirname(__file__), "frontend/build")
        )

    def call(self):
        """
        Renders the component and returns the recorded audio as base64 string.
        """
        return self._component_func()

