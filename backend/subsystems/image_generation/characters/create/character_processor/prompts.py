from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage
from core_game.character.schemas import CharacterBaseModel

SYSTEM_PROMPT = """You are an expert concept artist. Craft a vivid prompt for OpenAI's image generation API to depict a character. Use the provided details and keep it self contained."""

HUMAN_PROMPT = """
Game context: "{context}"
Graphic style: "{style}"
Character visual description: "{visual_prompt}"
"""

SYSTEM_PROMPT_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_PROMPT_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)

chat_prompt_template = ChatPromptTemplate([
    SYSTEM_PROMPT_TEMPLATE,
    HUMAN_PROMPT_TEMPLATE,
])

def format_prompt(context: str, character: CharacterBaseModel, style: str) -> List[BaseMessage]:
    prompt_input_values = {
        "context": context,
        "style": style,
        "visual_prompt": character.physical.visual_prompt,
    }
    return chat_prompt_template.format_messages(**prompt_input_values)
