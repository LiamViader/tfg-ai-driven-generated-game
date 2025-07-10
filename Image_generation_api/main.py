from fastapi import FastAPI
from schemas import GenerationRequest
import asyncio
from comfyui_create_scenario import generate_image

app = FastAPI()

# List of comfyui servers
COMFYUI_SERVERS = ["127.0.0.1:3020", "127.0.0.1:3021"]
NUM_SERVERS = len(COMFYUI_SERVERS)
generation_queue = asyncio.Queue()

# Índex to balance
server_index = 0

@app.post("/generate")
async def generate(req: GenerationRequest):
    fut = asyncio.get_event_loop().create_future()
    await generation_queue.put((req, fut))
    return await fut

async def worker():
    global server_index
    while True:
        req, fut = await generation_queue.get()

        # cyclic assign
        server_address = COMFYUI_SERVERS[server_index]
        server_index = (server_index + 1) % NUM_SERVERS

        try:
            image_base64 = await generate_image(req, server_address)
            fut.set_result({"image_base64": image_base64})
        except Exception as e:
            fut.set_exception(e)
        generation_queue.task_done()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker())