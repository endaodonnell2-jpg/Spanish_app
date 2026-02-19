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

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
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
            # Cleanup files if transcription fails
            if os.path.exists(input_path): os.remove(input_path)
            if ext == "webm" and os.path.exists(wav_path): os.remove(wav_path)
            return JSONResponse({"error": "Audio transcription failed", "details": str(e)}, status_code=400)

    # GPT response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Sarah. flirty, forthcoming, sexual inneundo, max 30 words."},
            {"role": "user", "content": transcript}
        ]
    )
    ai_text = response.choices[0].message.content

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

    # Backup: search whole project
    for root, dirs, files in os.walk(root_dir):
        if "index.html" in files:
            with open(os.path.join(root, "index.html"), "r", encoding="utf-8") as f:
                return f.read()

    return HTMLResponse("Error: index.html not found.", status_code=500)

