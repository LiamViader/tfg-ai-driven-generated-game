using System;
using System.Collections;
using UnityEngine;
using Api.Models;

public static class GenerationAPI
{
    private static readonly string baseUrl = "http://localhost:8000";

    public static IEnumerator StartGeneration(string prompt, Action<GenerationStatus> onSuccess = null, Action<string> onError = null)
    {
        string url = $"{baseUrl}/generate";
        var payload = new { user_prompt = prompt };

        yield return HttpUtils.Post<GenerationStatus>(url, payload,
            onSuccess: status =>
            {
                Debug.Log("Generation started.");
                onSuccess?.Invoke(status);
            },
            onError: error =>
            {
                Debug.LogError($"Error starting generation: {error}");
                onError?.Invoke(error);
            }
        );
    }

    public static IEnumerator GetStatus(Action<GenerationStatus> onSuccess, Action<string> onError = null)
    {
        string url = $"{baseUrl}/generate/status";

        yield return HttpUtils.Get<GenerationStatus>(url,
            onSuccess: onSuccess,
            onError: error =>
            {
                Debug.LogError($"Error getting status: {error}");
                onError?.Invoke(error);
            }
        );
    }

    public static IEnumerator GetFullState(Action<ChangesetResponse> onSuccess, Action<string> onError = null)
    {
        string url = $"{baseUrl}/state/full";

        yield return HttpUtils.Get<ChangesetResponse>(url,
            onSuccess: onSuccess,
            onError: error =>
            {
                Debug.LogError($"Error getting full game state: {error}");
                onError?.Invoke(error);
            }
        );
    }

    public static IEnumerator GetIncrementalChanges(string fromCheckpointId, Action<ChangesetResponse> onSuccess, Action<string> onError = null)
    {
        string url = $"{baseUrl}/state/changes?from_checkpoint={fromCheckpointId}";

        yield return HttpUtils.Get<ChangesetResponse>(url,
            onSuccess: onSuccess,
            onError: error =>
            {
                Debug.LogError($"Error getting incremental changes: {error}");
                onError?.Invoke(error);
            }
        );
    }
}
