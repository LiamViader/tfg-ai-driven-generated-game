IDENTITY_MODEL_FIELDS = {
    "full_name": "Character's full name.",
    "alias": "An optional nickname or alias. Can be empty.",
    "age": "Character's age.",
    "gender": "Character's gender.",
    "profession": "Character's profession or social role within the narrative world.",
    "species": "The character's species or type of creature (e.g., human, elf, robot, monster).",
    "alignment": "Character's ethical and moral alignment (e.g., 'lawful good', 'chaotic neutral', 'benign')."
}

PHYSICAL_ATTRIBUTES_MODEL_FIELDS = {
    "appearance": "A detailed description of the character's physical appearance. Aprox 100 words. The description must be visually concrete and self-contained, explicitly stating all physical traits, Detailed enough for someone to draw it unequivocally.",
    "distinctive_features": "A list of distinctive physical features like scars, tattoos, or unique traits.",
    "clothing_style": "Description of the character's clothing, armor, or style of dress.",
    "characteristic_items": "A list of notable items the character carries that reinforce their identity, can be empty."
}

PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS = {
    "personality_summary": "A summary of the character's dominant personality traits.",
    "personality_tags": "A list of keywords that describe the personality (e.g., 'loyal', 'extroverted', 'cynical').",
    "motivations": "The character's core desires, personal goals, or deep-seated motivations.",
    "values": "Core beliefs, ideals, or a moral code that influences decisions.",
    "fears_and_weaknesses": "Relevant fears, phobias, or weaknesses that can be exploited or influence behavior.",
    "communication_style": "The individual's communication style, including their typical manner of speech and other characteristic traits.",
    "backstory": "A brief background story for the character, providing context for their personality and motivations to reinforce narrative coherence.",
    "quirks": "Patterns, mannerisms, habits, or peculiarities that define external behavior or speech, helping to reinforce unique personality and narrative coherence."
}

NARRATIVE_PURPOSE_MODEL_FIELDS = {
    "mission": "The text of the specific mission or purpose (e.g., 'protect the king', 'spy on the player').",
    "is_hidden": "Set to True if the purpose is implicit (hidden from the player), False if it is explicit (known)."
}

NARRATIVE_WEIGHT_MODEL_FIELDS = {
    "narrative_role": "The character's narrative role (e.g., protagonist, extra, etc).",
    "narrative_importance": "The character's current degree of relevance in the narrative (important, secondary, marginal, or inactive).",
    "narrative_purpose": "The specific missions that guide the character, including whether it's known or hidden to the others."
}

KNOWLEDGE_MODEL_FIELDS = {
    "background_knowledge": "Information the character possesses at the start, conditioning their initial motivations, attitudes, and interactions.",
    "acquired_knowledge": "Information the character gains during the narrative, which dynamically modulates their behavior and decisions."
}

DYNAMIC_STATE_MODEL_FIELDS = {
    "current_emotion": "The character's dominant emotional state at this moment, which can change based on events.",
    "immediate_goal": "The objective or purpose the character is actively trying to achieve in the present narrative moment."
}
