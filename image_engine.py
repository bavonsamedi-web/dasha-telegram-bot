
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_IMAGE

client = OpenAI(api_key=OPENAI_API_KEY)

DASHA_LOOK = """
Beautiful 21-year-old woman.
Dark brown straight hair.
Soft feminine face.
Full natural lips.
Deep brown eyes.
Slim waist.
Curvy hips.
Natural proportions.
Realistic skin texture.
"""

def generate_image(scene):

    prompt = f"""
Realistic photo of Dasha.

Appearance:
{DASHA_LOOK}

Scene:
{scene}

High detail. Natural lighting.
Photorealistic.
"""

    result = client.images.generate(
        model=MODEL_IMAGE,
        prompt=prompt,
        size="1024x1024"
    )

    return result.data[0].url
