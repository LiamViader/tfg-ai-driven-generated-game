
using UnityEngine;
using Api.Models;
public class FollowUpActionHandler : MonoBehaviour
{
    public static FollowUpActionHandler Instance { get; private set; }

    // TODO: You will need to create and assign your NarrativeStreamer client here.
    // [SerializeField] private NarrativeStreamer narrativeStreamer;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void ProcessFollowUpAction(FollowUpAction followUpAction)
    {
        if (followUpAction == null || followUpAction.Type == FollowUpActionType.NONE)
        {
            return;
        }


        switch (followUpAction.Type)
        {
            case FollowUpActionType.START_NARRATIVE_STREAM:
                HandleStartNarrativeStream(followUpAction.Payload);
                break;
            default:
                Debug.Log("NOT IMPLEMENTED");
                break;
        }
    }

    private void HandleStartNarrativeStream(StartNarrativeStreamPayload payload)
    {
        string eventId = payload?.EventId;
        if (string.IsNullOrEmpty(eventId))
        {
            Debug.LogError("[FollowUpActionHandler] Received START_NARRATIVE_STREAM action but eventId was null or empty.");
            return;
        }

        Debug.Log($"[FollowUpActionHandler] Instructed to start narrative stream for event: '{eventId}'");

        // Here you would call your NarrativeStreamer client to begin the event.
        // This is the next component you will need to build.
        // For example:
        // narrativeStreamer.StartEventStream(eventId);
    }
}
