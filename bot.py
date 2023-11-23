import functools
import json
import os
import random
import re
import asyncio
import discord
import datetime
from discord import app_commands
from discord.ext import commands
from os.path import join, dirname
from dotenv import load_dotenv
from colorama import Fore
from openai import OpenAI
from openai import RateLimitError
from functools import reduce

ai = OpenAI()
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)
tree = bot.tree

SYS_PROMPT = "You are Ryan Lee, a college student who likes videogames, memes, and anime. You have weird humor and you have many opinions."
MSG_PROB = 0.01
ADMIN = "jcho_114"
MODELS = {
    "MASHYY": "ft:gpt-3.5-turbo-1106:personal::8Mo0BVif",
    "MASHYY-GPT": "ft:gpt-3.5-turbo-1106:personal::8OBVMd59",
    "COMBINED-LEGACY": "ft:gpt-3.5-turbo-1106:personal::8MqQfeYh",
    "COMBINED": "ft:gpt-3.5-turbo-1106:personal::8Nxi2PqH",
}
SETTINGS = {
    "temperature": 1,
    "model": "MASHYY-GPT",
    "reply_memory": 8,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "max_chars": 500
}

def formatter(Q, R):
    Q, R = filter(Q), filter(R)
    json_str = f'{{"messages": [{{"role": "system", "content": "{SYS_PROMPT}"}}, {{"role": "user", "content": "{Q}"}}, {{"role": "assistant", "content": "{R}"}}]}}'
    return json_str

def filter(M):
    M = re.sub(r"<@!\d{18,}>", "", M)
    M = re.sub(r"<@\d{18,}>", "", M)
    M = re.sub(r"<@&\d{18,}>", "", M)
    M = re.sub(r"<:.+:\d{18,}>", "", M)
    M = re.sub(r"\\|\"|\n", "", M)
    M = re.sub(r"^ +", "", M)
    M = re.sub(r" +$", "", M)
    M = re.sub(r" +", " ", M)
    return M

def isValidMessage(M):
    return not M.startswith("https://") and filter(M) != "" and not re.match(r'"', M)

def to_thread(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

async def generateResponse(ctx):
    async def replyHistory(ctx):
        res = [filter(ctx.content)]
        count = 0
        while ctx.reference and count < SETTINGS["reply_memory"]:
            channel = bot.get_channel(ctx.reference.channel_id)
            ctx = await channel.fetch_message(ctx.reference.message_id)
            filtered = filter(ctx.content)
            res.append(filtered)
            count += 1
        return res
    def addToPromptList(history, prompts):
        messages = set()
        while len(history) > 1:
            m1, m2 = history.pop(), history.pop()
            if m1 not in messages and m2 not in messages:
                prompts.append({"role": "user", "content": m1})
                prompts.append({"role": "assistant", "content": m2})
            messages.add(m1)
            messages.add(m2)
        if len(history):
            latest_message = history.pop()
            prompts.append({"role": "user", "content": latest_message})
        print(format(json.dumps(prompts, indent=2)))
    def completeScenario(prev_messages):
        return ai.chat.completions.create(
            model=f'{MODELS[SETTINGS["model"]]}',
            temperature=SETTINGS["temperature"],
            messages=prev_messages,
            frequency_penalty=SETTINGS["frequency_penalty"],
            presence_penalty=SETTINGS["presence_penalty"],
            max_tokens=SETTINGS["max_chars"]
        )
    try:
        prev_messages = [
            {"role": "system", "content": f'You are Ryan Lee, a college student who likes videogames, memes, and anime. You have weird humor and you have many opinions. You are creative, and you don\'t like to repeat what people say.'}
        ]
        replies = await replyHistory(ctx)
        addToPromptList(replies, prev_messages)
        completion = completeScenario(prev_messages)
        response = completion.choices[0].message.content
        print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE GENERATED] {response}')
        await ctx.reply(f'{response}', mention_author=False)
    except RateLimitError:
        print(Fore.RED + f'[{datetime.datetime.now()}::ERROR] RATE LIMIT EXCEEDED')
        await ctx.channel.send(random.choice(["oh no my wifi broke", "dinner time", "sorry my dad is calling me"]))

tree.remove_command("help")

def encodeSettings():
    return reduce(lambda acc, el: acc + f'{el}: {SETTINGS[el]}, ', SETTINGS.keys(), "")[:-2]

@tree.command(name="help", description="Provides a summary of commands.")
async def help(interaction):
    print(Fore.GREEN + f'[{datetime.datetime.now()}::PROVIDING MANUEL]')
    embed = discord.Embed(title="ChatGPLee Commands", description="A list of commands for ChatGPLee")
    embed.add_field(name="$help", value="Provides a summary of commands.", inline=False)
    embed.add_field(name="$settings", value="Provides the bot's current settings.", inline=False)
    embed.add_field(name="@ChatGPLee <message>", value="Format to ask @ChatGPLee a <message>. Uses a fine-tuned gpt3.5-turbo model to send back a response.", inline=False)
    embed.add_field(name="$ss <message-count>", value="Provides a screenshot of the past <message-count> messages in a reply chain.", inline=False)
    if interaction.user.name == "jcho_114":
        embed.add_field(name="**privileged** $history <username> <output-file-name> <limit>", value="Filters past <limit> messages to provide a history of <username> messages in jsonl format.", inline=False)
        embed.add_field(name="**privileged** $ct <temperature>", value="Changes the current bot's temperature to <temperature>. The lower the temperature, the more coherent and less creative the bot is. The opposite it true for high temperatures.", inline=False)
        embed.add_field(name="**privileged** $cm <model>", value="Changes the current bot's model to <model>.", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="settings", description="Provides the bot's current settings.")
async def settings(interaction):
    print(Fore.GREEN + f'[{datetime.datetime.now()}::PROVIDING SETTINGS]')
    await interaction.response.send_message(codeblock(encodeSettings()))

async def checkPermissions(interaction):
    if interaction.user.name == ADMIN:
        return True
    else:
        await interaction.followup.send("Access Denied")
        return False

@tree.command(name="ct", description="Changes the current bot's temperature to <temperature>.")
@app_commands.describe(temperature="float between 0 (inclusive) and 2 (noninclusive)")
async def ct(interaction, temperature: float):
    if await checkPermissions(interaction):
        if temperature > 0 and temperature <= 2.0:
            SETTINGS["temperature"] = temperature
            print(Fore.GREEN + f'[{datetime.datetime.now()}::CHANGING TEMPERATURE] NEW TEMPERATURE: {temperature}')
            await interaction.response.send_message(codeblock(f'Changed temperature of model {SETTINGS["model"]} to {SETTINGS["temperature"]}'))
        else:
            print(Fore.RED + f'[{datetime.datetime.now()}::INVALID INPUT] FOR COMMAND $ct')
            await interaction.response.send_message(codeblock(f'Invalid parameters, maintaining current settings ({encodeSettings()})'))

@tree.command(name="cm", description="Changes the current bot's model to <model>.")
@app_commands.describe(model="Any of the following: COMBINED, MASHYY, COMBINED-LEGACY")
async def cm(interaction, model: str):
    if await checkPermissions(interaction):
        if model in MODELS:
            SETTINGS["model"] = model
            print(Fore.GREEN + f'[{datetime.datetime.now()}::CHANGING MODEL] NEW MODEL: {model}')
            await interaction.reply.send_message(codeblock(f'Changed model of model {SETTINGS["model"]} to {SETTINGS["model"]}'))
        else:
            print(Fore.RED + f'[{datetime.datetime.now()}::INVALID INPUT] FOR COMMAND $cm')
            await interaction.response.send_message(codeblock(f'Invalid parameters, maintaining current settings ({encodeSettings()})'))

@tree.command(name="cmc", description="Changes the current bot's max characters to <max_chars>.")
@app_commands.describe(max_chars="int between 10 and 1000 inclusive")
async def cmc(interaction, max_chars: int):
    if await checkPermissions(interaction):
        if max_chars >= 10 and max_chars <= 1000:
            SETTINGS["max_chars"] = max_chars
            print(Fore.GREEN + f'[{datetime.datetime.now()}::CHANGING MAX_CHARS] NEW MAX_CHARS: {max_chars}')
            await interaction.reply.send_message(codeblock(f'Changed max_chars of model {SETTINGS["model"]} to {SETTINGS["max_chars"]}'))
        else:
            print(Fore.RED + f'[{datetime.datetime.now()}::INVALID INPUT] FOR COMMAND $cmc')
            await interaction.response.send_message(codeblock(f'Invalid parameters, maintaining current settings ({encodeSettings()})'))

@tree.command(name="crm", description="Changes the current bot's reply memory to <reply_memory>.")
@app_commands.describe(reply_memory="int between 1 and 10 (inclusive)")
async def crm(interaction, reply_memory: int):
    if await checkPermissions(interaction):
        if reply_memory > 0 and reply_memory <= 10:
            SETTINGS["reply_memory"] = reply_memory
            print(Fore.GREEN + f'[{datetime.datetime.now()}::CHANGING MAX_CHARS] NEW MAX_CHARS: {reply_memory}')
            await interaction.reply.send_message(codeblock(f'Changed max_chars of model {SETTINGS["model"]} to {SETTINGS["reply_memory"]}'))
        else:
            print(Fore.RED + f'[{datetime.datetime.now()}::INVALID INPUT] FOR COMMAND $crm')
            await interaction.response.send_message(codeblock(f'Invalid parameters, maintaining current settings ({encodeSettings()})'))

@tree.command(name="history", description="Filters past <limit> messages to provide a history of <username> messages in jsonl format.")
@app_commands.describe(username="username of target", output_name="name of jsonl file", generation_method="one of GPT and PREV", limit="number of past messages bot looks through")
async def history(interaction, username: str, output_name: str, generation_method: str, limit: int):
    async def prev(limit):
        nonlocal res
        prev = None
        async for message in channel.history(limit=limit):
            if message.author.name.lower() == username.lower() and isValidMessage(message.content):
                print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE FOUND] {filter(message.content)}')
                print(Fore.GREEN + f'[{datetime.datetime.now()}::PREVIOUS MESSAGE] {filter(prev.content) if prev else "NONE"}')
                res += formatter(prev.content if prev else "generic message", message.content) + '\n'
            if message.author.name.lower() != username.lower() and isValidMessage(message.content):
                prev = message
    @to_thread
    def generateQuestion(response):
        completion = ai.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            max_tokens=random.randint(20,60),
            messages=[
                {"role": "system", "content": f"Create a single message that would plausibly lead to this response: \"{response}\". "
                 + "Make it general, casual, and short, basically a quick text in a groupchat of friends. Do not include any "
                 + "emojis. It doesn't have to be a question."}
            ]
        )
        return completion.choices[0].message.content
    async def gpt(limit):
        nonlocal res
        async for message in channel.history(limit=limit):
            if message.author.name.lower() == username.lower() and isValidMessage(message.content):
                print(Fore.GREEN + f'[{datetime.datetime.now()}::MESSAGE FOUND] {filter(message.content)}')
                question = await generateQuestion(message.content)
                res += formatter(question, message.content) + '\n'
                print(Fore.GREEN + f'[{datetime.datetime.now()}::GENERATED QUESTION] {filter(question)}')
    print(Fore.GREEN + f'[{datetime.datetime.now()}::STARTING HISTORY]')
    await interaction.response.defer()
    if await checkPermissions(interaction):
        res = ''
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel):
                if generation_method == "PREV":
                    await prev(limit)
                elif generation_method == "GPT":
                    await gpt(limit)
                else:
                    await interaction.response.send_message("Invalid Command Format")
        f = open(f"{output_name}", "w")
        f.write(res[:-1])
        f.close()
        print(Fore.GREEN + f'[{datetime.datetime.now()}::DONE]')
        await interaction.followup.send(file=discord.File(f"{output_name}"))

@tree.command(name="sync", description="Syncs commands")
async def sync(interaction):
    if await checkPermissions(interaction):
        try:
            synced = await tree.sync()
            message = f'Synced {len(synced)} command(s)'
            print(message)
            await interaction.response.send_message(message)
        except Exception as e:
            print(e)
            await interaction.response.send_message("Failed to sync command(s)")

def codeblock(M):
    return f'```python\n{M}\n```'

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message) or random.random() < MSG_PROB:
        print(Fore.GREEN + f'[{datetime.datetime.now()}::GENERATING MESSAGE] RESPONDING TO {message.author.nick}: {message.content}')
        await generateResponse(message)
    await bot.process_commands(message)

bot.run(os.environ.get("TOKEN"))
