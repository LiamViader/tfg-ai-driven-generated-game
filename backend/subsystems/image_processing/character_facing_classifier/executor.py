import asyncio
import os
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor

import keras
import numpy as np
from PIL import Image

class FacingDirectionClassifier:
    def __init__(self, model_path: str, img_size=(220, 300), max_batch_size=32, wait_time_ms=100):
        # --- Configuración del Modelo y Rutas ---
        self.model = keras.models.load_model(model_path) # type: ignore
        self.img_size = img_size
        
        self.temp_dir = os.path.join("images", "temp_predict")
        self.predict_dir = os.path.join(self.temp_dir, "predict_images")

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.predict_dir)

        # --- Configuración de Concurrencia ---
        self.max_batch_size = max_batch_size
        self.wait_time = wait_time_ms / 1000.0
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.queue = []
        self.lock = asyncio.Lock()
        self.running = False

    def _process_batch_from_disk_sync(self, batch_to_process: list) -> dict:
        file_paths_in_batch = [info[0] for info in batch_to_process]
        
        try:
            temp_ds = keras.utils.image_dataset_from_directory(
                directory=self.temp_dir,
                labels=None, # type: ignore
                image_size=self.img_size,
                batch_size=self.max_batch_size,
                shuffle=False,
                color_mode="rgba"
            )
            
            raw_predictions = self.model.predict(temp_ds, verbose=0) # type: ignore
            
            predicted_labels = (raw_predictions > 0.5).astype(int).flatten()
            labels = ["left" if p == 0 else "right" for p in predicted_labels]
            
            # ✅ Silenciamos el falso error de Pylance aquí
            results_map = dict(zip(temp_ds.file_paths, labels)) # type: ignore
            return results_map

        finally:
            for path in file_paths_in_batch:
                if os.path.exists(path):
                    os.remove(path)

    async def predict(self, pil_image: Image.Image) -> str:
        unique_filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(self.predict_dir, unique_filename)
        pil_image.save(file_path, "PNG")
        
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async with self.lock:
            self.queue.append((file_path, future))
            if not self.running:
                self.running = True
                asyncio.create_task(self._run_batch())

        return await future

    async def _run_batch(self):
        await asyncio.sleep(self.wait_time)
        
        async with self.lock:
            batch_to_process = self.queue[:self.max_batch_size]
            self.queue = self.queue[self.max_batch_size:]
            
            if self.queue:
                asyncio.create_task(self._run_batch())
            else:
                self.running = False

        if not batch_to_process:
            return

        futures_map = {path: future for path, future in batch_to_process}
        
        loop = asyncio.get_running_loop()
        try:
            results_map = await loop.run_in_executor(
                self.executor, self._process_batch_from_disk_sync, batch_to_process
            )
            for path, result in results_map.items():
                if path in futures_map:
                    futures_map[path].set_result(result)
        except Exception as e:
            for future in futures_map.values():
                if not future.done():
                    future.set_exception(e)