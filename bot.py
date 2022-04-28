# bot.py
import os
import re

from dotenv import load_dotenv
import random

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


def appender(filename: str, text: str):
    """
    Opens a file with the given filename and appends a line to it.

    Opens a file with the given filename or creates one if it doesn't exist. Appends a line to it.
    :param filename: the filename to open
    :param text: the text to append
    """
    with open(filename, mode='a+') as file:
        file.write(f'{text}\n')


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
        'Oppai oppai!',
        'Are you tired? You can touch my oppai, Master.']
    #
    # responses = [
    #     'Hello, Master!',
    #     'Can I help you, Master?',
    #     "Come a little closer, I can't hear you from here <3"
    # ]
    response = random.choice(responses_oppai)
    await msg.channel.send(response)


@bot.event
async def on_message(msg):
    if msg.attachments:
        appender('oppai-img.log', f'{msg.author}: {msg.content}')
        for i, attachment in enumerate(msg.attachments):
            appender('oppai-img.log', f'Attachment {i+1}: {attachment.filename}: {attachment.proxy_url}')
    appender('oppai.log', f'{msg.author}: {msg.content}')
    if re.search("^[Oo]ppai(| |-)[Cc]han.*\\?$", msg.content):
        n = random.random()
        yes_responses = ["Of course, Master!", "I think so, Master.", "Yes, master!", "I'm sure of it, Master!"]
        no_responses = ["I don't think so, Master!", "Definitely not, Master.", "No, master!", "Probably not, Master!"]
        if n > 0.5:
            response = random.choice(yes_responses)
        else:
            response = random.choice(no_responses)
        await msg.channel.send(response)
    elif re.search("^おっぱいちゃん.*[?|？]$", msg.content):
        n = random.random()
        yes_responses = ["もちろんです、ご主人様", "そう思います、ご主人様", "はい、ご主人様!", "必ず、ご主人様"]
        no_responses = ["そう思いません、ご主人様", "いいえ、ご主人様", "そんなことはありません、ご主人様"]
        if n > 0.5:
            response = random.choice(yes_responses)
        else:
            response = random.choice(no_responses)
        await msg.channel.send(response)
    elif re.search("!game", msg.content):
        response = "Let's play a game, master!"
        await msg.channel.send(response)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)
