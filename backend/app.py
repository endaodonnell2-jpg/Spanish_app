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

# This tells Python: "Go find the value of the variable named Lucas14 in Render's settings"
client = OpenAI(api_key=os.getenv("Lucas14"))
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
    # 1. Get the absolute path of the folder where app.py lives (/backend)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Get the project root (one level up from /backend)
    root_dir = os.path.dirname(current_dir)
    
    # 3. Create the direct path to the file
    target_path = os.path.join(root_dir, "frontend", "index.html")

    # 4. Try to open it
    if os.path.exists(target_path):
        with open(target_path, "r") as f:
            return f.read()
    
    # 5. BACKUP: If the path above fails, search the whole project for index.html
    # This is the 'Nuclear Option' to ensure you never see a 500 error again
    for root, dirs, files in os.walk(root_dir):
        if "index.html" in files:
            found_path = os.path.join(root, "index.html")
            with open(found_path, "r") as f:
                return f.read()

    return f"Error: index.html not found. Checked: {target_path}"
