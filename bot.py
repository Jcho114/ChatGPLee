import os
import discord
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

SYS_PROMPT = "<prompt>"

def formatter(Q, R):
        json_str = f'{{"messages": [{{"role": "system", "content": "{SYS_PROMPT}"}}, {{"role": "user", "content": "{Q}"}}, {{"role": "assistant", "content": "{R}"}}]}}'
        return json_str

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
        channels = client.get_all_channels()
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                async for message in channel.history(limit=200):
                    if message.author.name == "jcho_114":
                        res += formatter("<Q>", message.content) + '\n'
        f = open("file.txt", "w")
        f.write(res)
        f.close()
        await message.channel.send(file=discord.File("file.txt"))

client.run(os.environ.get("TOKEN"))
