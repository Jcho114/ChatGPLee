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

SYS_PROMPT = "<prompt>"

def formatter(Q, R):
    R = re.sub("\s<@!\d{18}>\s", "", R)
    R = re.sub("\s<@\d{18}>\s", "", R)
    R = re.sub("\s<:.:\d{18}>\s", "", R)
    json_str = f'{{"messages": [{{"role": "system", "content": "{SYS_PROMPT}"}}, {{"role": "user", "content": "{Q}"}}, {{"role": "assistant", "content": "{R}"}}]}}'
    return json_str

def isValidMessage(M):
    M = re.sub("\s<@!\d{18}>\s", "", M)
    M = re.sub("\s<@\d{18}>\s", "", M)
    M = re.sub("\s<:.:\d{18}>\s", "", M)
    return not M.content.startswith("https://") and M.content != "" and not re.match(r'^"', M.content)

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
        res = ''
        if re.match(r"\$history (.+)", message.content):
            username = re.match(r"\$history (.+)", message.content)[1]
        else: await message.channel.send("Invalid Command Format")
        for guild in client.guilds:
            if guild == message.guild:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        async for message in channel.history(limit=30000):
                            if message.author.name.lower() == username.lower() and isValidMessage(message):
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE FOUND] {message.content}')
                                res += formatter("<Q>", message.content) + '\n'
        f = open(".txt", "w")
        f.write(res)
        f.close()
        print(Fore.GREEN + f'[{datetime.datetime.now()}::DONE]')
        await message.channel.send(file=discord.File(".txt"))

client.run(os.environ.get("TOKEN"))
