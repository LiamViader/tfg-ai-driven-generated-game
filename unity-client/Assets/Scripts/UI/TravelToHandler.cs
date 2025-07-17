using UnityEngine;
using UnityEngine.UI;
using DG.Tweening;
using System.Collections.Generic;
using TMPro;

public class TravelToHandler : MonoBehaviour
{
    [SerializeField] private Button _northButton;
    [SerializeField] private Button _southButton;
    [SerializeField] private Button _eastButton;
    [SerializeField] private Button _westButton;
    [SerializeField] private float animationDuration = 0.3f;
    [SerializeField] private float fadeOnlyHideOffset = 40f;
    [SerializeField] private float delayAfterClick = 0.4f;
    [SerializeField] private float hideDurationNormal = 0.2f;
    [SerializeField] private float hideDurationSelected = 1.5f;

    [SerializeField] private Button _showOptionsButton;
    [SerializeField] private Button _backgroundBlocker;

    private Dictionary<Button, Vector2> _originalPositions = new();
    private List<Button> _allButtons;
    private bool _isAnimating = false;

    private void Awake()
    {
        _allButtons = new List<Button> { _northButton, _southButton, _eastButton, _westButton };

        foreach (var button in _allButtons)
        {
            RectTransform rt = button.GetComponent<RectTransform>();
            _originalPositions[button] = rt.anchoredPosition;
            button.gameObject.SetActive(false);
        }

        _showOptionsButton.onClick.AddListener(() =>
        {
            if (_isAnimating) return;
            ShowOptions();
        });
    }

    private void SetupButton(Button button, string direction, string connectedScenarioId)
    {
        button.gameObject.SetActive(true);

        var label = button.GetComponentInChildren<TMP_Text>();
        if (label != null)
        {
            var scenario = GameManager.Instance.GetScenario(connectedScenarioId);
            label.text = scenario != null ? scenario.name : connectedScenarioId;
        }

        RectTransform rt = button.GetComponent<RectTransform>();
        CanvasGroup cg = GetOrAddCanvasGroup(button.gameObject);

        Vector2 targetPos = _originalPositions[button];
        rt.anchoredPosition = Vector2.zero;
        rt.localScale = Vector3.zero;
        cg.alpha = 0f;

        button.onClick.RemoveAllListeners();
        button.onClick.AddListener(() =>
        {
            _isAnimating = true;
            HideAllExcept(button);
            GameManager.Instance.TravelTo(connectedScenarioId);
            DOVirtual.DelayedCall(delayAfterClick, () =>
            {
                HideBlocker();
                HideButton(button, hideDurationSelected, 0f, () =>
                {
                    _isAnimating = false; // desbloquear al terminar el último botón
                });
            });
        });

        rt.DOAnchorPos(targetPos, animationDuration).SetEase(Ease.OutBack);
        rt.DOScale(Vector3.one, animationDuration).SetEase(Ease.OutBack);
        cg.DOFade(1f, animationDuration * 0.25f).SetEase(Ease.OutQuad);
    }
    private void HideAllExcept(Button except)
    {
        int toHide = 0;
        int hidden = 0;

        foreach (var button in _allButtons)
        {
            if (button == except || !button.gameObject.activeSelf) continue;
            toHide++;

            HideButton(button, hideDurationNormal, 0f);
        }

        if (toHide == 0)
            _isAnimating = false;
    }

    private void HideButton(Button button, float duration, float delay, System.Action onComplete = null)
    {
        RectTransform rt = button.GetComponent<RectTransform>();
        CanvasGroup cg = GetOrAddCanvasGroup(button.gameObject);

        Vector2 targetPos = _originalPositions[button];

        Sequence s = DOTween.Sequence();
        s.AppendInterval(delay);
        s.Join(rt.DOAnchorPos(targetPos, duration).SetEase(Ease.InOutQuad));
        s.Join(cg.DOFade(0f, duration).SetEase(Ease.Linear));
        s.Join(rt.DOScale(0.9f, duration).SetEase(Ease.InOutQuad));
        s.OnComplete(() =>
        {
            button.gameObject.SetActive(false);
            onComplete?.Invoke();
        });
    }

    public void ShowOptions()
    {
        if (_isAnimating) return;
        _isAnimating = true;

        ShowBlocker(() =>
        {
            if (_isAnimating) return;
            HideAll();
        });

        foreach (var button in _allButtons)
            button.gameObject.SetActive(false);

        var currentScenario = GameManager.Instance.GetScenario(GameManager.Instance.CurrentScenarioId);
        if (currentScenario == null)
        {
            Debug.LogError("No se encontró el escenario actual.");
            _isAnimating = false;
            return;
        }

        var dirMap = new Dictionary<string, Button>
        {
            { "north", _northButton },
            { "south", _southButton },
            { "east",  _eastButton },
            { "west",  _westButton },
        };

        foreach (var kvp in currentScenario.connectionIdsByDirection)
        {
            string dir = kvp.Key;
            string connectionId = kvp.Value;

            var connection = GameManager.Instance.GetConnection(connectionId);
            if (connection == null || !dirMap.ContainsKey(dir)) continue;

            string otherId = connection.scenarioAId == currentScenario.id
                ? connection.scenarioBId
                : connection.scenarioAId;

            SetupButton(dirMap[dir], dir, otherId);
        }

        DOVirtual.DelayedCall(animationDuration, () => _isAnimating = false);
    }

    public void HideAll()
    {
        if (_isAnimating) return;
        HideBlocker();
        _isAnimating = true;

        int total = 0;
        int completed = 0;

        foreach (var button in _allButtons)
        {
            if (!button.gameObject.activeSelf) continue;

            total++;
            HideButton(button, hideDurationNormal, 0f, () =>
            {
                completed++;
                if (completed >= total)
                    _isAnimating = false;
            });
        }

        if (total == 0)
            _isAnimating = false;

    }

    private CanvasGroup GetOrAddCanvasGroup(GameObject go)
    {
        CanvasGroup cg = go.GetComponent<CanvasGroup>();
        if (cg == null)
            cg = go.AddComponent<CanvasGroup>();
        return cg;
    }

    public void ShowBlocker(System.Action onClickOutside)
    {
        if (_backgroundBlocker == null) return;

        _backgroundBlocker.gameObject.SetActive(true);
        _backgroundBlocker.onClick.RemoveAllListeners();
        _backgroundBlocker.onClick.AddListener(() =>
        {
            onClickOutside?.Invoke();
            if (!_isAnimating) HideBlocker();
        });
    }

    public void HideBlocker()
    {
        if (_backgroundBlocker == null) return;

        _backgroundBlocker.onClick.RemoveAllListeners();
        _backgroundBlocker.gameObject.SetActive(false);
    }

}
