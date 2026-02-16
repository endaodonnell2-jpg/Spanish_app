from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from gtts import gTTS
import uuid
import os

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key="YOUR_OPENAI_KEY_HERE")

# Setup static folder for the MP3s
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    # 1. Save the incoming walkie-talkie audio
    temp_name = f"{uuid.uuid4().hex}.wav"
    with open(temp_name, "wb") as f:
        f.write(await file.read())

    # 2. Transcribe with Whisper
    with open(temp_name, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=f
        ).text

    # 3. Get Lucas11's witty response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Lucas11. Very short, witty answers. Max 10 words."},
            {"role": "user", "content": transcript}
        ]
    )
    ai_text = response.choices[0].message.content

    # 4. Generate the Spanish/English voice response
    tts_filename = f"static/{uuid.uuid4().hex}_tts.mp3"
    tts = gTTS(ai_text, lang="en") # Change lang="es" if you want Lucas to speak Spanish
    tts.save(tts_filename)

    # 5. Cleanup temp file
    os.remove(temp_name)

    # 6. Send back the URL for the frontend to play
    return JSONResponse({"tts_url": f"/{tts_filename}"})

# Optional: Serve your index.html if you want it hosted on the same URL
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r") as f:
        return f.read()
