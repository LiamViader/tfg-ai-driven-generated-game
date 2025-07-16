using System;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class ChangesetResponse
    {
        public string checkpoint_id;
        public ChangeBlock changes;
    }

    [Serializable]
    public class ChangeBlock
    {
        public MapChanges map;
        public CharactersChanges characters;
    }
}