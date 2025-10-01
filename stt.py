import os
import requests
import time

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ASSEMBLYAI_BASE_URL = "https://api.assemblyai.com/v2"

HEADERS = {
    "authorization": ASSEMBLYAI_API_KEY
}

def upload_audio(file_path: str) -> str:
    """Uploads an audio file to AssemblyAI and returns the uploaded URL."""
    with open(file_path, "rb") as f:
        response = requests.post(f"{ASSEMBLYAI_BASE_URL}/upload", headers=HEADERS, files={"file": f})
    response.raise_for_status()
    return response.json()["upload_url"]

def transcribe_audio(file_path: str, auto_chapters=False) -> str:
    """
    Uploads audio and gets the transcription.
    Returns the transcribed text.
    """
    audio_url = upload_audio(file_path)
    
    payload = {
        "audio_url": audio_url,
        "auto_chapters": auto_chapters
    }
    response = requests.post(f"{ASSEMBLYAI_BASE_URL}/transcript", json=payload, headers=HEADERS)
    response.raise_for_status()
    transcript_id = response.json()["id"]

    # Poll until transcription is complete
    while True:
        poll = requests.get(f"{ASSEMBLYAI_BASE_URL}/transcript/{transcript_id}", headers=HEADERS)
        poll.raise_for_status()
        status = poll.json()["status"]
        if status == "completed":
            return poll.json()["text"]
        elif status == "failed":
            raise Exception("Transcription failed.")
        time.sleep(1)  # Wait a bit before polling again
