using System;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class CharacterOperation
    {
        public string op;       // "add", "remove", "update"
        public string id;

        public string type;
        public string image_path;
        public string present_in_scenario;

        public IdentityAttributes identity;
        public PhysicalAttributes physical;
        public PsychologicalAttributes psychological;
        public KnowledgeAttributes knowledge;
        public DynamicState dynamic_state;
        public NarrativeAttributes narrative;
    }

    [Serializable]
    public class IdentityAttributes
    {
        public string full_name;
        public string alias;
        public int age;
        public string gender;
        public string profession;
        public string species;
        public string alignment;
    }

    [Serializable]
    public class PhysicalAttributes
    {
        public string appearance;
        public string visual_prompt;
        public string distinctive_features;
        public string clothing_style;
        public string characteristic_items;
    }

    [Serializable]
    public class PsychologicalAttributes
    {
        public string personality_summary;
        public string[] personality_tags;
        public string[] motivations;
        public string[] values;
        public string[] fears_and_weaknesses;
        public string communication_style;
        public string backstory;
        public string quirks;
    }

    [Serializable]
    public class KnowledgeAttributes
    {
        public string background_knowledge;
        public string acquired_knowledge;
    }

    [Serializable]
    public class DynamicState
    {
        public string current_emotion;
        public string immediate_goal;
    }

    [Serializable]
    public class NarrativeAttributes
    {
        public string narrative_role;
        public int current_narrative_importance;
        public string[] narrative_purposes;
    }
}
