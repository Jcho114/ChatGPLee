# ChatGPLee

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