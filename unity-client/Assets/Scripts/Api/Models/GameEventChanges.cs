using System.Collections.Generic;
using System;
using UnityEngine;
using Api.Models;

namespace Api.Models
{
    [Serializable]
    public class GameEventChanges
    {
        public Dictionary<string, List<GameEventCharacterOptionOperation>> character_interaction_options_delta;
    }
}