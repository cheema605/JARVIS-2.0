import requests
import os

from Cython.Compiler.Errors import message
from dotenv import load_dotenv
import asyncio
# from jieba.lac_small.predict import results

from tts import generate_tts_audio
import simpleaudio as sa
import json
import io
import re
from stt import *
from pydub import AudioSegment


from Trigger import filter_prompt
from execute_functions import call_corresponding_func
from prompt import build_model_prompt  # Used for constructing messages

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# ...existing code...
def call_model(prompt_messages, temperature=1):
    # Use OpenRouter API instead of Groq
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": prompt_messages,
        "temperature": temperature
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

    return response.json()["choices"][0]["message"]["content"]

async def run_jarvis_interaction(
    prompt,
    memories=None,
    chat_history=None,
    result=None
):


    # Filter for possible functions
    functions = filter_prompt(prompt)
    message = None
    workflow_return = None
    return_status = None

    # Use helper to construct prompt messages
    messages = build_model_prompt(
        prompt=prompt,
        memories=memories,
        chat_history=chat_history,
        result=result,
        functions_available=functions
    )

    # ✅ Check if messages is a list
    if not isinstance(messages, list):
        raise ValueError("Prompt builder must return a list of messages.")

    # Call LLM
    response_text = call_model(messages)

    print(f"🧠 Jarvis says: {response_text}\n")

    match = re.search(r"{[\s\S]+}", response_text)
    if match:
        json_text = match.group(0)

        try:
            parsed = json.loads(json_text)
            functions = parsed.get("functions", "")
            workflow_return = await call_corresponding_func(functions)
            return_status = workflow_return
            message = parsed.get("message", "")
            print(message)
        except json.JSONDecodeError:
            print("Failed to parse JSON.")
    else:
        print("No JSON found in response.")
    # # TTS Audio Response
    # audio_bytes = generate_tts_audio(message)
    # # audio_bytes = asyncio.run(generate_tts_audio(message))
    # if audio_bytes:
    #     audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    #     raw_data = audio.raw_data
    #     sample_rate = audio.frame_rate
    #     num_channels = audio.channels
    #     sample_width = audio.sample_width
    #     play_obj = sa.play_buffer(raw_data, num_channels, sample_width, sample_rate)
    #     play_obj.wait_done()
    # else:
    #     print("❌ Failed to generate or play audio.")
    print(return_status)
    return response_text, return_status, workflow_return




def load_user_context(path="user_context.json"):
    """
    Loads memories, preferences, and personal_info from a JSON file.

    Returns:
        tuple: (memories: list[str], preferences: list[str], personal_info: list[str])
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    memories_data = data.get("memories", [])

    return memories_data


if __name__ == "__main__":
    loop = True
    errors = []
    chat_history = "ammarcheema140@gmail.com is the email used by cheema"
    error_detected = True

    while loop:
        # If previous iteration had errors, retry them
        if error_detected is False:
            prompt = "You cannot call it in func without asking again"
            error_detected = True
        if errors:
            prompt = " Ask to retry DO NOT ADD INTO FUNCTIONS AGAIN IF USER DOESNT SAY SO BUT ASK AGAIN IF ANYTHING FAILS AGAIN".join(errors)
        else:
            prompt = input("Enter prompt: ") or ""

        memories = load_user_context()


        # Run interaction
        MAX_CHARS = 2000
        if len(chat_history) > MAX_CHARS:
            chat_history = chat_history[-MAX_CHARS:]


        result_text, func_status_dict, func_status_codes = asyncio.run(run_jarvis_interaction(
            prompt=prompt,
            memories=memories,
            chat_history=chat_history,
            result=None
        )
        )


        chat_history += f"\nUser: {prompt}\nJarvis: {result_text}\n"

        # Match by index between dict (func_status_dict) and list (func_status_codes)
        errors = []
        func_names = []
        func_values = []


        # if func_status_dict.keys():
        #     func_names = list(func_status_dict.keys())
        #     func_values = list(func_status_dict.values())

        # for idx, success_str in enumerate(func_values):
        #     if success_str == "False":
        #         errors.append(f"{func_names[idx]} failed with status: {func_status_codes[idx]}")
        #         error_detected = True

        # for idx, success_str in enumerate(func_values):
        #     if success_str == "Send":
        #         errors.append(f"{func_names[idx]} sent back data: {func_status_codes[idx]}")
        #         error_detected = True


        # Preview next prompt
        if errors:
            next_prompt = " ".join(errors) + " Ask to retry"
        else:
            next_prompt = prompt

        print("Next prompt:", next_prompt)
