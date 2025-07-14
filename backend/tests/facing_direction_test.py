import asyncio
import base64
import os
from typing import List, Dict, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# --- Configuración y Schemas ---
# Definimos los modelos Pydantic necesarios para la salida estructurada.

class FacingDirectionStructure(BaseModel):
    """Define la estructura de la respuesta que esperamos del LLM."""
    reasoning: str = Field(
        description="A step-by-step analysis of the character's orientation. Do you see a character? If so, is the character's body oriented more towards the left edge of the frame, or the right edge of the frame? Provide a detailed reasoning before concluding."
    )
    facing_direction: Literal["left", "right"] = Field(
        description="The final conclusion, either 'left' or 'right'."
    )
    clothing_colors: str = Field(
        description="The colors of the character's clothing, if visible. If not visible, return 'unknown'."
    )

# --- Cliente del LLM ---
# Inicializamos el cliente del modelo multimodal que vamos a usar.
# La temperatura se pone a 0.0 para que la respuesta sea lo más determinista posible.
llm_multimodal = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
)
# Creamos una cadena que fuerza al LLM a devolver una salida con la estructura de nuestro modelo.
structured_multimodal_llm = llm_multimodal.with_structured_output(FacingDirectionStructure)


async def analyze_image_direction(image_path: str):
    """
    Analiza una única imagen para determinar la dirección a la que mira el personaje.
    Imprime los datos enviados y recibidos para depuración.
    """
    print(f"\n{'='*20}\n--- ANALIZANDO IMAGEN: {image_path} ---\n{'='*20}")

    try:
        # 1. Leer y codificar la imagen en base64
        with open(image_path, "rb") as image_file:
            image_b64 = base64.b64encode(image_file.read()).decode("utf-8")
        print("  - ✅ Imagen leída y codificada en base64.")

        # 2. Construir el prompt y el mensaje para la API
        analysis_prompt_text = (
            """You are given an image of a character. Your task is to determine whether the character is facing toward the **left side of the image** or the **right side of the image** — from the viewer's perspective.

            IMPORTANT CLARIFICATION:
            - "Left" means the character is facing toward the **left side of the image** (the left edge of the frame as seen by the viewer).
            - "Right" means the character is facing toward the **right side of the image** (the right edge of the frame as seen by the viewer).
            - This is not about the character's own left or right — it is from the viewer’s perspective only.

            Use these cues to decide:
            1. Eye direction: Where are the pupils pointing? Left or right in the frame?
            2. Nose direction: Which edge of the frame is the nose pointing toward?
            3. Face angle: Is one side of the face more visible than the other?
            4. Body posture: Use only if face and eyes are ambiguous.

            Return a detailed reasoning and a final answer: "left" or "right" (from the viewer's point of view).
            """
        )

        prompt_message = HumanMessage(
            content=[
                {"type": "text", "text": analysis_prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
            ]
        )

        # 3. Imprimir el mensaje que se va a enviar (para depuración)
        print("\n--- 📤 MENSAJE ENVIADO A LA API ---")
        # Hacemos una representación más legible del contenido
        print(f"  - Texto: {prompt_message}")
        print(f"  - Imagen: data:image/png;base64,[...{len(image_b64)} bytes...]")
        print("------------------------------------")


        # 4. Llamar al LLM y obtener la respuesta
        print("\n  - ⏳ Esperando respuesta del modelo...")
        response = await structured_multimodal_llm.ainvoke([prompt_message])

        # 5. Imprimir la respuesta recibida (para depuración)
        print("\n--- 📥 RESPUESTA RECIBIDA DE LA API ---")
        print(f"  - Tipo de objeto: {type(response)}")
        print(f"  - Contenido: {response}")
        print("--------------------------------------")

        # 6. Imprimir el resultado final extraído
        if isinstance(response, FacingDirectionStructure):
            print(f"\n--- ✅ RESULTADO FINAL ---")
            print(f"  - Dirección detectada: {response.facing_direction}")
            print("-------------------------")
        else:
            print("\n--- ⚠️ ADVERTENCIA ---")
            print("  - La respuesta no es del tipo esperado 'FacingDirectionStructure'.")
            print("-------------------")


    except FileNotFoundError:
        print(f"\n--- ❌ ERROR: Archivo de prueba no encontrado en '{image_path}'. Por favor, asegúrate de que existe. ---")
    except Exception as e:
        print(f"\n--- ❌ ERROR INESPERADO: {e} ---")

async def main():
    """Punto de entrada principal para el script de depuración."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: La variable de entorno OPENAI_API_KEY no está configurada. Asegúrate de tener un archivo .env.")
        return

    # --- CONFIGURACIÓN DE LA PRUEBA ---
    # Cambia esta ruta a la imagen que quieras probar.
    image_to_test = os.path.join("images", "characters", "character_004_2.png")
    
    await analyze_image_direction(image_to_test)

if __name__ == "__main__":
    asyncio.run(main())