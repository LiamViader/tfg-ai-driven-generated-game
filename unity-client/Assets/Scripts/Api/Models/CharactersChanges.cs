using System;
using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class CharactersChanges
    {
        public string? player_character_id;
        public List<CharacterOperation>? registry;
    }
}
