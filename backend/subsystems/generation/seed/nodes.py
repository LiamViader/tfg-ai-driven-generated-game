from dotenv import load_dotenv
load_dotenv()

from typing import cast
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from subsystems.generation.seed.prompts.refine_generation_prompt import format_refining_prompt
from subsystems.generation.seed.prompts.generate_main_goal import format_main_goal_generation_prompt
from subsystems.generation.seed.prompts.select_narrative_structure import format_structure_selection_prompt
from subsystems.generation.seed.schemas.graph_state import SeedGenerationGraphState
from subsystems.generation.seed.schemas.main_goal import MainGoal
from subsystems.generation.seed.tools.narrative_structure_selection_tools import STRUCTURE_TOOLS, select_narrative_structure
from core_game.narrative.structures import AVAILABLE_NARRATIVE_STRUCTURES
from utils.message_window import get_valid_messages_window
from pydantic import ValidationError, BaseModel, Field
from simulated.singleton import SimulatedGameStateSingleton

def receive_generation_prompt(state: SeedGenerationGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    SimulatedGameStateSingleton.begin_transaction()
    game_state = SimulatedGameStateSingleton.get_instance()
    game_state.set_user_prompt(state.initial_prompt)
    print("---ENTERING: RECEIVE USER PROMPT NODE---")
    return {}

def refine_generation_prompt(state: SeedGenerationGraphState):
    """
    This node calls an llm to refine the user promp and validates the result.
    """

    print("---ENTERING: REFINE USER PROMPT NODE---")

    class RefinedPromptValidation(BaseModel):
        valid: bool = Field(..., description="Whether the refined prompt is valid for creativity, coherence, and richness.")
        reason: str = Field(..., description="If not valid, a short reason why.")

    def validate_prompt_word_count(prompt: str, desired_word_count: int, min_ratio: float = 0.75) -> tuple[bool, int, int]:
        """
        Validates if the prompt has at least min_ratio * desired_word_count words.
        Returns (is_valid, word_count, min_words_required)
        """
        word_count = len(prompt.split())
        min_words = int(desired_word_count * min_ratio)
        return word_count >= min_words, word_count, min_words

    def validate_prompt_with_llm_structured(prompt: str, original_prompt: str) -> tuple[bool, str]:
        """
        Uses a validator LLM to check the quality of the refined prompt with structured output.
        Returns (is_valid, message)
        Now also checks that the refined prompt is a true refinement of the original prompt.
        """
        validator_llm = ChatOpenAI(model="gpt-4.1-nano")
        system = SystemMessagePromptTemplate.from_template(
            """
            You are a narrative design assistant. Your job is to validate a narrative seed for creativity, coherence, and richness, and to ensure it is a true refinement of the original user prompt. 
            The refined prompt must:
            - Be creative, coherent, and rich in narrative potential.
            - Clearly expand, enrich, or clarify the original prompt, not contradict or ignore it.
            - Maintain the core ideas of the original prompt, but add value and depth.
            If the refined prompt is not a true refinement, set 'valid' to false and explain why in 'reason'.
            """
        )
        human = HumanMessagePromptTemplate.from_template(
            """
            ORIGINAL PROMPT:
            {original_prompt}
            ---
            REFINED PROMPT (narrative seed):
            {prompt}
            """
        )
        chat_prompt = ChatPromptTemplate([system, human])
        messages = chat_prompt.format_messages(prompt=prompt, original_prompt=original_prompt)
        validator_llm_structured = validator_llm.with_structured_output(RefinedPromptValidation)
        try:
            result = validator_llm_structured.invoke(messages)
            structured_response = cast(RefinedPromptValidation, result)
            return structured_response.valid, structured_response.reason
        except Exception as e:
            return False, f"Validator LLM failed to return structured output: {str(e)}"

    refining_llm = ChatOpenAI(model="gpt-4.1")

    full_prompt = format_refining_prompt(
        initial_user_prompt=state.initial_prompt,
        refined_prompt_length=state.refined_prompt_desired_word_length
    )


    response = refining_llm.invoke(full_prompt)
    refined_prompt = response.content

    if isinstance(refined_prompt, list):
        refined_prompt = " ".join([str(x) for x in refined_prompt if isinstance(x, str)])

    desired_word_count = state.refined_prompt_desired_word_length
    is_valid, word_count, min_words = validate_prompt_word_count(refined_prompt, desired_word_count)
    state.refine_generation_prompt_attempts += 1
    if not is_valid:
        return {
            "refined_prompt": refined_prompt,
            "refine_generation_prompt_error_message": f"Refined prompt too short: {word_count} words (minimum required: {min_words})",
            "refine_generation_prompt_attempts": state.refine_generation_prompt_attempts
        }

    # LLM-based structured validation
    llm_valid, llm_message = validate_prompt_with_llm_structured(refined_prompt, state.initial_prompt)
    if not llm_valid:
        return {
            "refined_prompt": refined_prompt,
            "refine_generation_prompt_error_message": f"Validator LLM rejected the prompt: {llm_message}",
            "refine_generation_prompt_attempts": state.refine_generation_prompt_attempts
        }

    return {
        "refined_prompt": refined_prompt,
        "refine_generation_prompt_error_message": "",
        "refine_generation_prompt_attempts": state.refine_generation_prompt_attempts
    }

def generate_main_goal(state: SeedGenerationGraphState):
    """
    This node uses an llm to generate a narrative main goal from the refined user prompt. 
    This goal purpose is to give direction to the player on the narrative.
    """
    #save the refined prompt
    game_state = SimulatedGameStateSingleton.get_instance()
    game_state.set_refined_prompt(state.refined_prompt)

    print("---ENTERING: GENERATE MAIN GOAL NODE---")

    class MainGoalValidation(BaseModel):
        valid: bool = Field(..., description="Whether the main goal is actionable, open-ended and coherent with the narrative seed.")
        reason: str = Field(..., description="If not valid, a short reason why.")

    def validate_main_goal_with_llm_structured(main_goal: str, refined_prompt: str) -> tuple[bool, str]:
        validator_llm = ChatOpenAI(model="gpt-4.1-nano")
        system = SystemMessagePromptTemplate.from_template(
            """
            You are a narrative design assistant. Validate the proposed main goal for a narrative game.
            The main goal must be player centric, actionable, concise and open-ended.
            It should align with the following narrative seed.
            """
        )
        human = HumanMessagePromptTemplate.from_template(
            """
            NARRATIVE SEED:
            {refined_prompt}
            ---
            MAIN GOAL:
            {main_goal}
            """
        )
        chat_prompt = ChatPromptTemplate([system, human])
        messages = chat_prompt.format_messages(refined_prompt=refined_prompt, main_goal=main_goal)
        validator_llm_structured = validator_llm.with_structured_output(MainGoalValidation)
        try:
            result = validator_llm_structured.invoke(messages)
            structured_response = cast(MainGoalValidation, result)
            return structured_response.valid, structured_response.reason
        except Exception as e:
            return False, f"Validator LLM failed to return structured output: {str(e)}"

    try:
        generate_main_goal_llm = ChatOpenAI(model="o4-mini")
        generate_main_goal_llm_structured_output = generate_main_goal_llm.with_structured_output(MainGoal)

        full_prompt = format_main_goal_generation_prompt(
            refined_user_prompt=state.refined_prompt
        )
        result = generate_main_goal_llm_structured_output.invoke(full_prompt)

        structured_response = cast(MainGoal, result)

        if "as an ai model" in structured_response.main_goal.lower():
            raise ValueError("LLM returned a refusal response.")

        llm_valid, llm_message = validate_main_goal_with_llm_structured(structured_response.main_goal, state.refined_prompt)
        if not llm_valid:
            raise ValueError(f"Validator LLM rejected the main goal: {llm_message}")

        state.main_goal = structured_response.main_goal
        state.generate_main_goal_error_message = ""

    except (ValidationError, ValueError) as e:
        state.main_goal = ""
        state.generate_main_goal_error_message = str(e)

    return {
        "main_goal": state.main_goal,
        "generate_main_goal_attempts": state.generate_main_goal_attempts+1,
        "generate_main_goal_error_message": state.generate_main_goal_error_message
    }


def narrative_structure_reason_node(state: SeedGenerationGraphState):
    """Reasoning step for selecting a narrative structure."""

    #save the main goal
    game_state = SimulatedGameStateSingleton.get_instance()
    game_state.set_player_main_goal(state.main_goal)

    print("---ENTERING: NARRATIVE STRUCTURE REASON NODE---")

    #Si s'acosta el màxim d'iteracions, es força a seleccionar la estructura. 2 iteracions de marge per si hi ha errors
    if state.current_structure_selection_iteration < state.max_structure_selection_reason_iterations:
        tools_availale = STRUCTURE_TOOLS
    else:
        tools_availale = [select_narrative_structure]

    llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(tools_availale, tool_choice="any")

    names = ", ".join([f"id: {s.id} name: {s.name}\n" for s in AVAILABLE_NARRATIVE_STRUCTURES])
    prompt = format_structure_selection_prompt(
        refined_prompt=state.refined_prompt,
        main_goal=state.main_goal,
        structure_names=names,
        messages=get_valid_messages_window(state.structure_selection_messages, 10),
    )

    state.current_structure_selection_iteration += 1
    response = llm.invoke(prompt)

    return {
        "structure_selection_messages": [response],
        "current_structure_selection_iteration": state.current_structure_selection_iteration,
    }


narrative_structure_tool_node = ToolNode(STRUCTURE_TOOLS)
narrative_structure_tool_node.messages_key = "structure_selection_messages"


def final_success_node(state: SeedGenerationGraphState):
    """Last step if all succeeded."""
    #save narrative structure TODOOO IMPORTANT
    SimulatedGameStateSingleton.commit()
    return {
        "seed_generation_succeeded": True
    }


def final_failed_node(state: SeedGenerationGraphState):
    """Last step if something failed."""
    SimulatedGameStateSingleton.rollback()
    return {
        "seed_generation_succeeded": False
    }