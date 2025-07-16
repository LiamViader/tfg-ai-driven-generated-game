using System;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public static class AssetsAPI
{
    private static readonly string baseUrl = "http://localhost:8000/assets/image";

    public static IEnumerator GetImage(string relativePath, Action<Texture2D> onSuccess, Action<string> onError = null)
    {
        string url = $"{baseUrl}?path={UnityWebRequest.EscapeURL(relativePath)}";

        using var request = UnityWebRequestTexture.GetTexture(url);
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success || request.responseCode >= 400)
        {
            Debug.LogError($"[AssetsAPI] Failed to load image: {request.error} ({request.responseCode})");
            onError?.Invoke(request.error);
            yield break;
        }

        var texture = DownloadHandlerTexture.GetContent(request);
        onSuccess?.Invoke(texture);
    }
}
