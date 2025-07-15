import os
import asyncio
from PIL import Image
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.image_processing.character_facing_classifier.executor import FacingDirectionClassifier  # Ajusta la ruta si es necesario

# Ruta de test
LEFT_DIR = "images/predict_facing_test/left"
RIGHT_DIR = "images/predict_facing_test/right"
MODEL_PATH = "models/facing_direction_classifier_v1.keras"

# Tamaño de imagen usado en el entrenamiento
IMG_SIZE = (220, 300)

# Carga del clasificador
classifier = FacingDirectionClassifier(model_path=MODEL_PATH, img_size=IMG_SIZE)

async def classify_folder(folder_path, expected_label):
    errors = 0
    total = 0
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue

        image_path = os.path.join(folder_path, filename)
        image = Image.open(image_path)

        predicted = await classifier.predict(image)

        total += 1
        if predicted != expected_label:
            print(f"❌ {filename}: predicted {predicted}, expected {expected_label}")
            errors += 1
        else:
            print(f"✅ {filename}: {predicted}")

    return total, errors

async def main():
    print("🔍 Testing images facing LEFT...")
    total_left, errors_left = await classify_folder(LEFT_DIR, "left")

    print("\n🔍 Testing images facing RIGHT...")
    total_right, errors_right = await classify_folder(RIGHT_DIR, "right")

    total_images = total_left + total_right
    total_errors = errors_left + errors_right
    accuracy = 100 * (1 - total_errors / total_images) if total_images else 0

    print("\n📊 --- Final Report ---")
    print(f"Total images: {total_images}")
    print(f"Correct predictions: {total_images - total_errors}")
    print(f"Errors: {total_errors}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())