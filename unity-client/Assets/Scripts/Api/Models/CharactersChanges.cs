using System;
using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    public class CharactersChanges
    {
        public string? player_character_id { get; set; }
        public List<CharacterOperation>? registry { get; set; }
    }
}
