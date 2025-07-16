using System;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class ScenarioOperation
    {
        public string op;       // "add", "remove", "update"
        public string id;

        public string name;
        public string visual_description;
        public string narrative_context;
        public string summary_description;
        public string indoor_or_outdoor;
        public string type;
        public string zone;
        public string image_path;

        public ScenarioConnectionChange[] connections;
    }

    [Serializable]
    public class ScenarioConnectionChange
    {
        public string op;          // "add", "remove", "update"
        public string direction;   // e.g. "north", "east", etc.
        public string value;       // ID de la conexión (puede ser null en "remove")
    }
}