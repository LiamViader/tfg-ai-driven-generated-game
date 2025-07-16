using System;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public static class HttpUtils
{
    public static IEnumerator Get<T>(string url, Action<T> onSuccess, Action<string> onError = null)
    {
        using var request = UnityWebRequest.Get(url);
        request.downloadHandler = new DownloadHandlerBuffer();

        yield return request.SendWebRequest();

        var responseText = request.downloadHandler?.text;

        if (request.result != UnityWebRequest.Result.Success || request.responseCode >= 400)
        {
            Debug.LogError($"GET {url} failed: {request.error} ({request.responseCode})");
            onError?.Invoke(responseText ?? request.error);
            yield break;
        }

        try
        {
            T data = JsonUtility.FromJson<T>(responseText);
            onSuccess?.Invoke(data);
        }
        catch (Exception ex)
        {
            Debug.LogError($"GET {url} JSON parse error: {ex.Message}");
            onError?.Invoke($"Invalid JSON: {ex.Message}");
        }
    }

    public static IEnumerator Post<T>(string url, object payload, Action<T> onSuccess, Action<string> onError = null)
    {
        string json = JsonUtility.ToJson(payload);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(json);

        using var request = new UnityWebRequest(url, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        var responseText = request.downloadHandler?.text;

        if (request.result != UnityWebRequest.Result.Success || request.responseCode >= 400)
        {
            Debug.LogError($"POST {url} failed: {request.error} ({request.responseCode})");
            onError?.Invoke(responseText ?? request.error);
            yield break;
        }

        try
        {
            T data = JsonUtility.FromJson<T>(responseText);
            onSuccess?.Invoke(data);
        }
        catch (Exception ex)
        {
            Debug.LogError($"POST {url} JSON parse error: {ex.Message}");
            onError?.Invoke($"Invalid JSON: {ex.Message}");
        }
    }

    public static IEnumerator Post(string url, object payload, Action onSuccess = null, Action<string> onError = null)
    {
        string json = JsonUtility.ToJson(payload);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(json);

        using var request = new UnityWebRequest(url, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        var responseText = request.downloadHandler?.text;

        if (request.result != UnityWebRequest.Result.Success || request.responseCode >= 400)
        {
            Debug.LogError($"POST {url} failed: {request.error} ({request.responseCode})");
            onError?.Invoke(responseText ?? request.error);
        }
        else
        {
            onSuccess?.Invoke();
        }
    }
}
