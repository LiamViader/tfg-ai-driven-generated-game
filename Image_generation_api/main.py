from fastapi import FastAPI
from schemas import GenerationRequest
import asyncio
from comfyui_create_scenario import generate_image

app = FastAPI()

# Single ComfyUI server
COMFYUI_SERVER = "127.0.0.1:3020"

generation_queue = asyncio.Queue()

@app.post("/generate")
async def generate(req: GenerationRequest):
    print("GOT REQUEST")
    fut = asyncio.get_event_loop().create_future()
    await generation_queue.put((req, fut))
    return await fut

async def worker():
    while True:
        req, fut = await generation_queue.get()
        try:
            image_base64 = await generate_image(req, COMFYUI_SERVER)
            fut.set_result({"image_base64": image_base64})
        except Exception as e:
            fut.set_exception(e)
        generation_queue.task_done()

async def preload_models():
    print("🚀 Preloading models on ComfyUI server...")
    dummy_req = GenerationRequest(
        scene_summary="a simple scene",
        scene_detail="a basic background",
        ground_detail="plain ground",
        ground_summary="ground",
        graphic_style="sketch"
    )
    try:
        await generate_image(dummy_req, COMFYUI_SERVER)
        print("✅ Preload complete.")
    except Exception as e:
        print(f"⚠️ Preload failed: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker())
    await preload_models()
