using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class GenerationUI : MonoBehaviour
{
    [Header("Input Section")]
    [SerializeField] private TMP_InputField promptInputField;
    [SerializeField] private Button generateButton;

    [Header("Loading Section")]
    [SerializeField] private GameObject loadingPanel;
    [SerializeField] private Image progressBarFillImage;
    [SerializeField] private TMP_Text statusMessageText;
    [SerializeField] private TMP_Text errorText;

    [Header("Logic Reference")]
    [SerializeField] private GameGenerationManager generationManager;

    private void Start()
    {
        generateButton.onClick.AddListener(OnGenerateClicked);
        HideLoadingUI();
        HideError();
    }

    private void OnGenerateClicked()
    {
        string prompt = promptInputField.text.Trim();

        if (string.IsNullOrEmpty(prompt))
        {
            ShowError("Prompt cannot be empty.");
            return;
        }

        HideError();
        ShowLoadingUI("Starting generation...");
        SetInteractable(false);

        generationManager.StartGeneration(prompt);
    }

    public void UpdateProgressBar(float progress)
    {
        progressBarFillImage.fillAmount = Mathf.Clamp01(progress);
    }

    public void UpdateStatusText(string message)
    {
        statusMessageText.text = message;
    }

    public void ShowError(string message)
    {
        errorText.text = message;
        errorText.gameObject.SetActive(true);
    }

    public void HideError()
    {
        errorText.text = "";
        errorText.gameObject.SetActive(false);
    }

    public void ShowLoadingUI(string initialMessage = "")
    {
        loadingPanel.SetActive(true);
        UpdateProgressBar(0f);
        statusMessageText.text = initialMessage;
    }

    public void HideLoadingUI()
    {
        loadingPanel.SetActive(false);
    }

    public void SetInteractable(bool interactable)
    {
        generateButton.interactable = interactable;
        promptInputField.interactable = interactable;
    }

    public void ResetUI()
    {
        SetInteractable(true);
        HideLoadingUI();
        HideError();
    }
}
