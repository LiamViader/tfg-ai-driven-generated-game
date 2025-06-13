from dotenv import load_dotenv
load_dotenv()

from typing import cast
from langchain_openai import ChatOpenAI
from subsystems.generation.prompts.refine_generation_prompt import format_refining_prompt
from subsystems.generation.prompts.generate_main_goal import format_main_goal_generation_prompt
from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.schemas.main_goal import MainGoal
from pydantic import ValidationError

def receive_generation_prompt(state: GenerationGraphState) -> GenerationGraphState:
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE GENERATION PROMPT NODE---")
    return state

def refine_generation_prompt(state: GenerationGraphState):
    """
    This node calls an llm to refine the user promp.
    """

    print("---ENTERING: REFINE GENERATION PROMPT NODE---")


    refining_llm = ChatOpenAI(model="gpt-4.1")

    full_prompt = format_refining_prompt(
        initial_user_prompt=state.initial_prompt,
    )


    response = refining_llm.invoke(full_prompt)

    return {
        "refined_prompt": response.content
    }

def generate_main_goal(state: GenerationGraphState):
    """
    This node uses an llm to generate a narrative main goal from the refined user prompt. 
    This goal purpose is to give direction to the player on the narrative.
    """
    print("---ENTERING: GENERATE MAIN GOAL NODE---")


    try:
        generate_main_goal_llm = ChatOpenAI(model="gpt-4.1")
        generate_main_goal_llm_structured_output=generate_main_goal_llm.with_structured_output(MainGoal)

        full_prompt = format_main_goal_generation_prompt(
            refined_user_prompt=state.refined_prompt
        )
        result = generate_main_goal_llm_structured_output.invoke(full_prompt)

        structured_response = cast(MainGoal, result)

        if "as an ai model" in structured_response.main_goal.lower():
            raise ValueError("LLM returned a refusal response.")

        print(f"---SUCCESS! Main goal: {structured_response.main_goal}---")
        state.main_goal = structured_response.main_goal
        state.generate_main_goal_error_message = ""

    except (ValidationError, ValueError) as e:
        print(f"---VALIDATION FAILED: {e}---")
        state.main_goal = ""
        state.generate_main_goal_error_message = str(e)

    return {
        "main_goal": state.main_goal,
        "generate_main_goal_attempts": state.generate_main_goal_attempts+1,
        "generate_main_goal_error_message": state.generate_main_goal_error_message
    }

