import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TTS_API_KEY")
print(API_KEY)

# VOICE_ID = "lByq3Bo4rauXrULoiG8p"  # Your cloned Jarvis-style voice
VOICE_ID = "MAPRQTO21cH868qoSTp1"

def generate_tts_audio(text, model="eleven_turbo_v2"):
    """
    Generates TTS audio using Eleven Labs and returns raw audio content.

    Args:
        text (str): Text to convert to speech.
        model (str): Model to use ("eleven_turbo_v2" for low-latency, "eleven_multilingual_v2" for HQ).

    Returns:
        bytes: Raw MP3 audio data if successful, None if failed.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.85,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.content  # MP3 audio bytes
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None


# Example usage:



# import asyncio
# import edge_tts
#
# async def generate_tts_audio(text, voice="en-US-GuyNeural"):
#     """
#     Generates TTS audio using Edge TTS and returns raw audio bytes.
#
#     Args:
#         text (str): Text to convert.
#         voice (str): Edge TTS voice ID.
#
#     Returns:
#         bytes: Raw MP3 audio data.
#     """
#     try:
#         communicate = edge_tts.Communicate(text=text, voice=voice)
#         audio_bytes = b""
#         async for chunk in communicate.stream():
#             if chunk["type"] == "audio":
#                 audio_bytes += chunk["data"]
#         return audio_bytes
#     except Exception as e:
#         print(f"❌ Failed to generate audio: {e}")
#         return None

