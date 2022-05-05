# bot.py
import math
import os
import re
from io import BytesIO
import pickle
import discord
from dotenv import load_dotenv
import random

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

game_stats = {}
trading_game = {}


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
    load_game_data()
    load_trading_game_data()


# Loads game data into dictionary
def load_game_data():
    with open('game_stats', 'rb') as stats_file:
        global game_stats
        game_stats = pickle.load(stats_file)


# Loads trading game data into dictionary
def load_trading_game_data():
    with open('trading_game_stats', 'rb') as trading_stats_file:
        global trading_game
        trading_game = pickle.load(trading_stats_file)


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"{member.name}-sama, time for your punishment!"
    )


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
    # If the message has attachments, logs them
    if msg.attachments:
        log_attachments(msg)
    # Logs message author and contents
    appender('oppai.log', f'{msg.author}: {msg.content}')
    await game_update(msg)
    # Uses regex to respond to various commands
    if re.search("^[Oo]ppai(| |-)[Cc]han.*\\?$", msg.content):
        await ask_oppai(msg)
    elif re.search("^おっぱいちゃん.*[?|？]$", msg.content):
        await ask_oppai_japanese(msg)
    elif re.search("!send", msg.content):
        await distribute_files(msg)
    elif re.search("!startgame", msg.content) and msg.author.name == "Maxwell":
        await start_game(msg)
    elif re.search("!starttrading", msg.content) and msg.author.name == "Maxwell":
        await start_trading_game(msg)
    elif re.search("!stats", msg.content):
        await check_stats(msg)


def log_attachments(msg):
    appender('oppai-img.log', f'{msg.author}: {msg.content}')
    for i, attachment in enumerate(msg.attachments):
        appender('oppai-img.log', f'Attachment {i + 1}: {attachment.filename}: {attachment.proxy_url}')


async def start_game(msg):
    stats_list = {}
    for member in msg.guild.members:
        stats = {
            "name": member.name,
            "lvl": 1,
            "exp": 0
        }
        stats_list[member.id] = stats
    with open('game_stats', 'wb') as save_file:
        pickle.dump(stats_list, save_file)


async def start_trading_game(msg):
    trading_game = {}
    for member in msg.guild.members:
        stats = {
            "name": member.name,
            "lvl": 1,
            "exp": 0,
            "oppai": 1000,
            "investments": [],
            "pets": [],
            "tokens": [],
            "achievements": []
        }
        trading_game[member.id] = stats
    with open('trading_game_stats', 'wb') as save_file:
        pickle.dump(trading_game, save_file)


def save_game():
    with open('game_stats', 'wb') as save_file:
        pickle.dump(game_stats, save_file)


def save_trading_game():
    with open('trading_game_stats', 'wb') as save_file:
        pickle.dump(trading_game, save_file)


async def game_update(msg):
    game_stats[msg.author.id]['exp'] += 5 + math.floor(math.log2(len(msg.content)))
    save_game()
    if check_level_up(game_stats[msg.author.id]):
        game_stats[msg.author.id]['lvl'] += 1
        await msg.channel.send(f"Congrats, {msg.author.name}-sama! You just advanced to level {game_stats[msg.author.id]['lvl']}!")


def check_level_up(stats: dict) -> bool:
    if stats['lvl'] * stats['lvl'] * 100 <= stats['exp']:
        return True
    return False


async def check_stats(msg):
    stats = game_stats[msg.author.id]
    response = f"{stats['name']}-sama's stats:\nLevel {stats['lvl']}\tXP: {stats['exp']}/{stats['lvl'] * stats['lvl'] * 100}"
    await msg.channel.send(response)


async def ask_oppai(msg):
    n = random.random()
    yes_responses = ["Of course, Master!", "I think so, Master.", "Yes, master!", "I'm sure of it, Master!"]
    no_responses = ["I don't think so, Master!", "Definitely not, Master.", "No, master!", "Probably not, Master!"]
    if n > 0.5:
        response = random.choice(yes_responses)
    else:
        response = random.choice(no_responses)
    await msg.channel.send(response)


async def ask_oppai_japanese(msg):
    n = random.random()
    yes_responses = ["もちろん、ご主人様", "そう思います、ご主人様", "はい、ご主人様!", "必ず、ご主人様"]
    no_responses = ["そう思いません、ご主人様", "いいえ、ご主人様", "そんなことはありません、ご主人様"]
    if n > 0.5:
        response = random.choice(yes_responses)
    else:
        response = random.choice(no_responses)
    await msg.channel.send(response)


async def distribute_files(msg):
    with open('img/oppaichan.jpg', mode='rb') as oppai_binary:  # opens a file in read binary mode
        for member in msg.guild.members:  # for each member in this guild
            if member.bot:
                continue
            print(f'Sending message to {member.name}...')
            oppai_binary.seek(0)
            buffer = BytesIO(oppai_binary.read())  # BytesIO object must be created with the BinaryIO object
            await member.send(content="Master Maxwell told me to send you this picture!",
                              file=discord.File(fp=buffer, filename='oppai.jpg'))
    response = "Sent, Master!"
    await msg.channel.send(response)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


bot.run(TOKEN)
