// Api/Models/ActionModels.cs
// It's recommended to have Newtonsoft.Json for Unity installed for robust JSON handling.
// You can get it from the Unity Asset Store or via the Package Manager.
using Newtonsoft.Json;
using NUnit.Framework;
using System.Collections.Generic;

namespace Api.Models
{
    // --- Enums for Type Safety ---

    public enum ActionType
    {
        MOVE_PLAYER,
        TRIGGER_ACTIVATION_CONDITION
    }

    public enum FollowUpActionType
    {
        NONE,
        START_NARRATIVE_STREAM
    }

    // --- Request Models (Client -> Server) ---

    [System.Serializable]
    public class ActionPayload
    {
        // These fields are nullable by default because they are reference types (string).
        // The serializer will omit them if they are null.
        [JsonProperty("new_scenario_id")]
        public string NewScenarioId;

        [JsonProperty("activation_condition_id")]
        public string ActivationConditionId;
    }

    [System.Serializable]
    public class ActionRequest
    {
        [JsonProperty("from_checkpoint_id")]
        public string FromCheckpointId;

        [JsonProperty("action_type")]
        public string ActionType; // We send the enum value as a string

        [JsonProperty("payload")]
        public ActionPayload Payload;
    }


    [System.Serializable]
    public class StartNarrativeStreamPayload
    {
        [JsonProperty("event_id")]
        public string EventId;

        [JsonProperty("involved_character_ids")]
        public List<string> InvolvedCharacterIds;
    }

    [System.Serializable]
    public class FollowUpAction
    {
        [JsonProperty("type")]
        public FollowUpActionType Type;

        // This payload can be null if the action type is NONE.
        [JsonProperty("payload")]
        public StartNarrativeStreamPayload Payload;
    }

    [System.Serializable]
    public class ActionResponse
    {
        // UPDATED: Now uses your ChangesetResponse class.
        [JsonProperty("changeset")]
        public ChangesetResponse Changeset;

        [JsonProperty("follow_up_action")]
        public FollowUpAction FollowUpAction;

        // This error field will be null in successful responses.
        [JsonProperty("error")]
        public string Error;
    }
}
