import os
from openai import OpenAI
from prompt_config import DASHA_BASE_APPEARANCE, PHOTO_STYLE, NEGATIVE_PROMPT

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_dasha_image(user_scene):
    full_prompt = f"""
{DASHA_BASE_APPEARANCE}

Scene description:
{user_scene}

Style:
{PHOTO_STYLE}
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=full_prompt,
        size="1024x1024"
    )

    return result.data[0].url
