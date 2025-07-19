using System;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class ChangesetResponse
    {
        // CORREGIDO: Usamos propiedades { get; set; } para consistencia.
        public string checkpoint_id;
        public ChangeBlock changes;
    }

    [Serializable]
    public class ChangeBlock
    {
        public MapChanges? map;
        public CharactersChanges? characters;
        public GameEventChanges? events;
    }
}