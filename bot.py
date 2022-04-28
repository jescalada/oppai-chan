# bot.py
import os
import re

from dotenv import load_dotenv
import random

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"{member.name}-sama, time for your punishment!"
    )


@bot.command(name='yn', help='Simulates a yes or no.')
async def roll(ctx):
    n = random.random()
    yes_responses = ["Of course, Master!", "I think so, Master.", "Yes, master!", "I'm sure of it, Master!"]
    no_responses = ["I don't think so, Master!", "Definitely not, Master.", "No, master!", "Probably not, Master!"]
    if n > 0.5:
        response = random.choice(yes_responses)
    else:
        response = random.choice(no_responses)
    await ctx.send(response)


@bot.command(name='oppai')
async def oppai(msg):
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

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)
