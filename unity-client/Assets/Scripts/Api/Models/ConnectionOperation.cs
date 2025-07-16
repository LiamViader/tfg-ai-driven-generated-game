using System;
using UnityEngine;

namespace Api.Models
{
    [Serializable]
    public class ConnectionOperation
    {
        public string op;      // "add", "remove", "update"
        public string id;

        // Campos posibles en add/update:
        public string from;
        public string to;
        public string direction;
        public string type;
    }
}
