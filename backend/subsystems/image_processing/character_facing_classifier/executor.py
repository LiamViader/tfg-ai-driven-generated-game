import asyncio
import tensorflow as tf
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

class FacingDirectionClassifier:
    def __init__(self, model_path: str, img_size=(220, 300), max_batch_size=4, wait_time_ms=100):
        # Carga del modelo
        self.model = tf.keras.models.load_model(model_path)
        self.img_size = img_size  # (height, width)
        self.max_batch_size = max_batch_size
        self.wait_time = wait_time_ms / 1000
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.queue = []
        self.lock = asyncio.Lock()
        self.running = False

    def _preprocess(self, image: Image.Image) -> np.ndarray:
        # Convierte a RGBA y redimensiona
        image = image.convert("RGBA")
        image = image.resize(self.img_size)
        array = np.array(image).astype(np.float32) / 255.0  # Normaliza
        return array  # shape: (H, W, 4)

    def _predict_batch_sync(self, images: list[Image.Image]) -> list[str]:
        batch = np.stack([self._preprocess(img) for img in images])
        predictions = self.model.predict(batch, verbose=0)
        labels = (predictions > 0.5).astype(int).flatten()
        return ["left" if p == 0 else "right" for p in labels]

    async def predict(self, pil_image: Image.Image) -> str:
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async with self.lock:
            self.queue.append((pil_image, future))
            if not self.running:
                asyncio.create_task(self._run_batch())
                self.running = True

        return await future

    async def _run_batch(self):
        await asyncio.sleep(self.wait_time)
        async with self.lock:
            batch = self.queue[:self.max_batch_size]
            self.queue = self.queue[self.max_batch_size:]
            if self.queue:
                asyncio.create_task(self._run_batch())
            else:
                self.running = False

        images, futures = zip(*batch)
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(self.executor, self._predict_batch_sync, images)

        for future, result in zip(futures, results):
            future.set_result(result)