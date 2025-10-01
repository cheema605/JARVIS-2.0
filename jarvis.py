import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import json
import re
import requests

from stt import transcribe_audio
from Trigger import filter_prompt
from execute_functions import call_corresponding_func
from prompt import build_model_prompt
from tts import generate_tts_audio
from chat_history import get_chat_history_from_channel
from pydub import AudioSegment
import io

# --- Load environment variables ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- Discord bot setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# --- Helper functions ---
def call_model(prompt_messages, temperature=1):
    """Call OpenRouter API for model response."""
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

def load_user_context(user_id: str, path="user_context.json"):
    """
    Load only the memories of the specified user.
    Returns in the format:
    {
        "user_memories": {
            "user_id": [ ...memories... ]
        }
    }
    """
    if not os.path.exists(path):
        return {"user_memories": {user_id: []}}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_user_memories = data.get("user_memories", {})
    current_user_memories = all_user_memories.get(user_id, [])

    return {"user_memories": {user_id: current_user_memories}}

async def run_jarvis_interaction(prompt, memories=None, chat_history=None):
    """
    Runs a single interaction:
    1. Filters possible functions
    2. Builds the model prompt
    3. Calls the model
    4. Calls corresponding functions via webhook
    """
    functions = filter_prompt(prompt)
    messages = build_model_prompt(
        prompt=prompt,
        memories=memories,
        chat_history=chat_history,
        functions_available=functions
    )
    print("📝 Prompt to model:")
    print(messages)
    response_text = call_model(messages)

    workflow_return = None
    return_status = None
    message = None

    # Parse JSON from model response
    match = re.search(r"{[\s\S]+}", response_text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            functions_to_call = parsed.get("functions", [])
            workflow_return = await call_corresponding_func(functions_to_call)
            return_status = workflow_return
            message = parsed.get("message", "")
        except json.JSONDecodeError:
            print("⚠ Failed to parse JSON from model response.")
            message = response_text
    else:
        message = response_text

    return message, return_status, workflow_return

# --- Discord Events ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only respond if in DM or bot is mentioned
    if isinstance(message.channel, discord.DMChannel) or bot.user in message.mentions:
        # Remove bot mention from message content if present
        prompt_text = message.content.replace(f"<@{bot.user.id}>", "").strip()

        # Load user-specific memories
        user_id = str(message.author)
        memories = load_user_context(user_id)

        # Get last 20 messages from this channel
        chat_history = await get_chat_history_from_channel(message, limit=20)

        try:
            message_to_send, func_status, workflow_return = await run_jarvis_interaction(
                prompt=prompt_text,
                memories=memories,
                chat_history=chat_history
            )

            await message.channel.send(f"{message_to_send}")
            print(f"🛠 Function Status: {func_status}")
            print(f"🧠 Workflow Return: {workflow_return}")

        except Exception as e:
            await message.channel.send(f"❌ Error: {str(e)}")

    # Ensure commands still work
    await bot.process_commands(message)


# --- Voice commands ---
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.send("❌ I'm already in a voice channel.")
        else:
            await channel.connect()
            await ctx.send(f"✅ Joined {channel.name}!")
    else:
        await ctx.send("❌ You are not in a voice channel.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")
    else:
        await ctx.send("❌ I'm not in a voice channel.")

# --- Run bot ---
bot.run(TOKEN)
