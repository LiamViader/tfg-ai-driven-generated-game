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
    private string eventId;
    private string baseUrl = "http://localhost:8000/game";
    private int lastProcessedLength = 0;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject); // Opcional, si querés que sobreviva entre escenas
        }
        else
        {
            Destroy(gameObject); // Evita duplicados si la escena lo tiene varias veces
        }
    }

    public void StartStream(string eventId)
    {
        this.eventId = eventId;
        StartCoroutine(ConnectToEventStream());
    }

    private IEnumerator ConnectToEventStream()
    {
        string url = $"{baseUrl}/event/stream/{eventId}";
        Debug.Log($"[NarrativeStreamerAPI] Connecting to stream: {url}");

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Accept", "text/event-stream");

            var async = request.SendWebRequest();

            while (!async.isDone)
            {
                string fullText = request.downloadHandler.text;

                if (!string.IsNullOrEmpty(fullText) && fullText.Length > lastProcessedLength)
                {
                    string newText = fullText.Substring(lastProcessedLength);
                    lastProcessedLength = fullText.Length;

                    string[] lines = newText.Split(new[] { "\n\n" }, StringSplitOptions.RemoveEmptyEntries);

                    foreach (string line in lines)
                    {
                        if (line.StartsWith("data: "))
                        {
                            string jsonPayload = line.Substring(6).Trim();

                            try
                            {
                                StreamedMessage parsed = JsonConvert.DeserializeObject<StreamedMessage>(jsonPayload);

                                SimpleMainThreadDispatcher.Instance.Enqueue(() =>
                                {
                                    NarrativeEventManager.Instance.OnParsedMessageReceived(parsed);
                                });
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
            {
                Debug.LogError($"[NarrativeStreamerAPI] Stream error: {request.error}");
            }
            else
            {
                Debug.Log($"[NarrativeStreamerAPI] Stream finished successfully.");
            }
        }
    }
}