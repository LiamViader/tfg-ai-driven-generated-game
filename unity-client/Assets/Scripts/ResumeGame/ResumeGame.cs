using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using Api.Models;
using TMPro;
public class ResumeGame : MonoBehaviour
{
    [SerializeField] private Button resumeButton;
    void Start()
    {
        resumeButton.onClick.AddListener(StartLoading);
    }

    private void StartLoading()
    {
        StartCoroutine(LoadFullState());
    }

    private IEnumerator LoadFullState()
    {
        bool hasError = false;

        yield return StartCoroutine(StateAPI.GetFullState(
            onSuccess: changeset =>
            {
                Debug.Log("Full game state received:");
                Debug.Log(JsonUtility.ToJson(changeset, true));

                var applier = new ChangeSetApplier();
                applier.Apply(changeset);
            },
            onError: error =>
            {
                Debug.LogError($"Failed to get full state: {error}");
                hasError = true;
            }
        ));

        if (hasError)
            yield break;


        ImageLoadTracker.Instance.OnAllImagesLoaded(() =>
        {
            GameManager.Instance.InitializeWorld();
        });
    }
}
