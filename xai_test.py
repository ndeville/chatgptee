import os

from dotenv import load_dotenv
load_dotenv()

NIC_XAI_API_KEY = os.getenv("NIC_XAI_API_KEY")


# In your terminal, first run:
# pip install openai
from openai import OpenAI

client = OpenAI(
    api_key=NIC_XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

completion = client.chat.completions.create(
    model="grok-2-latest",
    messages=[
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        },
    ],
)

print(completion.choices[0].message.content)