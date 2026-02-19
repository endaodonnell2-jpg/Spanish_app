from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
import uuid, os, tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("Lucas14"))
HOST_URL = os.getenv("HOST_URL", "http://localhost:10000")

# --- MEMORY START ---
# We initialize the memory with Sarah's persona instructions.
memory = [{"role": "system", "content": "You are Sarah, forthcoming, max 50 words."}]
# --- MEMORY END ---

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    global memory # Tell Python we want to update the memory list defined above
    
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
    with open(input_for_whisper, "rb") as f:
        try:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text
        except Exception as e:
            if os.path.exists(input_path): os.remove(input_path)
            if ext == "webm" and os.path.exists(wav_path): os.remove(wav_path)
            return JSONResponse({"error": "Audio transcription failed", "details": str(e)}, status_code=400)

    # --- MEMORY LOGIC START ---
    # 1. Add your new message to memory
    memory.append({"role": "user", "content": transcript})

    # 2. Limit memory to last 12 messages (6 exchanges) + the System prompt at index 0
    if len(memory) > 13:
        memory = [memory[0]] + memory[-12:]

    # 3. Pass the entire memory list to GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=memory
    )
    ai_text = response.choices[0].message.content

    # 4. Save Sarah's response to memory
    memory.append({"role": "assistant", "content": ai_text})
    # --- MEMORY LOGIC END ---

    # Generate TTS
    tts = gTTS(ai_text, lang="en")
    tts.save(output_path)

    # Cleanup input files
    if os.path.exists(input_path): os.remove(input_path)
    if ext == "webm" and os.path.exists(wav_path): os.remove(wav_path)

    # Return TTS URL
    return JSONResponse({"tts_url": f"{HOST_URL}/get_audio/{file_id}"})


@app.get("/get_audio/{file_id}")
async def get_audio(file_id: str):
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return JSONResponse({"error": "Audio not found"}, status_code=404)


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    target_path = os.path.join(root_dir, "frontend", "index.html")

    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()

    for root, dirs, files in os.walk(root_dir):
        if "index.html" in files:
            with open(os.path.join(root, "index.html"), "r", encoding="utf-8") as f:
                return f.read()

    return HTMLResponse("Error: index.html not found.", status_code=500)
