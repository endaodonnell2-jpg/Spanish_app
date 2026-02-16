from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from gtts import gTTS
import uuid, os, tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key="Lucas14")

# We are NOT using app.mount anymore. We'll serve files directly.
# This bypasses the "Directory does not exist" crash entirely.

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    # Create a unique name for this walkie-talkie burst
    file_id = uuid.uuid4().hex
    input_path = os.path.join(tempfile.gettempdir(), f"{file_id}.wav")
    output_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")

    # 1. Save incoming audio
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # 2. Transcribe
    with open(input_path, "rb") as f:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text

    # 3. Lucas11 Logic
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are Lucas11. Witty, max 10 words."},
                  {"role": "user", "content": transcript}]
    )
    ai_text = response.choices[0].message.content

    # 4. Generate Voice to the temp folder
    tts = gTTS(ai_text, lang="en")
    tts.save(output_path)

    # 5. Send back a link that points to our new download route
    return JSONResponse({"tts_url": f"/get_audio/{file_id}"})

@app.get("/get_audio/{file_id}")
async def get_audio(file_id: str):
    # This serves the file directly from the temp folder
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")
    return FileResponse(file_path)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Looks for index.html in the same folder as app.py
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "index.html"), "r") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Render's current directory is /opt/render/project/src/
    # Your index is at /opt/render/project/src/frontend/index.html
    
    # This reaches out of the 'backend' folder and into the 'frontend' folder
    dir_path = os.path.dirname(os.path.realpath(__file__)) # This is /backend
    parent_path = os.path.dirname(dir_path) # This is project root
    index_path = os.path.join(parent_path, "frontend", "index.html")

    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    else:
        # If it still fails, this debug message will tell us EXACTLY where Render put your files
        return f"File Not Found. I looked here: {index_path}. Current folder is: {os.getcwd()}"
