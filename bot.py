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
    elif re.search("!oppai", msg.content):
        await check_oppai(msg)
    elif re.search("!shop", msg.content):
        await check_store(msg)
    elif re.search("!buy ", msg.content):
        await buy_item(msg)
    # If the message has attachments, logs them
    if msg.attachments:
        log_attachments(msg)
    # Logs message author and contents
    appender('oppai.log', f'{msg.author}: {msg.content}')


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


async def check_oppai(msg):
    stats = trading_game[msg.author.id]
    response = f"{stats['name']}-sama, you have {stats['oppai']} oppai!"
    await msg.channel.send(response)


async def check_store(msg):
    response = "Today we have these items available, Master!"
    store = {
        'investment_store': load_investment_store(),
        'token_store': [],
        'pet_store': [],
    }
    for mini_store in store.values():
        for item in mini_store:
            response += f'\n{item["name"]}: {item["description"]}\tCost: {item["cost"]} oppai\tCommand: {item["buy_command"]}'
    await msg.channel.send(response)


async def buy_item(msg):
    player = trading_game[msg.author.id]
    store = {
        'investment_store': load_investment_store()
    }
    response = ""
    for investment in store['investment_store']:
        if investment['buy_command'] == msg.content:
            if player['oppai'] >= investment['cost']:
                player['oppai'] -= investment['cost']
                player['investments'].append(investment)
                response = f"You just bought a {investment['name']}, Master! You have {player['oppai']} oppai left."
                save_trading_game()
                break
            else:
                response = f"You don't have enough oppai for that, Master! You have {player['oppai']} oppai."
                break
    else:
        response = f"We don't sell any {msg.content.split('!buy ')[1]}, Master!"
    await msg.channel.send(response)


def load_investment_store():
    store = [
        generate_investment("Code Monkey", 'A little rhesus monkey often used for software development purposes.', 50,
                            [generate_item('Awful Code', 20, 1), generate_item('Bad Code', 12, 2), generate_item('Decent Code', 7, 3),
                             generate_item('Good Code', 4, 4), generate_item('Professional Code', 2, 5), generate_item('Godly Code', 1, 6)],
                            1.1, "None", '!buy monkey'),
        generate_investment("Carrot Farm", 'A monocrop farm that produces nothing but carrots.', 100,
                            [generate_item('Rotten Carrot', 15, 1), generate_item('Limp Carrot', 10, 2), generate_item('Carrot', 5, 3),
                             generate_item('Yummy Carrot', 3, 4), generate_item('Succulent Carrot', 2, 5), generate_item('Golden Carrot', 1, 6)],
                            1.1, "None", '!buy carrot'),
        generate_investment("Wheat Farm", 'A monocrop farm that produces nothing but wheat.', 200,
                            [generate_item('Bug-eaten Wheat', 40, 1), generate_item('Moldy Wheat', 25, 2), generate_item('Wheat', 15, 3),
                             generate_item('Fresh Wheat', 8, 4), generate_item('Quality Wheat', 5, 5), generate_item('Golden Wheat', 3, 6)],
                            1.1, "None", '!buy wheat'),
        generate_investment("Apple Farm", 'A monocrop farm that produces nothing but apples.', 350,
                            [generate_item('Rotten Apple', 12, 1), generate_item('Wormy Apple', 8, 2),
                             generate_item('Apple', 6, 3),
                             generate_item('Juicy Apple', 4, 4), generate_item('Delicious Apple', 2, 5),
                             generate_item('Golden Apple', 1, 6)],
                            1.1, "None", '!buy apple'),
        generate_investment("Meth Lab", "A lab that produces meth. Hey, don't ask me about it.", 1500,
                            [generate_item('Awful Meth', 15, 1), generate_item('Bad Meth', 9, 2),
                             generate_item('Crystal Meth', 7, 3),
                             generate_item('Quality Meth', 4, 4), generate_item('High-quality Meth', 2, 5),
                             generate_item('Godly Meth', 1, 6)],
                            1.2, "None", '!buy meth'),
        # generate_investment("Slave", 200, {}, 1.05, "None"),
    ]
    return store


def generate_investment(name: str, description: str, cost: int, yields: list, growth_rate: float, img: str, buy_command: str) -> dict:
    return {
        'name': name,
        'description': description,
        'cost': cost,
        'yields': yields,
        'growth_rate': growth_rate,
        'img': img,
        'buy_command': buy_command
    }


def generate_item(name: str, base_yield: int, quality: int) -> dict:
    return {
        'item_name': name,
        'base_yield': base_yield,
        'item_quality': quality,
    }


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
