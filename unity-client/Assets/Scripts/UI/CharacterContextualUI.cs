using UnityEngine;
using DG.Tweening;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using System.Collections.Generic;

public class CharacterContextualUI : MonoBehaviour
{
    [SerializeField] private Canvas _canvas;
    [SerializeField] private Transform _itemsParent;

    private bool _showing = false;
    public bool IsAnimatingShow { get; private set; } = false;
    public bool IsAnimatingHide { get; private set; } = false;

    private System.Action _onHideCallback;

    private void OnEnable()
    {
        if (_canvas != null && Camera.main != null)
        {
            _canvas.worldCamera = Camera.main;
        }
    }

    void Update()
    {
        if (_showing && !IsAnimatingShow && !IsAnimatingHide && Input.GetMouseButtonDown(0))
        {
            if (!IsPointerOverAnyItemWithSpacing())
            {
                HideContextualMenu();
            }
        }
    }

    private bool IsPointerOverAnyItemWithSpacing()
    {
        Vector2 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);

        float spacing = 0f;
        VerticalLayoutGroup layoutGroup = _itemsParent.GetComponent<VerticalLayoutGroup>();
        if (layoutGroup != null)
        {
            spacing = layoutGroup.spacing;
        }

        foreach (Transform item in _itemsParent)
        {
            RectTransform rect = item.GetComponent<RectTransform>();
            if (rect == null) continue;

            Vector3[] worldCorners = new Vector3[4];
            rect.GetWorldCorners(worldCorners);

            float extra = spacing / 2f;

            if (PointInExpandedRect(mouseWorldPos, worldCorners, extra))
            {
                return true;
            }
        }

        return false;
    }

    private bool PointInExpandedRect(Vector2 point, Vector3[] corners, float verticalPadding)
    {
        float minX = corners[0].x;
        float maxX = corners[2].x;
        float minY = corners[0].y - verticalPadding;
        float maxY = corners[2].y + verticalPadding;

        return point.x >= minX && point.x <= maxX &&
               point.y >= minY && point.y <= maxY;
    }

    public void ShowContextualMenu(Transform contextualMenuOrigin, bool right, System.Action onHide = null)
    {
        if (_canvas == null || IsAnimatingShow || IsAnimatingHide) return;

        _onHideCallback = onHide;

        RectTransform rect = _canvas.GetComponent<RectTransform>();
        rect.pivot = right ? new Vector2(0f, 1f) : new Vector2(1f, 1f);

        _canvas.gameObject.SetActive(true);
        _canvas.transform.SetParent(contextualMenuOrigin, worldPositionStays: false);
        _canvas.transform.localPosition = Vector3.zero;
        _canvas.transform.localRotation = Quaternion.identity;
        _canvas.transform.localScale = Vector3.one;

        _showing = true;
        AnimateAppearItems();
    }

    public void HideContextualMenu()
    {
        if (_canvas == null || !gameObject.activeInHierarchy || IsAnimatingHide || IsAnimatingShow) return;

        AnimateHideItems(() =>
        {
            _canvas.gameObject.SetActive(false);

        });
    }

    public void AnimateAppearItems()
    {
        int childCount = _itemsParent.childCount;
        float itemDuration = 0.4f;
        float overlap = 0.2f;

        IsAnimatingShow = true;

        Sequence fullSequence = DOTween.Sequence();

        for (int i = 0; i < childCount; i++)
        {
            Transform item = _itemsParent.GetChild(i);
            RectTransform rt = item.GetComponent<RectTransform>();
            CanvasGroup cg = item.GetComponent<CanvasGroup>();

            if (cg == null)
                cg = item.gameObject.AddComponent<CanvasGroup>();

            rt.localScale = new Vector3(1f, 0f, 1f);
            cg.alpha = 0f;

            Sequence itemSequence = DOTween.Sequence();
            itemSequence.Join(rt.DOScaleY(1f, itemDuration).SetEase(Ease.OutBack));
            itemSequence.Join(cg.DOFade(1f, itemDuration * 0.8f).SetEase(Ease.Linear));

            fullSequence.Insert(i * (itemDuration - overlap), itemSequence);
        }

        float totalDuration = itemDuration + (childCount - 1) * (itemDuration - overlap);
        fullSequence.OnComplete(() => IsAnimatingShow = false);
    }

    public void AnimateHideItems(System.Action onComplete)
    {
        int childCount = _itemsParent.childCount;
        float duration = 0.2f;

        IsAnimatingHide = true;

        Sequence hideSequence = DOTween.Sequence();

        for (int i = 0; i < childCount; i++)
        {
            Transform item = _itemsParent.GetChild(i);
            RectTransform rt = item.GetComponent<RectTransform>();
            CanvasGroup cg = item.GetComponent<CanvasGroup>();

            if (cg == null)
                cg = item.gameObject.AddComponent<CanvasGroup>();

            hideSequence.Join(rt.DOScaleX(0f, duration).SetEase(Ease.InBack));
            hideSequence.Join(cg.DOFade(0f, duration * 1.5f).SetEase(Ease.Linear));
        }

        _showing = false;
        _onHideCallback?.Invoke();
        _onHideCallback = null;
        hideSequence.OnComplete(() =>
        {
            IsAnimatingHide = false;
            onComplete?.Invoke();
        });
    }
}
