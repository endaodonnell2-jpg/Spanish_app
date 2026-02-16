from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from gtts import gTTS
import uuid, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key="YOUR_OPENAI_KEY_HERE")

# --- THE FIX ---
# This "try" block prevents the Errno 17 crash AND the "Directory does not exist" crash
static_dir = os.path.join(os.path.dirname(__file__), "static")
try:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
except Exception:
    pass 

app.mount("/static", StaticFiles(directory=static_dir), name="static")
# ----------------

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    temp_name = f"{uuid.uuid4().hex}.wav"
    with open(temp_name, "wb") as f:
        f.write(await file.read())

    with open(temp_name, "rb") as f:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are Lucas11. Witty, max 10 words."},
                  {"role": "user", "content": transcript}]
    )
    ai_text = response.choices[0].message.content

    tts_filename = os.path.join(static_dir, f"{uuid.uuid4().hex}_tts.mp3")
    gTTS(ai_text, lang="en").save(tts_filename)

    os.remove(temp_name)
    
    # Return just the relative path for the frontend
    return JSONResponse({"tts_url": f"/static/{os.path.basename(tts_filename)}"})

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(index_path, "r") as f:
        return f.read()
