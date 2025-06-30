SCENARIO_FIELDS = {
    "name": "Descriptive name of the scenario.",
    "visual_description": "Describes the visual appearance of the scenario—its layout, key visual elements, atmosphere, and spatial composition.",
    "visual_prompt": "Around 200 words providing a complete, self-contained description of the scenario intended as a direct prompt for AI image generation. It must detail the environment, important features, mood and spatial arrangement without assuming any prior context.",
    "narrative_context": "Narrative background of the scenario, including its history, role in the story, mood, important events that occur here, relevance within the world’s lore, etc.",
    "summary_description": "Short, high-level summary of the scenario, capturing its essence in one or two sentences.",
    "indoor_or_outdoor": "Indicates whether the scenario takes place in an indoor or outdoor environment.",
    "type": "The primary category or biome of the scenario (e.g., 'house', 'dark_forest', 'cave', 'bridge', 'street', etc).",
    "zone": "Indicates the broader area or region the scenario belongs to. This can be generic (e.g., 'village', 'mountains') or specific (e.g., 'City of Wartle', 'Black Crystal Valley')."
}

EXIT_FIELDS = {
    "connection_type": "Type of path. e.g., 'path', 'door', 'secret_passage', 'street', etc",
    "travel_description": "Small description of the connection only if relevant: e.g., 'A dark path descending through gnarled trees.'",
    "traversal_conditions": "Optional conditions required to use this path. Only include if the connection is meant to be restricted in specific, justified situations (e.g., ['requires_rusty_key', 'only_at_night']).",
    "is_blocked": "Indicates whether this exit is currently blocked and cannot be used.",
    "exit_appearance_description": "Description of how this exit appears visually from the current scenario."
}