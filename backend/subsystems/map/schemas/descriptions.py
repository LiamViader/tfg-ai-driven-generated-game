SCENARIO_FIELDS = {
    "name": "Descriptive name of the scenario.",
    "visual_description": "Describes the visual appearance of the scenario—its layout, key visual elements, atmosphere, and spatial composition.",
    "narrative_context": "Narrative background of the scenario, including its history, role in the story, mood, important events that occur here, relevance within the world’s lore, etc.",
    "summary_description": "Short, high-level summary of the scenario, capturing its essence in one or two sentences.",
    "indoor_or_outdoor": "Indicates whether the scenario takes place in an indoor or outdoor environment.",
}

EXIT_FIELDS = {
    "connection_type": "Type of path. e.g., 'path', 'door', 'secret_passage', 'street', etc",
    "travel_description": "Small description of the connection only if relevant: e.g., 'A dark path descending through gnarled trees.'",
    "traversal_conditions": "Optional conditions required to use this path. Only include if the connection is meant to be restricted in specific, justified situations (e.g., ['requires_rusty_key', 'only_at_night']).",
    "is_blocked": "Indicates whether this exit is currently blocked and cannot be used."
}