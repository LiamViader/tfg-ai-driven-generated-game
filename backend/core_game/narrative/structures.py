from core_game.narrative.schemas import NarrativeStructureModel, NarrativeStageModel

FIVE_ACT_STRUCTURE = NarrativeStructureModel(
    name="Five Act Structure",
    description="A well-balanced narrative structure divided into five phases. Allows for gradual build-up of tension, multiple turning points, and a strong climactic resolution. Offers more granularity than the classic three-act model.",
    orientative_use_cases="Ideal for games where controlled pacing and gradual narrative escalation are desired. Useful for political intrigue, complex mysteries, relationship-driven stories, and character-centric drama.",
    stages=[
        NarrativeStageModel(
            name="Introduction",
            narrative_objectives="Present the world, main characters, and initial situation.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Initial Development",
            narrative_objectives="Introduce conflicts, obstacles, and deepen character relationships.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Advanced Development",
            narrative_objectives="Escalate conflicts, introduce new information or twists.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Climax",
            narrative_objectives="Bring key conflicts to a head. Force critical decisions.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Resolution",
            narrative_objectives="Resolve main conflicts, show consequences of decisions.",
            stage_beats=[]
        ),
    ]
)

THREE_ACT_STRUCTURE = NarrativeStructureModel(
    name="Three Act Structure",
    description="A simple and versatile narrative structure divided into three main phases: setup, confrontation, and resolution. Provides a clear progression arc while allowing flexibility in pacing and tone.",
    orientative_use_cases="Ideal for flexible narrative-driven games where a balance between player agency and structured progression is desired. Works well for mysteries, political intrigue, adventure, and hybrid genres.",
    stages=[
        NarrativeStageModel(
            name="Introduction",
            narrative_objectives="Present the world, the main characters, the initial situation and set up both the main goal and the failure conditions.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Development",
            narrative_objectives="Advance the narrative towards the goal, introduce obstacles and complications, grow the risk level, force decisions.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Resolution",
            narrative_objectives="Bring the main goal and failure condition to resolution, close key narrative threads, present the final state of the world.",
            stage_beats=[]
        ),
    ]
)

HEROS_JOURNEY_STRUCTURE = NarrativeStructureModel(
    name="Hero’s Journey",
    description="A classic narrative structure centered around a transformative journey. The player progresses through distinct phases of growth, challenge, and resolution. Encourages strong character arcs and emotional engagement.",
    orientative_use_cases="Ideal for character-driven narratives where the player undertakes a personal journey or quest. Supports both epic fantasy, mystery, and more intimate human stories with transformational arcs.",
    stages=[
        NarrativeStageModel(
            name="Ordinary World",
            narrative_objectives="Introduce the world, current status quo, and main characters. Show the player's ordinary life before the adventure.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Call to Adventure",
            narrative_objectives="Introduce the main goal and the reason why the player should pursue it. Increase narrative tension.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Crossing the Threshold",
            narrative_objectives="The player crosses into the new narrative space. The world reacts to this change. Initial real consequences appear.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Trials and Allies",
            narrative_objectives="Introduce challenges and secondary goals. Allow the player to build relationships, alliances, and knowledge.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Approach to the Inmost Cave",
            narrative_objectives="Build tension towards the main climax. Force the player to confront difficult choices or learn important truths.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Ordeal / Climax",
            narrative_objectives="Confront the main obstacle or enemy. Allow the player to resolve the primary narrative arc.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Reward and Return",
            narrative_objectives="Reward the player. Let the world reflect the impact of the player's decisions. Allow room for a potential new arc.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Resolution",
            narrative_objectives="Tie up loose ends. Reflect on how the world and characters have changed. Optionally, set up new possible adventures.",
            stage_beats=[]
        ),
    ]
)

TENSION_DISCOVERY_STRUCTURE = NarrativeStructureModel(
    name="Tension & Discovery Arc",
    description="A narrative structure focused on building tension progressively while allowing the player to discover key elements of the world and the plot. Balances structured escalation with periods of free exploration and relationship building.",
    orientative_use_cases="Ideal for stories where mystery, gradual worldbuilding, and mounting tension are central. Supports both linear and emergent narratives where pacing and atmosphere are key components.",
    stages=[
        NarrativeStageModel(
            name="World Establishment",
            narrative_objectives="Establish the tone, rules of the world, and key factions or characters.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Initial Discovery",
            narrative_objectives="Let the player uncover initial information, mysteries or conflicts.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="First Conflicts",
            narrative_objectives="Present the player with first meaningful conflicts or dilemmas. Force some initial choices.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Tension Building",
            narrative_objectives="Introduce layers of mystery and escalating stakes. The player should feel the situation is getting more complex.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Free Development",
            narrative_objectives="Allow the player to freely pursue side goals, explore relationships, gather knowledge or power.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Escalation to Climax",
            narrative_objectives="Drive the narrative towards a point of maximum tension. Events converge towards the main goal or a decisive moment.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Climax and Resolution",
            narrative_objectives="Conclude the main narrative arcs, resolve major conflicts.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Epilogue and World State",
            narrative_objectives="Reflect on how the player's actions changed the world. Show consequences and possible new threads.",
            stage_beats=[]
        ),
    ]
)

BRANCHING_STORY_STRUCTURE = NarrativeStructureModel(
    name="Branching Story Structure",
    description="A narrative structure where the player's decisions cause the story to branch into distinct paths, leading to multiple possible developments and outcomes. The narrative adapts dynamically to player agency, offering replayability and divergent experiences.",
    orientative_use_cases="Suitable for experiences where player choice and consequence are central. Encourages exploration of different narrative possibilities and supports non-linear storytelling.",
    stages=[
        NarrativeStageModel(
            name="Introduction and Premise",
            narrative_objectives="Establish the setting, main goal, and present the initial conflict or mystery.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="First Critical Choice",
            narrative_objectives="Present a choice that will split the narrative into different possible paths.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Branched Development",
            narrative_objectives="Develop the chosen path with unique narrative beats, characters, and events.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Second Critical Choice",
            narrative_objectives="Present another major choice, possibly within the current path or re-aligning paths.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Resonance and Consequences",
            narrative_objectives="Have the world and characters react to the player's cumulative choices.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Multiple Climaxes",
            narrative_objectives="Reach different climaxes or narrative resolutions depending on the player's path.",
            stage_beats=[]
        ),
        NarrativeStageModel(
            name="Adaptive Epilogue",
            narrative_objectives="Show an epilogue that reflects the player's path and choices throughout the story.",
            stage_beats=[]
        ),
    ]
)

MYSTERY_STRUCTURE = NarrativeStructureModel(
    name="Mystery Investigation",
    description="A narrative structure centered around the gradual discovery of information, where the player investigates a mystery through exploration, deduction, and interaction. The narrative unfolds as the player uncovers clues and navigates misdirection.",
    orientative_use_cases="Useful for narrative experiences focused on investigation, discovery, and tension, where the player progressively reconstructs hidden truths through their actions.",
    stages=[
        NarrativeStageModel(
            name="Mystery Setup",
            narrative_objectives="Introduce the central mystery or crime, the initial setting, and key characters."
        ),
        NarrativeStageModel(
            name="Clue Discovery",
            narrative_objectives="Guide the player through finding clues and gathering information about the mystery."
        ),
        NarrativeStageModel(
            name="Red Herrings",
            narrative_objectives="Introduce misleading clues and narrative twists to challenge the player's understanding."
        ),
        NarrativeStageModel(
            name="Major Revelations",
            narrative_objectives="Reveal key pieces of the puzzle that change the player's perspective on the mystery."
        ),
        NarrativeStageModel(
            name="Confrontation",
            narrative_objectives="Lead to a direct confrontation with the antagonist or a resolution of the mystery."
        ),
        NarrativeStageModel(
            name="Resolution",
            narrative_objectives="Conclude the mystery and show the aftermath of the player's choices."
        ),
    ]
)

FACTION_CONFLICT_STRUCTURE = NarrativeStructureModel(
    name="Faction Conflict",
    description="A narrative structure centered around conflicts between multiple factions or groups, where the player's choices influence the balance of power and the ultimate outcome of the world.",
    orientative_use_cases="Suitable for narrative experiences where shifting alliances, moral ambiguity, and complex power dynamics are key drivers of the story. Encourages emergent outcomes and reactive worldbuilding.",
    stages=[
        NarrativeStageModel(
            name="World and Factions Introduction",
            narrative_objectives="Introduce the world, the factions, and their main conflicts or goals."
        ),
        NarrativeStageModel(
            name="Rising Tensions",
            narrative_objectives="Escalate conflicts between factions and present dilemmas to the player."
        ),
        NarrativeStageModel(
            name="Player Influence",
            narrative_objectives="Allow the player to take actions that shift the balance between factions."
        ),
        NarrativeStageModel(
            name="Conflict Climax",
            narrative_objectives="Reach a major turning point where faction conflicts culminate in significant events."
        ),
        NarrativeStageModel(
            name="New Stability",
            narrative_objectives="Establish a new world state based on the outcomes of the player's actions."
        ),
    ]
)

SANDBOX_STRUCTURE = NarrativeStructureModel(
    name="Sandbox Driven",
    description="An open, player-driven narrative structure where the world is highly reactive and the player has significant agency. The narrative emerges organically from player choices and interactions with the world, rather than following a tightly scripted path.",
    orientative_use_cases="Suitable for narrative experiences focused on player agency and emergent storytelling, where the player shapes the narrative through free exploration and interaction rather than following a linear storyline.",
    stages=[
        NarrativeStageModel(
            name="World Setup",
            narrative_objectives="Establish the world and its initial conditions, key locations, and characters."
        ),
        NarrativeStageModel(
            name="First Opportunities",
            narrative_objectives="Present initial opportunities and allow the player to explore freely."
        ),
        NarrativeStageModel(
            name="World Reactivity",
            narrative_objectives="Have the world and factions react dynamically to the player's choices."
        ),
        NarrativeStageModel(
            name="Emerging Plotlines",
            narrative_objectives="Let new plotlines and conflicts emerge based on the player's interactions."
        ),
        NarrativeStageModel(
            name="Player-Driven Climax",
            narrative_objectives="Build toward a climax or major world change influenced by the player's actions."
        ),
        NarrativeStageModel(
            name="Outcome and Epilogue",
            narrative_objectives="Reflect on the player's impact on the world and wrap up active plotlines."
        ),
    ]
)

TENSION_RELEASE_STRUCTURE = NarrativeStructureModel(
    name="Tension / Release Loop",
    description="A cyclical narrative structure that alternates between building tension and providing emotional release, creating a rhythm that keeps the player engaged.",
    orientative_use_cases="Works well in thriller, horror, mystery, adventure, and action-driven stories where pacing and emotional modulation are key.",
    stages=[
        NarrativeStageModel(
            name="Initial Calm",
            narrative_objectives="Introduce the setting and main characters in a relatively safe and calm context."
        ),
        NarrativeStageModel(
            name="First Tension Build-Up",
            narrative_objectives="Introduce initial conflicts, dangers, or mysteries that begin to create tension."
        ),
        NarrativeStageModel(
            name="First Release",
            narrative_objectives="Provide a partial resolution or relief that gives the player a sense of progress and control."
        ),
        NarrativeStageModel(
            name="Second Tension Build-Up",
            narrative_objectives="Escalate the stakes, introduce new dangers, or deepen existing conflicts."
        ),
        NarrativeStageModel(
            name="Second Release",
            narrative_objectives="Allow the player to achieve significant progress or resolve key conflicts, providing emotional release."
        ),
        NarrativeStageModel(
            name="Final Tension Climax",
            narrative_objectives="Reach the highest point of narrative tension, where the main conflicts are at their peak."
        ),
        NarrativeStageModel(
            name="Final Resolution",
            narrative_objectives="Resolve the central conflicts, reward the player with closure, and reflect on the outcome."
        ),
    ]
)

AVAILABLE_NARRATIVE_STRUCTURES = [
    FIVE_ACT_STRUCTURE,
    THREE_ACT_STRUCTURE,
    HEROS_JOURNEY_STRUCTURE,
    TENSION_DISCOVERY_STRUCTURE,
    BRANCHING_STORY_STRUCTURE,
    MYSTERY_STRUCTURE,
    FACTION_CONFLICT_STRUCTURE,
    SANDBOX_STRUCTURE,
    TENSION_RELEASE_STRUCTURE
]