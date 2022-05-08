# bot.py
import math
import os
import re
from io import BytesIO
import pickle
import discord
from dotenv import load_dotenv
import random

from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True
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
    trading_game_update.start()


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
    # elif re.search("^!send", msg.content):
    #     await distribute_files(msg)
    elif re.search("^!startgame", msg.content) and msg.author.name == "Maxwell":
        await start_game(msg)
    elif re.search("^!starttrading", msg.content) and msg.author.name == "Maxwell":
        await start_trading_game(msg)
    elif re.search("^!stats", msg.content):
        await check_stats(msg)
    elif re.search("^!oppai", msg.content):
        await check_oppai(msg)
    elif re.search("^!shop", msg.content):
        await check_store(msg)
    elif re.search("^!buypet", msg.content):
        await buy_pet(msg)
    elif re.search("^!buy ", msg.content):
        await buy_investment(msg)
    elif re.search("^!update", msg.content) and msg.author.name == "Maxwell":
        await trading_game_update()
    elif re.search("^!status", msg.content):
        await status(msg)
    elif re.search("^!resetall", msg.content) and msg.author.name == "Maxwell":
        await reset_all_trading_stats(msg)
    elif re.search("^!help", msg.content):
        await help_prompt(msg)
    elif re.search("^!petstatus", msg.content):
        await pets_status(msg)
    elif re.search("^!feed", msg.content):
        await feed_pet(msg)
    elif re.search("^!sell", msg.content):
        await sell_item(msg)
    elif re.search("^!play", msg.content):
        await play_with_pet(msg)


# # If the message has attachments, logs them
    # if msg.attachments:
    #     log_attachments(msg)
    # # Logs message author and contents
    # appender('oppai.log', f'{msg.author}: {msg.content}')


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
            "investment_counts": {},
            "pets": [],
            "tokens": [],
            "achievements": [],
            "items": {},
            "item_info": {},
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


@tasks.loop(minutes=60)
async def trading_game_update():
    channel = bot.get_channel(971979909310328852)
    for member in channel.members:  # for each member in this guild
        if member.bot:
            continue
        player = trading_game[member.id]
        response = ""
        for investment in player['investments']:
            response += investment_production(investment, player)
        for pet in player['pets']:
            response += pet_production(pet, player)
            pet_status_update(pet)
            response += check_pet_growth_achieved(pet)
            response += f'{pet["name"]} is {pet_hunger_text(pet)} and {pet_mood_text(pet)}.\n'
        if response != "":
            await channel.send(response)
    save_trading_game()
    await channel.send(f"Updated trading game!")


def investment_production(investment, player):
    count = player['investment_counts'][investment['name']]
    quality = roll_investment_yield_quality(count)
    obtained = investment['yields'][quality - 1]
    add_item_to_player(obtained, player)
    return f"{player['name']}'s {investment['name']} produced {obtained['base_yield']} {obtained['item_name']}!\n"


def pet_production(pet, player):
    growth_factor = pet['growth_percent'] + (pet['growth_stage'] - 1) * 200
    quality = roll_investment_yield_quality(growth_factor + 1)
    obtained = pet['pet_info']['yields'][quality - 1]
    add_item_to_player(obtained, player)
    return f"{player['name']}'s {pet['name']} produced {obtained['base_yield']} {obtained['item_name']}!\n"


def add_item_to_player(obtained, player):
    if obtained['item_name'] not in player['items']:
        player['item_info'][obtained['item_name']] = obtained
        player['items'][obtained['item_name']] = obtained['base_yield']
    else:
        player['items'][obtained['item_name']] += obtained['base_yield']


def pet_status_update(pet):
    pet['hunger'] = max(0, pet['hunger'] - 10)
    pet['happiness'] = max(0, pet['happiness'] - 5)
    if pet['hunger'] > 25 and pet['happiness'] > 25:
        pet['growth_percent'] = min(100, pet['pet_info']['base_growth_rate'] + pet['growth_percent'])
        if pet['happiness'] > 75:
            pet['growth_percent'] = min(100, pet['pet_info']['base_growth_rate'] + pet['growth_percent'])


def check_pet_growth_achieved(pet):
    if pet['growth_percent'] == 100:
        pet['growth_stage'] += 1
        pet['growth_percent'] = 0
        return f"Congrats! {pet['name']} grew up!\n"
    return ""


def pet_hunger_text(pet):
    return f"{'Starving' if pet['hunger'] < 15 else 'Very Hungry' if pet['hunger'] < 30 else 'Hungry' if pet['hunger'] < 45 else 'Not Hungry' if pet['hunger'] < 60 else 'Satisfied' if pet['hunger'] < 75 else 'Full' if pet['hunger'] < 90 else 'Bloated'}"


def pet_mood_text(pet):
    return f"{'Suicidal' if pet['happiness'] < 15 else 'Depressed' if pet['happiness'] < 30 else 'Sad' if pet['happiness'] < 45 else 'Okay' if pet['happiness'] < 60 else 'Pleased' if pet['happiness'] < 75 else 'Happy' if pet['happiness'] < 90 else 'Blissful'}"


async def status(msg):
    player = trading_game[msg.author.id]
    response = f"= {msg.author.name}'s status =\n"
    response += f"{player['oppai']} Ø\n"
    response += f"Investments\n"
    for investment in player['investment_counts'].keys():
        response += f"{player['investment_counts'][investment]} {investment}s\n"
    response += f"\nItems:\n"
    for item in player['items']:
        response += f"{player['items'][item]} {item} - Value: {player['item_info'][item]['base_value']} Ø\n"
    await msg.channel.send(response)


async def pets_status(msg):
    player = trading_game[msg.author.id]
    response = f"= {msg.author.name}'s pets =\n"
    for pet in player['pets']:
        response += f"{pet['name']} the {pet['pet_info']['name']} - " \
                    f"Hunger: {pet_hunger_text(pet)} - " \
                    f"Mood: {pet_mood_text(pet)} - " \
                    f"Growth: {'Baby' if pet['growth_stage'] == 0 else 'Child' if pet['growth_stage'] else 'Adult'} [{pet['growth_percent']}%]\n"
    await msg.channel.send(response)


async def feed_pet(msg):
    response = ""
    player = trading_game[msg.author.id]
    command = msg.content.split(" ")
    pet_name = command[1]
    pet = get_pet_by_name(pet_name, player)
    if not pet:
        response += f"You don't have a pet called {pet_name}, Master!"
        await msg.channel.send(response)
        return
    item_name = msg.content.replace("!feed ", "").replace(pet_name, "").strip()
    if check_item_in_inventory(item_name, 1, player):
        player['items'][item_name] -= 1
        quality = player['item_info'][item_name]['item_quality']
        pet['hunger'] = min(pet['hunger'] + quality * quality, 100)
        response += f"You feed {pet_name} a {item_name}.\n"
        response += f"{pet_name}'s fullness increased by {quality * quality}.\n"
        if any(element in item_name for element in pet['pet_info']['favorite']):
            pet['happiness'] = min(100, pet['happiness'] + quality * quality)
            response += f"{pet_name} loves {item_name}!\n"
            response += f"{pet_name}'s happiness increased by {quality * quality}.\n"
        response += f'{pet_name} says: "{random.choice(pet["pet_info"]["quotes"])}"'
    else:
        response += f"You don't have any {item_name}s, Master!"
    await msg.channel.send(response)
    save_trading_game()


async def play_with_pet(msg):
    response = ""
    player = trading_game[msg.author.id]
    command = msg.content.split(" ")
    pet_name = command[1]
    pet = get_pet_by_name(pet_name, player)
    if not pet:
        response += f"You don't have a pet called {pet_name}, Master!"
        await msg.channel.send(response)
        return
    pet['happiness'] = min(100, pet['happiness'] + 10)
    response += f"You play with {pet_name}.\n{pet_name}'s happiness increased by 10.\n{pet_name} feels {pet_mood_text(pet)}."
    await msg.channel.send(response)
    save_trading_game()


def get_pet_by_name(pet_name, player) -> dict:
    for pet in player['pets']:
        if pet['name'] == pet_name:
            return pet
    return {}


def check_item_in_inventory(item_name: str, quantity: int, player: dict) -> bool:
    return item_name in player['items'] and player['items'][item_name] >= quantity


def roll_investment_yield_quality(count: int):
    quality1_weight = 1500 - count * 5
    quality2_weight = 650 - count
    quality3_weight = 250 - int(count / 10)
    quality4_weight = int(60 * max(1.0, math.log10(count)))
    quality5_weight = int(30 * max(1.0, 1.5 * math.log10(count)))
    quality6_weight = int(10 * max(1.0, 2 * math.log10(count)))
    total = quality1_weight + quality2_weight + quality3_weight + quality4_weight + quality5_weight + quality6_weight
    num = random.randint(0, total)
    if num < quality6_weight:
        return 6
    elif num < quality5_weight:
        return 5
    elif num < quality4_weight:
        return 4
    elif num < quality3_weight:
        return 3
    elif num < quality2_weight:
        return 2
    else:
        return 1


async def reset_all_trading_stats(msg):
    for member in msg.guild.members:  # for each member in this guild
        if member.bot:
            continue
        player = trading_game[member.id]
        player['investments'] = []
        player['investment_counts'] = {}
        player['items'] = {}
        player['pets'] = []
        player["lvl"] = 1
        player["exp"] = 0
        player["oppai"] = 1000
        player["tokens"] = []
        player["achievements"] = []
        player["item_info"] = {}
    await msg.channel.send("I just reset the trading stats for everybody, Master!")


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
    response = f"{stats['name']}-sama, you have {stats['oppai']} Ø!"
    await msg.channel.send(response)


async def check_store(msg):
    response = "Today we have these items available, Master!"
    store = {
        'investment_store': load_investment_store(),
        'token_store': [],
        'pet_store': load_pet_store(),
    }
    for mini_store in store.values():
        for item in mini_store:
            response += f'\n{item["name"]}: {item["description"]}\tCost: {item["cost"]} Ø\tCommand: {item["buy_command"]}'
    await msg.channel.send(response)


async def buy_investment(msg):
    player = trading_game[msg.author.id]
    for investment in load_investment_store():
        if investment['buy_command'] == msg.content:
            if player['oppai'] >= investment['cost']:
                player['oppai'] -= investment['cost']
                player['investments'].append(investment)
                if investment['name'] not in player['investment_counts']:
                    player['investment_counts'][investment['name']] = 1
                else:
                    player['investment_counts'][investment['name']] += 1
                response = f"You just bought a {investment['name']}, Master! You have {player['oppai']} Ø left."
                save_trading_game()
                break
            else:
                response = f"You don't have enough oppai for that, Master! You have {player['oppai']} Ø."
                break
    else:
        response = f"We don't sell any {msg.content.split('!buy ')[1]}, Master!"
    await msg.channel.send(response)
    save_trading_game()


async def buy_pet(msg):
    player = trading_game[msg.author.id]
    pet_name = msg.content.split(" ")[2]
    for pet in load_pet_store():
        if pet['buy_command'] == msg.content.replace(pet_name, "").rstrip():
            if player['oppai'] >= pet['cost']:
                player['oppai'] -= pet['cost']
                new_pet = create_pet_instance(pet, pet_name, stats={})
                player['pets'].append(new_pet)
                response = f"You just bought a pet {pet['name']} called {pet_name}, Master! You have {player['oppai']} Ø left."
                save_trading_game()
                break
            else:
                response = f"You don't have enough oppai for that, Master! You have {player['oppai']} Ø."
                break
    else:
        response = f"We don't sell any {msg.content.split(' ')[1]}, Master!"
    await msg.channel.send(response)
    save_trading_game()


async def sell_item(msg):
    response = ""
    player = trading_game[msg.author.id]
    try:
        quantity = int(msg.content.split(" ")[1])
    except ValueError:
        response += f"{msg.content.split(' ')[1]} is not a number, Master!"
        await msg.channel.send(response)
        return
    item_name = msg.content.replace("!sell ", "").replace(str(quantity), "").strip()
    if item_name not in player['items']:
        response += f"You don't have any {item_name} to sell, Master!"
    elif player['items'][item_name] < quantity:
        response += f"You only have {player['items'][item_name]} {item_name}s to sell, Master!"
    else:
        player['items'][item_name] -= quantity
        sale_value = player['item_info'][item_name]['base_value'] * quantity
        player['oppai'] += sale_value
        response += f"Sold {quantity} {item_name}s for {sale_value} Ø, Master!\nYou now have {player['oppai']} Ø."
    await msg.channel.send(response)
    save_trading_game()


def load_investment_store():
    store = [
        generate_investment("Code Monkey", 'A little rhesus monkey often used for software development purposes.', 50,
                            [generate_item('Awful Code', 20, 1, 0), generate_item('Bad Code', 12, 2, 0), generate_item('Decent Code', 7, 3, 1),
                             generate_item('Good Code', 4, 4, 2), generate_item('Professional Code', 2, 5, 3), generate_item('Godly Code', 1, 6, 5)],
                            1.1, "None", '!buy monkey'),
        generate_investment("Carrot Farm", 'A monocrop farm that produces nothing but carrots.', 100,
                            [generate_item('Rotten Carrot', 15, 1, 0), generate_item('Limp Carrot', 10, 2, 0), generate_item('Carrot', 5, 3, 1),
                             generate_item('Yummy Carrot', 3, 4, 2), generate_item('Succulent Carrot', 2, 5, 5), generate_item('Golden Carrot', 1, 6, 15)],
                            1.1, "None", '!buy carrot'),
        generate_investment("Wheat Farm", 'A monocrop farm that produces nothing but wheat.', 200,
                            [generate_item('Bug-eaten Wheat', 40, 1, 0), generate_item('Moldy Wheat', 25, 2, 0), generate_item('Wheat', 15, 3, 1),
                             generate_item('Fresh Wheat', 8, 4, 2), generate_item('Quality Wheat', 5, 5, 4), generate_item('Golden Wheat', 3, 6, 8)],
                            1.1, "None", '!buy wheat'),
        generate_investment("Apple Farm", 'A monocrop farm that produces nothing but apples.', 350,
                            [generate_item('Rotten Apple', 12, 1, 0), generate_item('Wormy Apple', 8, 2, 0),
                             generate_item('Apple', 6, 3, 2),
                             generate_item('Juicy Apple', 4, 4, 4), generate_item('Delicious Apple', 2, 5, 10),
                             generate_item('Golden Apple', 1, 6, 25)],
                            1.1, "None", '!buy apple'),
        generate_investment("Meth Lab", "A lab that produces meth. Hey, don't ask me about it.", 1500,
                            [generate_item('Awful Meth', 15, 1, 0), generate_item('Bad Meth', 9, 2, 1),
                             generate_item('Crystal Meth', 7, 3, 2),
                             generate_item('Quality Meth', 4, 4, 5), generate_item('High-quality Meth', 2, 5, 15),
                             generate_item('Godly Meth', 1, 6, 40)],
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


def generate_item(name: str, base_yield: int, quality: int, base_value: int) -> dict:
    return {
        'item_name': name,
        'base_yield': base_yield,
        'item_quality': quality,
        'base_value': base_value
    }


def load_pet_store():
    pet_store = [generate_pet_info(name="Goat",
                                   description="A baby goat. Looks so cute and innocent!",
                                   cost=200,
                                   yields=[generate_item('Pile of Shit', 1, 1, 0), generate_item('Smelly Beard', 1, 2, 1),
                                           generate_item('Goat Milk', 5, 3, 3), generate_item('Sleek Beard', 3, 4, 6),
                                           generate_item('Shiny Horn', 2, 5, 11), generate_item('Goat Elixir', 1, 1, 30)],
                                   base_growth_rate=1,
                                   quotes=["Baaaaaa!", "Baaaa", "I don't know", "I'll get back to you next week",
                                           "I'm not sure", "Just copy paste it"],
                                   favorite=["Carrot", "Code"],
                                   img="None",
                                   buy_command="!buypet goat"),
                 generate_pet_info(name="Chicken",
                                   description="A baby chick. So small and cute, makes you want to eat it whole.",
                                   cost=200,
                                   yields=[generate_item('Rotten Egg', 10, 1, 0), generate_item('Leathery Chicken', 5, 2, 0),
                                           generate_item('Egg', 5, 3, 2), generate_item('Juicy Chicken', 3, 4, 4),
                                           generate_item('Delicious Egg', 2, 5, 8), generate_item('Heavenly Chicken', 1, 1, 22)],
                                   base_growth_rate=2,
                                   quotes=["Cluck", "Cluck cluck", "CLUCK", "*stares*", "*flaps wings*"],
                                   favorite=["Wheat", "Worm"],
                                   img="None",
                                   buy_command="!buypet chicken"),
                 generate_pet_info(name="Unicorn",
                                   description="A little unicorn. A legendary creature that apparently shits sugar and rainbows.",
                                   cost=300,
                                   yields=[generate_item('Gooey Sugar', 8, 1, 0), generate_item('Pale Rainbow', 5, 2, 1),
                                           generate_item('Sugar', 4, 3, 3), generate_item('Colorful Rainbow', 3, 4, 5),
                                           generate_item('Savory Sugar', 2, 5, 10), generate_item('Unicorn Horn', 1, 1, 100)],
                                   base_growth_rate=0.5,
                                   quotes=["Neigh", "SUNSHINE LOLLIPOPS AND RAINBOWS", "*prances around*", "*barfs a rainbow*",
                                           "*unintelligible unicorn noises*", "UGH I WANNA KILL A VAMPIRE RIGHT NOW",
                                           "Pst... kid, got any apples?"],
                                   favorite=["Apple", "Magic"],
                                   img="None",
                                   buy_command="!buypet unicorn"),
                 generate_pet_info(name="Cowgirl",
                                   description="A cow girl. She has huge tits and probably has enough milk to feed a family of four.",
                                   cost=500,
                                   yields=[generate_item('Rancid Milk', 10, 1, 0),
                                           generate_item('Old Milk', 7, 2, 2),
                                           generate_item('Milk', 5, 3, 4), generate_item('Creamy Milk', 4, 4, 8),
                                           generate_item('Delicious Milk', 2, 5, 18),
                                           generate_item('Heavenly Milk', 1, 1, 50)],
                                   base_growth_rate=1,
                                   quotes=["Do you want milkies?", "*boing*", "*bouncy*", "Boing boing!",
                                           "You can touch them if you want...", "Do you want to... touch them?",
                                           "My back hurts...", "My chest hurts...", "I can give you some... milk",
                                           "Got milk?"],
                                   favorite=["Eggplant", "Banana"],
                                   img="None",
                                   buy_command="!buypet cowgirl")]
    return pet_store


def generate_pet_info(name: str, description: str, cost: int, yields: list, base_growth_rate: float, quotes: list, favorite: list, img: str, buy_command: str) -> dict:
    return {
        'name': name,
        'description': description,
        'cost': cost,
        'yields': yields,
        'base_growth_rate': base_growth_rate,
        'quotes': quotes,
        'favorite': favorite,
        'img': img,
        'buy_command': buy_command
    }


def create_pet_instance(pet_info: dict, name: str, stats: dict):
    return {
        'pet_info': pet_info,
        'name': name,
        'hunger': 100,
        'happiness': 70,
        'growth_stage': 1,
        'growth_percent': 0,
        'stats': stats
    }


async def help_prompt(msg):
    response = "Commands:\n" \
               "!shop\tShows the shop\n" \
               "!buy [item name]\tBuys an item\n" \
               "!status\tShows current game status\n" \
               "!oppai\tShows oppai balance\n" \
               "!buypet [pet type] [pet name]\tBuys a pet\n" \
               "!petstatus\tShows all your pets and their status\n" \
               "!feed [pet name] [item name]\tFeeds an item to a pet\n" \
               "!help Shows this prompt"
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
