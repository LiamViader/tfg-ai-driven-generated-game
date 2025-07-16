using System;
using UnityEngine;

using System;
using System.Collections.Generic;

namespace Api.Models
{
    [Serializable]
    public class CharacterOperation
    {
        public string? op { get; set; }  // "add", "remove", "update"
        public string? id { get; set; }

        public string? type { get; set; }
        public string? image_path { get; set; }
        public string? present_in_scenario { get; set; }

        public IdentityAttributes? identity { get; set; }
        public PhysicalAttributes? physical { get; set; }
        public PsychologicalAttributes? psychological { get; set; }
        public KnowledgeAttributes? knowledge { get; set; }
        public DynamicState? dynamic_state { get; set; }
        public NarrativeAttributes? narrative { get; set; }
    }

    [Serializable]
    public class IdentityAttributes
    {
        public string? full_name { get; set; }
        public string? alias { get; set; }
        public int? age { get; set; }
        public string? gender { get; set; }
        public string? profession { get; set; }
        public string? species { get; set; }
        public string? alignment { get; set; }
    }

    [Serializable]
    public class PhysicalAttributes
    {
        public string? appearance { get; set; }
        public string? visual_prompt { get; set; }
        public List<string>? distinctive_features { get; set; } // CORREGIDO: Era string?, ahora es una lista.
        public string? clothing_style { get; set; }
        public List<string>? characteristic_items { get; set; }
    }

    [Serializable]
    public class PsychologicalAttributes
    {
        public string? personality_summary { get; set; }
        public List<string>? personality_tags { get; set; }
        public List<string>? motivations { get; set; }
        public List<string>? values { get; set; }
        public List<string>? fears_and_weaknesses { get; set; }
        public string? communication_style { get; set; }
        public string? backstory { get; set; }
        public List<string>? quirks { get; set; }
    }

    [Serializable]
    public class KnowledgeAttributes
    {
        public List<string>? background_knowledge { get; set; } // CORREGIDO: Era string?, ahora es una lista.
        public List<string>? acquired_knowledge { get; set; } // CORREGIDO: Era string?, ahora es una lista.
    }

    [Serializable]
    public class DynamicState
    {
        public string? current_emotion { get; set; }
        public string? immediate_goal { get; set; }
    }

    [Serializable]
    public class NarrativePurpose
    {
        public string? mission { get; set; }
        public bool is_hidden { get; set; }
    }

    [Serializable]
    public class NarrativeAttributes
    {
        public string? narrative_role { get; set; }
        public string? current_narrative_importance { get; set; } // CORREGIDO: Era int?, ahora string para coincidir con el Enum.
        public List<NarrativePurpose>? narrative_purposes { get; set; } // CORREGIDO: Era List<string>?, ahora una lista de objetos.
    }
}
