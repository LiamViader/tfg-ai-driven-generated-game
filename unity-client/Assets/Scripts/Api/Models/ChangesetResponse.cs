using System;
using UnityEngine;

namespace Api.Models
{
    public class ChangesetResponse
    {
        public string checkpoint_id;
        public ChangeBlock changes;
    }

    public class ChangeBlock
    {
        public MapChanges? map { get; set; }
        public CharactersChanges? characters { get; set; }
    }
}