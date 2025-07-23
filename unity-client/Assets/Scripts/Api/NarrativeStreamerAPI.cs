using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using System;
using Newtonsoft.Json;
using Api.Models;

public class NarrativeStreamerAPI : MonoBehaviour
{
    public static NarrativeStreamerAPI Instance { get; private set; }
    private string _eventId;
    private string _baseUrl = "http://localhost:8000/game";
    private int _lastProcessedLength = 0;

    private void Awake()
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

    // Llamar para arrancar el primer stream
    public void StartStream(string eventId)
    {
        _eventId = eventId;
        _lastProcessedLength = 0;
        StartCoroutine(ConnectToEventStream());
    }

    private IEnumerator ConnectToEventStream()
    {
        string url = $"{_baseUrl}/event/stream/{_eventId}";
        yield return StreamCoroutine(url);
    }

    public void SendPlayerChoice(string choiceLabel)
    {
        StartCoroutine(ChoiceThenResumeCoroutine(choiceLabel));
    }

    private IEnumerator ChoiceThenResumeCoroutine(string choiceLabel)
    {
        // 1) POST de la elección
        string postUrl = $"{_baseUrl}/event/{_eventId}/choice";
        var payload = new { choice_label = choiceLabel };
        string json = JsonConvert.SerializeObject(payload);

        using (var request = new UnityWebRequest(postUrl, "POST"))
        {
            byte[] body = Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(body);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"[NarrativeStreamerAPI] Choice POST error: {request.error}");
                yield break;
            }
        }

        // 2) Limpiar estado y UI antes de reenganchar SSE
        SimpleMainThreadDispatcher.Instance.Enqueue(() =>
            NarrativeEventManager.Instance.PrepareForResumeAfterChoice()
        );

        // 3) Volver a escuchar SSE desde la ruta principal
        _lastProcessedLength = 0;
        yield return StreamCoroutine($"{_baseUrl}/event/stream/{_eventId}");
    }

    // Rutina común para leer cualquier SSE
    private IEnumerator StreamCoroutine(string url)
    {
        Debug.Log($"[NarrativeStreamerAPI] Connecting to stream: {url}");
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Accept", "text/event-stream");

            var async = request.SendWebRequest();

            while (!async.isDone)
            {
                string fullText = request.downloadHandler.text;
                if (!string.IsNullOrEmpty(fullText) && fullText.Length > _lastProcessedLength)
                {
                    string newText = fullText.Substring(_lastProcessedLength);
                    _lastProcessedLength = fullText.Length;

                    string[] lines = newText.Split(new[] { "\n\n" }, StringSplitOptions.RemoveEmptyEntries);
                    foreach (string line in lines)
                    {
                        if (line.StartsWith("data: "))
                        {
                            string jsonPayload = line.Substring(6).Trim();
                            try
                            {
                                StreamedMessage parsed = JsonConvert.DeserializeObject<StreamedMessage>(jsonPayload);
                                Debug.Log(parsed.content);
                                SimpleMainThreadDispatcher.Instance.Enqueue(() =>
                                    NarrativeEventManager.Instance.OnParsedMessageReceived(parsed)
                                );
                            }
                            catch (Exception ex)
                            {
                                Debug.LogError($"[NarrativeStreamerAPI] Error parsing JSON: {ex.Message}\nPayload: {jsonPayload}");
                            }
                        }
                    }
                }
                yield return null;
            }

            if (request.result != UnityWebRequest.Result.Success)
                Debug.LogError($"[NarrativeStreamerAPI] Stream error: {request.error}");
            else
            {
                Debug.Log($"[NarrativeStreamerAPI] Stream finished successfully.");
                // *** Aquí notificamos ***
                SimpleMainThreadDispatcher.Instance.Enqueue(() =>
                {
                    NarrativeEventManager.Instance.OnStreamCompleted();
                });
            }
        }
    }
}
