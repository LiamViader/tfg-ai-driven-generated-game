import asyncio
import base64
import os
from httpx import AsyncClient
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

API_URL = "https://vamtumkbs3pr94-5050.proxy.runpod.net/create-scenario-image"
OUTPUT_DIR = r"C:\Users\34640\OneDrive\Escritorio\GDDV\4t\TFG\tfg-ai-driven-generated-game"

payload = {
    "scene_summary": "hell",
    "scene_detail": "Golden door between lava rivers",
    "ground_detail": "cracked stone",
    "ground_summary": "dirt",
    "graphic_style": "A digital painting in a graphical cartoonish realistic art style"
}

async def generate_and_save_image(index: int):
    async with AsyncClient(timeout=300.0) as client:
        print(f"📤 Enviando petición {index}")
        response = await client.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        img_bytes = base64.b64decode(data["image_base64"])
        output_path = os.path.join(OUTPUT_DIR, f"image_{index}.png")
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        print(f"✅ Imagen {index} guardada en: {output_path}")

async def main():
    await asyncio.gather(
        generate_and_save_image(1),
        generate_and_save_image(2),
        generate_and_save_image(3),
    )

if __name__ == "__main__":
    asyncio.run(main())