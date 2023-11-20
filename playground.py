from openai import OpenAI
client = OpenAI()

message = "\"I AM PEEWEE AND I AM PROUUUUD\""
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": f"Create a single message that would plausibly lead to this \
     answer: {message}. Make it general, casual, and short, basically a quick text in a groupchat \
     of friends. Do not include any emojis. It doesn't have to be a question. Most importantly, \
     keep it below 10 words, make it a single sentence, and do not include the aforementioned plausible answer!"}
  ]
)

print(completion.choices[0].message)