from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from core_game.character.schemas import CharacterBaseModel
from typing import Any
from pydantic import BaseModel
import json

def _model_dump(value: Any) -> Any:
    """
    Safely dump a value. If it's a Pydantic model, dump it to a dict.
    Otherwise, return the value as is.
    """
    if isinstance(value, BaseModel):
        if hasattr(value, "model_dump"):
            return value.model_dump()
        return value.dict() 
    return value

SYSTEM_PROMPT = """
You are an expert art director and character concept artist. Your task is to write a single, cohesive, and vivid visual description paragraph for a video game character based on the structured data provided.

---
### CRITICAL INSTRUCTIONS

#### 1. **Prioritization and Inference:**
   - **Filter and Prioritize:** Your primary goal is to capture the CHARACTER'S ESSENCE. From all the data provided, you must select and emphasize the most **unique, important, and defining** features.
   - **Contextual Inference:** Actively use the `Game Context` to infer and add logical visual details that are not explicitly stated in the character description but make sense for a character in that world and you are sure the character has it. IMPORTANT, If a trait of the character is particularly relevant to the story or world, it must be included.
   - **Conciseness:** The description should be rich in detail but concise. Aim for a maximum length of 80-100 words.
   - **Don't List:** Your output must be a single, well-written paragraph. Do not use bullet points or any other structured format. Weave the details together naturally.

#### 2. **Required Descriptive Elements:**
   - Your description **might** (if suitable for the character(sometimes might not be suitable)) cover the following aspects, among others you deem relevant:
     - **Apparent Age & Gender:** How old and what gender the character appears to be.
     - **Eyes & Skin Tone:** The color and shape of their eyes, and the tone of their skin.
     - **Body:** Build, height.
     - **Face:** Shape, structure, and notable features.
     - **Hair:** Color, style, and condition.
     - **Clothing:** The style, condition, layers of their attire, and clothes they are wearing.
     - **Carried Items:** Any weapons, tools, or personal effects they have on them.
     - **Key Traits:** Visible personality traits reflected in their expression, or features.


#### 3. **Strict Content Boundaries:**
   - **Permitted Content:** Describe **only** the character's physical appearance.
   - **Forbidden Content (DO NOT INCLUDE):**
     - **NO Artistic Style:** Avoid terms like 'digital painting', 'anime style', 'photorealistic', etc.
     - **NO Image Composition:** Avoid terms like 'full body shot', 'portrait', 'close-up', 'action pose', etc.
     - **NO Environment:** Do not include backgrounds, floors, walls, or any element that is not intrinsically part of the character.
     - **NO Lighting or Shadows:** Do not describe how light hits the character or if they cast shadows.
     - **NO Posture:** Do not describe the posture of the character.
---
"""

HUMAN_PROMPT = """
Game context: "{context}"
Character info: "{character_info}"
"""

SYSTEM_PROMPT_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_PROMPT_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)

chat_prompt_template = ChatPromptTemplate([
    SYSTEM_PROMPT_TEMPLATE,
    HUMAN_PROMPT_TEMPLATE,
])

def format_prompt(context: str, character: CharacterBaseModel) -> List[BaseMessage]:
    character_data_to_serialize = {
        "identity": character.identity,
        "physical": character.physical,
        "psychological": character.psychological,
        "type_of_character": character.type
    }

    character_info_json = json.dumps(
        character_data_to_serialize, 
        default=_model_dump, 
        indent=2
    )

    prompt_input_values = {
        "context": context,
        "character_info": character_info_json,
    }
    return chat_prompt_template.format_messages(**prompt_input_values)
