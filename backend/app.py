from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from gtts import gTTS
import uuid, os, tempfile, traceback

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

    try:
        # 1️⃣ Save uploaded audio
        with open(input_path, "wb") as f:
            f.write(await file.read())
        print(f"Saved input audio at {input_path}")

        # 2️⃣ Transcribe
        with open(input_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text
        print(f"Transcript: {transcript}")

        # 3️⃣ GPT response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Lucas11. Witty, max 10 words."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = response.choices[0].message.content
        print(f"AI Response: {ai_text}")

        # 4️⃣ Generate TTS
        tts = gTTS(ai_text, lang="en")
        tts.save(output_path)
        print(f"TTS saved at {output_path}")

        # 5️⃣ Cleanup input file
        try:
            os.remove(input_path)
            print(f"Deleted input file {input_path}")
        except Exception as e:
            print(f"Failed to delete input file: {e}")

        return JSONResponse({"tts_url": f"{HOST_URL}/get_audio/{file_id}"})

    except Exception as e:
        # Catch any error and print stack trace for debugging
        print("Error in /process_audio:", e)
        traceback.print_exc()
        return JSONResponse(
            {"error": "Failed to process audio", "details": str(e)},
            status_code=500
        )


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
