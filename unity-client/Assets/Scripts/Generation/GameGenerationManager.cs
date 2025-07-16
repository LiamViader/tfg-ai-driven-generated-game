using UnityEngine;
using System.Collections;
using Api.Models;

public class GameGenerationManager : MonoBehaviour
{
    [SerializeField] private GenerationUI ui;

    public void StartGeneration(string prompt)
    {
        StartCoroutine(RunGenerationFlow(prompt));
    }

    private IEnumerator RunGenerationFlow(string prompt)
    {
        bool isDone = false;

        ui.HideError();
        ui.ShowLoadingUI();
        ui.SetInteractable(false);

        // 1. Launch generation
        yield return StartCoroutine(GenerationAPI.StartGeneration(
            prompt,
            onSuccess: status =>
            {
                Debug.Log("Generation started.");
                // status is usually "started", so nothing else here
            },
            onError: error =>
            {
                Debug.LogError($"Failed to start generation: {error}");
                ui.ShowError("Failed to start generation.");
                ui.HideLoadingUI();
                ui.SetInteractable(true);
                isDone = true;
            }
        ));

        if (isDone) yield break;

        // 2. Polling loop
        while (!isDone)
        {
            yield return StartCoroutine(GenerationAPI.GetStatus(
                onSuccess: status =>
                {
                    ui.UpdateProgressBar(status.progress);
                    ui.UpdateStatusText(status.message);

                    if (status.status == "done")
                    {
                        StartCoroutine(LoadFullState());
                        isDone = true;
                    }
                    else if (status.status == "error")
                    {
                        ui.ShowError("Generation failed.");
                        ui.HideLoadingUI();
                        ui.SetInteractable(true);
                        isDone = true;
                    }
                },
                onError: error =>
                {
                    Debug.LogError($"Error polling status: {error}");
                    ui.ShowError("Connection error while polling status.");
                    ui.HideLoadingUI();
                    ui.SetInteractable(true);
                    isDone = true;
                }
            ));

            if (!isDone)
                yield return new WaitForSeconds(1f);
        }
    }

    private IEnumerator LoadFullState()
    {
        bool loaded = false;

        yield return StartCoroutine(GenerationAPI.GetFullState(
            onSuccess: changeset =>
            {
                Debug.Log("Full game state received:");
                Debug.Log(JsonUtility.ToJson(changeset, true));
                ui.HideLoadingUI();
                ui.SetInteractable(true);
                loaded = true;
                // TODO: Pass changeset to your game state system
            },
            onError: error =>
            {
                Debug.LogError($"Failed to get full state: {error}");
                ui.ShowError("Failed to retrieve game state.");
                ui.HideLoadingUI();
                ui.SetInteractable(true);
                loaded = true;
            }
        ));

        yield return null;
    }
}
