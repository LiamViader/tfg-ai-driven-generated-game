using System;
using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    public class ScenarioOperation
    {
        public string? op { get; set; }   // "add", "remove", "update"
        public string? id { get; set; }

        public string? name { get; set; }
        public string? visual_description { get; set; }
        public string? narrative_context { get; set; }
        public string? summary_description { get; set; }
        public string? indoor_or_outdoor { get; set; }
        public string? type { get; set; }
        public string? zone { get; set; }
        public string? image_path { get; set; }

        public List<ScenarioConnectionChange>? connections { get; set; }
    }

    public class ScenarioConnectionChange
    {
        public string? op { get; set; }         // "add", "remove", "update"
        public string? direction { get; set; }  // e.g. "north", "east"
        public string? value { get; set; }      // ID de la conexión, o null en remove
    }
}