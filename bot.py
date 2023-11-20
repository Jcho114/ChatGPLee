import asyncio
import os
import random
import re
import discord
import datetime
import threading
from os.path import join, dirname
from dotenv import load_dotenv
from colorama import Fore
from openai import OpenAI
from openai import RateLimitError

ai = OpenAI()
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

SYS_PROMPT = "You are Ryan Lee, a college student who likes videogames, memes, and anime. You have weird humor and you have many opinions."
MSG_PROB = 0.01

def formatter(Q, R):
    Q, R = filter(Q), filter(R)
    json_str = f'{{"messages": [{{"role": "system", "content": "{SYS_PROMPT}"}}, {{"role": "user", "content": "{Q}"}}, {{"role": "assistant", "content": "{R}"}}]}}'
    return json_str

def filter(M):
    M = re.sub(r"<@!\d{18}>", "", M)
    M = re.sub(r"<@\d{18}>", "", M)
    M = re.sub(r"<@&\d{18}>", "", M)
    M = re.sub(r"<:.+:\d{18}>", "", M)
    M = re.sub(r"\\|\"|\n", "", M)
    M = re.sub(r"^ +", "", M)
    M = re.sub(r" +$", "", M)
    M = re.sub(r" +", " ", M)
    return M

def isValidMessage(M):
    return not M.startswith("https://") and filter(M) != "" and not re.match(r'"', M)

async def generateResponse(M):
    try:
        completion = ai.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal::8Mo0BVif",
            temperature=.75,
            messages=[
                {
                    "role": "system", "content": f'You are Ryan Lee, aka ChatGPLee, a college \
                        student who likes videogames, memes, and anime. You have weird humor \
                        and you have many opinions.',
                    "role": "system", "content": f'Please respond to this message {filter(M.content)}. \
                        keep it less than 280 characters, and do not repeat anything that was \
                        mentioned here. Also do not repeat the aforementioned message.',
                }
            ]
        )
        response = completion.choices[0].message.content
        print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE GENERATED] {response}')
        await M.channel.send(f'<@{M.author.id}> {response}')
    except RateLimitError:
        print(Fore.RED + f'[{datetime.datetime.now()}::ERROR] RATE LIMIT EXCEEDED')
        await M.channel.send(random.choice(["oh no my wifi broke", "dinner time", "sorry my dad is calling me"]))
    except:
        print(Fore.RED + f'[{datetime.datetime.now()}::ERROR] UNKNOWN ERROR')
        await M.channel.send("im confused")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user.mentioned_in(message) or random.random() < MSG_PROB:
        print(Fore.GREEN + f'[{datetime.datetime.now()}::GENERATING MESSAGE] RESPONDING TO {message.author.nick}: {message.content}')
        await generateResponse(message)
        await asyncio.sleep(1)
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$history') and message.author.name == "jcho_114":
        print(Fore.GREEN + f'[{datetime.datetime.now()}::STARTING]')
        res = ''
        output_name = ''
        limit = 0
        if re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", message.content):
            username = re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", message.content)[1]
            output_name = re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", message.content)[2]
            limit = int(re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", message.content)[3])
        else: await message.channel.send("Invalid Command Format")
        for guild in client.guilds:
            if guild == message.guild:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        prev = None
                        async for message in channel.history(limit=limit):
                            if message.author.name.lower() == username.lower() and isValidMessage(message.content):
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE FOUND] {filter(message.content)}')
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::PREVIOUS MESSAGE] {filter(prev.content) if prev else "NONE"}')
                                res += formatter(prev.content if prev else "generic message", message.content) + '\n'
                            if message.author.name.lower() != username.lower() and isValidMessage(message.content):
                                prev = message
        f = open(f"{output_name}", "w")
        f.write(res[:-1])
        f.close()
        print(Fore.GREEN + f'[{datetime.datetime.now()}::DONE]')
        await message.channel.send(file=discord.File(f"{output_name}"))

client.run(os.environ.get("TOKEN"))
