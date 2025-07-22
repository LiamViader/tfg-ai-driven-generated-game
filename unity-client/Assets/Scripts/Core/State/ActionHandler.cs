// Scripts/ActionHandler.cs
using UnityEngine;
using Api.Models;
using System.Collections;
using Newtonsoft.Json;

/// <summary>
/// A central MonoBehaviour to handle player actions and API communication.
/// This component orchestrates the flow between UI, game state, and the server.
/// </summary>
public class ActionHandler : MonoBehaviour
{
    public static ActionHandler Instance { get; private set; }


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

    /// <summary>
    /// This is the main method to call when the player wants to move.
    /// It handles the API call and the success/error callbacks.
    /// </summary>
    public void RequestMovePlayer(string targetScenarioId)
    {
        // Start the coroutine to handle the web request
        StartCoroutine(MovePlayerCoroutine(targetScenarioId));
    }

    public void RequestTriggerCondition(string activationConditionId, System.Action onError = null, System.Action onSuccess = null)
    {
        // Start the coroutine to handle the web request
        StartCoroutine(TriggerConditionCoroutine(activationConditionId, onError, onSuccess));
    }

    private IEnumerator MovePlayerCoroutine(string targetScenarioId)
    {
        Debug.Log("Starting player move transition...");

        // Store the original scenario ID in case we need to revert on error
        string originalScenarioId = GameManager.Instance.CurrentScenarioId;

        // 1. Fade out the current scenario and wait for it to complete
        yield return StartCoroutine(ScenarioVisualManager.Instance.FadeOutCurrentScenario());

        // --- Screen is now black ---

        // 2. Call the API and wait for a response
        ActionResponse finalResponse = null;
        string errorMessage = null;
        bool requestFinished = false;

        yield return ActionAPI.MovePlayer(
            targetScenarioId,
            GameManager.Instance.LastCheckpointId,
            onSuccess: (response) => {
                finalResponse = response;
                requestFinished = true;
            },
            onError: (error) => {
                errorMessage = error;
                requestFinished = true;
            }
        );

        // Wait until the callback has been executed
        yield return new WaitUntil(() => requestFinished);

        // 3. Process the response
        if (finalResponse != null && string.IsNullOrEmpty(finalResponse.Error))
        {
            // --- SUCCESS CASE ---
            Debug.Log("MovePlayer successful. Processing response...");
            var applier = new ChangeSetApplier();
            applier.Apply(finalResponse.Changeset);

            // 3c. Fade the NEW scenario back in
            yield return StartCoroutine(ScenarioVisualManager.Instance.FadeInScenario(targetScenarioId));

            // 3d. Handle any follow-up action after the scene is visible
            FollowUpActionHandler.Instance.ProcessFollowUpAction(finalResponse.FollowUpAction);
        }
        else
        {
            // --- ERROR CASE ---
            HandleActionError(errorMessage ?? finalResponse?.Error);

            // 3e. Fade the ORIGINAL scenario back in, since the move failed
            yield return StartCoroutine(ScenarioVisualManager.Instance.FadeInScenario(originalScenarioId));
        }
    }

    private IEnumerator TriggerConditionCoroutine(string activationConditionId, System.Action onError = null, System.Action onSuccess = null)
    {
        Debug.Log("Requesting trigger Event");

        // --- Screen is now black ---

        // 2. Call the API and wait for a response
        ActionResponse finalResponse = null;
        string errorMessage = null;
        bool requestFinished = false;

        yield return ActionAPI.TriggerEvent(
            activationConditionId,
            GameManager.Instance.LastCheckpointId,
            onSuccess: (response) => {
                finalResponse = response;
                requestFinished = true;
            },
            onError: (error) => {
                errorMessage = error;
                requestFinished = true;
            }
        );

        // Wait until the callback has been executed
        yield return new WaitUntil(() => requestFinished);

        // 3. Process the response
        if (finalResponse != null && string.IsNullOrEmpty(finalResponse.Error))
        {
            // --- SUCCESS CASE ---
            Debug.Log("Trigger event successful. Processing response...");
            var applier = new ChangeSetApplier();
            applier.Apply(finalResponse.Changeset);


          
            onSuccess?.Invoke();
            FollowUpActionHandler.Instance.ProcessFollowUpAction(finalResponse.FollowUpAction);

        }
        else
        {
            
            // --- ERROR CASE ---
            HandleActionError(errorMessage ?? finalResponse?.Error);

            onError?.Invoke();
        }
    }

    private void HandleActionError(string errorMessage)
    {
        Debug.LogError($"Action failed: {errorMessage}");

    }
}
