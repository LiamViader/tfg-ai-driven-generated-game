from typing import List, Annotated, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from core_game.map.schemas import ScenarioModel

SYSTEM_PROMPT = """You are an expert creative assistant for a video game. Your task is to generate parameters for an image generation API based on a high-level scenario description and the game context (because maybe you need some more context not provided on the scenario description). 
Your primary role is to create parameters that will generate an image capturing the input description as faithfully as possible. You must capture the most important elements of the scenario so the image will be faithfull to the description. You must include the maximum amount of detail from the input. 
If you need to omit details due to length constraints, ensure the most important and defining elements of the scenario are preserved.
The summary ground must be made of materials as uniform as possible that won't generate any dents, bumps, irregular terrain, etc when generating the image; because lately in the pipeline it will be used to place character sprites on top of it.
Detailed gound can be less uniform but has to make sense with the ground summary. Pay Close attention to wheter the scenario is an indoor or an outdoor, your output must adhere to that.
You must output a JSON object matching the requested structure. You can NOT exceed the maximum words stated on the field descriptions, Pay close attention to them.
"""

HUMAN_PROMPT = """
    Generate the image generation parameters based on the following details:
     
    Game context: "{context}"
    ## --- SCENARIO INFORMATION ---
    Scenario Visual Description: "{visual_description}"
    Scenario indoor or outdoor: "{indoor_or_outdoor}"
    Scenario zone: "{zone}"
    Scenario type: "{type}"
    Scenario summary description: "{summary_description}"
    Scenario narrative description: "{narrative_context}"

    Please generate the detailed fields for the API payload.
"""

SYSTEM_PROMPT_TEMPLATE = SystemMessagePromptTemplate.from_template(
    SYSTEM_PROMPT
)

HUMAN_PROMPT_TEMPLATE = HumanMessagePromptTemplate.from_template(
    HUMAN_PROMPT
)

chat_prompt_template = ChatPromptTemplate([
    SYSTEM_PROMPT_TEMPLATE,
    HUMAN_PROMPT_TEMPLATE,
])

def format_prompt(context: str, scenario: ScenarioModel) -> List[BaseMessage]:
    """
    Formats the prompt with all the necessary information from the game context and a specific scenario.
    """
    # El diccionario ahora incluye todos los campos requeridos por el HUMAN_PROMPT
    prompt_input_values = {
        "context": context, # Se asume que el contexto se puede convertir a string
        "visual_description": scenario.visual_description,
        "indoor_or_outdoor": scenario.indoor_or_outdoor,
        "zone": scenario.zone,
        "type": scenario.type,
        "summary_description": scenario.summary_description,
        "narrative_context": scenario.narrative_context,
    }
    formatted_messages = chat_prompt_template.format_messages(**prompt_input_values)
    
    return formatted_messages