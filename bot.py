# bot.py
import os

import discord
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    responses_oppai = [
        'Wanna see my oppai, master?',
        '(o)(o)',
        'Oppai oppai!']

    responses = [
        'Hello, Master!',
        'Can I help you, Master?',
        "Come a little closer, I can't hear you from here <3"
    ]

    if 'oppai' not in message.content:
        response = random.choice(responses)
    else:
        response = random.choice(responses_oppai)
    await message.channel.send(response)

client.run(TOKEN)
