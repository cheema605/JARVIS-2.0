import discord

async def get_chat_history_from_channel(message, limit=15):
    history = []

    async for msg in message.channel.history(limit=limit, oldest_first=True):
        # Determine role
        if msg.author == message.author:
            role = "user"
        elif msg.author == message.guild.me if message.guild else message.channel.me:
            role = "jarvis"
        else:
            role = "other"

        history.append({
            "role": role,
            "content": msg.content,
            "author": str(msg.author)
        })

    return history
