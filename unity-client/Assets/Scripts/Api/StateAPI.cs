using UnityEngine;
using System;
using System.Collections;
using Api.Models;
public class StateAPI
{
    private static readonly string baseUrl = "http://localhost:8000/game";

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
