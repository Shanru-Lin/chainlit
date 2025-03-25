import chainlit as cl
import json
import time
from openai import OpenAI

# Load secrets
with open("secrets.json") as f:
    secrets = json.load(f)

client = OpenAI(api_key=secrets["openai_api_key"])

MODEL_NAME = "gpt-3.5-turbo"
SYSTEM_PROMPT = """You are CritiqueAI, an assistant specialized in analyzing and critiquing various forms of media and art. 
Follow these specific guidelines:
1. Always structure your responses with a brief summary, followed by 3-5 bullet points of critique, and end with a rating out of 10
2. Use industry-specific terminology relevant to the medium being discussed
3. Compare to similar works in the same genre or by the same creator
4. Include one surprising or controversial opinion in each response
5. Suggest one specific improvement that could have made it better
6. Your tone should be witty and slightly sardonic, but knowledgeable"""

MAX_TOKENS = 500
TEMPERATURE = 0.9

# Add some visual flair with emojis for different media types
MEDIA_ICONS = {
    "movies": "🎬",
    "music": "🎵",
    "books": "📚",
    "games": "🎮",
    "art": "🖼️",
    "tv": "📺",
    "food": "🍽️",
    "technology": "💻",
    "general": "🔍"
}

@cl.on_chat_start
async def start():
    # Send welcome message with media options
    welcome_message = """# Welcome to CritiqueAI! 

I can provide insightful analysis and witty critiques of various media types:

- 🎬 **Movies**
- 🎵 **Music**
- 📚 **Books**
- 🎮 **Games**
- 📺 **TV Shows**
- 🍽️ **Food**
- 💻 **Technology**

What would you like me to critique today? Simply ask about any movie, album, book, game, or other creative work!
    """
    
    await cl.Message(content=welcome_message).send()

@cl.on_message
async def handle_message(message: cl.Message):
    start_time = time.time()
    
    # Detect media type from message
    media_type = detect_media_type(message.content)
    icon = MEDIA_ICONS.get(media_type, "🔍")
    
    # OpenAI API call
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message.content}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

    response = completion.choices[0].message.content
    usage = getattr(completion.usage, "total_tokens", "?")
    latency = round(time.time() - start_time, 2)

    # Format the response with the media icon
    formatted_response = f"{icon} **CRITIQUE** {icon}\n\n{response}"
    
    # Send the response
    await cl.Message(content=formatted_response, author="CritiqueAI").send()
    
    # Send analytics as a separate message
    analytics = f"**Model**: {MODEL_NAME} | **Tokens**: {usage} | **Response Time**: {latency}s"
    
    await cl.Message(content=analytics, author="system").send()

def detect_media_type(message):
    """Simple function to guess the media type based on message content"""
    message = message.lower()
    
    if any(word in message for word in ["movie", "film", "watch", "cinema", "actor", "director"]):
        return "movies"
    elif any(word in message for word in ["song", "album", "music", "band", "artist", "listen"]):
        return "music"
    elif any(word in message for word in ["book", "novel", "author", "read", "writer"]):
        return "books"
    elif any(word in message for word in ["game", "play", "gaming", "console", "xbox", "playstation"]):
        return "games"
    elif any(word in message for word in ["show", "series", "episode", "season", "television"]):
        return "tv"
    elif any(word in message for word in ["food", "restaurant", "dish", "menu", "chef", "taste"]):
        return "food"
    elif any(word in message for word in ["tech", "gadget", "device", "computer", "phone", "software"]):
        return "technology"
    
    return "general"