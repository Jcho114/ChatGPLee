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
MODELS = {
    "MASHYY": "ft:gpt-3.5-turbo-1106:personal::8Mo0BVif",
    "COMBINED": "ft:gpt-3.5-turbo-1106:personal::8MqQfeYh"
}
SETTINGS = {
    "temperature": 1.0,
    "model": "COMBINED"
}

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
            model=f'{MODELS[SETTINGS["model"]]}',
            temperature=SETTINGS["temperature"],
            messages=[
                {
                    "role": "system", "content": f'You are Ryan Lee, aka ChatGPLee, a college student who likes videogames, memes, and anime. You have weird humor and you have many opinions.',
                    "role": "system", "content": f'Please respond to this message {filter(M.content)}. keep it less than 280 characters, and do not repeat anything that was mentioned here. Also do not repeat the aforementioned message.',
                }
            ]
        )
        response = completion.choices[0].message.content
        print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE GENERATED] {response}')
        await M.channel.send(f'<@{M.author.id}> {response}')
    except RateLimitError:
        print(Fore.RED + f'[{datetime.datetime.now()}::ERROR] RATE LIMIT EXCEEDED')
        await M.channel.send(random.choice(["oh no my wifi broke", "dinner time", "sorry my dad is calling me"]))

async def history(M):
        print(Fore.GREEN + f'[{datetime.datetime.now()}::STARTING]')
        res = ''
        output_name = ''
        limit = 0
        if re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", M.content):
            username = re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", M.content)[1]
            output_name = re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", M.content)[2]
            limit = int(re.match(r"\$history (.+) (.+) ([1-9][0-9]*)", M.content)[3])
        else: await M.channel.send("Invalid Command Format")
        for guild in client.guilds:
            if guild == M.guild:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        prev = None
                        async for M in channel.history(limit=limit):
                            if M.author.name.lower() == username.lower() and isValidMessage(M.content):
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE FOUND] {filter(M.content)}')
                                print(Fore.GREEN + f'[{datetime.datetime.now()}::PREVIOUS MESSAGE] {filter(prev.content) if prev else "NONE"}')
                                res += formatter(prev.content if prev else "generic message", M.content) + '\n'
                            if M.author.name.lower() != username.lower() and isValidMessage(M.content):
                                prev = M
        f = open(f"{output_name}", "w")
        f.write(res[:-1])
        f.close()
        print(Fore.GREEN + f'[{datetime.datetime.now()}::DONE]')
        await M.channel.send(file=discord.File(f"{output_name}"))

async def ct(M):
    if re.match(r'^\$ct (0.\d+|1|1.\d+|2|2.0)$', M.content):
        temperature = float(re.match(r'^\$ct (0.\d+|1|1.\d+|2|2.0)$', M.content)[1])
        if temperature > 0 and temperature <= 2.0:
            SETTINGS["temperature"] = temperature
        print(Fore.GREEN + f'[{datetime.datetime.now()}::CHANGING TEMPERATURE] NEW TEMPERATURE: {temperature}')
        await M.channel.send(codeblock(f'Changed temperature of model {SETTINGS["model"]} to {SETTINGS["temperature"]}'))
    else:
        print(Fore.RED + f'[{datetime.datetime.now()}::INVALID INPUT] FOR COMMAND $ct')
        await M.channel.send(codeblock(f'Invalid parameters, maintaining current settings (model: {SETTINGS["model"]}, temperature: {SETTINGS["temperature"]})'))

async def cm(M):
    if re.match(r'^\$cm (MASHYY|COMBINED)$', M.content):
        model = re.match(r'^\$cm (MASHYY|COMBINED)$', M.content)[1]
        SETTINGS["model"] = model
        print(Fore.GREEN + f'[{datetime.datetime.now()}::CHANGING MODEL] NEW MODEL: {model}')
        await M.channel.send(codeblock(f'Changed model to {SETTINGS["model"]}'))
    else:
        print(Fore.RED + f'[{datetime.datetime.now()}::INVALID INPUT] FOR COMMAND $cm')
        await M.channel.send(codeblock(f'Invalid parameters, maintaining current settings (model: {SETTINGS["model"]}, temperature: {SETTINGS["temperature"]})'))

async def help(M):
    embed = discord.Embed(title="ChatGPLee Commands", description="A list of commands for ChatGPLee")
    embed.add_field(name="$help", value="Provides a summary of commands.", inline=False)
    embed.add_field(name="$settings", value="Provides the bot's current settings.", inline=False)
    embed.add_field(name="@ChatGPLee <message>", value="Format to ask @ChatGPLee a <message>. Uses a fine-tuned gpt3.5-turbo model to send back a response.", inline=False)
    embed.add_field(name="$ss <message-count>", value="Provides a screenshot of the past <message-count> messages in a reply chain.", inline=False)
    if M.author.name == "jcho_114":
        embed.add_field(name="**privileged** $history <username> <output-file-name> <limit>", value="Filters past <limit> messages to provide a history of <username> messages in jsonl format.", inline=False)
        embed.add_field(name="**privileged** $ct <temperature>", value="Changes the current bot's temperature to <temperature>. The lower the temperature, the more coherent and less creative the bot is. The opposite it true for high temperatures.", inline=False)
        embed.add_field(name="**privileged** $cm <model>", value="Changes the current bot's model to <model>.", inline=False)
    await M.channel.send(embed=embed)

def codeblock(M):
    return f'```python\n{M}\n```'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # public commands
    if message.content == '$help':
        print(Fore.GREEN + f'[{datetime.datetime.now()}::PROVIDING MANUEL]')
        await help(message)
    if message.content == '$settings':
        print(Fore.GREEN + f'[{datetime.datetime.now()}::PROVIDING SETTINGS]')
        await message.channel.send(codeblock(f'mode: {SETTINGS["model"]}, temperature: {SETTINGS["temperature"]}'))
    if client.user.mentioned_in(message) or random.random() < MSG_PROB:
        print(Fore.GREEN + f'[{datetime.datetime.now()}::GENERATING MESSAGE] RESPONDING TO {message.author.nick}: {message.content}')
        await generateResponse(message)
        await asyncio.sleep(1)
    # privileged commands
    if message.author.name == "jcho_114":
        if message.content.startswith('$history'):
            await history(message)
        if message.content.startswith("$ct"):
            await ct(message)
        if message.content.startswith("$cm"):
            await cm(message)

client.run(os.environ.get("TOKEN"))
