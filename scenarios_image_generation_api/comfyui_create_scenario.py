import uuid
import json
import urllib.request
import urllib.parse
import base64
import random
from PIL import Image
import os
import asyncio
import websockets  # Asegúrate de instalarlo: pip install websockets
from schemas import GenerationRequest

def queue_prompt(prompt, server_address, client_id):
    data = json.dumps({"prompt": prompt, "client_id": client_id}).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_history(prompt_id, server_address):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type, server_address):
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": folder_type
    })
    with urllib.request.urlopen(f"http://{server_address}/view?{params}") as response:
        return response.read()

async def generate_image(req: GenerationRequest, server_address: str):
    client_id = str(uuid.uuid4())

    # Prompts
    general_positive_prompt = f"{req.graphic_style}. The scene depicts a {req.scene_summary}. Viewed from a human eye-level perspective. The foreground, covering the bottom 20% of the image, is a clearly visible, walkable ground made of {req.ground_detail}. It is visually separated from the rest of the scene by a sharp horizontal transition. In the background, {req.scene_detail}."
    ground_positive_prompt = f"{req.graphic_style}. Walkable, flat, homogeneous ground made of {req.ground_summary}. No obstacles, clean and continuous"

    # Load workflow
    with open("workflows/api_create_scenario.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # Modify nodes
    workflow["16"]["inputs"]["text"] = general_positive_prompt
    workflow["61"]["inputs"]["text"] = ground_positive_prompt
    workflow["3"]["inputs"]["seed"] = random.randint(1, 1000000000)

    # Send prompt first
    prompt_response = queue_prompt(workflow, server_address, client_id)
    prompt_id = prompt_response['prompt_id']

    # Async WebSocket connection
    async with websockets.connect(f"ws://{server_address}/ws?clientId={client_id}") as ws:
        while True:
            out = await ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    if message['data']['node'] is None and message['data']['prompt_id'] == prompt_id:
                        break

    # Get result
    history = get_history(prompt_id, server_address)[prompt_id]
    output_images = []
    for node in history["outputs"]:
        imgs = history["outputs"][node].get("images", [])
        for image in imgs:
            img_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
            output_images.append(img_data)

    image_bytes = output_images[0]

    # Delete image from server
    image_path = f"/workspace/ComfyUI/output/{image['subfolder']}/{image['filename']}"
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        print(f"Couldn't delete the image: {image_path}. Error: {e}")

    return base64.b64encode(image_bytes).decode("utf-8")