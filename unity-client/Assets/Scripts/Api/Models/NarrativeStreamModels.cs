using System.Collections.Generic;
using UnityEngine;

namespace Api.Models
{
    [System.Serializable]
    public class StreamedMessage
    {
        public string message_id;
        public string type;
        public string speaker_id;
        public string content;
        public string title;
        public List<PlayerChoiceOptionModel> options;
    }

    [System.Serializable]
    public class PlayerChoiceOptionModel
    {
        public string type;
        public string label;
    }
}