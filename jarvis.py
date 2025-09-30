import discord
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # make sure you set this in Render

intents = discord.Intents.default()
intents.message_content = True  # needed to read messages
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # ignore itself
    if message.content.lower() == "ping":
        await message.channel.send("pong 🏓")
    elif message.content.lower() == "hello":
        await message.channel.send("Hello! I'm alive on Render 🚀")

client.run(TOKEN)
