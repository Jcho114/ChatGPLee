# ChatGPLee
A GPT 3.5 based Discord bot meant to respond to users with messages resembling those of the notorious Discord user mashyy and (to an extent) his imposter rnashy. The bot is powered by a fine-tuning of OpenAI's GPT-3.5-turbo model based on a given dataset. The bot includes the ability to respond to pings, collect Discord message data of a user (admin command), and take screenshots of previous messages. The bot, at the moment, has some weird issues to fix (responding and mentioning its own prompt, repeating the user's message back to them) but it is quite comedic. 

## Public Commands

```
$help
```
Provides a summary of commands.

```
$settings
```
Provides the bot's current settings.

```
@ChatGPLee <message>
```
Format to ask @ChatGPLee a \<message\>. Uses a fine-tuned gpt3.5-turbo model to send back a response.

```
$ss <message-count>
```
Provides a screenshot of the past \<message-count\> messages in a reply chain.

## Privileged Commands

```
$history <username> <output-file-name> <limit>
```
Filters past \<limit\> messages to provide a history of \<username\> messages in jsonl format.

```
$ct <temperature>
```
Changes the current bot's temperature to \<temperature\>.
The lower the temperature, the more coherent and less creative the bot is. The opposite it true for high temperatures.

```
$cm <model>
```
Changes the current bot's model to \<model\>.
