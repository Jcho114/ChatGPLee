from openai import OpenAI
import random

ai = OpenAI()

response = "not down for jackbox"

completion = ai.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            max_tokens=60,
            messages=[
                {"role": "system", "content": f"You are Ryan Lee, a college student who likes videogames, memes, and anime. "
                 + "You have weird humor and you have many opinions."},
                {"role": "system", "content": f"Create a single message that would lead to this response: \"{response}\". "
                 + "Make it general, casual, and short, basically a quick text in a groupchat of friends. Do not include any "
                 + "emojis. It doesn't have to be a question. Do not repeat the original message verbatim."}
            ]
        )
print(completion.choices[0].message.content)