using System;
using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class MapChanges
    {
        public List<ScenarioOperation> scenarios;
        public List<ConnectionOperation> connections;
    }
}