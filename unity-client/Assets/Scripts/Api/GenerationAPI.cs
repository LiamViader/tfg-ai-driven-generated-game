using System;
using System.Collections;
using UnityEngine;
using Api.Models;

public static class GenerationAPI
{
    private static readonly string baseUrl = "http://localhost:8000/game";

    public static IEnumerator StartGeneration(string prompt, Action<GenerationStatus> onSuccess = null, Action<string> onError = null)
    {
        Debug.Log("STARTING GENERATION. PROMPT:");
        Debug.Log(prompt);
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
}
