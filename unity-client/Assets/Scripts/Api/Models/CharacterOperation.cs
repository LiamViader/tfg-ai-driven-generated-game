using System;
using UnityEngine;

using System;
using System.Collections.Generic;

namespace Api.Models
{
    [Serializable]
    public class CharacterOperation
    {
        public string? op;  // "add", "remove", "update"
        public string? id;

        public string? type;
        public string? image_path;
        public string? present_in_scenario;

        public IdentityAttributes? identity;
        public PhysicalAttributes? physical;
        public PsychologicalAttributes? psychological;
        public KnowledgeAttributes? knowledge;
        public DynamicState? dynamic_state;
        public NarrativeAttributes? narrative;
    }

    [Serializable]
    public class IdentityAttributes
    {
        public string? full_name;
        public string? alias;
        public int? age;
        public string? gender;
        public string? profession;
        public string? species;
        public string? alignment;
    }

    [Serializable]
    public class PhysicalAttributes
    {
        public string? appearance;
        public string? visual_prompt;
        public List<string>? distinctive_features; 
        public string? clothing_style;
        public List<string>? characteristic_items;
    }

    [Serializable]
    public class PsychologicalAttributes
    {
        public string? personality_summary;
        public List<string>? personality_tags;
        public List<string>? motivations;
        public List<string>? values;
        public List<string>? fears_and_weaknesses;
        public string? communication_style;
        public string? backstory;
        public List<string>? quirks;
    }

    [Serializable]
    public class KnowledgeAttributes
    {
        public List<string>? background_knowledge;
        public List<string>? acquired_knowledge; 
    }

    [Serializable]
    public class DynamicState
    {
        public string? current_emotion;
        public string? immediate_goal;
    }

    [Serializable]
    public class NarrativePurpose
    {
        public string? mission;
        public bool is_hidden;  
    }

    [Serializable]
    public class NarrativeAttributes
    {
        public string? narrative_role;
        public string? current_narrative_importance;
        public List<NarrativePurpose>? narrative_purposes;
    }
}
