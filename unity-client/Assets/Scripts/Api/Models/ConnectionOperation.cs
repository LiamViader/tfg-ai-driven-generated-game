using System;
using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    public class ConnectionOperation
    {
        public string? op { get; set; }  // "add", "remove", "update"
        public string? id { get; set; }

        public string? scenario_a_id { get; set; }
        public string? scenario_b_id { get; set; }
        public string? direction_from_a { get; set; }
        public string? connection_type { get; set; }

        public string? travel_description { get; set; }
        public List<string>? traversal_conditions { get; set; }
        public string? exit_appearance_description { get; set; }
        public bool? is_blocked { get; set; }
    }
}
