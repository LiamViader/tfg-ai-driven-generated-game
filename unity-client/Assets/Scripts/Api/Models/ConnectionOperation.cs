using System;
using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class ConnectionOperation
    {
        public string? op;  // "add", "remove", "update"
        public string? id;

        public string? scenario_a_id;
        public string? scenario_b_id;
        public string? direction_from_a;
        public string? connection_type;

        public string? travel_description;
        public List<string>? traversal_conditions;
        public string? exit_appearance_description;
        public bool? is_blocked;
    }
}
