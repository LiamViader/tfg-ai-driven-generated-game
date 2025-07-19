
using System;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class GameEventCharacterOptionOperation
    {
        public string op; // "add", "update", "remove"
        public string condition_id; // The ID of the activation condition, key for the delta

        // The following fields are for "add" and "update" operations.
        // They are marked with '?' to indicate they can be null,
        // which is expected for "remove" operations where these fields won't be present.
        public string? event_id;
        public string? title;
        public string? description;
        public string? menu_label;
        public bool? is_repeatable;
    }
}