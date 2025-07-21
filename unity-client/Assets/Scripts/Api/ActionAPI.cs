// Api/ActionAPI.cs
using System;
using System.Collections;
using UnityEngine;
using Api.Models; // Make sure this namespace matches where your model classes are

/// <summary>
/// A static class to handle all API calls related to player actions.
/// It provides specific methods for each type of action the player can take.
/// </summary>
public static class ActionAPI
{
    // The base URL for your game's API endpoints.
    private static readonly string baseUrl = "http://localhost:8000/game";

    /// <summary>
    /// Sends a request to the backend to move the player to a new scenario.
    /// </summary>
    /// <param name="scenarioId">The ID of the scenario to move to.</param>
    /// <param name="fromCheckpointId">The last known checkpoint ID from the client.</param>
    /// <param name="onSuccess">Callback executed on a successful response, returning an ActionResponse.</param>
    /// <param name="onError">Callback executed if an error occurs.</param>
    public static IEnumerator MovePlayer(string scenarioId, string fromCheckpointId, Action<ActionResponse> onSuccess = null, Action<string> onError = null)
    {
        string url = $"{baseUrl}/action";

        // 1. Create the specific payload for this action
        var payload = new ActionPayload
        {
            NewScenarioId = scenarioId
        };

        // 2. Create the full request object
        var requestData = new ActionRequest
        {
            FromCheckpointId = fromCheckpointId,
            ActionType = ActionType.MOVE_PLAYER.ToString(), // Convert enum to string for JSON
            Payload = payload
        };

        Debug.Log($"[ActionAPI] Sending MOVE_PLAYER action to scenario: {scenarioId}");

        // 3. Use HttpUtils to send the POST request
        yield return HttpUtils.Post<ActionResponse>(url, requestData,
            onSuccess: response =>
            {
                Debug.Log("[ActionAPI] MovePlayer action successful.");
                onSuccess?.Invoke(response);
            },
            onError: error =>
            {
                Debug.LogError($"[ActionAPI] Error in MovePlayer action: {error}");
                onError?.Invoke(error);
            }
        );
    }


    public static IEnumerator TriggerEvent(string activationConditionId, string fromCheckpointId, Action<ActionResponse> onSuccess = null, Action<string> onError = null)
    {
        string url = $"{baseUrl}/action";

        // 1. Create the specific payload for this action
        var payload = new ActionPayload
        {
            ActivationConditionId = activationConditionId
        };

        // 2. Create the full request object
        var requestData = new ActionRequest
        {
            FromCheckpointId = fromCheckpointId,
            ActionType = ActionType.TRIGGER_ACTIVATION_CONDITION.ToString(), // Convert enum to string
            Payload = payload
        };

        Debug.Log($"[ActionAPI] Sending TRIGGER_EVENT action for condition: {activationConditionId}");

        // 3. Use HttpUtils to send the POST request
        yield return HttpUtils.Post<ActionResponse>(url, requestData,
            onSuccess: response =>
            {
                Debug.Log("[ActionAPI] TriggerEvent action successful.");
                onSuccess?.Invoke(response);
            },
            onError: error =>
            {
                Debug.LogError($"[ActionAPI] Error in TriggerEvent action: {error}");
                onError?.Invoke(error);
            }
        );
    }
}