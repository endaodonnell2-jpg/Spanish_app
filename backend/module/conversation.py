from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
import uuid, os, tempfile

# OpenAI client
client = OpenAI(api_key=os.getenv("Lucas14"))
HOST_URL = os.getenv("HOST_URL", "http://localhost:10000")

def register_conversation_routes(app: FastAPI, user_memories: dict):

    # --- UI WITH HOME BUTTON ---
    @app.get("/conversation", response_class=HTMLResponse)
    async def conversation_page():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: sans-serif; text-align: center; padding-top: 50px; background: #f4f7f6; }
                .home-btn { position: absolute; top: 20px; left: 20px; text-decoration: none; color: #7f8c8d; font-weight: bold; border: 1px solid #ccc; padding: 5px 10px; border-radius: 8px; }
                #record-btn { width: 150px; height: 150px; border-radius: 50%; border: none; background: #e74c3c; color: white; font-weight: bold; cursor: pointer; font-size: 16px; }
                #record-btn:active { background: #c0392b; }
                #status { margin-top: 20px; font-weight: bold; color: #2c3e50; }
            </style>
        </head>
        <body>
            <a href="/" class="home-btn">← HOME</a>
            <h1>Talk to Sarah</h1>
            <button id="record-btn">HOLD TO TALK</button>
            <div id="status">Ready</div>

            <script>
                let mediaRecorder;
                let audioChunks = [];
                const btn = document.getElementById('record-btn');
                const status = document.getElementById('status');

                btn.onmousedown = async () => {
                    audioChunks = [];
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();
                    status.innerText = "Listening...";
                    
                    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {
                        status.innerText = "Sarah is thinking...";
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const formData = new FormData();
                        formData.append('file', audioBlob, 'audio.webm');

                        const response = await fetch('/process_audio', { method: 'POST', body: formData });
                        const data = await response.json();
                        if (data.tts_url) {
                            const audio = new Audio(data.tts_url);
                            audio.play();
                            status.innerText = "Sarah is speaking...";
                            audio.onended = () => status.innerText = "Ready";
                        }
                    };
                };

                btn.onmouseup = () => {
                    if (mediaRecorder) {
                        mediaRecorder.stop();
                        status.innerText = "Processing...";
                    }
                };
            </script>
        </body>
        </html>
        """

    @app.post("/process_audio")
    async def process_audio(request: Request, file: UploadFile = File(...)):

        session_id = request.cookies.get("lucas_session_id")

        # Create memory for new session
        if session_id not in user_memories:
            user_memories[session_id] = [
                {"role": "system", "content": "You are Sarah, forthcoming, max 50 words."}
            ]

        memory = user_memories[session_id]

        file_id = uuid.uuid4().hex
        ext = file.filename.split(".")[-1].lower()
        input_path = os.path.join(tempfile.gettempdir(), f"{file_id}.{ext}")
        output_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")

        # Save uploaded file
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Convert WebM/Opus to WAV for Whisper
        if ext == "webm":
            wav_path = os.path.join(tempfile.gettempdir(), f"{file_id}.wav")
            AudioSegment.from_file(input_path, format="webm").export(wav_path, format="wav")
            input_for_whisper = wav_path
        else:
            input_for_whisper = input_path

        # Transcribe audio
        try:
            with open(input_for_whisper, "rb") as f:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text
        except Exception as e:
            if os.path.exists(input_path): os.remove(input_path)
            if ext == "webm" and os.path.exists(input_for_whisper): os.remove(input_for_whisper)
            return JSONResponse({"error": "Audio transcription failed", "details": str(e)}, status_code=400)

        # --- MEMORY LOGIC ---
        memory.append({"role": "user", "content": transcript})

        if len(memory) > 13:
            user_memories[session_id] = [memory[0]] + memory[-12:]
            memory = user_memories[session_id]

        response = client.chat.completions.create(model="gpt-4o", messages=memory)
        ai_text = response.choices[0].message.content
        memory.append({"role": "assistant", "content": ai_text})
        # --- END MEMORY LOGIC ---

        # Generate TTS
        tts = gTTS(ai_text, lang="en")
        tts.save(output_path)

        # Cleanup input files
        if os.path.exists(input_path): os.remove(input_path)
        if ext == "webm" and os.path.exists(input_for_whisper): os.remove(input_for_whisper)

        # Return TTS URL
        return JSONResponse({"tts_url": f"{HOST_URL}/get_audio/{file_id}"})

    # --- AUDIO RETRIEVAL ---
    @app.get("/get_audio/{file_id}")
    async def get_audio(file_id: str):
        file_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/mpeg")
        return JSONResponse({"error": "Audio not found"}, status_code=404)
