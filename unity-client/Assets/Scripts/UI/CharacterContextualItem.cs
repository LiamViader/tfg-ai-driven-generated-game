using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ContextualMenuItem : MonoBehaviour
{
    [SerializeField] private TMP_Text _labelText;
    private System.Action _onClick;
    [SerializeField] private Button _button;

    public string ConditionId { get; private set; }
    private void Awake()
    {
        if (_button == null)
        {
            return;
        }

        _button.enabled = true;
        _button.onClick.AddListener(Trigger);
    }

    public void Initialize(string label, System.Action onClick, string conditionId)
    {
        ConditionId = conditionId;
        _labelText.text = label;
        _onClick = onClick;
    }

    public void Trigger()
    {
        Debug.Log("BUTTON CLICKED");
        _onClick?.Invoke();
    }
}