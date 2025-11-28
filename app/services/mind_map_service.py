import os
import base64
from datetime import datetime
from openai import OpenAI

from app.prompts.MIND_MAP_PROMPT import PROMPT_MIND_MAP_SYSTEM

client = OpenAI()


def generate_mind_map_text(material: str) -> str:
    """Generate a Markdown mind map using GPT-4.1."""
    messages = [
        {"role": "system", "content": PROMPT_MIND_MAP_SYSTEM},
        {"role": "user", "content": f"LEARNING MATERIAL:\n\n{material}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
        max_tokens=1500,
    )

    return (response.choices[0].message.content or "").strip()


def generate_mind_map_image(mind_map_text: str, output_dir="mind_maps") -> str:
    """Generate a mind map image using gpt-image-1."""
    os.makedirs(output_dir, exist_ok=True)

    visual_prompt = (
        "Create a clean, readable mind map card. "
        "Use nodes with short labels connected by lines. "
        "Follow this structure exactly:\n\n"
        f"{mind_map_text}\n\n"
        "Style: minimalistic, white background, soft pastel colors, rounded shapes."
    )

    response = client.images.generate(
        model="gpt-image-1",
        prompt=visual_prompt,
        size="1024x1024",
    )

    image_b64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_b64)

    filename = f"mindmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(output_dir, filename)

    with open(path, "wb") as f:
        f.write(image_bytes)

    return path


def generate_mind_map_card(material: str):
    """
    Full pipeline:
    1. Convert learning material → Markdown mind map
    2. Convert Markdown mind map → image
    Returns dict for DTO model.
    """
    mind_map_text = generate_mind_map_text(material)
    image_path = generate_mind_map_image(mind_map_text)

    return {
        "mind_map_text": mind_map_text,
        "image_path": image_path
    }
