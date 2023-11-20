import os
import re
import discord
import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from colorama import Fore

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

SYS_PROMPT = "You are Ryan Lee, a college student who likes videogames, memes, and anime. You have weird humor and you have many opinions."

def formatter(Q, R):
    Q, R = filter(Q), filter(R)
    json_str = f'{{"messages": [{{"role": "system", "content": "{SYS_PROMPT}"}}, {{"role": "user", "content": "{Q}"}}, {{"role": "assistant", "content": "{R}"}}]}}'
    return json_str

def filter(M):
    M = re.sub(r"<@!\d{18}>", "", M)
    M = re.sub(r"<@\d{18}>", "", M)
    M = re.sub(r"<@&\d{18}>", "", M)
    M = re.sub(r"<:.:\d{18}>", "", M)
    M = re.sub(r"\"", "", M)
    M = re.sub(r"\n", "", M)
    M = re.sub(r"^ +", "", M)
    M = re.sub(r" +$", "", M)
    M = re.sub(r" +", " ", M)
    return M

def isValidMessage(M):
    M = filter(M)
    return not M.startswith("https://") and M != "" and not re.match(r'"', M)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$history') and message.author.name == "jcho_114":
        print(Fore.GREEN + f'[{datetime.datetime.now()}::STARTING]')
        res = ''
        output_name = ''
        if re.match(r"\$history (.+) (.+)", message.content):
            username = re.match(r"\$history (.+) (.+)", message.content)[1]
            output_name = re.match(r"\$history (.+) (.+)", message.content)[2]
        else: await message.channel.send("Invalid Command Format")
        for guild in client.guilds:
            if guild == message.guild:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        prev = None
                        async for message in channel.history(limit=30000):
                            if message.author.name.lower() == username.lower() and isValidMessage(message.content):
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE FOUND] {filter(message.content)}')
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::PREVIOUS MESSAGE] {filter(prev.content) if prev else "NONE"}')
                                res += formatter(prev.content if prev else "generic message", message.content) + '\n'
                            if message.author.name.lower() != username.lower() and isValidMessage(message.content):
                                prev = message
        f = open(output_name, "w")
        f.write(res)
        f.close()
        print(Fore.GREEN + f'[{datetime.datetime.now()}::DONE]')
        await message.channel.send(file=discord.File("data.jsonl"))

client.run(os.environ.get("TOKEN"))
