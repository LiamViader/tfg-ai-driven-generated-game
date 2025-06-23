from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import Annotated, List, Dict, Any
import os
from typing import Dict, List, Any, Optional, Literal, Set, Tuple, Annotated
from pydantic import BaseModel, Field as PydanticField
from langchain_core.tools import tool, InjectedToolCallId,InjectedToolArg
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from core_game.map.schemas import Direction, OppositeDirections
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS
from langgraph.types import Command

from simulated.game_state import SimulatedGameStateSingleton
from subsystems.agents.map_handler.tools.helpers import  get_observation

from subsystems.agents.map_handler.tools.map_tools import create_scenario
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState

# 3. Node LLM que decideix quina tool cridar
def llm_node(state: MapGraphState) -> Dict[str, Any]:
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0).bind_tools([create_scenario], tool_choice="any")
    print("🧠 LLM NODE: invoking LLM...")
    response = llm.invoke(state.map_executor_messages)

    return {"map_executor_messages": [response]}

# 4. Node Tool que executa la tool
tool_node = ToolNode([create_scenario])
tool_node.messages_key = "map_executor_messages"

# 5. Crea el gràfic
graph = StateGraph(MapGraphState)
graph.add_node("llm", llm_node)
graph.add_node("tool", tool_node)
graph.set_entry_point("llm")
graph.add_edge("llm", "tool")
graph.add_edge("tool", "llm")

# 6. Compila l'app
app = graph.compile()

# 7. Crida inicial
initial_state = MapGraphState(
    map_global_narrative_context="asd",
    map_rules_and_constraints=["saddsa"],
    map_current_objective="",
    map_other_guidelines="asd",
    map_max_executor_iterations=2,
    map_max_validation_iterations=3,
    messages_field_to_update="map_executor_messages",
    map_executor_messages=[HumanMessage("Use The tool")]
)
# 8. Execució
final_state = app.invoke(initial_state)

# 9. Mostra resultats
print("\n🧾 FINAL STATE:")
for msg in final_state["messages"]:
    print("-", msg)